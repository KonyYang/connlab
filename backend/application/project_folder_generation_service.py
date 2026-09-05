"""Backend-owned Project Folder chain with explicit, durable interruption recovery."""

from uuid import uuid4
import logging

GENERATION_STEPS = ("workspace", "materials", "check", "customer_feedback_form", "fee_form",
                    "test_record", "test_status", "application_form")


class ProjectFolderGenerationService:
    """Start, observe and resume one project operation; callers never drive its steps."""

    def __init__(self, journal, context, run_step, dispatch, preview_context=None, preview=None):
        self.journal, self.context = journal, context
        self.run_step, self.dispatch = run_step, dispatch
        self.owner = uuid4().hex
        self.preview_context = preview_context or context
        self.preview = preview or (lambda project_id: {"expected_context": self.preview_context(project_id)})

    def start(self, project_id, strategy, expected_context, request_id, replaces_operation_id=None):
        with self.journal.lock(project_id):
            existing = self.journal.read(project_id)
            if existing and existing.get("request_id") == request_id:
                return self._view(existing)
            if existing and existing["status"] != "completed":
                if replaces_operation_id != existing["operation_id"] or not self._can_replace(existing):
                    raise ValueError("Resume the existing operation, or review a fresh preview before explicitly replacing a safely checkpointed operation.")
            context = self.context(project_id)
            if self.preview_context(project_id) != expected_context:
                raise ValueError("Project folder preview changed. Refresh the preview before starting.")
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
                        self.run_step(state, name)
                        # run_step returns only after its own session commits.
                        state["completed_steps"].append(name)
                        state["step"] += 1
                        self.journal.save(state)
                    state.update(status="completed", message="Project folder generation completed.")
                    self.journal.save(state)
                except Exception as exc:
                    logging.getLogger(__name__).warning("Folder generation stopped: project=%s operation=%s step=%s",
                                                        project_id, operation_id, state["step"], exc_info=True)
                    message = ("Folder storage is unavailable or changed. Review the configured folder before resuming."
                               if isinstance(exc, OSError) else str(exc))
                    state.update(status="blocked", message=message)
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
        return state["status"] in {"blocked", "running"} and all(
            effect["step"] in state["completed_steps"] for effect in state["effects"].values())
