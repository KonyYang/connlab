"""Report evidence candidates, never inferred business authority or automatic imports."""
from pathlib import PurePosixPath
from collections import Counter


def describe_candidate(relative_path):
    """Filename hints select a UI default only; mappings remain unconfirmed."""
    path = PurePosixPath(relative_path)
    name = path.name.casefold()
    if any(part.casefold() in {'history', 'archive', 'archives', 'backup', 'backups',
                               'temp', 'tmp', 'stage', '.connlab', '.git', '__pycache__'}
           or '.connlab-backup-' in part.casefold() for part in path.parts):
        return {'status': 'excluded', 'suggested_role': None, 'reason': 'History, temporary or application-managed material is excluded.'}
    if name.startswith('~$') or path.suffix.casefold() in {'.tmp', '.bak', '.lock'}:
        return {'status': 'excluded', 'suggested_role': None, 'reason': 'Temporary, locked-workfile or backup output is excluded.'}
    suffix = path.suffix.casefold()
    if suffix == '.zip' and name.endswith('_reportresults.zip'):
        return {'status': 'candidate', 'suggested_role': 'tools_result_package', 'reason': 'Tools package candidate; its contents and hashes are validated only when selected.'}
    roles = {'.png': 'photo', '.jpg': 'photo', '.jpeg': 'photo', '.docx': 'evidence',
             '.xlsx': 'evidence', '.csv': 'evidence', '.pdf': 'evidence', '.txt': 'evidence'}
    if suffix not in roles:
        return {'status': 'unsupported', 'suggested_role': None, 'reason': 'This format has no direct report source import. Prepare it with the relevant Tools tool or retain it outside this report.'}
    return {'status': 'candidate', 'suggested_role': roles[suffix],
            'reason': 'Choose its source role and confirm its meaning; the filename does not establish Group, Step or Pass.'}


class ReportInventory:
    def __init__(self, files):
        self.files = files

    def scan(self, project_id):
        result = self.files.scan(project_id, describe=describe_candidate)
        for item in result['items']:
            if item['status'] != 'candidate':
                continue
            limit = 220 if item['suggested_role'] == 'tools_result_package' else 50
            if not item['size_bytes'] or item['size_bytes'] > limit * 1024 * 1024:
                item.update(status='unsupported', suggested_role=None,
                            reason=f'Choose nonempty evidence smaller than {limit} MB; this file is empty or exceeds the limit.')
        names = Counter(item['name'].casefold() for item in result['items'] if item['status'] == 'candidate')
        for item in result['items']:
            item['duplicate_name'] = item['status'] == 'candidate' and names[item['name'].casefold()] > 1
            if item['duplicate_name']:
                item['reason'] += ' Other folders contain the same filename. Review the relative source location before selecting.'
        return result

    def read_selected(self, project_id, *, root_token, relative_path, file_token):
        description = describe_candidate(relative_path)
        if description['status'] != 'candidate':
            raise ValueError(description['reason'])
        return self.files.read_selected(project_id, root_token=root_token,
                                        relative_path=relative_path, file_token=file_token)
