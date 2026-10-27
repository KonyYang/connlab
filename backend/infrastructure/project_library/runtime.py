"""OS-owned process lease for a selected business library."""
import os
from pathlib import Path
import threading
from sqlalchemy import event
from backend.domain.project_library import ProjectLibraryConflict
from backend.infrastructure.project_library.files import checked_path, read_json, atomic_json

_LEASES = {}
_MUTEX = threading.RLock()


class RuntimeLease:
    def __init__(self, key):
        self.key = key
        self.released = False

    def release(self):
        with _MUTEX:
            if self.released:
                return
            self.released = True
            entry = _LEASES[self.key]
            entry["references"] -= 1
            if not entry["references"]:
                entry["handle"].close()
                del _LEASES[self.key]


def claim_runtime(settings):
    root = checked_path(settings.library_root, must_exist=False)
    if any(not Path(path).resolve().is_relative_to(root) for path in
           (settings.data_dir, settings.database_path, settings.projects_dir)):
        raise ValueError("Data, projects and database must remain inside the selected project library.")
    marker = root / ".connlab" / "library-format.json"
    binding = {"format_version": 1, "database_relative_path": settings.database_path.relative_to(root).as_posix()}
    key = str(root).casefold()
    with _MUTEX:
        if marker.is_file() and read_json(marker) != binding:
            raise ProjectLibraryConflict("The selected library version or database binding is incompatible.")
        if key in _LEASES:
            _LEASES[key]["references"] += 1
            return RuntimeLease(key)
        lock_path = checked_path(root / ".connlab" / "runtime.lock", must_exist=False)
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = lock_path.open("a+b")
        try:
            if not lock_path.stat().st_size:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            handle.close()
            raise ProjectLibraryConflict("This project library is already open in another ConnLab process. Close that instance before starting another.") from error
        try:
            if marker.is_file():
                if read_json(marker) != binding:
                    raise ProjectLibraryConflict("The selected library version or database binding changed.")
            else:
                atomic_json(marker, binding)
        except Exception:
            handle.close()
            raise
        _LEASES[key] = {"handle": handle, "references": 1}
        return RuntimeLease(key)


def bind_engine_lease(engine, lease):
    event.listen(engine, "engine_disposed", lambda _engine: lease.release())
    @event.listens_for(engine, "connect")
    def reject_reused_disposed_engine(_connection, _record):
        if lease.released:
            raise ProjectLibraryConflict("This library instance was closed. Create a new engine before reopening it.")
