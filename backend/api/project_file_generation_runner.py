"""Own worker and short database sessions independently of browser lifetimes."""

from contextlib import contextmanager

from backend.application.project_file_generation_service import ProjectFileGenerationService
from backend.infrastructure.files.generation_journal import GenerationJournal
from backend.infrastructure.files.project_file_generation_journal import ProjectFileGenerationJournal
from backend.infrastructure.files.recoverable_project_file_publisher import ProjectFilePublicationGateway


class ProjectFileGenerationRunner:
    def __init__(self, sessions, settings):
        self.sessions, self.settings = sessions, settings

    @staticmethod
    def submit(function, *arguments):
        # Reuse the existing cached application-owned dispatcher. A request does
        # not create another executor or carry its database session to a worker.
        from backend.api.dependencies import get_project_folder_generation_service
        return get_project_folder_generation_service().dispatch(lambda: function(*arguments))

    @contextmanager
    def components(self):
        from backend.api.project_file_generation_composition import build_components
        with self.sessions() as session:
            yield build_components(session, self.settings)

    def check_other_writes(self, project_id):
        for name in ("project_folder_generation", "basic_project_workspace", "official_folder_relocation",
                     "llcr_cr_record_publication", "ir_dwv_record_publication"):
            state = GenerationJournal(self.settings.data_dir / name).read(project_id)
            if state and state["status"] != "completed":
                raise ValueError("Another project operation is unfinished. Resume it before generating files.")
        from backend.api.project_folder_write_guard import require_report_delivery_clear
        require_report_delivery_clear(self.settings, project_id)
        from backend.infrastructure.storage.repositories.project_library import ProjectLibraryRepository
        with self.sessions() as session:
            member = ProjectLibraryRepository(session).imported_identity(project_id)
        if member:
            change = GenerationJournal(self.settings.data_dir / "project_library" / "changes").read(member["member_id"])
            if change and change["status"] != "completed":
                raise ValueError("A Project Library move is unfinished. Recover it before generating files.")

    def service(self):
        return ProjectFileGenerationService(
            journal=ProjectFileGenerationJournal(self.settings.data_dir / "project_file_generation"),
            shared=GenerationJournal(self.settings.data_dir / "project_folder_generation"),
            components=self.components, submit=self.submit,
            check_other_writes=self.check_other_writes, files=ProjectFilePublicationGateway())
