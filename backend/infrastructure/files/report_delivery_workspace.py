"""Trusted project-ID resolution for saving already-generated reports."""
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifestGateway, stable_folder_identity
from backend.infrastructure.files.report_delivery_receipt import safe_path, identity
from backend.domain.report_authoring import ReportAuthoringConflict


class ReportDeliveryWorkspace:
    def __init__(self, metadata, files):
        self.metadata, self.files = metadata, files

    def _authority(self, project_id):
        data = self.metadata(project_id)
        workspace, configured = data['workspace'], data['configured_root']
        if workspace is None or configured is None:
            raise ValueError('Create or link the registered project folder before saving reviewed reports.')
        root = safe_path(configured)
        local, official, manifest_path = map(safe_path, (workspace.local_workspace_path,
            workspace.official_folder_path, workspace.manifest_path))
        if (not root.is_dir() or not local.is_dir() or not official.is_dir() or not manifest_path.is_file()
                or local == root or not local.is_relative_to(root) or official.parent != local
                or workspace.source_book_path != local / 'Source Book'
                or manifest_path != local / '.connlab' / 'manifest.json'):
            raise ValueError('The registered project folder is unavailable or no longer matches Settings. Restore or link it before saving.')
        manifest = OfficialWorkspaceManifestGateway().read(manifest_path)
        if (manifest.get('project_id') != project_id or manifest.get('dl_number') != workspace.dl_number
                or manifest.get('local_workspace_path') != str(local)
                or manifest.get('official_project_folder_path') != str(official)
                or (manifest.get('official_folder_identity') is not None
                    and manifest['official_folder_identity'] != stable_folder_identity(official))):
            raise ValueError('The project folder identity changed. Link the correct folder before saving.')
        facts = {'workspace': asdict(workspace), 'root': str(root), 'root_identity': identity(root),
            'local_identity': identity(local), 'official_identity': identity(official),
            'manifest_sha256': sha256(manifest_path.read_bytes()).hexdigest(), 'project_context': data.get('context')}
        signature = sha256(json.dumps(facts, sort_keys=True, default=str).encode()).hexdigest()
        return workspace, signature

    def snapshot(self, project_id):
        workspace, signature = self._authority(project_id)
        folder, history = Path(workspace.official_folder_path), Path(workspace.local_workspace_path) / 'History' / 'Report'
        safe_path(history)
        internal = self.files.discover_internal_reports(official_folder=folder, dl_number=workspace.dl_number)
        customer = self.files.discover_customer_reports(folder=folder, dl_number=workspace.dl_number)
        if len(internal) > 1 or len(customer) > 1:
            raise ValueError('Multiple current reports were found. Keep one Internal Report and one customer report before saving.')
        items = []
        for role, candidates, name in [('internal', internal, f'{workspace.dl_number} Internal Report.docx'),
                                      ('customer', customer, f'{workspace.dl_number}-CR Customer Report.docx')]:
            current = safe_path(candidates[0]) if candidates else None
            target = current or folder / name
            items.append({'role': role, 'current': str(current) if current else None, 'target': str(target),
                'old_sha256': self.files.fingerprint(current) if current else None,
                'old_identity': identity(current) if current else None, 'history_root': str(history)})
        return {'authority_sha256': signature, 'items': items}

    def revalidate(self, project_id, snapshot):
        _, signature = self._authority(project_id)
        if signature != snapshot['authority_sha256']:
            raise ReportAuthoringConflict('Project folder registration or identity changed during report saving. Retain files and review recovery.')
