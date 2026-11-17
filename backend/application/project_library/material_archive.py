"""Single-folder archival receipt; no business-project adoption or restoration."""
from datetime import datetime,timezone
from pathlib import Path,PureWindowsPath
from uuid import uuid4
import logging
from backend.application.project_library.material_receipt import MaterialReceiptService
from backend.domain.project_library import ProjectLibraryConflict

logger=logging.getLogger(__name__)

class MaterialArchiveService:
    def __init__(self,store,files,catalog):
        self.store,self.files,self.catalog=store,files,catalog

    def _runtime(self):
        return MaterialReceiptService(self.store.receipts,self.files.configuration_files(),self.catalog).runtime(ensure_default=True)

    def refresh(self):
        runtime=self._runtime(); root=runtime['root_path']
        if not runtime['available']:
            self.store.mark_root_unavailable(root)
            return dict(available=False,root_path=root,folders=self.store.catalog(),warnings=['Materials library folder is unavailable. Check its connection in Settings.'])
        warnings=[]
        with self.files.lock():
            operations=self.store.operations()
            by_path={str(Path(op['target_path']).resolve()).casefold():op for op in operations}
            for path in self.files.children(root):
                self.files.check_cancel()
                op=by_path.get(str(path).casefold())
                number,title=self.files.metadata(path)
                try:
                    self.store.register(root,path,number,title,op['batch_id'] if op else None,op['folder_id'] if op else None)
                except Exception:
                    logger.exception('Materials directory registration failed: %s',path)
                    self.files.check_cancel()
                    self.store.rollback();warnings.append('Some materials could not be indexed. Refresh to retry registration.')
                    break
            for entry in self.catalog.catalog():
                self.files.check_cancel()
                if entry.get('intake_status','completed')!='completed':continue
                try:
                    if not self.files.available(entry['folder_path']):
                        self.store.mark_available(entry['folder_path'],False);continue
                    rows=self.files.scan_index(entry['folder_path'])
                    self.store.cache(entry,rows)
                except (ValueError,OSError):
                    self.files.check_cancel()
                    warnings.append('Some materials could not be indexed. Check access and refresh again.')
        return dict(available=True,root_path=root,folders=self.store.catalog(),warnings=list(dict.fromkeys(warnings)))

    def preview(self,source,independent=False):
        runtime=self._runtime()
        if not runtime['available']: raise ValueError('Materials library folder is unavailable. Check Settings.')
        root=Path(runtime['root_path'])
        with self.files.lock():
            source=self.files.source(root,source)
            for op in self.store.operations():
                if op['status']!='completed' and op['root_path']==str(root) and (op['target_path']==str(source) or op['source_path']==str(source) and not independent):
                    return dict(status='pending',operation=op,target_path=op['target_path'],source_path=str(source))
            if source.parent==root:
                number,title=self.files.metadata(source)
                row=self.store.register(root,source,number,title)
                # Existing receipt/project identities own their links and selection state.
                row=self._entry_for_path(source) or row
                self.store.cache(row,self.files.scan_index(source))
                return dict(status='existing',source_path=str(source),target_path=str(source),target_key=row['key'])
            target=root/source.name
            occupied={op['target_path'] for op in self.store.operations() if op['status']!='completed'}
            if target.exists() or str(target) in occupied:
                if not independent:
                    return dict(status='conflict',source_path=str(source),target_path=str(target),target_key=self._key_for_path(target))
                counter=2
                while (root/f'{source.name} ({counter})').exists() or str(root/f'{source.name} ({counter})') in occupied:
                    counter+=1
                target=root/f'{source.name} ({counter})'
            for entry in self.catalog.catalog():
                path=entry.get('folder_path')
                if path and self.files.overlaps(target,path):
                    raise ProjectLibraryConflict('Choose an independent folder; the destination belongs to an existing entry.')
            operation_id,folder_id=uuid4().hex,uuid4().hex
            number,title=self.files.metadata(source)
            entries=self.files.entries(source)
            payload=dict(operation_id=operation_id,folder_id=folder_id,source_path=str(source),target_path=str(target),
                root_path=str(root),binding=self.files.binding(self.store.receipts.settings()),source_identity=self.files.root_identity(source),
                entries=entries,number=number,title=title,created_at=datetime.now(timezone.utc).isoformat())
            plan=self.files.control.save_plan('material_archive',payload)
            return dict(status='ready',source_path=str(source),target_path=str(target),plan_id=plan['plan_id'],fingerprint=plan['fingerprint'],
                batch_id=operation_id,file_count=sum(not row['directory'] for row in entries))

    def _entry_for_path(self,path):
        return next((row for row in self.catalog.catalog() if row.get('folder_path') and PureWindowsPath(path)==PureWindowsPath(row['folder_path'])),None)

    def _key_for_path(self,path):
        entry=self._entry_for_path(path)
        return entry['key'] if entry else None

    def confirm(self,plan_id,fingerprint):
        with self.files.lock():
            plan=self.files.control.plan(plan_id,fingerprint,'material_archive')
            try: operation=self.store.operation(plan['operation_id'])
            except LookupError:
                operation=dict(batch_id=plan['operation_id'],operation='material_archive',folder_id=plan['folder_id'],
                    plan_id=plan_id,fingerprint=fingerprint,status='running',phase='preparing',source_path=plan['source_path'],
                    target_path=plan['target_path'],root_path=plan['root_path'],target_key='archive:'+plan['folder_id'],
                    number=plan['number'],title=plan['title'],created_at=plan['created_at'],stage_path=None,root_identity=None,
                    items=[dict(row,target_relative=row['relative_path'],action='copy',status='pending',message='') for row in plan['entries']],
                    counts={},directory_counts={},message='',receipt_id=None)
                self.store.save(operation)
            return self._continue(plan,operation)

    def retry(self,operation_id):
        op=self.store.operation(operation_id)
        return self.confirm(op['plan_id'],op['fingerprint'])

    def operation(self,operation_id): return self.store.operation(operation_id)

    def _continue(self,plan,op):
        if op['status']=='completed': return op
        if self.files.binding(self.store.receipts.settings())!=plan['binding']:
            raise ProjectLibraryConflict('Materials library folder changed. Restore the original setting to continue this receipt.')
        try:
            final=Path(op['target_path'])
            published=op['root_identity'] is not None and final.exists() and self.files.root_identity(final)==op['root_identity']
            if op['phase']=='index_pending' or published:
                if not published: raise ProjectLibraryConflict('The published directory changed. Existing files were retained.')
                return self._register(plan,op)
            if final.exists(): raise ProjectLibraryConflict('The destination appeared during receipt. Existing files were retained.')
            if self.files.root_identity(plan['source_path'])!=plan['source_identity']:
                raise ProjectLibraryConflict('The source directory changed. Continue only with the original source.')
            if op['root_identity'] is None:
                stage,root_identity=self.files.new_stage(plan['root_path'],op['batch_id'])
                op['stage_path'],op['root_identity']=stage,root_identity
                # No file may be copied until this identity is durable.
                self.store.save(op)
            self.files.check_root(op['stage_path'],op['root_identity'])
            for item in op['items']:
                self.files.check_cancel()
                if item['status'] in {'copied','skipped'}:
                    if not self.files.matches(op['stage_path'],item,op['root_identity']):
                        item['status']='retained_changed';item['message']='A received item was edited or removed; it was retained as-is.'
                    continue
                if item['status']=='retained_changed': continue
                try:
                    item['status']=self.files.publish(plan['source_path'],op['stage_path'],item,op['root_identity'])
                    item['message']=''
                except (ValueError,OSError) as error:
                    self.files.check_cancel()
                    item['status']='failed';item['message']=str(error)
                self.store.save(op)
            if any(item['status'] not in {'copied','skipped'} for item in op['items']):
                return self._incomplete(op,'Some files were not received. Continue this operation; existing files are retained.')
            if self.files.entries(plan['source_path'])!=plan['entries']:
                return self._incomplete(op,'The source changed during receipt. Restore its reviewed contents before continuing.')
            op['phase']='publishing';self.store.save(op)
            with self.files.publication_lock():
                if self.files.binding(self.store.receipts.settings())!=plan['binding']:
                    raise ProjectLibraryConflict('Materials library folder changed before publication. Continue only with its original setting.')
                self.files.publish_folder(op['stage_path'],op['target_path'],op['root_identity'])
            op['phase']='index_pending';self.store.save(op)
            return self._register(plan,op)
        except (ValueError,OSError) as error:
            return self._incomplete(op,str(error))

    def _register(self,plan,op):
        op['phase']='index_pending'
        try:
            row=self.store.register(op['root_path'],op['target_path'],op['number'],op['title'],op['batch_id'],op['folder_id'])
            self.store.cache(row,self.files.scan_index(op['target_path']))
        except Exception:
            logger.exception('Materials registration incomplete for operation %s',op['batch_id'])
            self.store.rollback()
            return self._incomplete(op,'Files are received but registration is incomplete. Continue to repair registration.')
        op['phase']='completed';op['status']='completed';op['message']='';self._counts(op);self.store.save(op)
        return op

    def _counts(self,op):
        op['counts']={status:sum(not row['directory'] and row['status']==status for row in op['items']) for status in ['copied','skipped','failed','retained_changed']}
        op['directory_counts']={status:sum(row['directory'] and row['status']==status for row in op['items']) for status in ['copied','skipped','failed','retained_changed']}

    def _incomplete(self,op,message):
        op['status']='incomplete';op['message']=message;self._counts(op);self.store.save(op)
        return op
