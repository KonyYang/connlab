"""Planning helpers for request-material collection."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from backend.application.project_request_material_collection_types import (
    PlannedTarget,
    RequestMaterialPreviewItem,
    SourceCandidate,
)
from backend.domain import FileAsset, FileAssetType


def candidate_from_asset(asset: FileAsset, dedupe_key: str) -> SourceCandidate:
    """Create a source candidate from a project file asset."""
    path = asset.path
    exists = path.is_file()
    size = path.stat().st_size if exists else None
    sha = hash_file(path) if exists else asset.sha256
    return SourceCandidate(
        asset=asset,
        dedupe_key=dedupe_key,
        role=asset.source_role,
        name=asset.original_name or path.name,
        path=path,
        source_exists=exists,
        size_bytes=size,
        sha256=sha,
    )


def target(
    candidate: SourceCandidate,
    area: str,
    folder: Path,
    review_required: bool,
) -> PlannedTarget:
    """Build one planned target for a candidate and target folder."""
    filename = safe_material_filename(candidate.name, candidate.asset.asset_id)
    message = (
        "Needs review before Submitted Material placement."
        if review_required
        else "Ready to copy."
    )
    return PlannedTarget(
        candidate=candidate,
        target_area=area,
        target_path=folder / filename,
        review_required=review_required,
        message=message,
    )


def safe_material_filename(original_name: str | None, source_asset_id: str) -> str:
    """Return a Windows-safe filename for request-material targets."""
    base = (original_name or f"request-material-{source_asset_id}").strip()
    cleaned = re.sub(r'[<>:"/\\|?*]+', "_", base)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return cleaned or f"request-material-{source_asset_id}"


def dedupe_target_names(plans: list[PlannedTarget]) -> tuple[PlannedTarget, ...]:
    """Append a stable source id suffix when target names collide."""
    counts: dict[Path, int] = {}
    result: list[PlannedTarget] = []
    for plan in plans:
        count = counts.get(plan.target_path, 0)
        counts[plan.target_path] = count + 1
        if count == 0:
            result.append(plan)
            continue
        suffix = plan.candidate.asset.asset_id[:8]
        target_path = plan.target_path
        renamed = target_path.with_name(
            f"{target_path.stem}-{suffix}{target_path.suffix}"
        )
        result.append(
            PlannedTarget(
                candidate=plan.candidate,
                target_area=plan.target_area,
                target_path=renamed,
                review_required=plan.review_required,
                message=plan.message,
            )
        )
    return tuple(result)


def is_request_email(candidate: SourceCandidate) -> bool:
    """Return whether a candidate is the request email."""
    role = (candidate.role or "").casefold()
    return role == "email_source"


def is_application_form(candidate: SourceCandidate) -> bool:
    """Return whether a candidate is the selected Application Form."""
    return (
        candidate.asset.asset_type is FileAssetType.APPLICATION_FORM
        or (candidate.role or "").casefold() == "selected_application_form"
    )


def application_form_authority_priority(
    asset_type: FileAssetType | str,
    source_role: str | None,
) -> int:
    """Rank the typed current form ahead of legacy role-only candidates."""
    normalized_type = (
        asset_type.value if isinstance(asset_type, FileAssetType) else str(asset_type)
    ).casefold()
    if normalized_type == FileAssetType.APPLICATION_FORM.value:
        return 0
    if (source_role or "").casefold() == "selected_application_form":
        return 1
    return 2


def is_confirmed_request_attachment(candidate: SourceCandidate) -> bool:
    """Return whether an attachment may be copied into Submitted Material."""
    return (candidate.role or "").casefold() in {"supporting_attachment", "specification"}


def same_content(candidate: SourceCandidate, target_path: Path) -> bool:
    """Return whether the target file content matches the source candidate."""
    if not target_path.is_file() or candidate.size_bytes is None:
        return False
    if target_path.stat().st_size != candidate.size_bytes:
        return False
    target_hash = hash_file(target_path)
    return candidate.sha256 == target_hash if candidate.sha256 else False


def hash_file(path: Path) -> str:
    """Return a SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_path(path: Path) -> str:
    """Return a case-insensitive canonical path key."""
    return str(path).replace("/", "\\").casefold()


def role_priority(role: str | None) -> int:
    """Return lower numbers for higher-confidence request-material roles."""
    return {
        "selected_application_form": 0,
        "email_source": 1,
        "supporting_attachment": 2,
        "specification": 3,
        "application_form_candidate": 4,
        "unknown": 5,
        "inline_image": 6,
        "ignored": 7,
    }.get((role or "").casefold(), 8)


def preview_status(
    items: tuple[RequestMaterialPreviewItem, ...],
    blockers: list[str],
    warnings: list[str],
) -> str:
    """Return the overall preview status from items, blockers, and warnings."""
    if blockers:
        if any(item.status == "conflict" for item in items):
            return "conflict"
        return "blocked"
    if any(item.status == "conflict" for item in items):
        return "conflict"
    if warnings or any(item.status in {"missing_source", "skipped"} for item in items):
        return "partial"
    if any(item.status == "needs_review" for item in items):
        if any(item.action == "copy" for item in items):
            return "partial"
        return "review_required"
    if items and all(item.action == "already_present" for item in items):
        return "collected"
    return "ready"
