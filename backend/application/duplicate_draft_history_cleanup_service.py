"""Cleanup historical duplicate intake draft packages by email identity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakePackage,
    IntakePackageSourceType,
)


@dataclass(frozen=True, slots=True)
class DuplicateDraftGroupCandidate:
    """One eligible package candidate in a duplicate draft group."""

    package_id: str
    case_id: str
    draft_exists: bool
    source_original_name: str
    source_size_bytes: int
    source_sha256: str
    package_created_at: str | None
    package_updated_at: str | None


@dataclass(frozen=True, slots=True)
class DuplicateDraftGroupSkip:
    """One package skipped from cleanup candidate grouping."""

    package_id: str
    reason: str


@dataclass(frozen=True, slots=True)
class DuplicateDraftCleanupDryRun:
    """Read-only duplicate draft cleanup report."""

    generated_at: str
    total_packages: int
    candidate_count: int
    duplicate_group_count: int
    keep_package_ids: tuple[str, ...]
    remove_package_ids: tuple[str, ...]
    skipped: tuple[DuplicateDraftGroupSkip, ...]


@dataclass(frozen=True, slots=True)
class DuplicateDraftCleanupExecuteResult:
    """Execution summary for duplicate draft history cleanup."""

    removed_count: int
    removed_package_ids: tuple[str, ...]
    skipped_count: int
    skipped: tuple[DuplicateDraftGroupSkip, ...]


class IntakePackageStore(Protocol):
    def list(self) -> list[IntakePackage]: ...

    def delete(self, package_id: str) -> bool: ...


class IntakeAssetStore(Protocol):
    def list_by_package(self, package_id: str) -> list[IntakeAsset]: ...

    def delete_by_package(self, package_id: str) -> int: ...


class IntakeCaseStore(Protocol):
    def list_by_package(self, package_id: str) -> list[IntakeCase]: ...

    def delete_by_package(self, package_id: str) -> int: ...


class IntakeDraftStore(Protocol):
    def get_by_case(self, case_id: str): ...

    def delete_by_package(self, package_id: str) -> int: ...


class IntakeStoragePort(Protocol):
    def delete_package(self, package_id: str) -> bool: ...


class DuplicateDraftHistoryCleanupService:
    """Keep one latest active duplicate draft package per email identity."""

    def __init__(
        self,
        *,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
        storage: IntakeStoragePort,
    ) -> None:
        self._packages = package_store
        self._assets = asset_store
        self._cases = case_store
        self._drafts = draft_store
        self._storage = storage

    def dry_run(self) -> DuplicateDraftCleanupDryRun:
        """Return cleanup candidates without mutating storage."""
        candidates, skipped = self._collect_candidates()
        keep_ids, remove_ids = self._plan_keep_and_remove(candidates)
        return DuplicateDraftCleanupDryRun(
            generated_at=datetime.now(UTC).isoformat(),
            total_packages=len(self._packages.list()),
            candidate_count=len(candidates),
            duplicate_group_count=len(set(keep_ids)),
            keep_package_ids=keep_ids,
            remove_package_ids=remove_ids,
            skipped=tuple(skipped),
        )

    def execute(self) -> DuplicateDraftCleanupExecuteResult:
        """Delete redundant duplicate draft package graphs and folders."""
        report = self.dry_run()
        removed: list[str] = []
        skipped = list(report.skipped)
        for package_id in report.remove_package_ids:
            try:
                self._drafts.delete_by_package(package_id)
                self._cases.delete_by_package(package_id)
                self._assets.delete_by_package(package_id)
                self._packages.delete(package_id)
                self._storage.delete_package(package_id)
                removed.append(package_id)
            except Exception as exc:
                skipped.append(
                    DuplicateDraftGroupSkip(
                        package_id=package_id,
                        reason=f"cleanup_failed: {exc}",
                    )
                )
        return DuplicateDraftCleanupExecuteResult(
            removed_count=len(removed),
            removed_package_ids=tuple(removed),
            skipped_count=len(skipped),
            skipped=tuple(skipped),
        )

    def _collect_candidates(
        self,
    ) -> tuple[list[DuplicateDraftGroupCandidate], list[DuplicateDraftGroupSkip]]:
        candidates: list[DuplicateDraftGroupCandidate] = []
        skipped: list[DuplicateDraftGroupSkip] = []
        for package in self._packages.list():
            if package.source_type is not IntakePackageSourceType.OUTLOOK_MSG:
                continue
            email_source = self._email_source_asset(package.package_id)
            if email_source is None:
                skipped.append(
                    DuplicateDraftGroupSkip(
                        package_id=package.package_id,
                        reason="missing_email_source_asset",
                    )
                )
                continue
            cases = self._cases.list_by_package(package.package_id)
            if any(case.confirmed_project_id for case in cases):
                skipped.append(
                    DuplicateDraftGroupSkip(
                        package_id=package.package_id,
                        reason="has_confirmed_project_case",
                    )
                )
                continue
            reusable_case = next(
                (
                    case for case in cases
                    if case.status is not IntakeCaseStatus.CONFIRMED
                    and case.confirmed_project_id is None
                ),
                None,
            )
            if reusable_case is None:
                skipped.append(
                    DuplicateDraftGroupSkip(
                        package_id=package.package_id,
                        reason="no_reusable_case",
                    )
                )
                continue
            draft = self._drafts.get_by_case(reusable_case.case_id)
            if draft is None:
                skipped.append(
                    DuplicateDraftGroupSkip(
                        package_id=package.package_id,
                        reason="missing_draft_for_reusable_case",
                    )
                )
                continue
            candidates.append(
                DuplicateDraftGroupCandidate(
                    package_id=package.package_id,
                    case_id=reusable_case.case_id,
                    draft_exists=True,
                    source_original_name=email_source.original_name,
                    source_size_bytes=email_source.size_bytes,
                    source_sha256=email_source.sha256,
                    package_created_at=package.created_at,
                    package_updated_at=package.updated_at,
                )
            )
        return candidates, skipped

    def _plan_keep_and_remove(
        self,
        candidates: list[DuplicateDraftGroupCandidate],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        groups: dict[tuple[str, int, str], list[DuplicateDraftGroupCandidate]] = {}
        for item in candidates:
            identity = (
                item.source_sha256 or "",
                item.source_size_bytes,
                item.source_original_name if not item.source_sha256 else "",
            )
            groups.setdefault(identity, []).append(item)

        keep_ids: list[str] = []
        remove_ids: list[str] = []
        for group in groups.values():
            if len(group) < 2:
                continue
            ranked = sorted(
                group,
                key=lambda item: (
                    _sort_timestamp(item.package_updated_at),
                    _sort_timestamp(item.package_created_at),
                    item.package_id,
                ),
                reverse=True,
            )
            keep_ids.append(ranked[0].package_id)
            remove_ids.extend(item.package_id for item in ranked[1:])
        return tuple(keep_ids), tuple(remove_ids)

    def _email_source_asset(self, package_id: str) -> IntakeAsset | None:
        return next(
            (
                asset for asset in self._assets.list_by_package(package_id)
                if asset.asset_role is IntakeAssetRole.EMAIL_SOURCE
            ),
            None,
        )


def _sort_timestamp(raw: str | None) -> datetime:
    if not raw:
        return datetime.min.replace(tzinfo=UTC)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)
