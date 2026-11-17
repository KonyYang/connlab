"""One-machine development relocation coordinator. Never deletes sources or restores a database automatically.

The CLI profile is deliberately fixed to the reviewed 2026-11-17 inventory. Python
fixtures can supply a synthetic profile; this is not an end-user migration feature.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sqlite3
import sys
from dataclasses import dataclass

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.domain import ExternalResourceType
from backend.domain.project_library import ProjectLibraryConflict
from backend.infrastructure.project_library.files import (
    atomic_json, checked_path, copy_verified, inventory, read_json, identity,
)
from backend.infrastructure.project_library.ownership import capture, transform_paths
from backend.infrastructure.storage.repositories.material_archive import MaterialArchiveRepository, normalized
from backend.infrastructure.storage.repositories.material_receipt import MaterialReceiptRepository
from backend.infrastructure.storage.repositories.external_resources import ExternalResourceRepository
from backend.infrastructure.storage.models_project_library import MaterialArchiveFolderModel
from backend.application.external_resource_service import ExternalResourceService

@dataclass(frozen=True)
class Relocation:
    kind: str
    key: str
    source: Path
    target: Path


def local_profile():
    project_ids = {
        "DL-2024-12-050": "d34ffc06013042128ed0c71ae95d6c7c",
        "DL-2025-02-054": "d9764e8dbbf64597ad873d02f9cc1710",
        "DL-2026-01-072": "9400d97e31d0402283c0c7bc1f81b4b2",
        "DL-2026-11-013": "b9ea5f68db534edc84d906bf2650adaa",
    }
    archives = {"DL-2026-04-032": "ef5e038cefbd43cb86bc0807bbf7057c",
                "DL-2026-05-001": "e894aff9c09f44e4a0046ca835f8242a"}
    rows = [Relocation("project", key, Path("D:/ConnLabProjectsDev")/name, Path("D:/ConnLabDev/Projects")/name) for name,key in project_ids.items()]
    rows += [Relocation("archive", key, Path("D:/ConnLabMaterials")/name, Path("D:/ConnLabDev/Materials")/name) for name,key in archives.items()]
    for name in ("Cable Assy Signal Porton Partial Qualification Testing_OPS", "Coolpower HD 3.5mm product qulification test", "PBU Pro BTB Connector system with cable assembly Qulification Testing_NPD"):
        rows.append(Relocation("temporary", name, Path("D:/ConnLabProjectsTemporary")/name, Path("D:/ConnLabDev/TemporaryMaterials")/name))
    return rows


def business_inventory(entries):
    return [row for row in entries if row["relative_path"] != ".connlab" and not row["relative_path"].startswith(".connlab/")]


class DevelopmentRelocation:
    def __init__(self, settings, engine, rows, evidence_dir, config_paths=()):
        if settings.environment != "development" or settings.library_root:
            raise ValueError("This reviewed relocation is only for the existing standalone development data instance.")
        self.settings, self.engine, self.rows = settings, engine, tuple(rows)
        self.evidence = checked_path(evidence_dir, must_exist=False)
        self.config_paths = tuple(Path(path) for path in config_paths)
        self.journal = self.evidence/"relocation.json"

    def _save(self, state): atomic_json(self.journal, state)

    def prepare(self):
        if self.journal.exists():
            state=read_json(self.journal)
            expected=[(row.kind,row.key,str(row.source),str(row.target)) for row in self.rows]
            actual=[(row['kind'],row['key'],row['source'],row['target']) for row in state['items']]
            if expected!=actual or state['database']!=str(self.settings.database_path):
                raise ProjectLibraryConflict("The retained relocation belongs to another profile or data instance.")
            return state
        # Inventory all inputs and reject target collisions before creating any output.
        items=[]
        with Session(self.engine) as session:
            from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
            members=ProjectLibraryRepository(session)
            archives=MaterialArchiveRepository(session)
            resources=ExternalResourceRepository(session)
            receipt_settings=MaterialReceiptRepository(session).settings()
            for row in self.rows:
                source=checked_path(row.source); target=checked_path(row.target,must_exist=False)
                if target.exists() or target.is_relative_to(source) or source.is_relative_to(target):
                    raise ProjectLibraryConflict(f"Destination conflict; retained unchanged: {target}")
                current=members.member(row.key) if row.kind=='project' else archives.folder(row.key) if row.kind=='archive' else None
                if current and normalized(current['folder_path'])!=normalized(source):
                    raise ProjectLibraryConflict(f"The registered source changed: {source}")
                if row.kind=='archive':
                    operation=archives.operation(current['operation_id']) if current['operation_id'] else None
                    if operation and operation['status']!='completed':
                        raise ProjectLibraryConflict("Finish the pending archive operation before relocation.")
                caches=[record.folder_id for record in session.scalars(select(MaterialArchiveFolderModel).where(MaterialArchiveFolderModel.normalized_path==normalized(source)))]
                items.append(dict(kind=row.kind,key=row.key,source=str(source),target=str(target),
                    source_identity=identity(source), entries=inventory(source), before=current, cache_ids=caches,
                    business_before=capture(session,current['project_id'],validate_history=False) if row.kind=='project' and current['project_id'] else None,phase='prepared'))
            before_resources=[dict(kind=value.resource_type.value,path=str(value.path),active=value.active) for value in resources.list_all() if value.resource_type in {ExternalResourceType.PROJECT_OUTPUT_ROOT, ExternalResourceType.TEMPORARY_MATERIALS_ROOT}]
            # Legacy receipt rows have a separate revision contract. This reviewed machine has none.
            if MaterialReceiptRepository(session).catalog():
                raise ProjectLibraryConflict("Unexpected legacy receipt entries require a separate exact-reference review.")
        self.evidence.mkdir(parents=True,exist_ok=False)
        backup=self.evidence/'development-before.sqlite3'
        with sqlite3.connect(self.settings.database_path.as_uri()+'?mode=ro',uri=True) as source, sqlite3.connect(backup) as target:
            source.backup(target)
            if target.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
                raise RuntimeError('The recovery database did not pass integrity_check.')
        configs=[]
        for index,path in enumerate(self.config_paths):
            if path.is_file():
                target=self.evidence/f'config-{index}-{path.name}'
                with path.open('rb') as source, target.open('xb') as destination: shutil.copyfileobj(source,destination)
                configs.append(dict(source=str(path),backup=str(target)))
        state=dict(version=1,database=str(self.settings.database_path),database_identity=identity(self.settings.database_path),
            database_backup=str(backup),configs=configs,before_resources=before_resources,before_materials=receipt_settings,
            status='prepared',items=items,retained=['D:/ConnLabProjectsDev/DL-2026-11-003: missing business folder; no member; held',
            'D:/ConnLabProjects: release-owned directories and seven development historical references held'],
            recovery='Keep writers stopped. Do not overwrite a live database. The consistent SQLite backup, config copies and unchanged source directories allow operator-reviewed recovery. Interrupted location changes resume with the saved original plan. Never delete either copy automatically.')
        self._save(state)
        return state

    def apply(self, *, writers_stopped=False):
        if not writers_stopped:
            raise ValueError('Stop and coordinate development writers before applying this reviewed relocation.')
        state=self.prepare()
        if identity(self.settings.database_path)!=state['database_identity']:
            raise ProjectLibraryConflict('The database file changed since preparation; restart the review.')
        from backend.api.routes_project_library import get_project_library_service
        for item in state['items']:
            source,target=Path(item['source']),Path(item['target'])
            if identity(source)!=item['source_identity'] or inventory(source)!=item['entries']:
                raise ProjectLibraryConflict(f'The retained source changed: {source}')
            if item['phase']=='prepared':
                item['phase']='copying';self._save(state)
                copy_verified(source,target,item['entries'])
                item['phase']='copied';self._save(state)
            elif item['phase']=='copying':
                raise ProjectLibraryConflict('An interrupted copy was retained. Its ownership must be reviewed before resuming; no existing target will be adopted or overwritten.')
            with Session(self.engine) as session:
                archives=MaterialArchiveRepository(session)
                if item['kind']=='project' and item['phase']!='completed':
                    service=get_project_library_service(session=session,settings=self.settings)
                    if 'plan' not in item:
                        item['plan']=service.location_plan(item['key'],str(target));self._save(state)
                    plan=item['plan']
                    result=service.change(item['key'],plan['plan_id'],plan['fingerprint'],'location')
                    before=item['before']
                    if any(result[key]!=before[key] for key in ('project_id','ltr_number','title')):
                        raise ProjectLibraryConflict('A business identity changed during relocation. Retain both copies and recovery evidence.')
                if item['kind'] in {'project','archive'}:
                    for folder_id in item['cache_ids']:
                        root=target.parent if item['kind']=='archive' else ''
                        archives.rebind_directory(folder_id,source,target,root)
                item['phase']='completed';self._save(state)
            if business_inventory(inventory(target))!=business_inventory(item['entries']):
                raise ProjectLibraryConflict('Business-file verification failed after reference updates. Keep all copies and evidence.')
        # Switch configured roots only after every verified copy and reference update succeeded.
        with Session(self.engine) as session:
            resources=ExternalResourceRepository(session)
            service=ExternalResourceService(resources)
            root_by_kind={row.kind:row.target.parent for row in self.rows}
            for kind,resource_kind in [('project',ExternalResourceType.PROJECT_OUTPUT_ROOT),('temporary',ExternalResourceType.TEMPORARY_MATERIALS_ROOT)]:
                if kind not in root_by_kind: continue
                current=resources.get_by_type(resource_kind)
                old=next((row for row in state['before_resources'] if row['kind']==resource_kind.value),None)
                if current and str(current.path) not in {str(root_by_kind[kind]),old['path'] if old else ''}:
                    raise ProjectLibraryConflict('The configured root changed while relocation was in progress.')
                service.upsert_resource(resource_kind,root_by_kind[kind],True)
            receipt=MaterialReceiptRepository(session)
            if 'archive' in root_by_kind:
                if receipt.settings()['root_path'] not in {state['before_materials']['root_path'],str(root_by_kind['archive'])}:
                    raise ProjectLibraryConflict('The configured materials root changed while relocation was in progress.')
                receipt.configure(str(root_by_kind['archive']))
            session.commit()
        state['status']='completed';self._save(state)
        return self.verify()

    def verify(self):
        state=read_json(self.journal)
        from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
        with Session(self.engine) as session:
            projects=ProjectLibraryRepository(session); archives=MaterialArchiveRepository(session)
            for item in state['items']:
                source,target=Path(item['source']),Path(item['target'])
                if inventory(source)!=item['entries'] or identity(source)!=item['source_identity']:
                    raise ProjectLibraryConflict('A retained source no longer matches its recovery manifest.')
                if business_inventory(inventory(target))!=business_inventory(item['entries']):
                    raise ProjectLibraryConflict('The new business files differ from their verified source.')
                current=projects.member(item['key']) if item['kind']=='project' else archives.folder(item['key']) if item['kind']=='archive' else None
                if current and normalized(current['folder_path'])!=normalized(target):
                    raise ProjectLibraryConflict('An active reference still uses its old location.')
                if item['kind']=='project':
                    before=item['before']
                    if any(current[key]!=value for key,value in before.items() if key not in {'folder_path','revision'}):
                        raise ProjectLibraryConflict('Non-location project membership changed during relocation.')
                    if item.get('business_before'):
                        def replace_path(value):
                            path=Path(value)
                            return str(target/path.relative_to(source)) if path.is_absolute() and path.is_relative_to(source) else value
                        expected=transform_paths(item['business_before'],replace_path)
                        actual=capture(session,current['project_id'],validate_history=False)
                        ordered=lambda graph: {key:sorted(records,key=lambda row:json.dumps(row,sort_keys=True,ensure_ascii=False)) for key,records in graph.items()}
                        if ordered(expected)!=ordered(actual):
                            raise ProjectLibraryConflict('Business state differs beyond the supported path reference updates.')
                    workspace=projects.workspace(current['project_id'])
                    if workspace and not Path(workspace['local_workspace_path']).is_relative_to(target):
                        raise ProjectLibraryConflict('The working project still uses an old location.')
        state['verified_at']=datetime.now(timezone.utc).isoformat()
        self._save(state)
        return state


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository-root',type=Path,default=Path('D:/PythonProject/connlab'))
    parser.add_argument('--evidence-dir',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--writers-stopped',action='store_true')
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    root=checked_path(args.repository_root)
    if root!=Path('D:/PythonProject/connlab').resolve():
        parser.error('The CLI is restricted to the reviewed primary development repository.')
    if not args.evidence_dir.resolve().is_relative_to(Path('D:/ConnLabDev/MigrationBackups').resolve()):
        parser.error('Keep this run under D:/ConnLabDev/MigrationBackups.')
    from backend.api.development import apply_development_environment_defaults
    from backend.shared.config import Settings
    from backend.infrastructure.storage.database import create_database_engine
    apply_development_environment_defaults(root)
    settings=Settings.load(base_dir=root)
    if settings.database_path.resolve()!=root/'data/connlab.sqlite3':
        parser.error('The selected database is not the reviewed primary development database.')
    engine=create_database_engine(settings)
    try:
        coordinator=DevelopmentRelocation(settings,engine,local_profile(),args.evidence_dir,
            [root/'connlab.local.toml',root/'connlab.admin.toml'])
        result=coordinator.verify() if args.verify else coordinator.apply(writers_stopped=args.writers_stopped) if args.apply else coordinator.prepare()
        print(json.dumps(dict(status=result['status'],evidence=str(coordinator.journal),items=len(result['items'])),ensure_ascii=False))
    finally: engine.dispose()

if __name__=='__main__': main()
