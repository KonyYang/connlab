"""Read existing report inputs and reuse section writers, never official publication."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

from backend.domain.report_authoring import ReportAuthoringConflict


class WorkingReportSections:
    def __init__(self, *, sources, datasets, writer, workspaces, drafts, equipment_reader, equipment_copies):
        self.sources = sources
        self.datasets = datasets
        self.writer = writer
        self.workspaces = workspaces
        self.drafts = drafts
        self.equipment_reader = equipment_reader
        self.equipment_copies = equipment_copies

    def current_source(self, project_id):
        source = self.sources.get_current_report(project_id)
        return replace(source, mode='download_draft') if source.status == 'ready' and source.mode != 'official' else source

    def read_source(self, project_id, expected_sha256, expected_mode):
        source = self.current_source(project_id)
        if source.status != 'ready' or not source.file_path:
            raise ValueError('Select a readable Internal Report before preparing its working copy.')
        if (source.file_sha256, source.mode) != (expected_sha256, expected_mode):
            raise ReportAuthoringConflict('The Internal Report source changed. Reload before selecting it.')
        content = source.file_path.read_bytes()
        if sha256(content).hexdigest() != expected_sha256:
            raise ReportAuthoringConflict('The Internal Report changed while reading it.')
        return source, content

    def llcr(self, project_id, dataset_id, matrix_id):
        dataset = self.datasets.require_current_llcr_dataset(project_id, dataset_id)
        if dataset.confirmed_matrix_id != matrix_id:
            raise ReportAuthoringConflict('The LLCR dataset belongs to another confirmed Matrix.')
        def generate(source, output):
            return self.writer.synchronize_llcr_results(source_path=source, output_path=output, dataset=dataset)
        def revalidate():
            if self.datasets.require_current_llcr_dataset(project_id, dataset_id) != dataset:
                raise ReportAuthoringConflict('LLCR data changed during the update. Reload and try again.')
        return generate, revalidate, {'dataset_revision_id': dataset_id, 'matrix_id': matrix_id}

    def equipment_path(self, project_id):
        workspace = self.workspaces.get_by_project(project_id)
        paths = [Path(workspace.local_workspace_path) / 'EquipmentID.docx'] if workspace else []
        current = self.sources.get_current_report(project_id)
        if current.mode == 'download_draft' and current.report_revision_id:
            paths.append(self.drafts.read_revision(project_id, current.report_revision_id).file_path.parent / 'EquipmentID.docx')
        for path in paths:
            try:
                self.equipment_reader.validate_path(path)
                if path.is_file():
                    return path
            except FileNotFoundError:
                continue
        return None

    def equipment(self, project_id, *, content=None, references_text=None, retained=False):
        selected = self.equipment_path(project_id)
        if content is not None and references_text:
            raise ValueError('Choose an equipment document or equipment IDs, not both.')
        if selected is not None and (content is not None or references_text) and not retained:
            raise ValueError('An equipment selection is available for this project. Retry without importing it.')
        if selected is None and content is None and not references_text:
            return None
        selected_hash = sha256(selected.read_bytes()).hexdigest() if selected else None
        evidence = {'selection_sha256': selected_hash, 'statistics': {}}
        def generate(source, output):
            selection = selected
            if selection is None and content is not None:
                selection = output.parent / 'EquipmentID.docx'
                self.equipment_reader.save_missing(selection, content=content)
            result = self.equipment_copies.update(source_path=source, output_path=output,
                equipment_path=selection, references_text=references_text if selection is None else None)
            evidence['statistics'] = result.statistics
        def revalidate():
            now = self.equipment_path(project_id)
            if now != selected or (selected and sha256(selected.read_bytes()).hexdigest() != selected_hash):
                raise ReportAuthoringConflict('The equipment selection changed during the update.')
        return generate, revalidate, evidence
