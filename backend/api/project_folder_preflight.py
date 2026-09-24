"""Read-only package readiness using the existing file-specific previews."""

from backend.shared.operation_diagnostics import safe_text


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
            raise ValueError("Confirm Project Schedule before Application Form write-back.")
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
            "items": items}
