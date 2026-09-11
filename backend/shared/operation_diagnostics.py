"""Bounded operation evidence; never changes publication or recovery decisions."""
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
import ctypes
import json
import logging
import os
from pathlib import Path
import re
import stat
import time
import traceback
from uuid import uuid4

_current = ContextVar("connlab_operation_diagnostics", default=None)
_logger = logging.getLogger("connlab.operations")


def safe_text(value):
    text = str(value)
    text = re.sub(r'''(?i)(["'])(password|passwd|token|api[_-]?key|secret)\1\s*:\s*(["']).*?\3''',
                  r'\1\2\1: "<REDACTED>"', text)
    text = re.sub(r'''(?i)\b(password|passwd|token|api[_-]?key|secret)\s*[=:]\s*(?:"[^"]*"|'[^']*'|[^\s,;]+)''',
                  r'\1=<REDACTED>', text)
    text = re.sub(r'''(["'])(?:[a-zA-Z]:[\\/]|\\\\).*?\1''', '"<LOCAL_PATH>"', text)
    text = re.sub(r'(?im)(?:[a-z]:[\\/]|\\\\).*?(?=\s+(?:winerror|errno|hresult|stage|operation_id|status|elapsed_ms)=|$)',
                  '<LOCAL_PATH>', text)
    return text[:4000]


def safe_value(value):
    if isinstance(value, dict):
        return {str(k): "<REDACTED>" if re.fullmatch(r"(?i)password|passwd|token|api[_-]?key|secret", str(k))
                else safe_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_value(v) for v in value[:64]]
    if value is None or isinstance(value, (int, float, bool)):
        return value
    return safe_text(value)


def path_summary(value):
    path = Path(value)
    result = {"length": len(str(path)), "suffix": path.suffix[:16],
              "location": "network" if str(path).startswith("\\\\") else "local"}
    try:
        if os.name == "nt":
            result["drive_type"] = int(ctypes.windll.kernel32.GetDriveTypeW(str(path.absolute().anchor)))
        result["exists"] = path.exists()
        if result["exists"]:
            info = path.stat()
            result.update(is_directory=stat.S_ISDIR(info.st_mode),
                          attributes=getattr(info, "st_file_attributes", 0),
                          size_bytes=info.st_size)
    except OSError as exc:
        result.update(metadata_errno=exc.errno, metadata_winerror=getattr(exc, "winerror", None))
    return result


def context_payload():
    current = _current.get()
    return {k: current[k] for k in ("operation_id", "operation", "stage", "project_id")} if current else {}


def emit(event, **fields):
    current = _current.get()
    if current is None:
        return
    record = safe_value({**context_payload(), "event": event, "timestamp_utc": datetime.now(UTC).isoformat(), **fields})
    if len(current["events"]) < 64:
        current["events"].append(record)
    try:
        _logger.info(json.dumps(record, ensure_ascii=False))
    except Exception:
        # A logging destination failure must never replace a business exception.
        pass


def failure_details(exc):
    retained = getattr(exc, "_connlab_diagnostic", None)
    if retained:
        return retained
    failures, seen = [], set()
    current = exc
    origin = context_payload()
    while current is not None and id(current) not in seen and len(failures) < 8:
        seen.add(id(current))
        caused_at = getattr(current, "_connlab_diagnostic", None)
        if caused_at:
            origin = {key: caused_at[key] for key in ("operation_id", "operation", "stage", "project_id") if key in caused_at}
        # SQLAlchemy exceptions can stringify full statements and bound business data.
        message = getattr(current, "orig", type(current).__name__) if hasattr(current, "params") else current
        item = {"type": type(current).__name__, "message": safe_text(message),
                "frames": [{"file": Path(frame.filename).name, "line": frame.lineno, "function": frame.name}
                           for frame in traceback.extract_tb(current.__traceback__)[-24:]]}
        for key in ("errno", "winerror", "hresult"):
            value = getattr(current, key, None)
            if isinstance(value, int):
                item[key] = value
        info = getattr(current, "excepinfo", None)
        if isinstance(info, tuple) and len(info) >= 6:
            item["com"] = safe_value({"source": info[1], "description": info[2], "scode": info[5]})
        failures.append(item)
        current = current.__cause__ or (None if current.__suppress_context__ else current.__context__)
    return {**origin, "exceptions": failures}


def attach_failure(exc, details=None):
    if not getattr(exc, "_connlab_diagnostic", None):
        exc._connlab_diagnostic = safe_value(details or failure_details(exc))
    return exc


def record_failure(exc):
    attach_failure(exc)
    current = _current.get()
    if current is not None:
        current["failed"] = True
    emit("failure", diagnostic=failure_details(exc))


def diagnostic_message(exc, message=None):
    details = failure_details(exc)
    identifier = details.get("operation_id")
    prefix = safe_text(message if message is not None else str(exc))
    if not identifier:
        return prefix
    code = ""
    for error in reversed(details.get("exceptions", [])):
        if isinstance(error, dict) and "winerror" in error:
            code = f"Windows error: {error['winerror']}; "
            break
        if isinstance(error, dict) and "hresult" in error:
            code = f"Office HRESULT: {error['hresult']}; "
            break
    return f"{prefix} [{code}Stage: {details.get('stage', 'unknown')}; Diagnostic ID: {identifier}]"


@contextmanager
def operation(name, *, operation_id=None, project_id=None):
    identifier = str(operation_id or uuid4().hex)
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", identifier):
        identifier = uuid4().hex
    state = {"operation_id": identifier, "operation": name, "stage": "validate", "events": [],
             "project_id": project_id or context_payload().get("project_id")}
    token = _current.set(state)
    started = time.monotonic()
    emit("operation_started", pid=os.getpid())
    try:
        yield state
    except Exception as exc:
        attach_failure(exc)
        emit("operation_failed", diagnostic=failure_details(exc), elapsed_ms=round((time.monotonic()-started)*1000, 2))
        raise
    else:
        emit("operation_failed" if state.get("failed") else "operation_succeeded",
             elapsed_ms=round((time.monotonic()-started)*1000, 2))
    finally:
        _current.reset(token)


@contextmanager
def stage(name, **paths):
    current = _current.get()
    if current is None:
        yield
        return
    previous = current["stage"]
    current["stage"] = name
    started = time.monotonic()
    emit("stage_started", paths={key: path_summary(value) for key, value in paths.items() if value is not None})
    try:
        yield
    except Exception as exc:
        attach_failure(exc)
        emit("stage_failed", diagnostic=failure_details(exc), elapsed_ms=round((time.monotonic()-started)*1000, 2))
        raise
    else:
        emit("stage_succeeded", elapsed_ms=round((time.monotonic()-started)*1000, 2))
    finally:
        current["stage"] = previous
