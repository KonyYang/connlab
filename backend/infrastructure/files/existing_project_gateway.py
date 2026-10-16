"""Bounded, read-only discovery and lazy access to operator-selected folders."""
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
from uuid import UUID


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class ExistingProjectGateway:
    MAX_ENTRIES = 500
    MAX_MANIFEST_BYTES = 65536
    SKIP = {".git", ".connlab", "history", "node_modules", "__pycache__", ".venv", "$recycle.bin"}

    def safe_path(self, raw, *, directory=True):
        path = Path(raw).expanduser()
        if not path.is_absolute():
            raise ValueError("Select an absolute existing folder path.")
        # Do not resolve first: doing so hides a junction in any ancestor.
        for part in [*reversed(path.parents), path]:
            info = part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("Redirected paths (links or junctions) cannot be used. Select the original folder.")
        if directory and not path.is_dir():
            raise ValueError("Select an existing directory.")
        return path.resolve()

    def inspect(self, raw):
        root = self.safe_path(raw)
        info = root.stat()
        manifest = root / ".connlab" / "manifest.json"
        source_id = None
        source_number = None
        number_origin = "none"
        error = None
        raw_digest = None
        if manifest.exists() or manifest.is_symlink():
            try:
                self.safe_path(str(manifest), directory=False)
                if manifest.stat().st_size > self.MAX_MANIFEST_BYTES:
                    raise ValueError("manifest is too large")
                with manifest.open("rb") as handle:
                    data = handle.read(self.MAX_MANIFEST_BYTES + 1)
                if len(data) > self.MAX_MANIFEST_BYTES:
                    raise ValueError("manifest is too large")
                raw_digest = sha256(data).hexdigest()
                payload = json.loads(data.decode("utf-8-sig"))
                if not isinstance(payload, dict) or type(payload.get("schema_version")) is not int or payload["schema_version"] != 1:
                    raise ValueError("unsupported manifest version")
                candidate = payload.get("project_id")
                if not isinstance(candidate, str) or len(candidate) != 32 or UUID(candidate).hex != candidate.lower():
                    raise ValueError("invalid manifest project identity")
                source_id = candidate.lower()
                number = payload.get("dl_number")
                if number is not None and (not isinstance(number, str) or len(number) > 128):
                    raise ValueError("invalid manifest project number")
                source_number = (number or "").strip() or None
                if source_number:
                    number_origin = "manifest"
            except (ValueError, OSError, UnicodeError) as exc:
                error = f"Review manifest: {exc}"
                source_id = None
        if source_number is None:
            match = re.search(r"DL-\d{4}-\d{2}-\d{3}(?:[A-Za-z][A-Za-z0-9]*)?\b", root.name, re.I)
            source_number = match.group(0).upper() if match else None
            if source_number:
                number_origin = "folder_hint"
        return {"path": os.path.normcase(str(root)), "name": root.name,
                "source_kind": "connlab" if source_id else "manual", "source_project_id": source_id,
                "source_number": source_number, "source_number_origin": number_origin, "manifest_error": error,
                "root_identity": fingerprint([info.st_dev, info.st_ino]),
                "source_fingerprint": fingerprint([str(root), info.st_dev, info.st_ino, raw_digest, error])}

    def scan(self, roots, *, depth=1):
        if not roots or len(roots) > 10 or depth not in range(4):
            raise ValueError("Choose 1–10 roots and a scan depth from 0 to 3.")
        candidates, diagnostics, seen = [], [], set()
        pending = [(raw, 0) for raw in reversed(roots)]
        visited = 0
        while pending and visited < self.MAX_ENTRIES:
            raw, level = pending.pop()
            visited += 1
            try:
                item = self.inspect(raw)
                if item["path"] in seen:
                    continue
                seen.add(item["path"])
                # Every explicitly selected root is a candidate; descendants need
                # a project marker/number or direct files. None is auto-imported.
                root = Path(item["path"])
                with os.scandir(root) as entries:
                    children = []
                    has_files = False
                    for count, entry in enumerate(entries):
                        if count >= self.MAX_ENTRIES:
                            diagnostics.append(f"Entry limit reached: {root}")
                            break
                        if entry.name.casefold() in self.SKIP:
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            children.append(entry.path)
                        else:
                            has_files = True
                if level == 0 or item["source_project_id"] or item["manifest_error"] or item["source_number"] or has_files:
                    candidates.append(item)
                if level < depth and not (item["source_project_id"] or item["manifest_error"] or item["source_number"]):
                    pending.extend((path, level + 1) for path in sorted(children, reverse=True))
            except (OSError, ValueError) as exc:
                diagnostics.append(f"Skipped {raw}: {exc}")
        if pending:
            diagnostics.append("Scan limit reached. Select a narrower root to continue.")
        return {"candidates": candidates, "diagnostics": diagnostics}

    def verify_root(self, root_path, identity):
        root = self.safe_path(root_path)
        info = root.stat()
        if fingerprint([info.st_dev, info.st_ino]) != identity:
            raise ValueError("The registered folder was replaced. Review and confirm its location again.")
        return root

    def files(self, root_path, relative="", *, identity=None):
        root = self.verify_root(root_path, identity) if identity else self.safe_path(root_path)
        rel = Path(relative)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("File location must stay inside the registered project folder.")
        target = self.safe_path(str(root / rel))
        if not target.is_relative_to(root) or any(part.casefold() in self.SKIP for part in rel.parts):
            raise ValueError("This folder is outside the browseable project files.")
        entries, diagnostics = [], []
        with os.scandir(target) as children:
            for index, child in enumerate(children):
                if index >= self.MAX_ENTRIES:
                    diagnostics.append("Entry limit reached. Open a narrower folder."); break
                if child.name.casefold() in self.SKIP:
                    continue
                try:
                    path = self.safe_path(child.path, directory=False)
                    entries.append({"name": child.name, "relative_path": path.relative_to(root).as_posix(),
                                    "is_directory": path.is_dir()})
                except (OSError, ValueError):
                    diagnostics.append(f"Skipped inaccessible or redirected entry: {child.name}")
        if identity:
            self.verify_root(root_path, identity)
        return {"relative_path": rel.as_posix() if relative else "", "entries": sorted(entries, key=lambda x: (not x["is_directory"], x["name"].casefold())),
                "diagnostics": diagnostics}

    def file(self, root_path, relative):
        root = self.safe_path(root_path)
        rel = Path(relative)
        if not relative or ":" in relative or rel.is_absolute() or ".." in rel.parts or any(p.casefold() in self.SKIP for p in rel.parts):
            raise ValueError("Choose a file inside the registered project folder.")
        target = self.safe_path(str(root / rel), directory=False)
        if not target.is_relative_to(root) or not target.is_file():
            raise ValueError("Choose an existing project file.")
        return target

    def open_file(self, root_path, identity, relative):
        """Verify the opened handle, rather than handing an unchecked path to a response."""
        self.verify_root(root_path, identity)
        target = self.file(root_path, relative)
        handle = target.open("rb")
        try:
            opened = os.fstat(handle.fileno())
            self.verify_root(root_path, identity)
            checked = self.file(root_path, relative)
            current = checked.stat()
            if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
                raise ValueError("File changed while opening. Refresh the file list and retry.")
            return handle, target.name
        except BaseException:
            handle.close()
            raise

