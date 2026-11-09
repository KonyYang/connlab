"""Ownership and retention for disposable pytest runs, never for generic tmp data."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
import os
from pathlib import Path
import shutil
import stat
import time
import uuid

ROOT_SCHEMA = "connlab.pytest-artifacts.v1"
RUN_SCHEMA = "connlab.pytest-run.v1"
DEFAULT_ROOT = Path("D:/ConnLabTestArtifacts/pytest")
ROOT_ENV = "CONNLAB_PYTEST_ARTIFACT_ROOT"


def configured_root() -> Path:
    """An explicit override is also useful for isolated CI/acceptance stores."""
    return Path(os.environ.get(ROOT_ENV, str(DEFAULT_ROOT)))


def _plain(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        raise ValueError(f"Link/reparse point is not a managed artifact path: {path}")
    return info


def _root_path(root: Path) -> Path:
    root = Path(root)
    if not root.is_absolute() or root == root.parent or str(root).startswith("\\\\"):
        raise ValueError(f"Use an absolute local artifact directory, not a drive root: {root}")
    for part in (*reversed(root.parents), root):
        if part.exists() or part.is_symlink():
            if not stat.S_ISDIR(_plain(part).st_mode):
                raise ValueError(f"Artifact ancestor is not an ordinary directory: {part}")
    return root


def _read(path: Path) -> dict:
    info = _plain(path)
    if not stat.S_ISREG(info.st_mode) or info.st_size > 4096:
        raise ValueError(f"Invalid artifact marker: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Invalid artifact marker: {path}")
    return value


def _write_new(path: Path, value: dict) -> None:
    staged = path.with_name(f".pending-{uuid.uuid4().hex}")
    try:
        with staged.open("x", encoding="utf-8") as stream:
            json.dump(value, stream)
            stream.flush()
            os.fsync(stream.fileno())
        # Exclusive atomic publication: readers never see a half-written marker,
        # and an existing marker is never overwritten (also on POSIX).
        if os.name == "nt":
            os.rename(staged, path)  # Windows rename fails if the destination exists.
        else:
            os.link(staged, path)
    finally:
        staged.unlink(missing_ok=True)


class _Lease:
    """OS-owned lock: crashes release the lock, but never manufacture completion."""

    def __init__(self, path: Path, *, create: bool = False, blocking: bool = False):
        if path.exists() or path.is_symlink():
            if not stat.S_ISREG(_plain(path).st_mode):
                raise ValueError(f"Invalid artifact lease: {path}")
        self.stream = path.open("a+b" if create else "r+b")
        try:
            if create and self.stream.seek(0, os.SEEK_END) == 0:
                self.stream.write(b"0")
                self.stream.flush()
            self.stream.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.stream.fileno(), msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        except BaseException:
            self.stream.close()
            raise

    def close(self) -> None:
        self.stream.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def _root_marker(root: Path) -> dict:
    marker = _read(root / ".connlab-pytest-root.json")
    if marker.get("schema") != ROOT_SCHEMA or not isinstance(marker.get("root_id"), str):
        raise ValueError(f"Invalid managed root marker: {root}")
    if uuid.UUID(hex=marker["root_id"]).hex != marker["root_id"]:
        raise ValueError(f"Invalid managed root identity: {root}")
    return marker


def _initialize(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    if (root / ".connlab-pytest-root.json").exists():
        return _root_marker(root)
    # A peer may be publishing its root marker. Only classify the contents
    # after acquiring that initializer's lease, not while its staging file exists.
    if not (root / ".maintenance.lock").exists() and any(root.iterdir()):
        raise ValueError(f"Refusing to adopt a nonempty unmanaged directory: {root}")
    with _Lease(root / ".maintenance.lock", create=True, blocking=True):
        if not (root / ".connlab-pytest-root.json").exists():
            if any(p.name != ".maintenance.lock" for p in root.iterdir()):
                raise ValueError(f"Refusing to adopt a nonempty unmanaged directory: {root}")
            _write_new(root / ".connlab-pytest-root.json", {"schema": ROOT_SCHEMA, "root_id": uuid.uuid4().hex})
        return _root_marker(root)


@dataclass
class ManagedRun:
    scratch: Path
    _marker: dict
    _lease: _Lease
    _identity: tuple[int, int]

    def finish(self) -> None:
        if self._lease.stream.closed:
            return
        try:
            _root_path(self.scratch.parent)
            current = _plain(self.scratch.parent)
            if ((current.st_dev, current.st_ino) != self._identity
                    or _read(self.scratch.parent / ".run.json") != self._marker
                    or _root_marker(self.scratch.parent.parent)["root_id"] != self._marker["root_id"]):
                raise ValueError(f"Run identity changed; completion not recorded: {self.scratch.parent}")
            _write_new(self.scratch.parent / ".finished.json", {**self._marker, "ended_at": time.time()})
        finally:
            self._lease.close()


def start_run(root: Path | None = None) -> ManagedRun:
    root = _root_path(configured_root() if root is None else root)
    owner = _initialize(root)
    run_id = uuid.uuid4().hex
    directory = root / f"run-{run_id}"
    directory.mkdir()
    lease = _Lease(directory / ".lease", create=True)
    try:
        marker = {"schema": RUN_SCHEMA, "root_id": owner["root_id"], "run_id": run_id}
        _write_new(directory / ".run.json", marker)
        identity = _plain(directory)
        return ManagedRun(directory / "scratch", marker, lease, (identity.st_dev, identity.st_ino))
    except BaseException:
        lease.close()
        raise


@dataclass
class CleanupResult:
    candidates: list[Path] = field(default_factory=list)
    deleted: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _newest_plain_tree(directory: Path) -> float:
    newest = _plain(directory).st_mtime
    pending = [directory]
    while pending:
        current = pending.pop()
        for entry in current.iterdir():
            info = entry.lstat()
            if stat.S_ISLNK(info.st_mode):
                # Pytest creates *-current symlinks. Only wholly internal links
                # may be unlinked by rmtree; never traverse them during inspection.
                try:
                    target = entry.resolve(strict=True)
                except RuntimeError as error:
                    raise ValueError(f"Cyclic artifact link: {entry}") from error
                if not target.is_relative_to(directory.resolve()):
                    raise ValueError(f"Artifact link escapes its run: {entry}")
            else:
                info = _plain(entry)
            newest = max(newest, info.st_mtime)
            if stat.S_ISLNK(info.st_mode):
                continue
            if stat.S_ISDIR(info.st_mode):
                pending.append(entry)
            elif not stat.S_ISREG(info.st_mode):
                raise ValueError(f"Special artifact file is not safe to remove: {entry}")
    return newest


def _candidate(entry: Path, owner: dict, cutoff: float) -> bool:
    if not stat.S_ISDIR(_plain(entry).st_mode):
        raise ValueError(f"Run is not an ordinary directory: {entry}")
    expected = {".lease", ".run.json", ".finished.json", "scratch"}
    if any(p.name not in expected for p in entry.iterdir()):
        raise ValueError(f"Unexpected content outside disposable scratch: {entry}")
    marker = _read(entry / ".run.json")
    if (marker.get("schema") != RUN_SCHEMA or marker.get("root_id") != owner["root_id"]
            or entry.name != f"run-{marker.get('run_id')}"):
        raise ValueError(f"Run ownership does not match: {entry}")
    completed = _read(entry / ".finished.json")
    if any(completed.get(k) != v for k, v in marker.items()):
        raise ValueError(f"Completion ownership does not match: {entry}")
    ended_at = completed.get("ended_at")
    if isinstance(ended_at, bool) or not isinstance(ended_at, (int, float)) or not math.isfinite(ended_at):
        raise ValueError(f"Invalid completion time: {entry}")
    if ended_at >= cutoff:
        return False
    return _newest_plain_tree(entry) < cutoff


def _delete_run(entry: Path) -> None:
    scratch = entry / "scratch"
    if scratch.exists() or scratch.is_symlink():
        if not stat.S_ISDIR(_plain(scratch).st_mode):
            raise ValueError(f"Scratch is not an ordinary directory: {scratch}")
        shutil.rmtree(scratch)
    # Keep ownership/completion records until all payload deletion succeeds.
    # Locked files or an interrupted payload sweep can then be retried safely.
    for name in (".lease", ".finished.json", ".run.json"):
        (entry / name).unlink()
    entry.rmdir()


def cleanup(root: Path | None = None, *, dry_run: bool = True,
            retention_days: float = 7, now: float | None = None) -> CleanupResult:
    """Only delete owned, completed, unlocked, unmodified-for-retention run trees."""
    if not math.isfinite(retention_days) or retention_days < 1:
        raise ValueError("Retention must be a finite number of days >= 1")
    result = CleanupResult()
    try:
        root = _root_path(configured_root() if root is None else root)
        if not root.exists():
            return result
        owner = _root_marker(root)
        with _Lease(root / ".maintenance.lock", create=True):
            cutoff = (time.time() if now is None else now) - retention_days * 86400
            for entry in sorted(root.iterdir()):
                if not entry.name.startswith("run-"):
                    continue
                try:
                    identity = _plain(entry)
                    with _Lease(entry / ".lease"):
                        eligible = _candidate(entry, owner, cutoff)
                    if not eligible:
                        continue
                    result.candidates.append(entry)
                    if dry_run:
                        continue
                    # Runs cannot be resumed after finish. The maintenance lease serializes
                    # cleaners; the per-run lease has to close before Windows can remove it.
                    _root_path(root)
                    current = _plain(entry)
                    if (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino):
                        raise ValueError(f"Run directory changed before deletion: {entry}")
                    if _root_marker(root) != owner or not _candidate(entry, owner, cutoff):
                        raise ValueError(f"Run ownership or contents changed before deletion: {entry}")
                    _delete_run(entry)
                    result.deleted.append(entry)
                except (OSError, ValueError) as error:
                    result.warnings.append(f"Preserved {entry}: {error}")
    except (OSError, ValueError) as error:
        result.warnings.append(f"Artifact cleanup skipped: {error}")
    return result
