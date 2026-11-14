"""Byte-preserving receipt publication with no overwrite or metadata interpretation."""
from datetime import datetime
import os
from pathlib import Path
import re
import shutil
from uuid import uuid4
from backend.domain.project_library import ProjectLibraryConflict
from backend.infrastructure.project_library.files import (
    LibraryFiles, checked_path, inventory, identity, file_hash,
)


def folder_name(value):
    value = value.strip()
    if (not value or value in {".", ".."} or value.endswith((".", " "))
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', value)
            or re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", value)):
        raise ValueError("Enter a folder description without reserved filename characters.")
    return value


class MaterialReceiptFiles:
    def __init__(self, settings):
        self.settings = settings
        self.control = LibraryFiles(settings)

    def selected_file(self, root, relative):
        from backend.infrastructure.project_library.material_copy_files import MaterialCopyFiles
        return MaterialCopyFiles(self).selected(root, relative)

    def plan_selected_copy(self, source_root, selected, target_root, directory, batch_id, prior):
        from backend.infrastructure.project_library.material_copy_files import MaterialCopyFiles
        return MaterialCopyFiles(self).plan_item(source_root, selected, target_root, directory, batch_id, prior)

    def lock(self):
        return self.control.lock()

    def project_lock(self, project_id):
        return self.control.project_lock(project_id)

    def save_plan(self, payload):
        return self.control.save_plan("material_receipt", payload)

    def plan(self, plan_id, fingerprint):
        return self.control.plan(plan_id, fingerprint, "material_receipt")

    def root(self, value):
        root = checked_path(value)
        if not root.is_dir():
            raise ValueError("Choose an available folder for received materials.")
        data = self.settings.data_dir.resolve()
        if root.is_relative_to(data) or data.is_relative_to(root):
            raise ValueError("The receive location must be separate from ConnLab internal data.")
        return root

    def binding(self, config):
        root = self.root(config["root_path"])
        return {**config, "root_path": str(root), "identity": identity(root)}

    def available(self, value):
        try:
            return checked_path(value).is_dir()
        except (ValueError, OSError):
            return False

    def snapshot(self, value):
        root = checked_path(value, must_exist=False)
        return {"identity": identity(root), "entries": inventory(root)} if root.exists() else None

    def validate_pair(self, source, target):
        source, target = checked_path(source), checked_path(target, must_exist=False)
        if not source.is_dir():
            raise ValueError("Choose one source folder.")
        if source == target or source.is_relative_to(target) or target.is_relative_to(source):
            raise ValueError("Source and destination folders must not overlap.")
        data = self.settings.data_dir.resolve()
        for root in (source, target):
            if root.is_relative_to(data) or data.is_relative_to(root):
                raise ValueError("Source and destination must not include ConnLab internal data.")
        return source, target

    def contains(self, parent, child):
        from pathlib import PureWindowsPath
        return PureWindowsPath(child).is_relative_to(PureWindowsPath(parent))

    def overlaps(self, first, second):
        from pathlib import PureWindowsPath
        left, right = PureWindowsPath(first), PureWindowsPath(second)
        return left == right or left.is_relative_to(right) or right.is_relative_to(left)

    def matches(self, target, entry, root_identity):
        try:
            root = self.check_root(target, root_identity)
            path = checked_path(root / entry["target_relative"])
            return path.is_dir() if entry["directory"] else path.is_file() and file_hash(path) == entry["sha256"]
        except (ValueError, OSError):
            return False

    def proposed_target(self, root, number, source, description):
        name = folder_name(Path(source).name)
        if description.strip():
            name += " " + folder_name(description)
        target = self.root(root) / name
        if target.exists():
            raise ProjectLibraryConflict("The planned folder already exists. Choose a different distinguishing description.")
        return str(target)

    def create_root(self, target):
        root = checked_path(target, must_exist=False)
        root.mkdir()
        return identity(root)

    def preview(self, source, target, batch_id, native=False, prior=()):
        source, target = self.validate_pair(source, target)
        source_state, target_state = self.snapshot(source), self.snapshot(target)
        existing = {row["relative_path"].casefold(): row for row in (target_state or {}).get("entries", [])}
        supplement = f"补充资料/{datetime.now():%Y%m%d-%H%M%S}-{folder_name(source.name)}-{batch_id[:8]}"
        if any(key == supplement.casefold() or key.startswith(supplement.casefold() + "/")
               for key in existing):
            raise ProjectLibraryConflict("The supplementary location is occupied. Preview again.")
        planned, redirected = [], []
        for entry in sorted(source_state["entries"], key=lambda row: (row["relative_path"].count("/"), row["relative_path"])):
            relative = entry["relative_path"]
            old = existing.get(relative.casefold())
            parent_redirected = any(relative.casefold().startswith(prefix + "/") for prefix in redirected)
            controls = native and relative.split("/")[0].casefold() == ".connlab"
            equal = old and old["directory"] == entry["directory"] and (entry["directory"] or old["sha256"] == entry["sha256"])
            conflict = parent_redirected or controls or bool(old and not equal)
            if conflict and entry["directory"]:
                redirected.append(relative.casefold())
            destination = f"{supplement}/{relative}" if conflict else relative
            preserved = next((previous for previous in prior
                if previous["relative_path"] == relative and previous["sha256"] == entry["sha256"]
                and previous.get("requested_target_relative", relative) == relative
                and previous["directory"] == entry["directory"]
                and (actual := existing.get(previous["target_relative"].casefold()))
                and actual["directory"] == entry["directory"]
                and (entry["directory"] or actual["sha256"] == entry["sha256"])), None)
            if preserved:
                destination, equal, conflict = preserved["target_relative"], True, False
            planned.append({**entry, "target_relative": destination,
                "action": "supplement" if conflict else "skip" if equal else "copy",
                "reason": "Incoming control data is archived without activating it." if controls else "Existing content retained." if conflict else ""})
        return source_state, target_state, planned

    def check_root(self, root, expected_identity):
        current = checked_path(root)
        if not current.is_dir() or identity(current) != expected_identity:
            raise ProjectLibraryConflict("The target folder changed. Retain the files and preview again.")
        return current

    def publish(self, source, target, entry, root_identity):
        root = self.check_root(target, root_identity)
        relative = entry["target_relative"]
        if Path(relative).is_absolute() or ".." in Path(relative).parts or ":" in relative:
            raise ValueError("Invalid receipt-relative path.")
        destination = checked_path(root / relative, must_exist=False)
        if not destination.is_relative_to(root):
            raise ValueError("The receipt path leaves its target folder.")
        if entry["directory"]:
            destination.mkdir(parents=True, exist_ok=True)
            checked_path(destination)
            return "skipped" if entry["action"] == "skip" else "supplemented" if entry["action"] == "supplement" else "copied"
        if destination.exists():
            if destination.is_file() and file_hash(destination) == entry["sha256"]:
                return "skipped"
            raise ProjectLibraryConflict("The destination now has different content. Existing files were retained; preview again.")
        if entry["action"] == "skip":
            raise ProjectLibraryConflict("A previously identical target is missing. Preview again.")
        origin = checked_path(Path(source) / entry["relative_path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        checked_path(destination.parent)
        temporary = destination.parent / (".receipt-" + uuid4().hex + ".tmp")
        try:
            with origin.open("rb") as reader, temporary.open("xb") as writer:
                shutil.copyfileobj(reader, writer, 1024 * 1024)
                writer.flush()
                os.fsync(writer.fileno())
            if temporary.stat().st_size != entry["size"] or file_hash(temporary) != entry["sha256"]:
                raise ProjectLibraryConflict("The source changed during copying. Preview again.")
            self.check_root(target, root_identity)
            checked_path(destination.parent)
            # Both publication operations fail if the final name already exists.
            if os.name == "nt":
                os.rename(temporary, destination)
            else:
                os.link(temporary, destination)
            return "supplemented" if entry["action"] == "supplement" else "copied"
        finally:
            temporary.unlink(missing_ok=True)
