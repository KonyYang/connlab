"""Owned same-volume staging and bounded archive folder discovery."""
from pathlib import Path
from uuid import uuid4
import os
import re
import hashlib
import logging
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
from threading import Event,Lock
from backend.infrastructure.project_library.material_receipt_files import MaterialReceiptFiles
from backend.infrastructure.project_library.files import checked_path,identity
from backend.infrastructure.project_library.search_files import internal_material_path

logger=logging.getLogger(__name__)

class MaterialArchiveFiles(MaterialReceiptFiles):
    def lock(self):
        return self.control.journal.lock('materials-archive')

    def publication_lock(self):
        return self.control.lock()

    def configuration_files(self):
        return MaterialReceiptFiles(self.settings)

    def direct(self, root, path):
        root=checked_path(root); path=checked_path(path)
        if not path.is_dir() or path.parent!=root or path.name.casefold()==".connlab":
            raise ValueError("Choose a direct project folder inside the materials library, not its root or a nested folder.")
        return path

    def children(self, root):
        root=checked_path(root)
        result=[]
        for child in sorted(root.iterdir(),key=lambda p:p.name.casefold()):
            if child.name.casefold() in {'.connlab','system volume information','$recycle.bin'}: continue
            try:
                child=checked_path(child)
                if child.is_dir(): result.append(child)
            except (OSError,ValueError): continue
        return result

    def source(self, root, source):
        root=checked_path(root);source=checked_path(source)
        if not source.is_dir() or source.name.casefold()=='.connlab': raise ValueError("Choose one project folder, not an internal control directory.")
        if source==root or root.is_relative_to(source): raise ValueError("Source and materials library must not contain each other.")
        if source.is_relative_to(root): self.direct(root,source)
        return source

    def check_cancel(self):
        if getattr(self,'cancellation',None) is not None and self.cancellation.is_set():
            raise ArchiveCancelled('Receipt or scan cancelled. Already received files are retained.')

    def digest(self,path):
        digest=hashlib.sha256()
        with path.open('rb') as stream:
            while chunk:=stream.read(1024*1024):
                self.check_cancel();digest.update(chunk)
        return digest.hexdigest()

    def entries(self,source):
        root=checked_path(source);pending=[(root,0)];result=[]
        while pending:
            folder,depth=pending.pop();self.check_cancel()
            if depth>40:raise ValueError('The folder is too deeply nested.')
            for path in folder.iterdir():
                self.check_cancel();path=checked_path(path);relative=path.relative_to(root).as_posix()
                if path.is_dir():
                    result.append(dict(relative_path=relative,directory=True,size=0,sha256=None));pending.append((path,depth+1))
                elif path.is_file():result.append(dict(relative_path=relative,directory=False,size=path.stat().st_size,sha256=self.digest(path)))
                else:raise ValueError('Unsupported filesystem entry: '+relative)
                if len(result)>100000:raise ValueError('The archive exceeds the supported file count.')
        return sorted(result,key=lambda row:row['relative_path'])

    def scan_index(self,source):
        root=checked_path(source);pending=[(root,0)];result=[]
        while pending:
            folder,depth=pending.pop();self.check_cancel()
            if depth>40:raise ValueError('The folder is too deeply nested to index.')
            for path in folder.iterdir():
                self.check_cancel()
                if internal_material_path(path.relative_to(root).as_posix()):continue
                path=checked_path(path)
                if path.is_dir():pending.append((path,depth+1))
                elif path.is_file():result.append(dict(name=path.name,relative_path=path.relative_to(root).as_posix(),modified_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()))
                if len(result)>100000:raise ValueError('The archive exceeds the supported index size.')
        return result

    def matches(self,target,entry,expected):
        root=self.check_root(target,expected)
        path=checked_path(root/entry['target_relative'],must_exist=False)
        return path.is_dir() if entry['directory'] else path.is_file() and self.digest(path)==entry['sha256']

    def publish(self,source,target,entry,expected):
        self.check_cancel();root=self.check_root(target,expected)
        relative=entry['target_relative'];destination=checked_path(root/relative,must_exist=False)
        if not destination.is_relative_to(root):raise ValueError('The receipt path leaves its target folder.')
        if entry['directory']:
            destination.mkdir(parents=True,exist_ok=True);checked_path(destination);return 'copied'
        if destination.exists():
            if destination.is_file() and self.digest(destination)==entry['sha256']:return 'skipped'
            raise ValueError('The destination was changed. Existing files are retained.')
        origin=checked_path(Path(source)/entry['relative_path'])
        destination.parent.mkdir(parents=True,exist_ok=True);checked_path(destination.parent)
        temporary_root=checked_path(root.parent/'pending',must_exist=False)
        temporary_root.mkdir(exist_ok=True);temporary=temporary_root/uuid4().hex
        try:
            digest=hashlib.sha256();size=0
            with origin.open('rb') as reader,temporary.open('xb') as writer:
                while chunk:=reader.read(1024*1024):
                    self.check_cancel();writer.write(chunk);digest.update(chunk);size+=len(chunk)
                writer.flush();os.fsync(writer.fileno())
            if size!=entry['size'] or digest.hexdigest()!=entry['sha256']:raise ValueError('The source changed during copying.')
            self.check_cancel();self.check_root(target,expected);checked_path(destination.parent)
            if os.name=='nt':os.rename(temporary,destination)
            else:os.link(temporary,destination)
            return 'copied'
        finally:temporary.unlink(missing_ok=True)


    def new_stage(self, root, operation_id):
        # Only this namespace is excluded from discovery. Never reuse an unverified instance.
        parent=checked_path(Path(root)/'.connlab'/'receiving',must_exist=False)
        parent.mkdir(parents=True,exist_ok=True);checked_path(parent)
        container=parent/(operation_id+'-'+uuid4().hex)
        container.mkdir();path=container/'payload';path.mkdir()
        return str(path),identity(path)

    def publish_folder(self, stage, target, expected):
        self.check_root(stage,expected)
        target=checked_path(target,must_exist=False)
        if target.exists(): raise ValueError("The target folder appeared during receipt. Existing files were retained.")
        if os.name=='nt': os.rename(stage,target)
        else:
            import ctypes
            library=ctypes.CDLL(None,use_errno=True)
            rename=getattr(library,'renameat2',None)
            if rename is None:raise OSError('This host cannot publish directories without replacement.')
            if rename(-100,os.fsencode(stage),-100,os.fsencode(target),1)!=0:
                raise OSError(ctypes.get_errno(),'Could not publish without replacing an existing folder.')
        self.check_root(target,expected)

    def directory_label(self, path):
        def parse(name):
            match = re.fullmatch(r"(DL-\d{4}-\d{2}-\d{3}[A-Z0-9]*)(?:[\s_-]+(.*))?", name, re.I)
            return (match[1].upper(), (match[2] or "").strip()) if match else (None, name)

        number, title = parse(path.name)
        if number and not title:
            descriptions = set()
            for child in self.children(path):
                self.check_cancel()
                other, description = parse(child.name)
                if other == number and description:
                    descriptions.add(description)
            if len(descriptions) == 1:
                title = descriptions.pop()
        return number, title

    def metadata(self, path):
        title=Path(path).name
        number=re.search(r"\bDL-\d{4}-\d{2}-\d{3}[A-Z0-9]*\b",title,re.I)
        return (number.group(0) if number else None),title


class ArchiveCancelled(ValueError): pass

class ArchiveJobs:
    """Small process-local worker pool; durable receipt identity remains in the existing journal."""
    def __init__(self):
        self.pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix='materials')
        self.lock=Lock();self.jobs={}

    def start(self,action):
        with self.lock:
            for key in list(self.jobs):
                if len(self.jobs)>64 and self.jobs[key]['status'] in {'done','failed','cancelled'}:self.jobs.pop(key)
            if sum(job['status'] in {'working','cancellation_requested'} for job in self.jobs.values())>=4:
                raise ValueError('Materials processing is busy. Cancel or finish the current operation first.')
            key=uuid4().hex;event=Event();job=dict(status='working',event=event)
            self.jobs[key]=job
        def execute():
            try:
                result=action(event)
                with self.lock:job.update(status='cancelled' if event.is_set() else 'done',result=result)
            except ArchiveCancelled as error:
                with self.lock:job.update(status='cancelled',error=str(error))
            except Exception as error:
                logger.exception('Materials background operation failed: %s',key)
                with self.lock:job.update(status='failed',error=str(error))
        self.pool.submit(execute)
        return {'job_id':key}

    def get(self,key):
        with self.lock:
            if key not in self.jobs:raise LookupError('Materials request ended. Check the original receipt result before retrying.')
            return {name:value for name,value in self.jobs[key].items() if name!='event'}

    def cancel(self,key):
        with self.lock:
            if key not in self.jobs:raise LookupError('Materials request not found.')
            job=self.jobs[key]
            if job['status']=='working':job['event'].set();job['status']='cancellation_requested'
        return self.get(key)

archive_jobs=ArchiveJobs()
