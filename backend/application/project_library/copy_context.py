"""Ephemeral per-browser copy intent; no navigation history or durable project state."""
from contextlib import contextmanager
from threading import RLock
from time import monotonic
from uuid import uuid4
from backend.domain.project_library import ProjectLibraryConflict


class CopyContextRegistry:
    def __init__(self):
        self._lock = RLock()
        self._sessions = {}

    def create(self):
        with self._lock:
            now = monotonic()
            expired = [key for key, value in self._sessions.items() if now - value["touched"] > 43200]
            for key in expired:
                del self._sessions[key]
            if len(self._sessions) >= 512:
                del self._sessions[min(self._sessions, key=lambda key: self._sessions[key]["touched"])]
            session_id = uuid4().hex
            self._sessions[session_id] = {"intent": 0, "token": None, "target": None, "touched": now}
            return {"session_id": session_id}

    def update(self, session_id, intent, target_resolver):
        with self._lock:
            current = self._sessions.get(session_id)
            if current is None:
                raise ProjectLibraryConflict("Open the target Workbench again to establish a copy context.")
            if intent <= current["intent"]:
                raise ProjectLibraryConflict("The Workbench context changed. Use the latest navigation.")
            # Clear first, including when the new target cannot be resolved. Older
            # activation requests may never revive a cleared or failed context.
            current.update(intent=intent, token=None, target=None, touched=monotonic())
            target = target_resolver()
            if target is not None:
                current.update(token=uuid4().hex, target=target)
            return {"session_id": session_id, **{key: current[key] for key in ("intent", "token", "target")}}

    @contextmanager
    def guard(self, context):
        # Held through publication: clearing/switching is ordered against writes.
        if not self._lock.acquire(blocking=False):
            raise ProjectLibraryConflict("A copy is already running. Wait for its result before retrying.")
        try:
            current = self._sessions.get((context or {}).get("session_id")) if isinstance(context, dict) else None
            if (current is None or not current["target"] or not context.get("token")
                    or current["token"] != context["token"] or monotonic() - current["touched"] > 43200):
                raise ProjectLibraryConflict("The copy context is no longer active. Open the target Workbench, then return to Library.")
            current["touched"] = monotonic()
            yield current
        finally:
            self._lock.release()


copy_contexts = CopyContextRegistry()
