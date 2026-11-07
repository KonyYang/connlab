"""Bounded, durable receipts for saving the two reviewed report files.

This journal, not the authoring JSON projection, owns filesystem recovery stages.
Never infer ownership from matching content alone: staged/archived inode identity
is recorded before exposing a replacement. Existing legacy publication is unchanged.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from backend.application.current_report_update_service import CurrentReportFileConflictError

STAGES = {'planned', 'staged', 'archiving', 'archived', 'publishing', 'published', 'committed', 'unchanged'}
INTENT_FIELDS = ('role', 'source', 'sha256', 'target', 'current', 'old_sha256', 'history_root', 'old_identity')


def intent_digest(data):
    payload = {'project_id': data['project_id'], 'operation_id': data['operation_id'],
        'context': data['context'], 'items': [{key: item.get(key) for key in INTENT_FIELDS} for item in data['items']]}
    return sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def identity(path):
    stat = Path(path).stat()
    if not stat.st_ino:
        raise CurrentReportFileConflictError('The report filesystem cannot prove file identity.')
    return [stat.st_dev, stat.st_ino]


def safe_path(path):
    path = Path(path)
    for part in (path, *path.parents):
        if part.exists() and (part.is_symlink() or getattr(part.lstat(), 'st_file_attributes', 0) & 0x400):
            raise CurrentReportFileConflictError('Report storage redirects through a link. Restore its original location.')
    return path


class ReportDeliveryReceipts:
    def __init__(self, root):
        self.root = Path(root)

    def _folder(self, project_id):
        return safe_path(self.root / sha256(project_id.encode()).hexdigest())

    def _path(self, project_id, operation_id):
        if not re.fullmatch('[a-f0-9]{32}', operation_id):
            raise ValueError('Invalid report save operation.')
        return self._folder(project_id) / (operation_id + '.json')

    def read(self, project_id, operation_id):
        path = safe_path(self._path(project_id, operation_id))
        if not path.is_file():
            raise LookupError('Report save operation not found.')
        if path.stat().st_size > 1024 * 1024:
            raise CurrentReportFileConflictError('Report save receipt is unreadable. Retain it for recovery.')
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            if (data['schema'] != 'connlab.report-delivery-receipt' or data['version'] != 1
                    or data['project_id'] != project_id or data['operation_id'] != operation_id
                    or len(data['items']) not in {1, 2}):
                raise ValueError('identity')
            roles = [item['role'] for item in data['items']]
            if (len(set(roles)) != len(roles) or not set(roles) <= {'internal', 'customer'}
                    or data['status'] not in {'saving', 'completed'}
                    or data.get('intent_sha256') != intent_digest(data)):
                raise ValueError('intent')
            for item in data['items']:
                if item['status'] not in STAGES or not re.fullmatch('[a-f0-9]{64}', item['sha256']):
                    raise ValueError('stage')
                target, history = Path(item['target']), Path(item['history_root'])
                if not target.is_absolute() or not history.is_absolute():
                    raise ValueError('path')
                if item.get('staging'):
                    staging = Path(item['staging'])
                    if staging.parent != target.parent or not staging.name.startswith('.report-') or staging.suffix != '.stage':
                        raise ValueError('staging')
                if item.get('archive') and Path(item['archive']).parent != history:
                    raise ValueError('archive')
            return data
        except (ValueError, KeyError, TypeError) as exc:
            raise CurrentReportFileConflictError('Report save receipt is invalid. Retain files and review recovery.') from exc

    def _write(self, project_id, data):
        path = self._path(project_id, data['operation_id'])
        safe_path(path).parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix='.receipt-', dir=path.parent)
        try:
            with os.fdopen(descriptor, 'w', encoding='utf-8', newline='\n') as stream:
                json.dump(data, stream, ensure_ascii=False, sort_keys=True, allow_nan=False)
                stream.flush(); os.fsync(stream.fileno())
            os.replace(name, path)
        finally:
            Path(name).unlink(missing_ok=True)

    def active(self, project_id):
        folder = self._folder(project_id)
        if not folder.exists():
            return None
        operations = [self.read(project_id, path.stem) for path in folder.glob('*.json')]
        pending = [item for item in operations if item['status'] != 'completed']
        if len(pending) > 1:
            raise CurrentReportFileConflictError('Multiple unfinished report saves require recovery review.')
        return pending[0] if pending else None

    def begin(self, project_id, operation_id, context, items):
        active = self.active(project_id)
        if active:
            if active['operation_id'] != operation_id:
                raise CurrentReportFileConflictError('Resume the unfinished report save before starting another.')
            if active['context'] != context or len(items) != len(active['items']) or any(
                    any(saved.get(key) != item.get(key) for key in INTENT_FIELDS if key != 'old_identity')
                    for saved, item in zip(active['items'], items)):
                raise CurrentReportFileConflictError('The original report save intent changed. Retain it for review.')
            return active
        if self._path(project_id, operation_id).exists():
            return self.read(project_id, operation_id)
        record = self.prepare(project_id, operation_id, context, items)
        self._write(project_id, record)
        return record

    def prepare(self, project_id, operation_id, context, items):
        """Construct the immutable intent before its authoring DB commit."""
        self._path(project_id, operation_id)
        prepared = []
        for item in items:
            current = safe_path(item['current']) if item.get('current') else None
            if 'old_identity' in item and item['old_identity'] != (identity(current) if current else None):
                raise CurrentReportFileConflictError('The target report identity changed after preview.')
            prepared.append({**item, 'status': 'planned', 'old_identity': identity(current) if current else None})
        record = {'schema': 'connlab.report-delivery-receipt', 'version': 1,
            'project_id': project_id, 'operation_id': operation_id, 'context': context,
            'status': 'saving', 'items': prepared}
        record['intent_sha256'] = intent_digest(record)
        return record

    def item(self, project_id, operation_id, role):
        return DeliveryFileReceipt(self, project_id, operation_id, role)

    def complete(self, project_id, operation_id):
        record = self.read(project_id, operation_id)
        if any(item['status'] not in {'committed', 'unchanged'} for item in record['items']):
            raise CurrentReportFileConflictError('Some report files are not saved yet.')
        record['status'] = 'completed'
        self._write(project_id, record)
        return record


class DeliveryFileReceipt:
    def __init__(self, receipts, project_id, operation_id, role):
        self.receipts, self.project_id, self.operation_id, self.role = receipts, project_id, operation_id, role

    def load(self):
        record = self.receipts.read(self.project_id, self.operation_id)
        return next(item for item in record['items'] if item['role'] == self.role)

    def update(self, **values):
        if set(values) & set(INTENT_FIELDS):
            raise ValueError('Report save intent is immutable.')
        record = self.receipts.read(self.project_id, self.operation_id)
        item = next(item for item in record['items'] if item['role'] == self.role)
        item.update(values)
        self.receipts._write(self.project_id, record)
        return item

    def publish(self, files, *, source_path, expected_source_sha256, current_path,
                expected_current_sha256, target_path, history_root, persist, pre_publish=None):
        from backend.infrastructure.files.report_publication_gateway import _reserve_archive_path, ReportFilePublicationResult
        source, target, history = map(safe_path, (source_path, target_path, history_root))
        current = safe_path(current_path) if current_path is not None else None
        item = self.load()
        expected = {'source': str(source), 'sha256': expected_source_sha256, 'target': str(target),
            'current': str(current) if current else None, 'old_sha256': expected_current_sha256,
            'history_root': str(history)}
        if any(item.get(key) != value for key, value in expected.items()):
            raise CurrentReportFileConflictError('Report save locations or reviewed files changed. Retain the receipt for review.')
        if not target.parent.is_dir() or target.suffix.lower() != '.docx':
            raise CurrentReportFileConflictError('The report destination is unavailable.')
        if files.fingerprint(source) != expected_source_sha256:
            raise CurrentReportFileConflictError('The reviewed report changed. Review the current copy again.')

        def validate():
            if pre_publish:
                pre_publish()
            safe_path(target); safe_path(history)
            if files.fingerprint(source) != expected_source_sha256:
                raise CurrentReportFileConflictError('The reviewed report changed during saving.')

        def matches(path, inode, digest):
            return path.is_file() and identity(path) == inode and files.fingerprint(path) == digest

        validate()
        if item['status'] == 'planned':
            if current:
                if not matches(current, item['old_identity'], expected_current_sha256):
                    raise CurrentReportFileConflictError('The current report changed after preview.')
            if target != current and target.exists():
                raise CurrentReportFileConflictError('Another file occupies the report destination.')
            if current == target and expected_current_sha256 == expected_source_sha256:
                result = ReportFilePublicationResult(target, expected_source_sha256, False, None)
                persist(result)
                self.update(status='unchanged', target_identity=identity(target))
                return result
            descriptor, name = tempfile.mkstemp(prefix='.report-', suffix='.stage', dir=target.parent)
            os.close(descriptor)
            staging = Path(name)
            shutil.copy2(source, staging)
            with staging.open('r+b') as stream:
                os.fsync(stream.fileno())
            if files.fingerprint(staging) != expected_source_sha256:
                raise CurrentReportFileConflictError('The staged report changed before saving.')
            archive = _reserve_archive_path(history, current, files._clock()) if current else None
            item = self.update(status='staged', staging=str(staging), staging_identity=identity(staging),
                archive=str(archive) if archive else None, archive_reservation_identity=identity(archive) if archive else None)
        staging = safe_path(item['staging']) if item.get('staging') else None
        archive = safe_path(item['archive']) if item.get('archive') else None
        if item['status'] in {'staged', 'archiving'}:
            validate()
            if not matches(staging, item['staging_identity'], expected_source_sha256):
                raise CurrentReportFileConflictError('The report staging file changed. Retain it for review.')
            if current:
                if matches(archive, item['old_identity'], expected_current_sha256) and not current.exists():
                    pass  # Previous process moved the old file after its durable intent.
                else:
                    if (not matches(current, item['old_identity'], expected_current_sha256)
                            or not matches(archive, item['archive_reservation_identity'], sha256(b'').hexdigest())):
                        raise CurrentReportFileConflictError('Report or History ownership changed. Retain both for recovery review.')
                    self.update(status='archiving')
                    validate()
                    os.replace(current, archive)
            item = self.update(status='archived')
        if item['status'] in {'archived', 'publishing'}:
            validate()
            if archive and not matches(archive, item['old_identity'], expected_current_sha256):
                raise CurrentReportFileConflictError('The recovery History file changed. Retain it for review.')
            if not matches(staging, item['staging_identity'], expected_source_sha256):
                raise CurrentReportFileConflictError('The staged report changed. Retain files for review.')
            if target.exists():
                if not matches(target, item['staging_identity'], expected_source_sha256):
                    raise CurrentReportFileConflictError('The report destination has an unowned file. Do not overwrite it.')
            else:
                self.update(status='publishing')
                validate()
                os.link(staging, target)
            item = self.update(status='published', target_identity=item['staging_identity'])
        if item['status'] not in {'published', 'committed', 'unchanged'}:
            raise CurrentReportFileConflictError('Report save receipt has an unknown stage. Retain files for review.')
        if not matches(target, item['target_identity'], expected_source_sha256):
            raise CurrentReportFileConflictError('The saved report was changed outside this operation.')
        if archive and not matches(archive, item['old_identity'], expected_current_sha256):
            raise CurrentReportFileConflictError('The saved History file changed outside this operation.')
        result = ReportFilePublicationResult(target, expected_source_sha256, item['status'] != 'unchanged', archive)
        persist(result)
        self.update(status='committed' if item['status'] != 'unchanged' else 'unchanged')
        if staging and staging.exists():
            if not matches(staging, item['staging_identity'], expected_source_sha256):
                raise CurrentReportFileConflictError('The staging file changed; it was retained for review.')
            staging.unlink()
        return result
