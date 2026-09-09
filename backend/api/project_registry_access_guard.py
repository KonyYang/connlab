"""Protect business writes from stale tabs and serialize them with registry moves."""

from contextlib import ExitStack, contextmanager

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.routing import APIRoute
from sqlalchemy import event, select
from sqlalchemy.orm import Session

from backend.api.dependencies import get_session, get_settings
from backend.api.project_folder_write_guard import require_project_folder_write_slot
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.storage.models import (
    ApplicationFormModel, IntakeAssetModel, IntakeCaseModel, PrecheckIssueModel,
    PrecheckResultModel, ProjectModel,
)
from backend.shared.config import Settings


_BOUND_PARAMETERS = {"project_id", "case_id", "package_id", "asset_id", "application_form_id", "issue_id"}
_BODY_PROJECT_FIELDS = {
    "/api/cleanup/project-ltr/no-ltr-projects/execute": "project_ids",
    "/api/test-plan/matrix-preview-from-path": "project_id",
}


def protect_project_mutations(router: APIRouter) -> APIRouter:
    """Add a dependency before include_router builds each route's dependency graph.

    Read routes and unrelated APIs keep their existing dependencies. Management
    owns its own atomic transaction and must not acquire the non-reentrant lock twice.
    """
    for route in router.routes:
        if not isinstance(route, APIRoute) or route.path.startswith("/api/project-registry/"):
            continue
        if not route.methods.intersection({"POST", "PUT", "PATCH", "DELETE"}):
            continue
        if not (_BOUND_PARAMETERS.intersection(route.param_convertors) or route.path in _BODY_PROJECT_FIELDS):
            continue
        if not any(item.dependency is require_registry_write_access for item in route.dependencies):
            dependency = Depends(require_registry_write_access)
            if _has_folder_write_slot(route):
                # Existing folder guards own the outer lock through session teardown.
                route.dependencies.append(dependency)
            else:
                route.dependencies.insert(0, dependency)
    return router


async def require_registry_write_access(
    request: Request,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    project_ids = _related_project_ids(session, request.path_params)
    field = _BODY_PROJECT_FIELDS.get(request.scope["route"].path)
    if field and request.headers.get("content-type", "").split(";", 1)[0] == "application/json":
        try:
            body = await request.json()
        except ValueError:
            body = None  # Request validation still owns malformed JSON.
        value = body.get(field) if isinstance(body, dict) else None
        values = value if isinstance(value, list) else [value]
        project_ids.update(item for item in values if isinstance(item, str) and item)

    journal = GenerationJournal(settings.data_dir / "project_folder_generation")
    generation_owns_lock = request.scope["route"].path in {
        "/api/projects/{project_id}/project-folder/generation/start",
        "/api/projects/{project_id}/project-folder/generation/resume",
    }
    folder_slot_owns_lock = _has_folder_write_slot(request.scope["route"])
    revisions = {}
    with ExitStack() as locks:
        for project_id in sorted(project_ids):
            if not generation_owns_lock and not folder_slot_owns_lock:
                try:
                    locks.enter_context(journal.lock(project_id))
                    state = journal.read(project_id)
                    if state and state["status"] in {"queued", "running"}:
                        raise ValueError("Project folder generation is pending or running.")
                except ValueError as exc:
                    raise HTTPException(409, detail={"code": "project_registry_busy", "message": str(exc)}) from exc
            project = session.get(ProjectModel, project_id, populate_existing=True)
            if project is not None and project.registry_state != "active":
                raise HTTPException(409, detail={
                    "code": "project_registry_read_only", "project_id": project_id,
                    "registry_state": project.registry_state,
                    "message": "This project is in the recycle bin or retained history. Restore it before editing.",
                })
            if project is not None and not generation_owns_lock:
                revisions[project_id] = project.registry_revision
        with _commit_project_writes(session, revisions):
            yield


def _has_folder_write_slot(route: APIRoute) -> bool:
    return any(item.dependency is require_project_folder_write_slot for item in route.dependencies)


@contextmanager
def _commit_project_writes(session: Session, revisions: dict[str, int]):
    """Invalidate confirmations after persisted edits, including indirect writes.

    Repositories often flush before returning, so inspecting dirty rows only at
    request teardown misses Matrix/fee/intake changes. Read-only POST previews do
    not change the revision. Generation owns its context and journal separately.
    """
    changed = False

    def after_flush(current, _context):
        nonlocal changed
        changed |= bool(current.new or current.deleted or any(
            current.is_modified(item, include_collections=True) for item in current.dirty
        ))

    def before_execute(state):
        nonlocal changed
        changed |= bool(getattr(state.statement, "is_dml", False))

    event.listen(session, "after_flush", after_flush)
    event.listen(session, "do_orm_execute", before_execute)
    try:
        yield
        session.flush()
        if changed:
            for project_id, revision in revisions.items():
                project = session.get(ProjectModel, project_id, populate_existing=True)
                if project is not None and project.registry_revision == revision:
                    project.registry_revision += 1
        # get_session tears down later. Commit before releasing the project lock.
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        event.remove(session, "after_flush", after_flush)
        event.remove(session, "do_orm_execute", before_execute)


def _related_project_ids(session: Session, params: dict) -> set[str]:
    ids = {params["project_id"]} if params.get("project_id") else set()
    case_id = params.get("case_id")
    package_id = params.get("package_id")
    if params.get("asset_id"):
        package_id = session.scalar(select(IntakeAssetModel.package_id).where(IntakeAssetModel.asset_id == params["asset_id"]))
    if case_id:
        ids.update(session.scalars(select(IntakeCaseModel.confirmed_project_id).where(IntakeCaseModel.case_id == case_id)))
    if package_id:
        ids.update(session.scalars(select(IntakeCaseModel.confirmed_project_id).where(IntakeCaseModel.package_id == package_id)))
    if params.get("application_form_id"):
        ids.update(session.scalars(select(ApplicationFormModel.project_id).where(ApplicationFormModel.form_id == params["application_form_id"])))
    if params.get("issue_id"):
        ids.update(session.scalars(select(ApplicationFormModel.project_id)
            .join(PrecheckResultModel, PrecheckResultModel.application_form_id == ApplicationFormModel.form_id)
            .join(PrecheckIssueModel, PrecheckIssueModel.result_id == PrecheckResultModel.result_id)
            .where(PrecheckIssueModel.issue_id == params["issue_id"])))
    return {item for item in ids if item}
