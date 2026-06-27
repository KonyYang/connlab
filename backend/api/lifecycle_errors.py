"""HTTP error mapping for project lifecycle write guards."""

from __future__ import annotations

from fastapi import HTTPException

from backend.application.project_lifecycle_write_guard import (
    ProjectLifecycleReadonlyError,
    ProjectLifecycleWriteGuardNotFoundError,
)


def lifecycle_guard_not_found(
    exc: ProjectLifecycleWriteGuardNotFoundError,
) -> HTTPException:
    """Map lifecycle guard project lookup misses to API 404."""
    return HTTPException(status_code=404, detail=str(exc))


def lifecycle_readonly_conflict(exc: ProjectLifecycleReadonlyError) -> HTTPException:
    """Map lifecycle readonly write rejections to structured API 409."""
    return HTTPException(
        status_code=409,
        detail={
            "code": "project_lifecycle_readonly",
            "project_id": exc.project_id,
            "lifecycle_state": exc.lifecycle_state.value,
            "closure_type": exc.closure_type.value if exc.closure_type else None,
            "message": exc.message,
            "allowed_actions": list(exc.allowed_actions),
        },
    )
