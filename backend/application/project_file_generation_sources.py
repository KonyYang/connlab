"""Per-file authority selection for generation in an existing trusted workspace."""
from __future__ import annotations

from pathlib import Path
from backend.application.fee_evaluation_template_resource import resolve_fee_evaluation_template_path
from backend.application.confirmed_fee_pricing_snapshot import edited_values_json_from_confirmed_fee_snapshot
from backend.application.fee_evaluation_pricing_draft_persistence_service import edited_values_from_json
from backend.application.project_output_record_service import RegisterProjectOutputCommand
from backend.application.confirmed_matrix_llcr_cr_record_projection import matrix_record_type
from backend.application.matrix_test_points_authority import electrical_test_kind
from backend.domain import ProjectOutputKind, ProjectOutputSource, ProjectOutputStatus
from backend.application.customer_feedback_template_discovery import CustomerFeedbackTemplateDiscoveryError, discover_customer_feedback_template
from backend.application.test_record_template_resource import resolve_test_record_template_path
from backend.domain import ExternalResourceType
from backend.application.project_file_generation_types import FILE_DEFINITIONS, ProjectFileSource
from backend.infrastructure.files.generation_journal import fingerprint
from backend.infrastructure.files.recoverable_output_publisher import file_hash, file_identity, require_safe_output_path


class ProjectFileGenerationSources:
    def __init__(self, *, workspaces, basic_workspace, confirmed, basic, fees, resources,
                 settings, schedules, input_context, staging, application, llcr, llcr_writer,
                 ir, outputs, commit, forms=None):
        self.workspaces, self.basic_workspace = workspaces, basic_workspace
        self.confirmed, self.basic, self.fees = confirmed, basic, fees
        self.resources, self.settings, self.schedules = resources, settings, schedules
        self.input_context, self.staging = input_context, staging
        self.application, self.llcr, self.llcr_writer, self.ir = application, llcr, llcr_writer, ir
        self.outputs, self.commit, self.forms = outputs, commit, forms

    def _workspace(self, project_id):
        if self.workspaces.get_by_project(project_id) is None:
            raise ValueError("Use an existing linked project directory before generating files.")
        record = self.basic_workspace._record(project_id)
        self.basic_workspace._verify_record(record)
        return record

    def workspace(self, project_id):
        record = self._workspace(project_id)
        local, official, manifest = record.local_workspace_path, record.official_folder_path, record.manifest_path
        directories = (local.parent, local, local / ".connlab", record.source_book_path,
                       official, official / "Submitted Material", official / "Test results")
        facts = {}
        for path in directories:
            require_safe_output_path(path)
            if not path.is_dir():
                raise ValueError(f"Required project directory is missing: {path}")
            facts[str(path)] = file_identity(path)
        require_safe_output_path(manifest)
        token = fingerprint({"project_id": project_id, "dl_number": record.dl_number,
            "directories": facts, "manifest": str(manifest),
            "manifest_identity": file_identity(manifest), "manifest_hash": file_hash(manifest)})
        return {"token": token, "official": str(official), "local": str(local), "manifest": str(manifest),
                "stage_parent": str(local.parent / ".connlab-file-staging")}

    def source(self, project_id, key):
        definition = next((item for item in FILE_DEFINITIONS if item[0] == key), None)
        if definition is None:
            raise ValueError("Unsupported project file.")
        _, label, kind = definition
        try:
            record = self._workspace(project_id)
            target, token, warnings = self._source(project_id, key, record)
            return ProjectFileSource(key, label, target, token, kind, "ready", "Ready to generate.", warnings)
        except (ValueError, LookupError, OSError, CustomerFeedbackTemplateDiscoveryError) as exc:
            return ProjectFileSource(key, label, None, None, kind, "blocked", str(exc))

    def _source(self, project_id, key, record):
        if key == "test_status":
            matrix = self._matrix(project_id)
            token = fingerprint({"matrix": _matrix_context(matrix), "layout": "test-status-v1"})
            return record.official_folder_path / "Submitted Material" / f"{record.dl_number} test status.xlsx", token, ()
        if key in {"customer_feedback_form", "test_record", "fee_form"}:
            basic = self._basic(project_id)
            if key == "customer_feedback_form":
                resource = self.resources.get_by_type(ExternalResourceType.PROJECT_FOLDER_TEMPLATE)
                if resource is None or not resource.active:
                    raise ValueError("Template folder is not configured or active.")
                _template_context(discover_customer_feedback_template(Path(resource.path)))
                context = self.input_context.context(project_id, key)
                owner = str(basic.values.get("project_leader", "") or "").strip()
                # Preserve the existing form naming fallback when Basic has no leader.
                if not owner and self.forms is not None:
                    forms = self.forms.list_by_project(project_id)
                    owner = str(getattr(forms[-1], "assigned_personnel", "") or "").strip() if forms else ""
                suffix = "_" + _safe_name(owner) if owner else ""
                target = record.official_folder_path / f"{record.dl_number} Customer Feedback Form{suffix}.xlsx"
                return target, fingerprint({"basic": _basic_context(basic), "inputs": context, "owner": owner}), ()
            matrix = self._matrix(project_id)
            if key == "test_record":
                _template_context(resolve_test_record_template_path(self.resources,
                    configured_template_path=self.settings.test_record.template_path))
                context = self.input_context.context(project_id, key)
                target = record.official_folder_path / "Submitted Material" / f"{record.dl_number} Test Record.docx"
                return target, fingerprint({"matrix": _matrix_context(matrix), "basic": _basic_context(basic), "inputs": context}), ()
            fee = self._fee(project_id)
            template = resolve_fee_evaluation_template_path(self.resources)
            edited_values_from_json(edited_values_json_from_confirmed_fee_snapshot(fee.pricing_snapshot_json))
            target = record.official_folder_path / f"{record.dl_number} Fee Form.xlsx"
            token = fingerprint({"matrix": _matrix_context(matrix), "basic": _basic_context(basic),
                "fee_id": fee.confirmed_fee_id, "fee_revision": getattr(fee, "confirmed_fee_revision", getattr(fee, "revision", 0)),
                "pricing_edit_id": fee.pricing_draft_edit_id, "pricing_snapshot": fee.pricing_snapshot_json,
                "template": _template_context(template), "fill_mode": "matrix_basic"})
            return target, token, ()
        if key in {"llcr_record", "cr_record", "ir_dwv_record"}:
            matrix = self._matrix(project_id)
            record_type = key.removesuffix("_record")
            if not _has_relevant_steps(matrix, record_type):
                raise ValueError("Not applicable: confirmed Matrix has no relevant selected test steps.")
            projection = (self.ir if record_type == "ir_dwv" else self.llcr).preview(project_id, record_type)
            diagnostics = tuple(getattr(projection, "diagnostics", ()))
            warnings = tuple(item.message for item in diagnostics
                if getattr(item, "level", getattr(item, "severity", "info")) not in {"error", "blocker", "blocked", "review_required"})
            if projection.status == "empty":
                raise ValueError("Not applicable: confirmed Matrix has no relevant selected test steps.")
            if record_type != "ir_dwv" and not getattr(projection, "point_profile_fingerprint", None):
                raise ValueError("Confirm an explicit Point Profile before generating LLCR/CR records.")
            if (projection.status not in {"ready", "complete", "partial_compatible"}
                    or not projection.preview_fingerprint or not projection.sections):
                errors = " ".join(item.message for item in diagnostics
                    if getattr(item, "level", getattr(item, "severity", "info")) in {"error", "blocker", "blocked", "review_required"})
                raise ValueError(errors or "Review explicit test points and sample quantities before generation.")
            label = "IR&DWV" if record_type == "ir_dwv" else record_type.upper()
            return (record.official_folder_path / "Test results" / f"{record.dl_number} {label} Record.xlsx",
                    fingerprint({"projection": projection.preview_fingerprint, "layout": "record-v1"}), warnings)
        if key == "application_form":
            context = self.application.prepare_staging(project_id)
            return context["target"], fingerprint(context), ()
        raise ValueError("Unsupported project file.")

    def _matrix(self, project_id):
        matrix = self.confirmed.get_active_by_project(project_id)
        if matrix is None:
            raise ValueError("Confirm Matrix before generating this file.")
        return matrix

    def generate(self, project_id, key, stage_dir: Path, target_name: str) -> Path:
        """Use the assigned operation stage; never publish or register here."""
        workspace = self.workspace(project_id)
        require_safe_output_path(stage_dir)
        stage_parent = Path(workspace["stage_parent"])
        if (not stage_dir.is_absolute() or not stage_dir.is_relative_to(stage_parent)
                or stage_dir == stage_parent or not stage_dir.is_dir() or any(stage_dir.iterdir())):
            raise ValueError("Generation requires an empty owned operation staging directory.")
        item = self.source(project_id, key)
        if item.status != "ready" or item.target is None:
            raise ValueError(item.message)
        if target_name != item.target.name or Path(target_name).name != target_name:
            raise ValueError("Staged filename does not match the reviewed target.")
        if key == "application_form":
            result = self.application.generate_staged(self.application.prepare_staging(project_id),
                stage_dir=stage_dir, target_name=target_name)
        elif key in {"llcr_record", "cr_record", "ir_dwv_record"}:
            record_type = key.removesuffix("_record")
            projection = (self.ir if record_type == "ir_dwv" else self.llcr).preview(project_id, record_type)
            if record_type == "ir_dwv":
                result = self.ir.write(output_path=stage_dir / target_name, projection=projection)
            else:
                result = self.llcr_writer.write(output_path=stage_dir / target_name, projection=projection)
        else:
            result = self.staging.generate(project_id=project_id, key=key, target_name=target_name,
                basic_information=self._basic(project_id) if key != "test_status" else None,
                confirmed_fee=self._fee(project_id) if key == "fee_form" else None, stage_dir=stage_dir)
        result = Path(result)
        require_safe_output_path(result)
        if result.parent != stage_dir or not result.is_file():
            raise ValueError("Generator returned a file outside its operation staging directory.")
        return result

    def registration(self, project_id, key):
        """Freeze lineage before publication, independent of later source availability."""
        item = self.source(project_id, key)
        if item.status != "ready" or not item.source_token:
            raise ValueError(item.message)
        summary = self.outputs.get_status_summary(project_id)
        return {"draft_id": getattr(summary, "active_draft_id", None), "output_kind": item.output_kind,
                "source_context_signature": f"project-file-generation:{key}:{item.source_token}"}

    def register(self, state, item, effect):
        """Commit a published output exactly once using its frozen lineage."""
        target = Path(item["target"])
        require_safe_output_path(target)
        if (str(target) != effect["target"] or not target.is_file()
                or file_hash(target) != effect["sha"] or file_identity(target) != effect["identity"]):
            raise ValueError("Published output changed before registration.")
        frozen = item["registration"]
        if frozen["output_kind"] != item["output_kind"] or not frozen["source_context_signature"]:
            raise ValueError("Frozen output registration is invalid.")
        size = target.stat().st_size
        command = RegisterProjectOutputCommand(project_id=state["project_id"],
            output_kind=ProjectOutputKind(frozen["output_kind"]),
            status=ProjectOutputStatus.CURRENT, source=ProjectOutputSource.SYSTEM_GENERATED,
            output_path=str(target), draft_id=frozen.get("draft_id"),
            output_sha256=effect["sha"], output_size_bytes=size,
            source_context_signature=frozen["source_context_signature"])
        for record in self.outputs.list_records(state["project_id"]):
            if all(getattr(record, field) == getattr(command, field) for field in (
                "draft_id", "output_kind", "status", "source", "output_path", "output_sha256",
                "output_size_bytes", "source_context_signature")):
                self.commit()
                return str(record.output_record_id)
        record = self.outputs.register_output(command)
        if file_hash(target) != effect["sha"] or file_identity(target) != effect["identity"]:
            raise ValueError("Published output changed during registration.")
        self.commit()
        return str(record.output_record_id)

    def _basic(self, project_id):
        basic = self.basic.get_latest_confirmed(project_id)
        if basic is None:
            raise ValueError("Confirm Basic Information before generating this file.")
        return basic

    def _fee(self, project_id):
        if self.fees is None:
            raise ValueError("Confirm Fee before generating Fee Form.")
        result = self.fees.get_latest(project_id)
        fee = getattr(result, "latest_confirmed_fee", None)
        if getattr(result, "status", None) != "current" or fee is None:
            raise ValueError("Confirm a current Fee before generating Fee Form.")
        return fee


def _has_relevant_steps(matrix, record_type):
    if not hasattr(matrix, "rows") or not hasattr(matrix, "step_quantities"):
        return True
    rows = {row.confirmed_row_id: row for row in matrix.rows}
    groups = {group.confirmed_group_id for group in matrix.groups}
    for quantity in matrix.step_quantities:
        row = rows.get(quantity.confirmed_row_id)
        if row is None or quantity.confirmed_group_id not in groups:
            continue
        if record_type == "ir_dwv":
            if electrical_test_kind(row.test_item):
                return True
        elif matrix_record_type(row, quantity) == record_type:
            return True
    return False


def _template_context(template):
    require_safe_output_path(template)
    if not template.is_file():
        raise ValueError("The configured template is unavailable.")
    return {"path": str(template.resolve()), "sha256": file_hash(template), "identity": file_identity(template)}


def _basic_context(basic):
    return {"version": basic.version, "signature": basic.source_signature_hash, "values": basic.values}


def _safe_name(value):
    return "".join(ch if ch.isalnum() or ch in {"-", " "} else " " for ch in value).strip(" .")


def _matrix_context(matrix):
    return {"confirmed_matrix_id": matrix.version.confirmed_matrix_id,
            "confirmed_revision": matrix.version.confirmed_revision}
