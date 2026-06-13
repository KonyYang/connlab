"""Request-material preview and collection service for Project Folder preparation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Sequence
from uuid import uuid4

from backend.application.official_project_workspace_service import OfficialWorkspaceRecord
from backend.application.project_request_material_collection_helpers import (
    canonical_path,
    candidate_from_asset,
    dedupe_target_names,
    is_application_form,
    is_confirmed_request_attachment,
    is_request_email,
    preview_status,
    role_priority,
    same_content,
    target,
)
from backend.application.project_request_material_collection_types import (
    FileAssetRepositoryPort,
    OfficialWorkspaceRepositoryPort,
    PlannedTarget,
    ProjectRepositoryPort,
    ProjectRequestMaterialCollectionConflictError,
    ProjectRequestMaterialCollectionError,
    ProjectRequestMaterialCollectionItemRecord,
    ProjectRequestMaterialCollectionNotFoundError,
    ProjectRequestMaterialCollectionRecord,
    RequestMaterialCollectResult,
    RequestMaterialCollectionRepositoryPort,
    RequestMaterialCopyGatewayPort,
    RequestMaterialPreview,
    RequestMaterialPreviewItem,
    SourceCandidate,
)
from backend.domain import FileAsset, FileAssetType


class ProjectRequestMaterialCollectionService:
    """Preview and collect request material into the local Project Folder."""

    def __init__(
        self,
        *,
        project_repository: ProjectRepositoryPort,
        workspace_repository: OfficialWorkspaceRepositoryPort,
        file_asset_repository: FileAssetRepositoryPort,
        collection_repository: RequestMaterialCollectionRepositoryPort,
        copy_gateway: RequestMaterialCopyGatewayPort,
    ) -> None:
        """Create the service with application-layer ports."""
        self._projects = project_repository
        self._workspaces = workspace_repository
        self._assets = file_asset_repository
        self._collections = collection_repository
        self._copy_gateway = copy_gateway

    def preview(self, project_id: str) -> RequestMaterialPreview:
        """Return a read-only preview of request-material collection."""
        project = self._projects.get(project_id)
        if project is None:
            raise ProjectRequestMaterialCollectionNotFoundError(
                f"Project not found: {project_id}"
            )
        workspace = self._workspaces.get_by_project(project_id)
        if workspace is None or not workspace.official_folder_path.is_dir():
            return RequestMaterialPreview(
                project_id=project_id,
                local_workspace_path=None,
                source_book_path=None,
                official_project_folder_path=None,
                status="blocked",
                items=tuple(),
                blockers=("Create local project folder before collecting request material.",),
                warnings=tuple(),
            )

        candidates = self._dedupe_candidates(self._assets.list_by_project(project_id))
        blockers: list[str] = []
        warnings: list[str] = []
        email_candidates = [candidate for candidate in candidates if is_request_email(candidate)]
        if len(email_candidates) > 1:
            blockers.append("Multiple request email candidates need review")
        if not email_candidates:
            warnings.append("Request email missing")

        application_forms = [
            candidate for candidate in candidates if is_application_form(candidate)
        ]
        if not application_forms:
            blockers.append("Selected Application Form source file is missing")
        form_candidate = application_forms[0] if application_forms else None
        if form_candidate and not form_candidate.source_exists:
            blockers.append("Selected Application Form source file is missing")

        planned = self._plan_targets(
            workspace,
            email_candidates[:1],
            form_candidate,
            [
                candidate
                for candidate in candidates
                if candidate not in email_candidates and candidate is not form_candidate
            ],
        )
        items = self._materialize_items(planned, blockers)
        if any(item.status == "needs_review" for item in items):
            warnings.append(
                "Attachment candidates need review before Submitted Material placement"
            )
        status = preview_status(items, blockers, warnings)
        return RequestMaterialPreview(
            project_id=project_id,
            local_workspace_path=workspace.local_workspace_path,
            source_book_path=workspace.source_book_path,
            official_project_folder_path=workspace.official_folder_path,
            status=status,
            items=items,
            blockers=tuple(blockers),
            warnings=tuple(dict.fromkeys(warnings)),
        )

    def collect(self, project_id: str) -> RequestMaterialCollectResult:
        """Copy request material after re-running preview and conflict checks."""
        preview = self.preview(project_id)
        if preview.status in {"blocked", "conflict"}:
            detail = preview.blockers[0] if preview.blockers else "Target file conflict"
            raise ProjectRequestMaterialCollectionConflictError(detail)
        assert preview.local_workspace_path is not None
        collection_id = uuid4().hex
        staging_root = (
            preview.local_workspace_path
            / ".connlab"
            / "tmp"
            / f"request-material-{collection_id}"
        )
        copy_items = [
            item
            for item in preview.items
            if item.action == "copy" and item.status in {"planned", "needs_review"}
        ]
        copied_paths = self._copy_gateway.copy_items(
            items=copy_items,
            staging_root=staging_root,
        )
        after = self.preview(project_id)
        result = RequestMaterialCollectResult(
            project_id=project_id,
            collection_id=collection_id,
            status=after.status,
            items=after.items,
            copied_paths=tuple(copied_paths),
            already_present_paths=tuple(
                item.target_path for item in after.items if item.action == "already_present"
            ),
            skipped_paths=_review_required_source_paths(preview.items),
            missing_source_paths=tuple(
                item.source_path for item in after.items if item.status == "missing_source"
            ),
            conflict_paths=tuple(
                item.target_path for item in after.items if item.status == "conflict"
            ),
            blockers=after.blockers,
            warnings=after.warnings,
        )
        self._persist_result(result)
        return result

    def _dedupe_candidates(self, assets: list[FileAsset]) -> list[SourceCandidate]:
        """Return one source candidate per canonical source path."""
        best_by_path: dict[str, FileAsset] = {}
        for asset in assets:
            key = canonical_path(asset.path)
            current = best_by_path.get(key)
            if current is None or role_priority(asset.source_role) < role_priority(
                current.source_role
            ):
                best_by_path[key] = asset
        return [
            candidate_from_asset(asset, f"path:{canonical_path(asset.path)}")
            for asset in best_by_path.values()
        ]

    def _plan_targets(
        self,
        workspace: OfficialWorkspaceRecord,
        email_candidates: Sequence[SourceCandidate],
        application_form: SourceCandidate | None,
        attachments: Sequence[SourceCandidate],
    ) -> tuple[PlannedTarget, ...]:
        """Build target-copy plans from classified source candidates."""
        source_root = workspace.source_book_path / "Request Material"
        plans: list[PlannedTarget] = []
        for email in email_candidates:
            plans.extend(
                [
                    target(email, "source_book_email", source_root / "E-mail", False),
                    target(
                        email,
                        "official_email",
                        workspace.official_folder_path / "E-mail",
                        False,
                    ),
                ]
            )
        if application_form is not None:
            plans.extend(
                [
                    target(
                        application_form,
                        "source_book_application_form",
                        source_root / "Application Form",
                        False,
                    ),
                    target(
                        application_form,
                        "submitted_material",
                        workspace.official_folder_path / "Submitted Material",
                        False,
                    ),
                ]
            )
        for attachment in attachments:
            if attachment.asset.asset_type is not FileAssetType.ATTACHMENT:
                continue
            review_required = not is_confirmed_request_attachment(attachment)
            plans.append(
                target(
                    attachment,
                    "source_book_attachment",
                    source_root / "Attachments",
                    review_required,
                )
            )
            if not review_required:
                plans.append(
                    target(
                        attachment,
                        "submitted_material",
                        workspace.official_folder_path / "Submitted Material",
                        False,
                    )
                )
        return dedupe_target_names(plans)

    def _materialize_items(
        self,
        plans: tuple[PlannedTarget, ...],
        blockers: list[str],
    ) -> tuple[RequestMaterialPreviewItem, ...]:
        """Convert target plans into preview items with file-system status."""
        items: list[RequestMaterialPreviewItem] = []
        for plan in plans:
            candidate = plan.candidate
            action = "copy"
            status = "planned"
            message = "Ready to copy."
            if not candidate.source_exists:
                action = "skip"
                status = "missing_source"
                message = "Source file is missing."
            elif plan.target_path.exists():
                if same_content(candidate, plan.target_path):
                    action = "already_present"
                    status = "needs_review" if plan.review_required else "already_present"
                    message = "Already collected."
                else:
                    action = "block"
                    status = "conflict"
                    message = "Target file already exists with different content."
                    if "Target file conflict" not in blockers:
                        blockers.append("Target file conflict")
            elif plan.review_required:
                status = "needs_review"
                message = "Needs review before Submitted Material placement."
            items.append(_preview_item(candidate, plan, action, status, message))
        return tuple(items)

    def _persist_result(self, result: RequestMaterialCollectResult) -> None:
        """Persist a collection run summary and item rows."""
        now = datetime.now(UTC).replace(microsecond=0).isoformat()
        collection = ProjectRequestMaterialCollectionRecord(
            collection_id=result.collection_id,
            project_id=result.project_id,
            workspace_id=None,
            status=result.status,
            item_count=len(result.items),
            copied_count=len(result.copied_paths),
            already_present_count=len(result.already_present_paths),
            conflict_count=len(result.conflict_paths),
            skipped_count=len(result.skipped_paths),
            missing_source_count=len(result.missing_source_paths),
            created_at=now,
            updated_at=now,
            warnings=result.warnings,
        )
        rows = tuple(
            ProjectRequestMaterialCollectionItemRecord(
                item_id=uuid4().hex,
                collection_id=result.collection_id,
                project_id=result.project_id,
                source_asset_id=item.source_asset_id,
                source_asset_type=item.source_asset_type,
                source_role=item.source_role,
                dedupe_key=item.dedupe_key,
                source_path=item.source_path,
                original_name=item.source_name,
                target_area=item.target_area,
                target_path=item.target_path,
                status=item.status,
                action=item.action,
                review_required=item.review_required,
                size_bytes=item.size_bytes,
                sha256=item.sha256,
            )
            for item in result.items
        )
        self._collections.save_collection(collection, rows)


def _preview_item(
    candidate: SourceCandidate,
    plan: PlannedTarget,
    action: str,
    status: str,
    message: str,
) -> RequestMaterialPreviewItem:
    """Build one preview item from a candidate, target plan, and status."""
    return RequestMaterialPreviewItem(
        source_asset_id=candidate.asset.asset_id,
        source_asset_type=candidate.asset.asset_type.value,
        source_role=candidate.role,
        source_name=candidate.name,
        source_path=candidate.path,
        dedupe_key=candidate.dedupe_key,
        target_area=plan.target_area,
        target_path=plan.target_path,
        action=action,
        status=status,
        message=message,
        review_required=plan.review_required,
        size_bytes=candidate.size_bytes,
        sha256=candidate.sha256,
    )


def _review_required_source_paths(
    items: tuple[RequestMaterialPreviewItem, ...],
) -> tuple:
    """Return source paths for items preserved in Source Book only."""
    return tuple(
        item.source_path
        for item in items
        if item.review_required and item.target_area == "source_book_attachment"
    )
