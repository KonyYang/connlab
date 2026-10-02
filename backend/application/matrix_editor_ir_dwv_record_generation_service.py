"""IR/DWV draft and confirmed records with explicit external-authority context."""

from dataclasses import asdict, replace
from hashlib import sha256
import json
import re

from backend.application.matrix_editor_ir_dwv_record_projection import (
    IrDwvRecordDiagnostic, IrDwvRecordProjection,
    build_ir_dwv_record_projection, build_matrix_editor_ir_dwv_record_projection,
)
from backend.application.matrix_editor_llcr_cr_record_generation_service import (
    MatrixEditorLlcrCrRecordGenerationResult,
)


class MatrixEditorIrDwvRecordGenerationService:
    """Own source selection; the injected writer owns XLSX and filesystem details."""

    def __init__(self, *, confirmed_store, basic_information_store, ltr_store,
                 workbook_gateway, artifact_store):
        self._confirmed = confirmed_store
        self._basic = basic_information_store
        self._ltrs = ltr_store
        self._writer = workbook_gateway
        self._artifacts = artifact_store

    def build_draft_projection(self, *, project_id, **draft):
        header, context, diagnostics = self._context(project_id)
        projection = build_matrix_editor_ir_dwv_record_projection(
            project_id=project_id, **draft, header=header, source_fingerprint=context,
        )
        return self._validate_projection(projection, diagnostics)

    def preview(self, project_id, record_type="ir_dwv"):
        if record_type != "ir_dwv":
            raise ValueError("Record type must be ir_dwv.")
        snapshot = self._confirmed.get_active_by_project(project_id)
        if snapshot is None:
            raise ValueError("Active confirmed Matrix not found.")
        header, context, diagnostics = self._context(project_id, snapshot)
        projection = build_ir_dwv_record_projection(snapshot, header=header, source_fingerprint=context)
        return self._validate_projection(projection, diagnostics)

    def generate(self, command, *, is_confirmed=False):
        projection = self.build_draft_projection(**{key: getattr(command, key) for key in command.__dataclass_fields__})
        return self._generate_projection(command, projection, is_confirmed=is_confirmed)

    def _generate_projection(self, command, projection, *, is_confirmed=False):
        if projection.status != "ready" or not projection.sections:
            raise ValueError(" ".join(item.message for item in projection.diagnostics if item.level == "error"))
        artifact = self._artifacts.prepare_draft(project_id=command.project_id, record_type="ir_dwv")
        try:
            path = self.write(output_path=artifact.output_path, projection=projection)
            current = self.build_draft_projection(**{key: getattr(command, key) for key in command.__dataclass_fields__})
            if current.status != "ready" or current.preview_fingerprint != projection.preview_fingerprint:
                raise ValueError("IR/DWV sources changed during generation. Preview again.")
        except Exception:
            # The artifact belongs to this operation only; never touch a business file.
            artifact.output_path.unlink(missing_ok=True)
            raise
        # The browser label follows authority; the owned artifact keeps its unique path.
        ltr_number = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", projection.workbook.request_number).strip(" .")
        file_name = (f"{ltr_number} IR&DWV Record{'' if is_confirmed else ' draft'}.xlsx"
                     if ltr_number else artifact.file_name)
        return MatrixEditorLlcrCrRecordGenerationResult(command.project_id, "ir_dwv", file_name, path)

    def write(self, *, output_path, projection):
        return self._writer.write(output_path=output_path, projection=projection.workbook)

    def _validate_projection(self, projection, diagnostics):
        if projection.status == "ready" and not any(item.level == "error" for item in diagnostics):
            try:
                self._writer.validate_projection(projection.workbook)
            except ValueError as exc:
                diagnostics += (IrDwvRecordDiagnostic("layout_unavailable", str(exc), "error"),)
        return self._with_diagnostics(projection, diagnostics)

    def _context(self, project_id, snapshot=None):
        snapshot = snapshot or self._confirmed.get_active_by_project(project_id)
        basic = self._basic.get_latest_confirmed(project_id)
        values = basic.values if basic is not None else {}
        registered = [record for record in self._ltrs.list_by_project(project_id)
                      if getattr(record.status, "value", record.status) == "registered"]
        ltr = max(registered, key=lambda record: (str(record.registered_on or ""), record.ltr_number)) if registered else None
        header = IrDwvRecordProjection(
            request_number=ltr.ltr_number if ltr else "",
            product_name=values.get("product_description", ""),
            requestor=values.get("requested_by", ""),
            start_date=getattr(snapshot.version, "planned_test_start_date", None) if snapshot else None,
            finish_date=getattr(snapshot.version, "planned_test_complete_date", None) if snapshot else None,
        )
        diagnostics = [
            IrDwvRecordDiagnostic("personnel_environment_unset", "Tester, checker, approver, temperature and humidity have no confirmed source and are left blank."),
            IrDwvRecordDiagnostic("equipment_template_defaults", "Instrument and Gage ID retain the configured template defaults; no project-specific equipment is selected and calibration fields are left blank."),
        ]
        if basic is None:
            diagnostics.append(IrDwvRecordDiagnostic("basic_information_unset", "Confirmed Basic Information is unavailable; product and requestor are left blank."))
        if ltr is None:
            diagnostics.append(IrDwvRecordDiagnostic("ltr_unset", "No registered LTR is available; Request No. is left blank."))
        try:
            template = self._writer.template_fingerprint()
        except (OSError, ValueError) as exc:
            template = None
            diagnostics.append(IrDwvRecordDiagnostic("template_unavailable", str(exc), "error"))
        context = json.dumps({"header": asdict(header), "basic_version": getattr(basic, "version", None),
                              "template": template}, sort_keys=True, default=str)
        return header, context, tuple(diagnostics)

    @staticmethod
    def _with_diagnostics(projection, diagnostics):
        merged = projection.diagnostics + diagnostics
        signature = sha256((projection.preview_fingerprint + json.dumps([asdict(item) for item in diagnostics], sort_keys=True)).encode()).hexdigest()
        return replace(projection, diagnostics=merged, preview_fingerprint=signature,
                       status="blocked" if any(item.level == "error" for item in merged) else projection.status)
