"""Selected-file plans; all publication remains in the no-overwrite receipt adapter."""
from datetime import datetime
from pathlib import Path
from backend.infrastructure.project_library.files import checked_path, file_hash, identity
from backend.infrastructure.project_library.material_receipt_files import folder_name
from backend.infrastructure.project_library.search_files import SearchFiles


class MaterialCopyFiles:
    def __init__(self, receipt_files):
        self.receipts = receipt_files

    def selected(self, root, relative):
        root = self.receipts.root(root)
        path = SearchFiles().resolve(str(root), relative)
        if not path.is_file():
            raise ValueError("Select one file to copy.")
        return {"root_identity": identity(root), "file_identity": identity(path),
                "relative_path": path.relative_to(root).as_posix(),
                "size": path.stat().st_size, "sha256": file_hash(path)}

    def plan_item(self, source_root, selected, target_root, directory, batch_id, prior):
        target = self.receipts.root(target_root)
        parts = directory.replace("\\", "/").split("/") if directory else []
        for part in parts:
            folder_name(part)
        relative = selected["relative_path"]
        name = Path(relative).name
        desired = "/".join([*parts, name])
        source = checked_path(Path(source_root) / relative)
        destination = checked_path(target / desired, must_exist=False)
        if not destination.is_relative_to(target):
            raise ValueError("Choose a folder inside the target project.")
        state = self.receipts.snapshot(target)
        existing = {row["relative_path"].casefold(): row for row in state["entries"]}
        controls = relative.split("/")[0].casefold() == ".connlab" or (parts and parts[0].casefold() == ".connlab")
        blocked_parent = any((old := existing.get("/".join(parts[:index]).casefold())) and not old["directory"]
                             for index in range(1, len(parts) + 1))
        old = existing.get(desired.casefold())
        equal = old and not old["directory"] and old["sha256"] == selected["sha256"]
        conflict = bool(controls or blocked_parent or old and not equal)
        archive = f"补充资料/{datetime.now():%Y%m%d-%H%M%S}-{folder_name(source.name)}-{batch_id[:8]}/{desired}"
        target_relative = archive if conflict else desired
        for previous in prior:
            actual = existing.get(previous["target_relative"].casefold())
            if (previous.get("requested_target_relative") == desired and previous["sha256"] == selected["sha256"]
                    and actual and not actual["directory"] and actual["sha256"] == selected["sha256"]):
                target_relative, equal, conflict = previous["target_relative"], True, False
                break
        return state, {"relative_path": relative, "directory": False, "size": selected["size"],
            "sha256": selected["sha256"], "requested_target_relative": desired,
            "target_relative": target_relative, "action": "supplement" if conflict else "skip" if equal else "copy",
            "reason": "Incoming control data is archived without activating it." if controls
                      else "Existing content retained." if conflict else ""}
