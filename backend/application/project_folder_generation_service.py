"""Backend-owned Project Folder chain with explicit, durable interruption recovery."""

from collections.abc import Sequence
from uuid import uuid4
from backend.shared.operation_diagnostics import operation, stage, record_failure, diagnostic_message

GENERATION_STEPS = ("workspace", "materials", "check", "customer_feedback_form", "fee_form",
                    "test_record", "test_status", "application_form")


class ProjectFolderInUseError(PermissionError):
    """Windows refused the initial move of a reviewed existing project folder."""

    def __init__(self, path: str):
        super().__init__(5, "Access is denied", path)


class ProjectFolderGenerationService:
    """Start, observe and resume one project operation; callers never drive its steps."""

    def __init__(self, journal, context, run_step, dispatch, preview_context=None, preview=None, finalize=None):
        self.journal, self.context = journal, context
        self.run_step, self.dispatch = run_step, dispatch
        self.owner = uuid4().hex
        self.preview_context = preview_context or context
        self.preview = preview or (lambda project_id: {"expected_context": self.preview_context(project_id)})
        self.finalize = finalize or (lambda state: None)

    def start(self, project_id, strategy, expected_context, request_id, replaces_operation_id=None):
        with self.journal.lock(project_id):
            existing = self.journal.read(project_id)
            if existing and existing.get("request_id") == request_id:
                return self._view(existing)
            if existing and existing["status"] != "completed":
                if replaces_operation_id != existing["operation_id"] or not self._can_replace(existing):
                    raise ValueError("Resume the existing operation, or review a fresh preview before explicitly replacing a safely checkpointed operation.")
            current_preview = self.preview(project_id)
            context = self.context(project_id)
            if current_preview.get("expected_context") != expected_context:
                raise ValueError("Project folder preview changed. Refresh the preview before starting.")
            blockers = current_preview.get("start_blockers", ())
            if blockers:
                raise ValueError(str(blockers[0]))
            if strategy == "continue_existing":
                raise ValueError("Choose preserve history and rebuild, or delete and rebuild.")
            if current_preview.get("workspace_preview", {}).get("status") in {"completed", "exists"} and strategy not in {"backup_and_recreate", "overwrite_rebuild"}:
                raise ValueError("The project folder already exists. Choose a rebuild option.")
            state = self.journal.create(project_id, strategy, context)
            state.update(request_id=request_id, owner=self.owner, preview_context=expected_context)
            self.journal.save(state)
        self.dispatch(lambda: self.run(project_id, state["operation_id"]))
        return self._view(state)

    def read(self, project_id):
        state = self.journal.read(project_id)
        if state is None:
            return None
        view = self._view(state)
        if state["status"] == "running" or (state["status"] == "queued" and state.get("owner") != self.owner):
            try:
                with self.journal.lock(project_id):
                    view["status"] = "interrupted"
                    view["message"] = "Generation was interrupted. Resume to verify and continue safely."
            except ValueError:
                pass
        return view

    def resume(self, project_id, operation_id):
        with self.journal.lock(project_id):
            state = self.journal.read(project_id)
            if state is None or state["operation_id"] != operation_id:
                raise ValueError("The generation operation no longer matches this project.")
            if state["status"] == "completed":
                return self._view(state)
            if self.context(project_id) != state["context"]:
                raise ValueError("Generation inputs changed. Review the operation before recovery; no files were written.")
            state.update(status="queued", message=None, owner=self.owner)
            self.journal.save(state)
        self.dispatch(lambda: self.run(project_id, operation_id))
        return self._view(state)

    def run(self, project_id, operation_id):
        with operation("project_folder_generation", operation_id=operation_id, project_id=project_id):
            self._run(project_id, operation_id)

    def _run(self, project_id, operation_id):
        try:
            with self.journal.lock(project_id):
                state = self.journal.read(project_id)
                if not state or state["operation_id"] != operation_id or state["status"] == "completed":
                    return
                try:
                    state.update(status="running", message=None)
                    self.journal.save(state)
                    while state["step"] < len(GENERATION_STEPS):
                        if self.context(project_id) != state["context"]:
                            raise ValueError("Generation inputs changed. No further files were written; review before recovery.")
                        name = GENERATION_STEPS[state["step"]]
                        with stage("folder_" + name):
                            self.run_step(state, name)
                        # run_step returns only after its own session commits.
                        state["completed_steps"].append(name)
                        state["step"] += 1
                        self.journal.save(state)
                    state["finalization_pending"] = True
                    self.journal.save(state)
                    with stage("folder_finalization"):
                        self.finalize(state)
                    state.update(status="completed", finalization_pending=False, message="Project folder generation completed.")
                    self.journal.save(state)
                except Exception as exc:
                    record_failure(exc)
                    if isinstance(exc, OSError) and state.get("finalization_pending"):
                        message = (
                            "Generated project outputs are ready, but old-copy cleanup is incomplete. "
                            "Check file locks and permissions, then resume this operation to finish cleanup."
                        )
                    elif isinstance(exc, ProjectFolderInUseError):
                        message = (
                            "Windows denied access to the existing project folder. "
                            "Check permissions or file locks, then resume, or start a new generation and "
                            "choose a rebuild option after resolving file access."
                        )
                    elif isinstance(exc, OSError):
                        message = (
                            "Folder storage is unavailable or changed. Review the "
                            "configured folder before resuming."
                        )
                    else:
                        message = str(exc)
                    state.update(status="blocked", message=diagnostic_message(exc, message))
                    self.journal.save(state)
        except ValueError:
            # Another backend worker owns the same project; it alone may advance it.
            return

    @staticmethod
    def _view(state):
        return {**{key: state.get(key) for key in ("project_id", "operation_id", "status", "step", "completed_steps", "message")},
                "can_restart": ProjectFolderGenerationService._can_replace(state)}

    @staticmethod
    def _can_replace(state):
        workspace = state["effects"].get("workspace", {})
        if (workspace.get("overwrite_cleanup") and workspace.get("prior") is not None
                and not workspace.get("overwrite_deleted")):
            return False
        return not state.get("finalization_pending", False) and state["status"] in {"blocked", "running"} and all(
            effect["step"] in state["completed_steps"] for effect in state["effects"].values())


def basic_information_generation_blocker(
    *, status: str, missing_required_labels: Sequence[str]
) -> str | None:
    """Return actionable Project Folder guidance for Basic Information authority."""
    if status == "confirmed":
        return None
    if missing_required_labels:
        return (
            "Basic Information is incomplete. Complete these required fields before "
            "generating Project Folder outputs: "
            + ", ".join(missing_required_labels)
            + "."
        )
    if status == "needs_review":
        return (
            "Basic Information source data changed after confirmation. Review and confirm "
            "the current Basic Information before generating Project Folder outputs."
        )
    return (
        "Basic Information is complete but not confirmed. Open Basic Information and "
        "click Confirm before generating Project Folder outputs."
    )
