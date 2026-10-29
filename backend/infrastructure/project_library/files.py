"""Bounded local file operations and durable library-owned review plans."""
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import file_digest, sha256
import json
import os
from pathlib import Path
import re
import shutil
from uuid import uuid4
from backend.domain.project_library import ProjectLibraryConflict, ProjectLibraryError
from backend.infrastructure.files.generation_journal import GenerationJournal

NUMBER = re.compile(r"\bDL-\d{4}-\d{2}-\d{3}(?:[A-Z][A-Z0-9]*)?\b", re.I)
SOFTWARE_MARKER = Path(".connlab") / "library.json"
PORTABLE_FILE = Path(".connlab") / "portable" / "snapshot.json"


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(value):
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def checked_path(value, *, must_exist=True):
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ProjectLibraryError("Choose an absolute folder path.")
    for parent in (*reversed(path.parents), path):
        if parent.exists() or parent.is_symlink():
            info = parent.lstat()
            if parent.is_symlink() or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ProjectLibraryError("Redirected paths cannot be used for project storage.")
    if must_exist and not path.exists():
        raise ProjectLibraryError("The selected location is unavailable.")
    return path.resolve()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def atomic_json(path, value):
    path = checked_path(path, must_exist=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / ("write-" + uuid4().hex + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_json(path):
    path = checked_path(path)
    if path.stat().st_size > 128 * 1024 * 1024:
        raise ProjectLibraryError("The project metadata exceeds the supported size.")
    try:
        with path.open("r", encoding="utf-8-sig") as stream:
            return json.load(stream)
    except (ValueError, UnicodeError) as error:
        raise ProjectLibraryError("Project metadata is damaged. Restore a verified copy.") from error


def safe_name(title):
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", title)
    title = " ".join(title.split()).rstrip(". ")
    if not title or title.casefold() in {"con", "prn", "aux", "nul"} or re.fullmatch(r"(com|lpt)[1-9]", title, re.I):
        raise ProjectLibraryError("Enter a usable project title.")
    return title[:150].rstrip(". ")


def identity(path):
    info = checked_path(path).stat()
    return [info.st_dev, info.st_ino]


def inventory(root, *, exclude_portable=False):
    root = checked_path(root)
    result = []
    pending = [(root, 0)]
    while pending:
        directory, depth = pending.pop()
        if depth > 40:
            raise ProjectLibraryError("The project folder is too deeply nested.")
        for path in sorted(directory.iterdir(), key=lambda child: child.name.casefold()):
            relative = path.relative_to(root).as_posix()
            if exclude_portable and (relative == ".connlab/portable" or relative.startswith(".connlab/portable/")):
                continue
            checked_path(path)
            if path.is_dir():
                result.append({"relative_path": relative, "directory": True, "size": 0, "sha256": None})
                pending.append((path, depth + 1))
            elif path.is_file():
                result.append({"relative_path": relative, "directory": False, "size": path.stat().st_size, "sha256": file_hash(path)})
            else:
                raise ProjectLibraryError("The project contains an unsupported filesystem entry.")
            if len(result) > 100000:
                raise ProjectLibraryError("The project exceeds the supported file count.")
    return sorted(result, key=lambda row: row["relative_path"])


def copy_verified(source, target, entries):
    source = checked_path(source)
    target = checked_path(target, must_exist=False)
    if target.exists():
        raise ProjectLibraryConflict("The destination already exists; review the intake again.")
    required = sum(item["size"] for item in entries)
    target.parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(target.parent).free < required + 1024 * 1024:
        raise ProjectLibraryError("There is not enough free space to receive this project.")
    target.mkdir()
    for entry in entries:
        relative = Path(entry["relative_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ProjectLibraryError("A project entry escapes its directory.")
        origin, destination = source / relative, target / relative
        checked_path(origin)
        checked_path(destination, must_exist=False)
        if entry["directory"]:
            destination.mkdir(parents=True, exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with origin.open("rb") as reader, destination.open("xb") as writer:
                shutil.copyfileobj(reader, writer, 1024 * 1024)
                writer.flush()
                os.fsync(writer.fileno())
            if destination.stat().st_size != entry["size"] or file_hash(destination) != entry["sha256"]:
                raise ProjectLibraryConflict("A source file changed while it was being copied. Review and retry.")
    if inventory(source) != entries:
        raise ProjectLibraryConflict("Source files changed during intake. Review the source again.")


class LibraryFiles:
    def __init__(self, settings, *, destination_configured=None):
        self.settings = settings
        self.destination_configured = bool(settings.library_root) if destination_configured is None else destination_configured
        self.root = settings.data_dir / "project_library"
        self.plans = self.root / "plans"
        self.stage = self.root / "stage"
        self.journal = GenerationJournal(self.root / "locks")
        self.changes = GenerationJournal(self.root / "changes")

    def lock(self):
        return self.journal.lock("library")

    def save_plan(self, kind, payload):
        if kind in {"intake", "restore"}:
            payload = {**payload, "destination_binding": self.destination_binding()}
        plan_id = uuid4().hex
        body = {"kind": kind, "payload": payload, "created_at": now()}
        value = {"plan_id": plan_id, "fingerprint": fingerprint(body), **body}
        atomic_json(self.plans / (plan_id + ".json"), value)
        return value

    def plan(self, plan_id, expected, kind):
        if not re.fullmatch(r"[a-f0-9]{32}", plan_id):
            raise ProjectLibraryError("The review identity is invalid.")
        value = read_json(self.plans / (plan_id + ".json"))
        body = {key: value[key] for key in ("kind", "payload", "created_at")}
        if value["kind"] != kind or value["fingerprint"] != expected or fingerprint(body) != expected:
            raise ProjectLibraryConflict("The review changed. Refresh before confirming.")
        if kind in {"intake", "restore"} and value["payload"].get("destination_binding") != self.destination_binding():
            raise ProjectLibraryConflict("The save location changed. Check the selected projects again before importing.")
        return value["payload"]

    def digest(self, value):
        return fingerprint(value)

    def runtime(self):
        error = None
        try:
            self.require_destination()
        except (OSError, ValueError) as cause:
            error = str(cause)
        return {"library_root": str(self.settings.library_root or self.settings.data_dir.parent),
                "projects_root": str(self.settings.projects_dir), "data_root": str(self.settings.data_dir),
                "database_path": str(self.settings.database_path), "configured": error is None, "format_version": 1,
                "destination_editable": self.settings.library_root is None, "location_error": error}

    def check_destination(self, value):
        root = checked_path(value)
        if not root.is_dir():
            raise ProjectLibraryError("Choose an existing folder for imported projects.")
        data = self.settings.data_dir.resolve()
        if root.is_relative_to(data) or data.is_relative_to(root) or self.settings.database_path.resolve().is_relative_to(root):
            raise ProjectLibraryError("Choose a project folder separate from ConnLab's database and data files.")
        return root

    def require_destination(self):
        if not self.destination_configured:
            raise ProjectLibraryError("Choose where imported projects will be saved before selecting projects.")
        return self.check_destination(self.settings.projects_dir)

    def destination_binding(self):
        root = self.require_destination()
        return {"path": str(root), "identity": identity(root)}

    def recovery_root(self):
        root = self.settings.library_root / "Backups" / "Project Recovery" if self.settings.library_root else self.root / "recovery"
        return checked_path(root, must_exist=False)

    def inspect_source(self, value):
        source = checked_path(value)
        if source == self.settings.projects_dir or self.settings.projects_dir.is_relative_to(source):
            raise ProjectLibraryError("Choose projects below the library root, not a directory containing the library.")
        entries = inventory(source) if source.is_dir() else [{"relative_path": source.name, "directory": False, "size": source.stat().st_size, "sha256": file_hash(source)}]
        return {**self.describe_source(source), "entries": entries, "identity": identity(source), "source_fingerprint": fingerprint(entries)}

    def describe_source(self, value):
        """Describe a selectable boundary without reading its material contents."""
        source = checked_path(value)
        if source == self.settings.projects_dir or self.settings.projects_dir.is_relative_to(source):
            raise ProjectLibraryError("Choose projects below the library root, not a directory containing the library.")
        kind = "project" if source.is_dir() else "file"
        name = source.name if kind == "project" else source.stem
        marker = {}
        if source.is_dir():
            for relative in (SOFTWARE_MARKER, Path(".connlab") / "manifest.json"):
                if (source / relative).is_file():
                    candidate = read_json(source / relative)
                    if not isinstance(candidate, dict):
                        continue
                    if not marker:
                        marker = candidate
                    if candidate.get("project_id") or candidate.get("source_project_id"):
                        marker = candidate
                        break
        match = NUMBER.search(name)
        number = marker.get("ltr_number") or marker.get("dl_number") or (match.group(0).upper() if match else None)
        children = [str(path) for path in source.iterdir() if path.is_dir() and path.name != ".connlab"] if kind == "project" else []
        title = NUMBER.sub("", name, count=1).strip(" _-") or name
        if number and kind == "project":
            business = [Path(path) for path in children if Path(path).name.upper().startswith(number.upper() + " ")]
            if len(business) == 1 and (source / "Source Book").is_dir():
                title = business[0].name[len(number):].strip()
        return {"source_path": str(source), "title": title, "ltr_number": number, "kind": kind,
                "warnings": [], "child_folders": children,
                "project_id": marker.get("project_id") or marker.get("source_project_id"), "has_portable": (source / PORTABLE_FILE).exists() if kind == "project" else False}

    def scan(self, roots):
        items, warnings, seen = [], [], set()
        boundaries = {}
        for value in roots:
            try:
                description = self.describe_source(value)
                if description["kind"] == "project":
                    boundaries.setdefault(description["source_path"].casefold(), description)
            except (OSError, ValueError) as error:
                warnings.append(f"{value}: {error}")
        pending = [(value, 0) for value in reversed(roots)]
        scanned = 0
        while pending and scanned < 10000:
            value, depth = pending.pop()
            scanned += 1
            try:
                source = checked_path(value)
                key = str(source).casefold()
                if key in seen:
                    continue
                seen.add(key)
                if source.is_file():
                    items.append(self.inspect_source(source))
                    continue
                children = [p for p in source.iterdir() if p.is_dir() and p.name.casefold() not in {".connlab", ".git", "node_modules", "history"}]
                files = [p for p in source.iterdir() if p.is_file()]
                numbered = [p for p in children if NUMBER.search(p.name)]
                template = any(p.name.casefold() == "source book" for p in children)
                recognized = NUMBER.search(source.name) or template or (source / SOFTWARE_MARKER).is_file()
                if recognized or not numbered and (files or not children):
                    items.append(self.inspect_source(source))
                elif depth < 6:
                    pending.extend((str(child), depth + 1) for child in reversed(sorted(children)))
                else:
                    warnings.append("Some folders are deeper than the preview limit. Choose a specific project.")
            except (OSError, ValueError) as error:
                warnings.append(f"{value}: {error}")
        keys = ("source_path", "title", "ltr_number", "kind", "warnings", "child_folders", "has_portable")
        return {"items": [{key: row[key] for key in keys} for row in items],
                "boundary_roots": [{key: row[key] for key in keys} for row in boundaries.values()],
                "warnings": list(dict.fromkeys(warnings)), "truncated": bool(pending)}

    def suggested_target(self, source, *, new_title=None, target_member=None):
        path = Path(source["source_path"])
        if target_member:
            return str(Path(target_member["folder_path"]) / "Imported Material" / path.name)
        if new_title:
            return str(self.settings.projects_dir / safe_name(new_title) / path.name)
        return str(self.settings.projects_dir / safe_name(path.name))

    def exists(self, value):
        return checked_path(value, must_exist=False).exists()

    def alternate(self, value, tag, *, is_file=None):
        path = Path(value)
        file_target = path.is_file() if is_file is None else is_file
        return str(path.with_name(path.stem + " [" + tag[:8] + "]" + path.suffix)) if file_target else str(path.with_name(path.name + " [" + tag[:8] + "]"))

    def same_content(self, source, target):
        path = checked_path(target)
        if source["kind"] == "file":
            return path.is_file() and source["entries"][0]["sha256"] == file_hash(path)
        def material(entries):
            return [row for row in entries if row["relative_path"] not in {".connlab", ".connlab/library.json", ".connlab/manifest.json", ".connlab/portable"}
                    and not row["relative_path"].startswith(".connlab/portable/")]
        return path.is_dir() and material(inventory(path)) == material(source["entries"])

    def receive(self, source, target, batch_id, item_id):
        target = checked_path(target, must_exist=False)
        if not target.is_relative_to(self.settings.projects_dir.resolve()):
            raise ProjectLibraryError("The destination is outside the selected project library.")
        stage = self.stage / batch_id / item_id
        checked_path(stage, must_exist=False)
        if stage.exists():
            # Only a batch-owned temporary copy may be discarded for a verified retry.
            if not stage.resolve().is_relative_to(self.stage.resolve()):
                raise ProjectLibraryConflict("The intake staging location changed.")
            inventory(stage)
            shutil.rmtree(stage)
        origin = Path(source["source_path"])
        if source["kind"] == "project":
            copy_verified(origin, stage, source["entries"])
        else:
            stage.mkdir(parents=True)
            shutil.copyfile(checked_path(origin), stage / origin.name)
            if file_hash(stage / origin.name) != source["entries"][0]["sha256"]:
                raise ProjectLibraryConflict("The source changed during intake.")
        if source.get("member_marker") and source["kind"] == "project":
            self.write_marker({**source["member_marker"], "folder_path": str(stage)})
        target.parent.mkdir(parents=True, exist_ok=True)
        checked_path(target.parent)
        if target.exists():
            raise ProjectLibraryConflict("The intake destination appeared during copying.")
        if source["kind"] == "file":
            os.rename(stage / origin.name, target)
            stage.rmdir()
        else:
            os.rename(stage, target)

    def has_portable(self, folder):
        return (checked_path(folder, must_exist=False) / PORTABLE_FILE).exists()

    def marker(self, folder):
        path = Path(folder) / SOFTWARE_MARKER
        return read_json(path) if path.is_file() else None

    def write_marker(self, member):
        root = checked_path(member["folder_path"])
        payload = {"format_version": 1, "member_id": member["member_id"], "project_id": member["project_id"], "source_project_id": member.get("source_project_id") or member["project_id"], "ltr_number": member["ltr_number"]}
        business = self.business_path(member)
        manifest = root / ".connlab" / "manifest.json"
        if manifest.is_file():
            official = read_json(manifest)
            if official.get("project_id") == (member["project_id"] or member.get("source_project_id")):
                registered = Path(official.get("official_project_folder_path") or root)
                if registered.is_dir() and registered.is_relative_to(root):
                    business = checked_path(registered)
        payload.update(business_relative_path=business.relative_to(root).as_posix(), business_identity=identity(business))
        atomic_json(root / SOFTWARE_MARKER, payload)

    def business_path(self, member):
        root = checked_path(member["folder_path"])
        number = member.get("ltr_number")
        if number and (root / "Source Book").is_dir():
            candidates = [p for p in root.iterdir() if p.is_dir() and p.name.upper().startswith(number.upper() + " ")]
            if len(candidates) == 1:
                return candidates[0]
        return root

    def business_candidates(self, root, number):
        if not number:
            return []
        return [checked_path(path) for path in root.iterdir()
                if path.is_dir() and path.name.upper().startswith(number.upper() + " ")]

    def workspace_business(self, member, workspace, root=None, *, allow_identity_refresh=False):
        if not workspace:
            return {"ready": True, "candidate": None, "warning": ""}
        root = checked_path(root or member["folder_path"])
        registered_root = Path(workspace["local_workspace_path"])
        registered = Path(workspace["official_folder_path"])
        if not registered.is_relative_to(registered_root):
            raise ProjectLibraryConflict("The registered business folder is outside its project root.")
        relative = registered.relative_to(registered_root)
        expected = root / relative
        marker = self.marker(root) or {}
        manifest = read_json(root / ".connlab" / "manifest.json") if (root / ".connlab" / "manifest.json").is_file() else {}
        proof = marker.get("business_identity") if marker.get("business_relative_path") == relative.as_posix() else manifest.get("official_folder_identity")
        if expected.is_dir() and (not proof or identity(checked_path(expected)) == proof):
            return {"ready": True, "candidate": str(checked_path(expected)), "warning": ""}
        candidates = self.business_candidates(root, member["ltr_number"])
        warning = "The inner project folder was moved or renamed. Reconnect this project root to review and update its registered references before continuing."
        if len(candidates) != 1:
            return {"ready": False, "candidate": None, "warning": "The registered business folder is missing or has multiple candidates. Restore a single verified project folder before reconnecting."}
        candidate = candidates[0]
        if proof and identity(candidate) != proof:
            if not allow_identity_refresh:
                return {"ready": False, "candidate": None, "warning": "The business folder identity changed. The existing project cannot be linked to an unverified replacement."}
            warning = "This complete project root was copied to a new location. Verify its project and full LTR before confirming; the file-system identity will be recorded for this location."
        return {"ready": False, "candidate": str(candidate), "warning": warning}

    def title_context(self, member, title):
        marker = self.marker(member["folder_path"])
        if not marker or marker.get("member_id") != member["member_id"]:
            raise ProjectLibraryConflict("The identity marker is missing or changed. Reconnect and verify the folder before renaming.")
        title = safe_name(title)
        number = member.get("ltr_number")
        if number and title.upper().startswith(number.upper()):
            title = title[len(number):].strip()
        title = safe_name(title)
        source = self.business_path(member)
        target = source.with_name(safe_name((number + " " if number else "") + title))
        return {"member_id": member["member_id"], "revision": member["revision"], "title": title,
                "source_path": str(source), "target_path": str(target), "identity": identity(source),
                "marker": self.marker(member["folder_path"])}

    def move(self, source, target, expected_identity):
        source, target = checked_path(source), checked_path(target, must_exist=False)
        if identity(source) != expected_identity:
            raise ProjectLibraryConflict("The project location changed. Review again.")
        if source != target:
            if target.exists():
                raise ProjectLibraryConflict("Another folder already uses the requested title.")
            os.rename(source, target)

    def locate_context(self, member, folder, workspace=None):
        candidate = checked_path(folder)
        marker = self.marker(candidate)
        expected_project = member["project_id"] or member.get("source_project_id")
        marker_project = marker.get("project_id") or marker.get("source_project_id") if marker else None
        if marker and (marker.get("member_id") != member["member_id"] or marker.get("ltr_number") != member["ltr_number"] or marker_project != expected_project):
            raise ProjectLibraryConflict("This folder carries another project's identity.")
        manifest_file = candidate / ".connlab" / "manifest.json"
        official = read_json(manifest_file) if manifest_file.is_file() else {}
        if official.get("project_id") and official["project_id"] != expected_project:
            raise ProjectLibraryConflict("The official folder manifest belongs to another project.")
        if official.get("dl_number") and official["dl_number"] != member["ltr_number"]:
            raise ProjectLibraryConflict("The official folder manifest has a different LTR number.")
        number = NUMBER.search(candidate.name)
        if number and member["ltr_number"] and number.group(0).upper() != member["ltr_number"].upper():
            raise ProjectLibraryConflict("The folder has a different LTR number. Verify its ownership before reconnecting.")
        # A copied complete root retains stable software identity while its inode
        # changes across volumes. Only explicit Locate with a matching marker may
        # review that new identity; ordinary refresh and same-root replacement
        # checks remain strict.
        copied_root = bool(marker and candidate != Path(member["folder_path"]))
        business = self.workspace_business(member, workspace, candidate, allow_identity_refresh=copied_root)
        if workspace and not business["candidate"]:
            raise ProjectLibraryConflict(business["warning"])
        details = {}
        if workspace:
            business_path = Path(business["candidate"])
            name = business_path.name
            title = name[len(member["ltr_number"]):].strip() if member["ltr_number"] and name.upper().startswith(member["ltr_number"].upper()+" ") else member["title"]
            details = {"business_target_path": str(business_path), "business_identity": identity(business_path),
                       "business_reconnect_required": not business["ready"], "business_warning": business["warning"], "title": title}
        return {**details, "member_id": member["member_id"], "revision": member["revision"],
                "source_path": member["folder_path"], "target_path": str(candidate), "identity": identity(candidate),
                "marker": marker, "manual_identity_rebuild": marker is None,
                "official_identity": {key: official.get(key) for key in ("project_id", "dl_number")}}

    def discover(self, member):
        original = Path(member["folder_path"])
        if original.is_dir() and self.marker(original) and self.marker(original).get("member_id") == member["member_id"]:
            return str(original)
        if not original.parent.is_dir():
            return None
        candidates = []
        for child in original.parent.iterdir():
            if child.is_dir():
                try:
                    marker = self.marker(child)
                    if marker and marker.get("member_id") == member["member_id"] and marker.get("ltr_number") == member["ltr_number"]:
                        candidates.append(str(child))
                except (OSError, ValueError):
                    continue
        return candidates[0] if len(candidates) == 1 else None

    def listing(self, folder, relative_path=""):
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ProjectLibraryError("Choose a folder inside this project.")
        root = checked_path(folder)
        target = checked_path(root / relative)
        if not target.is_relative_to(root) or not target.is_dir():
            raise ProjectLibraryError("Choose a folder inside this project.")
        items, warnings = [], []
        for path in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold())):
            if path.name == ".connlab":
                continue
            try:
                checked_path(path)
                items.append({"name": path.name, "relative_path": path.relative_to(root).as_posix(),
                              "is_directory": path.is_dir(), "size_bytes": None if path.is_dir() else path.stat().st_size})
            except (OSError, ValueError):
                warnings.append(f"{path.name} is unavailable or redirected.")
            if len(items) >= 2000:
                warnings.append("This folder is large. Open it in File Explorer to view all entries.")
                break
        return {"items": items, "warnings": warnings}

    def ensure_group(self, member):
        root = checked_path(member["folder_path"], must_exist=False)
        if not root.is_relative_to(self.settings.projects_dir.resolve()):
            raise ProjectLibraryError("The destination is outside the selected project library.")
        marker = self.marker(root) if root.is_dir() else None
        if root.exists() and (not marker or marker.get("member_id") != member["member_id"]):
            raise ProjectLibraryConflict("The grouping folder belongs to a different project.")
        root.mkdir(parents=True, exist_ok=True)
        self.write_marker(member)

    def root_for_target(self, target, source, assignment):
        path = Path(target)
        return str(path.parent) if source["kind"] == "file" or assignment else str(path)

    def source_unchanged(self, source):
        return self.inspect_source(source["source_path"])["source_fingerprint"] == source["source_fingerprint"]

    def member_folder_available(self, member):
        folder = self.discover(member)
        return folder is not None, folder

    def context_valid(self, member, payload):
        if member["revision"] != payload["revision"]:
            return False
        path = payload["target_path"] if payload["kind"] == "location" else payload["source_path"]
        if identity(path) != payload["identity"]:
            return False
        root = payload["target_path"] if payload["kind"] == "location" else member["folder_path"]
        if self.marker(root) != payload.get("marker"):
            return False
        if payload["kind"] == "location":
            business = payload.get("business_target_path")
            if business and (not Path(business).is_dir() or identity(checked_path(business)) != payload["business_identity"]):
                return False
            if business and payload.get("business_reconnect_required") and self.business_candidates(Path(root), member["ltr_number"]) != [Path(business)]:
                return False
            manifest_file = Path(root) / ".connlab" / "manifest.json"
            official = read_json(manifest_file) if manifest_file.is_file() else {}
            if {key: official.get(key) for key in ("project_id", "dl_number")} != payload.get("official_identity"):
                return False
        return True

    def rewrite_identity_metadata(self, root, source, target, project_id=None):
        path = Path(root) / ".connlab" / "manifest.json"
        if path.is_file():
            payload = read_json(path)
            if not isinstance(payload, dict) or (project_id and payload.get("project_id") != project_id):
                raise ProjectLibraryConflict("The project identity manifest belongs to a different project.")
            for key in ("local_workspace_path", "official_project_folder_path", "source_book_path"):
                value = payload.get(key)
                if isinstance(value, str):
                    old = Path(value)
                    if old == Path(source) or old.is_relative_to(Path(source)):
                        payload[key] = str(Path(target) / old.relative_to(Path(source)))
            official = payload.get("official_project_folder_path")
            if official and Path(official).is_dir():
                payload["official_folder_identity"] = identity(official)
            atomic_json(path, payload)

    def publish_workspace_metadata(self, root, workspace):
        if not workspace:
            return
        root = checked_path(root)
        path = root / ".connlab" / "manifest.json"
        payload = read_json(path) if path.is_file() else {}
        if payload and payload.get("project_id") != workspace["project_id"]:
            raise ProjectLibraryConflict("The project manifest belongs to another project.")
        official = checked_path(workspace["official_folder_path"])
        if not official.is_relative_to(root):
            raise ProjectLibraryConflict("The restored official folder is outside its project root.")
        payload.update(schema_version=1, project_id=workspace["project_id"], dl_number=workspace["dl_number"],
                       local_workspace_path=workspace["local_workspace_path"], source_book_path=workspace["source_book_path"],
                       official_project_folder_path=workspace["official_folder_path"], template_source_path=workspace["template_source_path"],
                       created_at=workspace["created_at"], official_folder_identity=identity(official))
        atomic_json(path, payload)

    @contextmanager
    def project_lock(self, project_id, *, restore_id=None):
        if not project_id:
            yield
            return
        journal = GenerationJournal(self.settings.data_dir / "project_folder_generation")
        with journal.lock(project_id):
            state = journal.read(project_id)
            matching_restore = bool(state and restore_id and state.get("strategy") == "project_library_replace"
                                    and state.get("operation_id") == restore_id
                                    and state.get("effects", {}).get("library_restore", {}).get("plan_id") == restore_id)
            if state and state.get("status") != "completed" and not matching_restore:
                raise ProjectLibraryConflict("Finish the interrupted project folder operation before changing its location.")
            yield

    def pending_replacement_gate(self, project_id):
        if not project_id:
            return None
        state = GenerationJournal(self.settings.data_dir / "project_folder_generation").read(project_id)
        return state if state and state.get("strategy") == "project_library_replace" and state.get("status") != "completed" else None

    def fence_replacement(self, project_id, plan_id):
        journal = GenerationJournal(self.settings.data_dir / "project_folder_generation")
        previous = journal.read(project_id)
        if previous and previous["status"] != "completed":
            raise ProjectLibraryConflict("Another unfinished project operation must be recovered first.")
        if previous:
            journal.archive(previous)
        state = {"version": 1, "project_id": project_id, "operation_id": plan_id,
                 "strategy": "project_library_replace", "context": "project_library_restore:" + plan_id,
                 "status": "running", "step": 0, "completed_steps": [], "message": "Resume this replacement from Project Library.",
                 "finalization_pending": True,
                 "effects": {"library_restore": {"step": "library_restore", "plan_id": plan_id, "previous_state": previous}}}
        journal.save(state)

    def release_replacement_fence(self, project_id, plan_id):
        journal = GenerationJournal(self.settings.data_dir / "project_folder_generation")
        state = self.pending_replacement_gate(project_id)
        if not state:
            return
        effect = state["effects"].get("library_restore", {})
        if effect.get("plan_id") != plan_id or state.get("operation_id") != plan_id:
            raise ProjectLibraryConflict("A different project replacement is pending. Its writer fence was retained.")
        previous = effect.get("previous_state")
        state.update(status="completed", finalization_pending=False, completed_steps=["library_restore"])
        journal.archive(state)
        if previous:
            journal.save(previous)
        else:
            checked_path(journal.project_path(project_id) / "operation.json").unlink()

    def pending_change(self, member_id):
        state = self.changes.read(member_id)
        return state if state and state["status"] != "completed" else None

    def overlap(self, first, second):
        a, b = Path(first), Path(second)
        return a == b or a.is_relative_to(b) or b.is_relative_to(a)

    def path_identity(self, path):
        return identity(path)
