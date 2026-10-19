"""Use official publication or independent, chained draft-copy section updates."""
from dataclasses import asdict, replace
from hashlib import file_digest
from pathlib import Path
import shutil

from backend.application.current_report_update_service import UpdateCurrentLlcrReportCommand


class ReportSectionUpdateService:
    def __init__(self, *, current_reports, sources, drafts, writer, official_equipment, equipment_copies,
                 workspaces, equipment_reader, inspect_source):
        self._current = current_reports
        self._sources = sources
        self._drafts = drafts
        self._writer = writer
        self._official_equipment = official_equipment
        self._equipment_copies = equipment_copies
        self._workspaces = workspaces
        self._equipment_reader = equipment_reader
        self._inspect_source = inspect_source

    def source(self, project_id):
        source = self._sources.get_current_report(project_id)
        if source.status == "ready" and source.mode != "official":
            source = replace(source, mode="download_draft", history_root=None, can_publish_to_official=False,
                             report_revision_id=source.report_revision_id if source.mode == "download_draft" else None)
        return source

    def _require_source(self, project_id, expected, expected_mode):
        source = self.source(project_id)
        if source.status != "ready" or not source.file_path or not source.file_sha256:
            raise ValueError("Select this project's Internal Report before updating it.")
        if expected != source.file_sha256 or expected_mode != source.mode:
            raise ValueError("The Internal Report changed. Reload its source and retry the update.")
        return source

    def _revalidate(self, project_id, expected):
        current = self.source(project_id)
        if (current.status, current.mode, current.file_path, current.file_sha256) != (
                expected.status, expected.mode, expected.file_path, expected.file_sha256):
            raise ValueError("The report source changed during the update. Reload and try again.")

    def update_llcr(self, project_id, dataset_id, expected, expected_mode="download_draft"):
        source = self._require_source(project_id, expected, expected_mode)
        if source.mode == "official":
            return asdict(self._current.update_llcr(UpdateCurrentLlcrReportCommand(
                project_id, dataset_id, expected, "Lab User")))
        dataset = self._current.require_current_llcr_dataset(project_id, dataset_id)
        if source.confirmed_matrix_id and source.confirmed_matrix_id != dataset.confirmed_matrix_id:
            raise ValueError("The draft belongs to a different Confirmed Matrix. Select a compatible report.")
        def revalidate():
            self._revalidate(project_id, source)
            if self._current.require_current_llcr_dataset(project_id, dataset_id) != dataset:
                raise ValueError("LLCR data changed during the update. Reload and try again.")
        result = self._drafts.update(project_id, self._sources.project_dl_number(project_id), source.file_path,
            lambda original, output: self._writer.synchronize_llcr_results(
                source_path=original, output_path=output, dataset=dataset),
            revalidate, matrix_id=dataset.confirmed_matrix_id)
        return self._draft_result(project_id, result, source.file_sha256)

    @staticmethod
    def _draft_result(project_id, artifact, prior_hash):
        return {"project_id": project_id, "mode": "download_draft", "file_name": artifact.file_name,
                "current_sha256": artifact.file_sha256, "changed": artifact.file_sha256 != prior_hash, "archive_path": None,
                "draft_revision_id": artifact.report_revision_id}

    def download(self, project_id, revision):
        return self._drafts.read_revision(project_id, revision)

    def select_source(self, project_id, path, expected=None):
        prior = self.source(project_id)
        if prior.mode == "official" or prior.status == "ambiguous":
            raise ValueError("Resolve the official Internal Report before selecting a draft.")
        if prior.status == "ready" and expected != prior.file_sha256:
            raise ValueError("The working draft changed. Reload before choosing another report.")
        dl_number = self._sources.project_dl_number(project_id)
        if not dl_number:
            raise ValueError("Confirm this project's DL number before selecting its report.")
        self._inspect_source(path, dl_number)
        result = self._drafts.update(project_id, dl_number, path, shutil.copy2,
                                    lambda: self._revalidate(project_id, prior))
        return self._draft_result(project_id, result, prior.file_sha256)

    def _equipment_selection(self, project_id, source):
        workspace = self._workspaces.get_by_project(project_id)
        paths = [Path(workspace.local_workspace_path) / "EquipmentID.docx"] if workspace else []
        if source.mode == "download_draft" and source.report_revision_id:
            owned = self._drafts.read_revision(project_id, source.report_revision_id)
            paths.append(owned.file_path.parent / "EquipmentID.docx")
        for path in paths:
            try:
                self._equipment_reader.validate_path(path)
                if path.is_file():
                    return path
            except FileNotFoundError:
                continue
        return None

    def update_equipment(self, project_id, expected, *, expected_mode="download_draft", content=None, references_text=None):
        source = self._require_source(project_id, expected, expected_mode)
        if source.mode == "official":
            outcome = self._official_equipment.update_one_click(project_id=project_id, updated_by="Lab User",
                                                                content=content, references_text=references_text)
            if outcome.status == "source_required":
                return {"status": "source_required", "project_id": project_id}
            result = asdict(outcome.update)
            result["statistics"] = {
                "filled": len(outcome.rows), "unmatched": [r.source_reference for r in outcome.rows if r.status == "unmatched"],
                "incomplete": [r.source_reference for r in outcome.rows if r.status == "incomplete"],
                "expired": [r.id_number for r in outcome.rows if r.expired],
            }
            return {**result, "status": "completed"}
        selected = self._equipment_selection(project_id, source)
        if selected is None and content is None and not references_text:
            return {"status": "source_required", "project_id": project_id}
        if content is not None and references_text:
            raise ValueError("Choose an equipment document or paste equipment IDs, not both.")
        if selected is not None and (content is not None or references_text):
            raise ValueError("An equipment selection is now available. Retry without importing it.")
        selected_hash = self._hash(selected) if selected else None
        statistics = {}
        def generate(original, output):
            input_path = selected
            if input_path is None and content is not None:
                input_path = output.parent / "EquipmentID.docx"
                self._equipment_reader.save_missing(input_path, content=content)
            outcome = self._equipment_copies.update(source_path=original, output_path=output,
                equipment_path=input_path, references_text=references_text if input_path is None else None)
            statistics.update(outcome.statistics)
            if input_path is not None and input_path.parent != output.parent:
                shutil.copy2(input_path, output.parent / "EquipmentID.docx")
        def revalidate():
            self._revalidate(project_id, source)
            if selected is not None and (self._equipment_selection(project_id, source) != selected
                                         or self._hash(selected) != selected_hash):
                raise ValueError("The equipment selection changed. Reload and retry.")
        result = self._drafts.update(project_id, self._sources.project_dl_number(project_id), source.file_path,
                                    generate, revalidate, matrix_id=source.confirmed_matrix_id)
        return {**self._draft_result(project_id, result, source.file_sha256), "status": "completed", "statistics": statistics}

    @staticmethod
    def _hash(path):
        with path.open("rb") as stream:
            return file_digest(stream, "sha256").hexdigest()
