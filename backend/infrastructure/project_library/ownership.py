"""Explicit ownership graph and path contracts for one portable project.

The table list and canonical parent links are a versioned product contract. SQL
foreign keys validate this graph; they do not decide what belongs to a project.
"""
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
from sqlalchemy import select, or_, Date, DateTime, Numeric, inspect
from backend.domain.project_library import ProjectLibraryConflict, ProjectLibraryError
from backend.infrastructure.storage.database import Base

DIRECT_TABLES = (
    "projects", "application_forms", "sample_infos", "ltr_records", "project_registry_events",
    "project_temporary_contexts", "project_cleanup_audit_records", "project_lifecycle_events",
    "project_folder_records", "project_official_workspace_records", "file_assets",
    "project_request_material_collections", "project_request_material_collection_items",
    "public_drive_upload_file_records", "project_public_folder_workflow_states",
    "project_public_folder_workflow_operations", "project_public_folder_workflow_file_records",
    "project_test_plan_drafts", "project_output_records", "project_basic_information_records",
    "fee_evaluation_pricing_draft_edits", "matrix_fee_pending_rebases", "confirmed_fee_versions",
    "source_matrix_import_records", "source_matrix_snapshots", "project_matrix_draft_records",
    "confirmed_matrix_versions", "measurement_plan_roots", "contact_point_profile_roots",
    "project_schedule_revisions", "result_dataset_revisions", "report_draft_revisions",
    "report_authoring_revisions",
)
PARENTS = {
    "precheck_results": ("application_forms", "application_form_id", "form_id"),
    "precheck_issues": ("precheck_results", "result_id", "result_id"),
    "source_matrix_row_snapshots": ("source_matrix_snapshots", "snapshot_id", "snapshot_id"),
    "source_matrix_group_snapshots": ("source_matrix_snapshots", "snapshot_id", "snapshot_id"),
    "source_matrix_cell_snapshots": ("source_matrix_snapshots", "snapshot_id", "snapshot_id"),
    "source_matrix_duration_authorities": ("source_matrix_snapshots", "source_snapshot_id", "snapshot_id"),
    **{name: ("project_matrix_draft_records", "project_matrix_draft_id", "project_matrix_draft_id")
       for name in ("project_matrix_draft_groups", "project_matrix_draft_rows", "project_matrix_draft_cells",
                    "project_matrix_draft_step_quantities", "project_matrix_draft_step_text_overrides",
                    "project_matrix_draft_duration_authorities")},
    **{name: ("confirmed_matrix_versions", "confirmed_matrix_id", "confirmed_matrix_id")
       for name in ("confirmed_matrix_groups", "confirmed_matrix_rows", "confirmed_matrix_cells",
                    "confirmed_matrix_step_quantities", "confirmed_matrix_step_text_overrides",
                    "confirmed_matrix_duration_authorities")},
    "measurement_plan_revisions": ("measurement_plan_roots", "measurement_plan_root_id", "measurement_plan_root_id"),
    "measurement_plan_target_snapshots": ("measurement_plan_revisions", "measurement_plan_revision_id", "measurement_plan_revision_id"),
    "measurement_plan_family_snapshots": ("measurement_plan_target_snapshots", "measurement_plan_target_snapshot_id", "measurement_plan_target_snapshot_id"),
    "measurement_plan_impacts": ("measurement_plan_roots", "measurement_plan_root_id", "measurement_plan_root_id"),
    "measurement_plan_audits": ("measurement_plan_roots", "measurement_plan_root_id", "measurement_plan_root_id"),
    "contact_point_profile_revisions": ("contact_point_profile_roots", "contact_point_profile_root_id", "contact_point_profile_root_id"),
    "contact_point_profile_categories": ("contact_point_profile_revisions", "contact_point_profile_revision_id", "contact_point_profile_revision_id"),
    "contact_point_profile_cr_category_selections": ("contact_point_profile_revisions", "contact_point_profile_revision_id", "contact_point_profile_revision_id"),
}
LINEAGE_TABLES = ("intake_packages", "intake_assets", "intake_cases", "intake_drafts", "ltr_association_events")
TABLES = frozenset((*DIRECT_TABLES, *PARENTS, *LINEAGE_TABLES))
EXCLUDED_TABLES = frozenset({"external_resources", "lookup_options", "legacy_project_records", "existing_project_locations",
                            "ltr_duplicate_resolution_tokens", "frozen_field_revision_requests",
                            "project_library_members", "project_library_batches"})

PATH_COLUMNS = {
    "project_folder_records": ("folder_path",),
    "project_official_workspace_records": ("local_workspace_path", "source_book_path", "official_folder_path", "manifest_path"),
    "file_assets": ("path",),
    "project_request_material_collection_items": ("source_path", "target_path"),
    "public_drive_upload_file_records": ("public_path",),
    "project_public_folder_workflow_states": ("local_official_folder_path", "public_open_path", "public_closed_path"),
    "project_public_folder_workflow_operations": ("public_root", "local_official_folder_path", "public_open_path", "public_closed_path", "target_path"),
    "project_public_folder_workflow_file_records": ("public_path",),
    "intake_packages": ("source_stored_path",),
    "intake_assets": ("stored_path",),
    "project_test_plan_drafts": ("source_document_path",),
    "project_output_records": ("output_path",),
    "source_matrix_import_records": ("source_document_path",),
    "report_draft_revisions": ("file_path",),
}
JSON_PATH_KEYS = frozenset({"path", "file_path", "output_path", "source_path", "target_path",
                            "source_document_path", "folder_path", "report_path", "draft_path"})
JSON_PATH_COLUMNS = {
    "report_authoring_revisions": ("payload_json",),
    "project_output_records": ("metadata_json", "source_context_json"),
    "project_basic_information_records": ("payload_json",),
    "project_test_plan_drafts": ("payload_json",),
    "source_matrix_import_records": ("preview_payload_json",),
}
IMPLICIT_ASSET_COLUMNS = {
    "file_assets": ("source_intake_asset_id",),
    "project_test_plan_drafts": ("source_asset_id",),
    "source_matrix_import_records": ("source_asset_id",),
    "project_request_material_collection_items": ("source_asset_id",),
}


def plain(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    return value


def table(name):
    if name not in TABLES:
        raise ProjectLibraryError("The snapshot contains an unsupported record family.")
    if name not in Base.metadata.tables:
        raise ProjectLibraryError(f"The installed version does not support {name}.")
    return Base.metadata.tables[name]


def rows_where(session, name, condition):
    model = table(name)
    return [plain(dict(row)) for row in session.execute(select(model).where(condition)).mappings()]


def selected(session, name, column, values):
    values = {value for value in values if value is not None}
    if not values:
        return []
    model = table(name)
    return rows_where(session, name, model.c[column].in_(values))


def capture(session, project_id, *, validate_history=True):
    if session.new or session.dirty or session.deleted:
        raise ProjectLibraryConflict("Finish the current project update before preparing a snapshot.")
    connection = session.connection()
    if not connection.connection.driver_connection.in_transaction:
        connection.exec_driver_sql("BEGIN")
    try:
        known = set(inspect(connection).get_table_names())
        unknown = known - TABLES - EXCLUDED_TABLES - {"sqlite_sequence"}
        if unknown:
            raise ProjectLibraryError("This database contains record families not covered by the portable contract: " + ", ".join(sorted(unknown)))
        result = {}
        for name in DIRECT_TABLES:
            if name not in known:
                result[name] = []
                continue
            model = table(name)
            result[name] = rows_where(session, name, model.c.project_id == project_id)
        if len(result["projects"]) != 1:
            raise LookupError("The managed project no longer exists.")
        remaining = dict(PARENTS)
        while remaining:
            progressed = False
            for name, (parent, column, parent_column) in list(remaining.items()):
                if parent not in result:
                    continue
                result[name] = selected(session, name, column, [row[parent_column] for row in result[parent]]) if name in known else []
                del remaining[name]
                progressed = True
            if not progressed:
                raise ProjectLibraryError("The portable ownership contract has an unresolved dependency.")
        _capture_intake(session, project_id, result)
        events = table("ltr_association_events")
        result["ltr_association_events"] = rows_where(session, "ltr_association_events",
            or_(events.c.old_project_id == project_id, events.c.new_project_id == project_id))
        for row in result["report_authoring_revisions"]:
            row.pop("id", None)  # Storage-local autoincrement identity is not a report revision.
        issues = validate_relations(result) if validate_history else []
        if issues:
            raise ProjectLibraryError("Project history has unresolved references; review before taking it to another computer: " + "; ".join(issues[:5]))
        return {name: sorted(rows, key=lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False)) for name, rows in result.items()}
    finally:
        session.rollback()


def _capture_intake(session, project_id, result):
    case_ids = {row.get("source_case_id") for row in result["project_test_plan_drafts"] if row.get("source_case_id")}
    cases = table("intake_cases")
    result["intake_cases"] = rows_where(session, "intake_cases",
        or_(cases.c.confirmed_project_id == project_id, cases.c.case_id.in_(case_ids)))
    if any(row.get("confirmed_project_id") not in (None, project_id) for row in result["intake_cases"]):
        raise ProjectLibraryError("A required intake case belongs to a different project. Review its lineage.")
    draft_ids = {row.get("source_draft_id") for row in result["project_test_plan_drafts"] if row.get("source_draft_id")}
    drafts = table("intake_drafts")
    result["intake_drafts"] = rows_where(session, "intake_drafts",
        or_(drafts.c.case_id.in_([row["case_id"] for row in result["intake_cases"]]), drafts.c.draft_id.in_(draft_ids)))
    asset_ids = {row.get("selected_form_asset_id") for row in result["intake_cases"]}
    for name, columns in IMPLICIT_ASSET_COLUMNS.items():
        asset_ids.update(row.get(column) for row in result[name] for column in columns)
    for row in result["project_temporary_contexts"]:
        if row.get("source_asset_ids_json"):
            asset_ids.update(json.loads(row["source_asset_ids_json"]))
    result["intake_assets"] = selected(session, "intake_assets", "asset_id", asset_ids)
    package_ids = {row["package_id"] for row in result["intake_cases"] + result["intake_assets"]}
    package_ids.update(row.get("source_package_id") for row in result["file_assets"])
    result["intake_packages"] = selected(session, "intake_packages", "package_id", package_ids)
    for package in result["intake_packages"]:
        all_asset_ids = {row["asset_id"] for row in selected(session, "intake_assets", "package_id", [package["package_id"]])}
        if all_asset_ids - {row["asset_id"] for row in result["intake_assets"]}:
            # Preserve package provenance, not a container that embeds unrelated attachments.
            package["source_stored_path"] = "shared-package-provenance:" + package["package_id"]


def validate_relations(rows):
    issues = []
    for name, records in rows.items():
        model = table(name)
        for constraint in model.foreign_key_constraints:
            elements = list(constraint.elements)
            parent_name = elements[0].column.table.name
            if parent_name not in rows:
                continue
            child_names = [element.parent.name for element in elements]
            parent_names = [element.column.name for element in elements]
            parents = {tuple(parent.get(key) for key in parent_names) for parent in rows[parent_name]}
            for row in records:
                value = tuple(row.get(key) for key in child_names)
                if any(item is None for item in value):
                    continue
                if value not in parents:
                    issues.append(f"{name} refers to a missing {parent_name} record")
                    break
    issues.extend(validate_explicit_references(rows))
    return issues


def validate_explicit_references(rows):
    """Validate supported semantic links that SQLite deliberately does not own."""
    issues = []
    def values(name, key):
        return {row.get(key) for row in rows.get(name, [])}
    def require(owner, value, allowed, label):
        if value not in (None, "") and value not in allowed:
            issues.append(owner + " refers to missing " + label + ": " + str(value))
    matrix = values("confirmed_matrix_versions", "confirmed_matrix_id")
    sources = values("file_assets", "asset_id") | values("intake_assets", "asset_id")
    refs = {
        "file_assets": (("source_package_id", "intake_packages", "package_id"), ("source_intake_asset_id", "intake_assets", "asset_id")),
        "project_test_plan_drafts": (("source_case_id", "intake_cases", "case_id"), ("source_draft_id", "intake_drafts", "draft_id")),
        "result_dataset_revisions": (("confirmed_matrix_id", "confirmed_matrix_versions", "confirmed_matrix_id"),),
        "report_draft_revisions": (("confirmed_matrix_id", "confirmed_matrix_versions", "confirmed_matrix_id"), ("base_report_revision_id", "report_draft_revisions", "report_revision_id")),
        "fee_evaluation_pricing_draft_edits": (("confirmed_matrix_id", "confirmed_matrix_versions", "confirmed_matrix_id"),),
        "matrix_fee_pending_rebases": (("base_confirmed_matrix_id", "confirmed_matrix_versions", "confirmed_matrix_id"),),
        "confirmed_fee_versions": (("confirmed_matrix_id", "confirmed_matrix_versions", "confirmed_matrix_id"), ("pricing_draft_edit_id", "fee_evaluation_pricing_draft_edits", "draft_edit_id")),
    }
    for name, links in refs.items():
        for row in rows.get(name, []):
            for key, parent, parent_key in links:
                require(name, row.get(key), values(parent, parent_key), parent)
    for name in ("project_test_plan_drafts", "source_matrix_import_records", "project_request_material_collection_items"):
        for row in rows.get(name, []):
            require(name, row.get("source_asset_id"), sources, "source asset")
    for row in rows.get("project_temporary_contexts", []):
        for asset_id in json.loads(row.get("source_asset_ids_json") or "[]"):
            require("project_temporary_contexts", asset_id, sources, "source asset")
    for row in rows.get("result_dataset_revisions", []):
        owner = "result_dataset_revisions"
        version = next((v for v in rows["confirmed_matrix_versions"] if v["confirmed_matrix_id"] == row["confirmed_matrix_id"]), None)
        if version and version["confirmed_revision"] != row["confirmed_matrix_revision"]:
            issues.append(owner + " refers to a different confirmed Matrix revision")
        payload = json.loads(row["payload_json"])
        groups = {g["confirmed_group_id"] for g in rows["confirmed_matrix_groups"] if g["confirmed_matrix_id"] == row["confirmed_matrix_id"]}
        row_ids = {r["confirmed_row_id"] for r in rows["confirmed_matrix_rows"] if r["confirmed_matrix_id"] == row["confirmed_matrix_id"]}
        for entry in payload.get("entries", []):
            require(owner, entry.get("confirmed_group_id"), groups, "Matrix group")
            require(owner, entry.get("confirmed_row_id"), row_ids, "Matrix row")
    for record in rows.get("report_authoring_revisions", []):
        owner = "report_authoring_revisions"
        payload = json.loads(record["payload_json"])
        local_sources = {source["source_id"] for source in payload.get("sources", [])}
        require(owner, payload.get("base_source_id"), local_sources, "report evidence source")
        for section in ("mappings", "results", "photos"):
            for item in payload.get(section, []):
                require(owner, item.get("source_id"), local_sources, "report evidence source")
                matrix_id = item.get("matrix_id")
                require(owner, matrix_id, matrix, "Matrix")
                if matrix_id:
                    require(owner, item.get("group_id"), {g["confirmed_group_id"] for g in rows["confirmed_matrix_groups"] if g["confirmed_matrix_id"] == matrix_id}, "Matrix group")
                    require(owner, item.get("row_id"), {r["confirmed_row_id"] for r in rows["confirmed_matrix_rows"] if r["confirmed_matrix_id"] == matrix_id}, "Matrix row")
    return issues


def map_json_paths(value, replace):
    if isinstance(value, dict):
        return {key: replace(item) if key in JSON_PATH_KEYS and isinstance(item, str)
                else map_json_paths(item, replace) for key, item in value.items()}
    if isinstance(value, list):
        return [map_json_paths(item, replace) for item in value]
    return value


def transform_paths(rows, replace):
    result = {}
    for name, records in rows.items():
        result[name] = []
        for original in records:
            row = dict(original)
            for column in PATH_COLUMNS.get(name, ()):
                if column in row and isinstance(row[column], str):
                    row[column] = replace(row[column])
            for column in JSON_PATH_COLUMNS.get(name, ()):
                if row.get(column):
                    payload = json.loads(row[column])
                    row[column] = json.dumps(map_json_paths(payload, replace), sort_keys=True, ensure_ascii=False)
            result[name].append(row)
    return result


def typed_record(name, row):
    model = table(name)
    result = dict(row)
    if set(result) - set(model.c.keys()):
        raise ProjectLibraryError(f"The snapshot has unsupported fields in {name}.")
    for column in model.c:
        value = result.get(column.name)
        if value is not None and isinstance(value, str):
            if isinstance(column.type, DateTime):
                result[column.name] = datetime.fromisoformat(value)
            elif isinstance(column.type, Date):
                result[column.name] = date.fromisoformat(value)
            elif isinstance(column.type, Numeric):
                result[column.name] = Decimal(value)
    return result


def rebind_project_paths(session, project_id, source, target, extra_maps=()):
    # Moving a known project updates only its path fields. Historical reference
    # gaps remain intact and continue to block export, not ordinary file access.
    rows = capture(session, project_id, validate_history=False)
    source, target = Path(source), Path(target)
    mappings = sorted([(source, target), *[(Path(a), Path(b)) for a, b in extra_maps]], key=lambda pair: len(pair[0].parts), reverse=True)
    def replace(value):
        try:
            path = Path(value)
            for old, new in mappings:
                if path.is_absolute() and path.is_relative_to(old):
                    return str(new / path.relative_to(old))
        except (OSError, ValueError):
            pass
        return value
    changed = transform_paths(rows, replace)
    for name, records in changed.items():
        model = table(name)
        for original, current in zip(rows[name], records):
            values = {key: value for key, value in current.items() if value != original.get(key)}
            if not values:
                continue
            keys = [column.name for column in model.primary_key]
            if name == "report_authoring_revisions":
                condition = (model.c.project_id == project_id) & (model.c.revision == current["revision"])
            else:
                condition = None
                for key in keys:
                    predicate = model.c[key] == original[key]
                    condition = predicate if condition is None else condition & predicate
            session.execute(model.update().where(condition).values(**values))
