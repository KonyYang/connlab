"""Project-scoped portable assets and explicit path rebinding, never source SQL access."""
from hashlib import sha256
from pathlib import Path
import shutil
import re
from backend.domain.project_library import ProjectLibraryError, ProjectLibraryConflict
from backend.infrastructure.project_library.files import checked_path, file_hash, inventory
from backend.infrastructure.project_library.ownership import transform_paths

SPECIAL_DATA_ROOTS = ("report_authoring_assets", "report_working_drafts")
JOURNAL_ROOTS = ("project_folder_generation", "official_folder_relocation", "llcr_cr_record_publication", "ir_dwv_record_publication")
REGISTERED_FILE_HASHES = {
    "file_assets": (("path", "sha256"),),
    "intake_assets": (("stored_path", "sha256"),),
    "project_request_material_collection_items": (("source_path", "sha256"), ("target_path", "sha256")),
    "project_output_records": (("output_path", "output_sha256"),),
    "report_draft_revisions": (("file_path", "file_sha256"),),
}
IDENTITY_FILES = {".connlab/library.json", ".connlab/manifest.json"}
FORBIDDEN_NAMES = {"connlab.sqlite3", "local_identity.sqlite3", "local_profile.sqlite3", "connlab.admin.toml"}


def project_inventory(root):
    entries = inventory(root, exclude_portable=True)
    if any(Path(entry["relative_path"]).name.casefold() in FORBIDDEN_NAMES for entry in entries):
        raise ProjectLibraryError("This project contains machine-local database or administrator configuration files. Remove those from the travelling project copy before preparing it.")
    return [entry for entry in entries if entry["relative_path"] not in IDENTITY_FILES]


class PortableAssets:
    def __init__(self, settings, member):
        self.settings, self.member = settings, member
        self.project = checked_path(member["folder_path"])
        self.records = {}
        self.warnings = []

    def encode(self, rows):
        def encode_path(value):
            if value.startswith(("manual:", "shared-package-provenance:")):
                return value
            try:
                path = Path(value)
                if not path.is_absolute():
                    return value
                checked_path(path, must_exist=False)
                if path.is_relative_to(self.project):
                    relative = path.relative_to(self.project).as_posix()
                    if not path.exists():
                        self.warnings.append("A referenced project file or folder is missing: " + relative)
                    return "@project/" + relative
                missing_root = self.settings.data_dir / "project_library_missing"
                if path.is_relative_to(missing_root):
                    self.warnings.append("A referenced location is unavailable or external: " + path.name)
                    return "@missing/" + path.relative_to(missing_root).as_posix()
                if path.name.casefold() in FORBIDDEN_NAMES:
                    raise ProjectLibraryError("A registered file points to machine credentials or a global database; review it before portability.")
                if path.is_file():
                    return self._retain_description(path)
                key = sha256(value.encode()).hexdigest()
                self.warnings.append("A referenced location is unavailable or external: " + path.name)
                return "@missing/" + key + "/" + path.name
            except OSError:
                key = sha256(value.encode()).hexdigest()
                self.warnings.append("A referenced location could not be read.")
                return "@missing/" + key
        transformed = transform_paths(rows, encode_path)
        for row in transformed.get("project_official_workspace_records", []):
            row["template_source_path"] = "@resource/project_folder_template"
        project_hash = sha256(self.member["project_id"].encode()).hexdigest()
        for name in SPECIAL_DATA_ROOTS:
            folder = self.settings.data_dir / name / project_hash
            if folder.is_dir():
                for entry in inventory(folder):
                    if not entry["directory"]:
                        self._retain_description(folder / entry["relative_path"], force_data=True)
        return transformed

    def warn_registered_changes(self, rows, project_files):
        # Reuse this capture's verified hashes; registered hashes remain evidence,
        # rather than being updated to accept a user's ordinary file edit.
        actual = {self.project / item["relative_path"]: item["sha256"]
                  for item in project_files if not item["directory"]}
        actual.update({Path(item["source_path"]): item["sha256"] for item in self.records.values()})
        for name, columns in REGISTERED_FILE_HASHES.items():
            for row in rows.get(name, []):
                for path_column, hash_column in columns:
                    value, expected = row.get(path_column), row.get(hash_column)
                    if not value or not isinstance(expected, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", expected):
                        continue
                    path = Path(value)
                    if not path.is_absolute():
                        continue
                    path = path.resolve()
                    current = actual.get(path)
                    if current is None or current.casefold() == expected.casefold():
                        continue
                    label = path.relative_to(self.project).as_posix() if path.is_relative_to(self.project) else path.name
                    self.warnings.append("A registered file has changed: " + label + ". Review it against the saved test data.")

    def _retain_description(self, path, *, force_data=False):
        path = checked_path(path)
        digest = file_hash(path)
        suffix = path.suffix.lower()
        blob = digest + suffix
        relative = path.relative_to(self.settings.data_dir) if path.is_relative_to(self.settings.data_dir) else None
        special = relative and relative.parts[0] in SPECIAL_DATA_ROOTS
        token = "@data/" + relative.as_posix() if special or force_data else "@asset/" + blob
        key = sha256(token.encode()).hexdigest()
        self.records[key] = {"key": key, "token": token, "blob": blob, "sha256": digest,
                             "size_bytes": path.stat().st_size, "source_path": str(path)}
        return token

    def descriptors(self):
        return [{key: value for key, value in record.items() if key != "source_path"} for record in sorted(self.records.values(), key=lambda row: row["key"])]

    def copy_to(self, portable_root):
        destination = checked_path(portable_root, must_exist=False) / "assets"
        destination.mkdir(parents=True, exist_ok=True)
        for record in self.records.values():
            source = checked_path(record["source_path"])
            target = destination / record["blob"]
            if target.exists():
                if file_hash(target) != record["sha256"]:
                    raise ProjectLibraryConflict("A portable asset already exists with different content.")
            else:
                with source.open("rb") as reader, target.open("xb") as writer:
                    shutil.copyfileobj(reader, writer)
            if target.stat().st_size != record["size_bytes"] or file_hash(target) != record["sha256"] or file_hash(source) != record["sha256"]:
                raise ProjectLibraryConflict("A source asset changed while preparing the snapshot.")

    @staticmethod
    def restore_assets(source_root, descriptors, settings, project_id):
        source_root = checked_path(source_root)
        for record in descriptors:
            token, blob = record["token"], record["blob"]
            if Path(blob).name != blob or "/" in blob or "\\" in blob:
                raise ProjectLibraryError("The snapshot asset name is invalid.")
            source = checked_path(source_root / ".connlab" / "portable" / "assets" / blob)
            if source.stat().st_size != record["size_bytes"] or file_hash(source) != record["sha256"]:
                raise ProjectLibraryConflict("A portable source asset is missing or changed.")
            target = decode_path(token, settings, settings.projects_dir, project_id)
            checked_path(target, must_exist=False)
            if not target.is_relative_to(settings.data_dir.resolve()):
                raise ProjectLibraryError("The snapshot asset escapes application storage.")
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if not target.is_file() or file_hash(target) != record["sha256"]:
                    raise ProjectLibraryConflict("An existing target asset has different content.")
            else:
                with source.open("rb") as reader, target.open("xb") as writer:
                    shutil.copyfileobj(reader, writer)
            if file_hash(target) != record["sha256"]:
                raise ProjectLibraryConflict("The restored asset could not be verified.")


def decode_path(token, settings, project_root, project_id=None):
    if token.startswith("@data/"):
        parts = Path(token[len("@data/"):]).parts
        expected = sha256(project_id.encode()).hexdigest() if project_id else None
        if len(parts) < 3 or parts[0] not in SPECIAL_DATA_ROOTS or parts[1] != expected or any(part.casefold() in FORBIDDEN_NAMES for part in parts):
            raise ProjectLibraryError("The portable asset is outside this project's supported data partition.")
    if token.startswith("@asset/") and not re.fullmatch(r"@asset/[a-f0-9]{64}(?:\.[a-z0-9]+)?", token):
        raise ProjectLibraryError("The portable content-addressed asset path is invalid.")
    mappings = {"@project/": Path(project_root), "@data/": settings.data_dir,
                "@asset/": settings.data_dir / "project_library_assets",
                "@missing/": settings.data_dir / "project_library_missing"}
    if token == "@resource/project_folder_template":
        return settings.templates_dir
    for prefix, root in mappings.items():
        if token.startswith(prefix):
            relative = Path(token[len(prefix):])
            if relative.is_absolute() or ".." in relative.parts:
                raise ProjectLibraryError("A portable path escapes its target storage.")
            target = checked_path(root / relative, must_exist=False)
            if not target.is_relative_to(root.resolve()):
                raise ProjectLibraryError("A portable path escapes its target storage.")
            return target
    return None


def decode_rows(rows, settings, project_root):
    project_id = rows["projects"][0]["project_id"]
    def replace(value):
        decoded = decode_path(value, settings, project_root, project_id)
        if decoded is not None:
            return str(decoded)
        if value and not value.startswith(("manual:", "shared-package-provenance:")):
            raise ProjectLibraryError("The snapshot contains an unbound file location.")
        return value
    result = transform_paths(rows, replace)
    for row in result.get("project_official_workspace_records", []):
        row["template_source_path"] = str(settings.templates_dir)
    return result
