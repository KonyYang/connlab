"""Worker composition: lock first, then an independent database/Office lifetime."""
from contextlib import ExitStack
from pathlib import Path
import time

from backend.application.customer_report_projection_service import CustomerReportGenerationCommand, CustomerReportProjectionService
from backend.application.test_report_template_resource import resolve_customer_report_template_path
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.report_publication_gateway import ReportPublicationGateway
from backend.infrastructure.office.customer_report_document_gateway import CustomerReportDocumentGateway
from backend.infrastructure.office.customer_report_subprocess_runner import CustomerReportSubprocessRunner
from backend.infrastructure.storage.models import ProjectModel


class ProjectCustomerReportRunner:
    def __init__(self, *, session_factory, settings, writer_factory=None, lock_timeout_seconds=10):
        self._sessions = session_factory
        self._settings = settings
        self._writer_factory = writer_factory or (lambda root: _IsolatedWriter(root))
        self._lock_timeout = lock_timeout_seconds

    def __call__(self, project_id, source_hash, customer_hash, operation_root, progress):
        from backend.api.dependencies import get_current_report_update_service, get_test_report_template_resource_store
        journal = GenerationJournal(self._settings.data_dir / "project_folder_generation")
        with ExitStack() as stack:
            # The POST's registry guard owns this same non-reentrant lock until
            # request teardown. Wait boundedly; never carry its session to a worker.
            deadline = time.monotonic() + self._lock_timeout
            while True:
                try:
                    stack.enter_context(journal.lock(project_id))
                    break
                except ValueError:
                    if time.monotonic() >= deadline:
                        raise ValueError("Project is busy with another operation. Retry after it finishes.")
                    time.sleep(0.05)
            state = journal.read(project_id)
            if state and state["status"] in {"queued", "running"}:
                raise ValueError("Project folder generation is pending or running. Retry after it finishes.")
            with self._sessions() as session:
                project = session.get(ProjectModel, project_id, populate_existing=True)
                if project is None or project.registry_state != "active":
                    raise ValueError("Project is unavailable or read-only. Restore it before generating a report.")
                template = resolve_customer_report_template_path(get_test_report_template_resource_store(session))
                service = CustomerReportProjectionService(
                    current_reports=get_current_report_update_service(session),
                    files=ReportPublicationGateway(), writer=self._writer_factory(operation_root),
                    generated_root=Path(operation_root))
                return service.generate(CustomerReportGenerationCommand(project_id, template, source_hash, customer_hash), progress=progress)


class _IsolatedWriter:
    def __init__(self, root):
        self._runner = CustomerReportSubprocessRunner(output_root=Path(root) / "word-runs")

    def generate_customer_report(self, **kwargs):
        return self._runner.generate_customer_report(**kwargs)

    def read_source_report_sha256(self, path):
        return CustomerReportDocumentGateway().read_source_report_sha256(path)
