"""Read-only evidence discovery within the existing project-library identity."""
from hashlib import sha256
from itertools import islice
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import stat

from backend.domain.project_library import ProjectLibraryConflict, ProjectLibraryError
from backend.infrastructure.project_library.files import checked_path, fingerprint, identity, read_json


class ReportEvidenceInventory:
    MAX_ENTRIES = 4000
    MAX_DEPTH = 20
    MAX_SOURCE_BYTES = 220 * 1024 * 1024

    def __init__(self, library_files, library_store):
        self.files = library_files
        self.store = library_store

    def _binding(self, project_id):
        context = self.store.project_context(project_id)
        if context['registry_state'] != 'active':
            raise ProjectLibraryConflict('Restore this project before selecting report evidence.')
        workspace = context.get('workspace')
        association = self.store.imported_identity(project_id)
        member = self.store.member(association['member_id']) if association else None
        if not workspace and not member:
            raise ProjectLibraryError('No controlled project folder is linked. Manual source upload remains available.')
        if member and (member.get('project_id') != project_id or member.get('is_history')):
            raise ProjectLibraryConflict('The project folder membership is no longer active.')
        root = checked_path(workspace['local_workspace_path'] if workspace else member['folder_path'])
        if not root.is_dir():
            raise ProjectLibraryError('The controlled project folder is unavailable. Manual source upload remains available.')
        if member and (checked_path(member['folder_path']) != root or self.files.pending_change(member['member_id'])):
            raise ProjectLibraryConflict('Reconnect or finish the pending project location change before selecting evidence.')
        if self.files.pending_replacement_gate(project_id):
            raise ProjectLibraryConflict('Finish project-folder replacement recovery before selecting evidence.')
        marker_path = root / '.connlab' / 'library.json'
        if marker_path.exists() and checked_path(marker_path).stat().st_size > 1024 * 1024:
            raise ProjectLibraryError('The project library marker exceeds the supported size.')
        marker = self.files.marker(root)
        if marker is not None and (not isinstance(marker, dict) or marker.get('format_version') != 1):
            raise ProjectLibraryError('The project library marker is malformed or has an unsupported version.')
        number = workspace['dl_number'] if workspace else member.get('ltr_number')
        if marker and ((marker.get('project_id') or marker.get('source_project_id')) != project_id
                       or marker.get('ltr_number') != number):
            raise ProjectLibraryConflict('The folder marker belongs to another project or LTR.')
        if member and (not marker or marker.get('member_id') != member['member_id']):
            raise ProjectLibraryConflict('The project library folder identity cannot be verified.')
        manifest = None
        business_identity = None
        if workspace:
            manifest_path = checked_path(root / '.connlab' / 'manifest.json')
            if manifest_path.stat().st_size > 1024 * 1024:
                raise ProjectLibraryError('The project identity manifest exceeds the supported size.')
            manifest = read_json(manifest_path)
            if not isinstance(manifest, dict) or manifest.get('schema_version', 1) != 1:
                raise ProjectLibraryError('The project identity manifest version is unsupported.')
            if manifest.get('project_id') != project_id or manifest.get('dl_number') != number:
                raise ProjectLibraryConflict('The project identity manifest belongs to another project or LTR.')
            if (not isinstance(manifest.get('local_workspace_path'), str)
                    or not isinstance(manifest.get('official_project_folder_path'), str)
                    or Path(manifest['local_workspace_path']) != root
                    or Path(manifest['official_project_folder_path']) != Path(workspace['official_folder_path'])):
                raise ProjectLibraryConflict('The project folder location changed. Reconnect its identity before selecting evidence.')
            view = member or {'folder_path': str(root), 'ltr_number': number, 'project_id': project_id}
            business = self.files.workspace_business(view, workspace, root)
            if not business['ready'] or not business.get('candidate'):
                raise ProjectLibraryConflict(business['warning'] or 'The business folder is not verified.')
            business_identity = identity(business['candidate'])
        # Registry revision also advances for unrelated report-source writes;
        # it is not directory identity and must not invalidate other selections.
        token = fingerprint({'project_id': project_id,
                             'root': str(root), 'root_identity': identity(root), 'workspace': workspace,
                             'member_revision': member.get('revision') if member else None,
                             'marker': marker, 'manifest': manifest, 'business_identity': business_identity})
        return root, token

    @staticmethod
    def _file_token(root_token, relative, info):
        return fingerprint([root_token, relative, info.st_dev, info.st_ino, info.st_size,
                            info.st_mtime_ns, info.st_ctime_ns])

    def scan(self, project_id, *, describe):
        try:
            root, token = self._binding(project_id)
        except (OSError, ValueError) as error:
            reason = str(error) if isinstance(error, ProjectLibraryError) else 'The controlled project folder cannot be read or verified. Manual source upload remains available.'
            return {'available': False, 'reason': reason, 'root_token': None, 'items': [], 'warnings': []}
        items, warnings = [], []
        pending = [(root, 0)]
        count = 0
        while pending:
            directory, depth = pending.pop()
            try:
                checked_path(directory)
                with os.scandir(directory) as stream:
                    entries = sorted(islice(stream, self.MAX_ENTRIES - count + 1), key=lambda item: item.name.casefold())
            except (OSError, ValueError):
                warnings.append(f'{directory.relative_to(root).as_posix()}: unavailable or redirected; not scanned.')
                continue
            for entry in entries:
                count += 1
                if count > self.MAX_ENTRIES:
                    warnings.append('The evidence inventory limit was reached. Narrow the project materials before rescanning.')
                    pending.clear()
                    break
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                description = describe(relative)
                try:
                    checked_path(path)
                    # Windows scandir metadata has zero inode/device fields;
                    # use an actual lstat for the later opened-handle identity.
                    info = path.stat(follow_symlinks=False)
                    directory_entry = stat.S_ISDIR(info.st_mode)
                    if directory_entry and description['status'] != 'excluded':
                        if depth >= self.MAX_DEPTH:
                            warnings.append(f'{relative}: nesting limit reached; not scanned.')
                        else:
                            pending.append((path, depth + 1))
                        continue
                    if not directory_entry and not stat.S_ISREG(info.st_mode):
                        raise ProjectLibraryError('Unsupported filesystem entry.')
                    if not directory_entry and info.st_size > self.MAX_SOURCE_BYTES:
                        description = {'status': 'unsupported', 'suggested_role': None, 'reason': 'This file exceeds the report evidence size limit.'}
                    items.append({'relative_path': relative, 'name': entry.name, 'size_bytes': None if directory_entry else info.st_size,
                                  'modified_ns': str(info.st_mtime_ns), 'file_token': self._file_token(token, relative, info), **description})
                except (OSError, ValueError):
                    items.append({'relative_path': relative, 'name': entry.name, 'size_bytes': None,
                                  'modified_ns': None, 'file_token': None, 'status': 'blocked', 'suggested_role': None,
                                  'reason': 'This entry is unavailable or redirected; it was not read.'})
        try:
            if self._binding(project_id)[1] != token:
                raise ProjectLibraryConflict('The project folder identity changed during discovery. Rescan before selecting evidence.')
        except (OSError, ValueError) as error:
            return {'available': False, 'reason': str(error) if isinstance(error, ProjectLibraryError) else 'The project folder changed during discovery.',
                    'root_token': None, 'items': [], 'warnings': warnings}
        return {'available': True, 'reason': '', 'root_token': token,
                'items': sorted(items, key=lambda item: item['relative_path'].casefold()), 'warnings': warnings}

    def read_selected(self, project_id, *, root_token, relative_path, file_token):
        relative = PurePosixPath(relative_path)
        if (not relative_path or relative.is_absolute() or PureWindowsPath(relative_path).drive
                or '\\' in relative_path or ':' in relative_path or '\x00' in relative_path
                or any(part in {'', '.', '..'} for part in relative_path.split('/'))):
            raise ProjectLibraryError('Choose one file inside the controlled project folder.')
        root, token = self._binding(project_id)
        if token != root_token:
            raise ProjectLibraryConflict('The project folder identity changed. Rescan before selecting evidence.')
        path = checked_path(root.joinpath(*relative.parts))
        if not path.is_relative_to(root) or not path.is_file():
            raise ProjectLibraryError('Choose one file inside the controlled project folder.')
        before = path.stat()
        if self._file_token(token, relative_path, before) != file_token:
            raise ProjectLibraryConflict('The selected file changed. Rescan and review its current version.')
        if before.st_size <= 0 or before.st_size > self.MAX_SOURCE_BYTES:
            raise ProjectLibraryError('Choose nonempty evidence within the supported size limit.')
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            if self._file_token(token, relative_path, opened) != file_token:
                raise ProjectLibraryConflict('The selected file changed while it was being opened.')
            content = stream.read(self.MAX_SOURCE_BYTES + 1)
            after = os.fstat(stream.fileno())
        checked_path(path)
        if (len(content) != before.st_size or self._file_token(token, relative_path, after) != file_token
                or self._file_token(token, relative_path, path.stat()) != file_token or self._binding(project_id)[1] != token):
            raise ProjectLibraryConflict('The selected file or project identity changed while reading. Rescan before selecting evidence.')
        return {'file_name': path.name, 'content': content, 'sha256': sha256(content).hexdigest(), 'source_locator': relative_path}
