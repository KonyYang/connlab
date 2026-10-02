"""Read-only package readiness using the existing file-specific previews."""

import os
from pathlib import Path

from backend.application.confirmed_matrix_llcr_cr_record_projection import matrix_record_type
from backend.application.matrix_test_points_authority import electrical_test_kind

from backend.shared.operation_diagnostics import safe_text
from backend.infrastructure.files.recoverable_output_publisher import file_hash, file_identity
from backend.infrastructure.official_workspace_manifest import OfficialWorkspaceManifestGateway


def contact_record_preflight(project_id, workspace, session, *, settings=None, rebuilding=False):
    """Preview optional Matrix record files and bind old-file identity to approval."""
    from backend.api import dependencies as deps

    snapshot = deps.ConfirmedMatrixAuthorityRepository(session).get_active_by_project(project_id)
    if snapshot is None or workspace.official_folder_path is None:
        return {}, []
    rows = {row.confirmed_row_id: row for row in snapshot.rows}
    kinds = set()
    for quantity in snapshot.step_quantities:
        row = rows.get(quantity.confirmed_row_id)
        if row is None:
            continue
        kind = matrix_record_type(row, quantity)
        if kind is not None:
            kinds.add(kind)
        if electrical_test_kind(row.test_item) is not None:
            kinds.add("ir_dwv")
    if not kinds:
        return {}, []
    targets, items = {}, []
    for kind in ("llcr", "cr", "ir_dwv"):
        if kind not in kinds:
            continue
        form_label = "IR&DWV" if kind == "ir_dwv" else kind.upper()
        label = f"{form_label} blank record"
        dl = "".join(ch if ch.isalnum() or ch in {"-", " "} else " " for ch in workspace.dl_number).strip(" .")
        target = workspace.official_folder_path / "Test results" / f"{dl} {form_label} Record.xlsx"
        entry = {"target": str(target), "prior": None, "preview_fingerprint": None, "action": "skip"}
        template = getattr(workspace, "template_path", None)
        template_form = Path(template) / "Test results" / target.name if template else None
        if (template_form is not None and (rebuilding or getattr(workspace, "status", None) == "ready")
                and os.path.lexists(template_form)):
            status, action = "blocked", "blocked"
            message = (
                f"The project template already contains {target.name}; review it before "
                "generating a new official blank form."
            )
        elif kind != "ir_dwv" and snapshot.version.point_profile is None:
            status, action = "current", "skip"
            message = f"{kind.upper()} form was skipped: confirm explicit Test points in Matrix Editor first."
        else:
            projection = (
                deps.get_matrix_editor_ir_dwv_record_generation_service(session, settings).preview(project_id)
                if kind == "ir_dwv" else
                deps.get_llcr_cr_record_workbook_preview_service(session).preview(project_id, kind)
            )
            errors = [diagnostic for diagnostic in projection.diagnostics
                      if getattr(diagnostic, "level", "error") == "error"] if projection.status != "ready" else []
            missing_codes = ({"missing_measurement_pairs"} if kind == "ir_dwv" else
                             {"step_point_coverage_empty", "point_profile_not_confirmed"})
            missing_coverage = (projection.status == "empty" and kind != "ir_dwv") or (
                projection.status == "blocked"
                and bool(errors)
                and all(
                    getattr(diagnostic, "code", None) in missing_codes
                    for diagnostic in errors
                )
            )
            if missing_coverage:
                status, action = "current", "skip"
                message = ("IR&DWV form was skipped: confirm explicit measurement pairs in Matrix Editor first."
                           if kind == "ir_dwv" else (
                    f"{kind.upper()} form was skipped: no explicit Test points cover "
                    "the confirmed Matrix steps."
                ))
            elif projection.status != "ready" or not projection.preview_fingerprint:
                status, action = "blocked", "blocked"
                message = (errors[0].message if errors else f"{form_label} record projection needs review.")
            else:
                entry["preview_fingerprint"] = projection.preview_fingerprint
                try:
                    paths = (target, *target.parents)
                    if OfficialWorkspaceManifestGateway.first_redirected_path(*paths) is not None:
                        raise ValueError("Contact record path redirects through a link or junction.")
                    if os.path.lexists(target) and not target.is_file():
                        raise ValueError("Existing contact record is not a regular file.")
                    sha = None if rebuilding else file_hash(target)
                    entry["prior"] = {"sha": sha, "identity": file_identity(target)} if sha else None
                    action = "archive_generate" if sha else "generate"
                    status = "ready"
                    message = (f"Existing {form_label} file, including any measurements, will be moved to "
                               "History/Test results before a new blank form is created."
                               if sha else (
                                   f"Existing folder contents remain in History/Folders; create a new {form_label} "
                                   "blank form in Test results."
                                   if rebuilding and os.path.lexists(target)
                                   else f"Create a new {form_label} blank form in Test results."
                               ))
                except (OSError, ValueError) as exc:
                    status, action = "blocked", "blocked"
                    message = f"Cannot verify {form_label} form target: {exc}"
        entry["action"] = action
        if action == "skip":
            entry["warning"] = message
        targets[kind] = entry
        items.append({"key": f"{kind}_record", "label": label,
                      "status": status, "action": action, "message": safe_text(message)})
    return targets, items


def package_preflight(project_id, workspace, session, settings, *, rebuilding=False):
    from backend.api import dependencies as deps

    directory_ready = workspace.status in {"ready", "adoptable", "completed"}
    planned = workspace if workspace.official_folder_path and workspace.dl_number else None
    items = []
    if planned is not None:
        forms = deps.get_project_folder_required_forms_service(session, settings).preview(
            project_id, planned_workspace=planned, rebuilding=rebuilding)
        items.extend({"key": item.key, "label": item.label, "status": item.status,
                      "action": item.action, "message": safe_text(item.message)} for item in forms.items)
        contact_targets, contact_items = contact_record_preflight(
            project_id, planned, session, settings=settings, rebuilding=rebuilding,
        )
        items.extend(contact_items)
        materials = deps.get_project_request_material_collection_service(session).preview(
            project_id, planned_workspace=planned, rebuilding=rebuilding)
        materials_ready = not materials.blockers and all(
            item.action in {"copy", "already_present"} and item.status not in {"missing", "missing_source", "needs_review"}
            for item in materials.items)
        replaced_root = workspace.local_workspace_path if workspace.conflict_paths == (workspace.local_workspace_path,) else workspace.official_folder_path
        source_inside_target = rebuilding and any(
            item.source_path.resolve().is_relative_to(replaced_root.resolve())
            for item in materials.items if item.source_path is not None)
        if source_inside_target:
            materials_ready = False
        material_errors = [item.message for item in materials.items
                           if item.action not in {"copy", "already_present"}
                           or item.status in {"missing", "missing_source", "needs_review"}]
        material_conflict_only = (
            not source_inside_target
            and any(item.status == "conflict" for item in materials.items)
            and all(item.status not in {"missing", "missing_source", "needs_review"}
                    and (item.action in {"copy", "already_present"} or item.status == "conflict")
                    for item in materials.items)
            and all(blocker == "Target file conflict" for blocker in materials.blockers)
        )
        items.insert(0, {"key": "materials", "label": "Request materials",
                        "status": "ready" if materials_ready else "conflict" if material_conflict_only else "blocked",
                        "action": "collect" if materials_ready else "review" if material_conflict_only else "blocked",
                        "message": ("Source material is inside the folder being rebuilt. Import an independent source copy before rebuilding."
                                    if source_inside_target else safe_text("; ".join([*materials.blockers, *material_errors] or materials.warnings)
                                             or "Source materials are ready for collection."))})
    else:
        contact_targets = {}
        from backend.application.project_folder_required_forms_service import REQUIRED_FORM_DEFINITIONS
        for key, label, *_ in REQUIRED_FORM_DEFINITIONS:
            items.append({"key": key, "label": label, "status": "blocked", "action": "blocked",
                          "message": "Resolve the project folder location and identity first."})

    try:
        basic = deps.ProjectBasicInformationSnapshotReader(
            deps.ProjectBasicInformationRepository(session)).get_latest_confirmed(project_id)
        if basic is None:
            raise ValueError("Confirm Basic Information before Application Form write-back.")
        schedule = deps.get_project_schedule_output_reader(session).get_latest_confirmed(project_id)
        if schedule is None:
            raise ValueError("Confirm Matrix plan dates before Application Form write-back.")
        service = deps.get_project_application_form_write_back_service(session, settings)
        indexed = deps.ProjectOfficialWorkspaceRepository(session).get_by_project(project_id)
        if not rebuilding and indexed is not None and indexed.official_folder_path.is_dir():
            application = service.preview(project_id)
        else:
            forms = deps.ApplicationFormRepository(session).list_by_project(project_id)
            if len(forms) != 1:
                raise ValueError("Select one Application Form before write-back.")
            application = {"key": "application_form", "label": "Application Form",
                           "status": "waiting", "action": "wait",
                           "message": "Requires the selected Application Form to be archived first; target safety is checked after collection."}
    except (ValueError, LookupError, OSError) as exc:
        application = {"key": "application_form", "label": "Application Form",
                       "status": "blocked", "action": "blocked", "message": safe_text(exc)}
    items.append({key: application[key] for key in ("key", "label", "status", "action", "message")})
    return {"directory_status": workspace.status,
            "package_ready": directory_ready and all(item["status"] in {"ready", "current"} for item in items),
            "contact_record_targets": contact_targets,
            "items": items}
