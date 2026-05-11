from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from backend.application.duplicate_draft_history_cleanup_service import (
    DuplicateDraftHistoryCleanupService,
)
from backend.domain import (
    IntakeAsset,
    IntakeAssetRole,
    IntakeCase,
    IntakeCaseStatus,
    IntakeDraft,
    IntakePackage,
    IntakePackageSourceType,
    IntakePackageStatus,
)


def test_cleanup_keeps_latest_duplicate_and_removes_older() -> None:
    packages = PackageStore(
        [
            _package("pkg-old", created_at="2026-05-10T08:00:00+00:00", updated_at="2026-05-10T08:00:00+00:00"),
            _package("pkg-new", created_at="2026-05-11T08:00:00+00:00", updated_at="2026-05-11T08:00:00+00:00"),
        ]
    )
    assets = AssetStore(
        [
            _email_asset("asset-old", "pkg-old", sha256="a" * 64),
            _email_asset("asset-new", "pkg-new", sha256="a" * 64),
        ]
    )
    cases = CaseStore(
        [
            _case("case-old", "pkg-old"),
            _case("case-new", "pkg-new"),
        ]
    )
    drafts = DraftStore(
        [
            _draft("draft-old", "case-old"),
            _draft("draft-new", "case-new"),
        ]
    )
    storage = FakeStorage()
    service = DuplicateDraftHistoryCleanupService(
        package_store=packages,
        asset_store=assets,
        case_store=cases,
        draft_store=drafts,
        storage=storage,
    )

    report = service.dry_run()
    assert report.keep_package_ids == ("pkg-new",)
    assert report.remove_package_ids == ("pkg-old",)

    result = service.execute()
    assert result.removed_package_ids == ("pkg-old",)
    assert "pkg-old" in storage.deleted
    assert packages.get("pkg-old") is None
    assert drafts.get_by_case("case-old") is None


def test_cleanup_skips_packages_with_confirmed_case() -> None:
    packages = PackageStore([_package("pkg-1")])
    assets = AssetStore([_email_asset("asset-1", "pkg-1", sha256="a" * 64)])
    cases = CaseStore(
        [
            replace(
                _case("case-1", "pkg-1"),
                confirmed_project_id="project-1",
                status=IntakeCaseStatus.CONFIRMED,
            )
        ]
    )
    drafts = DraftStore([_draft("draft-1", "case-1")])
    service = DuplicateDraftHistoryCleanupService(
        package_store=packages,
        asset_store=assets,
        case_store=cases,
        draft_store=drafts,
        storage=FakeStorage(),
    )

    report = service.dry_run()
    assert report.remove_package_ids == ()
    assert report.skipped[0].package_id == "pkg-1"
    assert report.skipped[0].reason == "has_confirmed_project_case"


class PackageStore:
    def __init__(self, items: list[IntakePackage]) -> None:
        self.items = {item.package_id: item for item in items}

    def list(self) -> list[IntakePackage]:
        return list(self.items.values())

    def get(self, package_id: str) -> IntakePackage | None:
        return self.items.get(package_id)

    def delete(self, package_id: str) -> bool:
        return self.items.pop(package_id, None) is not None


class AssetStore:
    def __init__(self, items: list[IntakeAsset]) -> None:
        self.items = {item.asset_id: item for item in items}

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        return [item for item in self.items.values() if item.package_id == package_id]

    def delete_by_package(self, package_id: str) -> int:
        keys = [key for key, item in self.items.items() if item.package_id == package_id]
        for key in keys:
            del self.items[key]
        return len(keys)


class CaseStore:
    def __init__(self, items: list[IntakeCase]) -> None:
        self.items = {item.case_id: item for item in items}

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        return [item for item in self.items.values() if item.package_id == package_id]

    def delete_by_package(self, package_id: str) -> int:
        keys = [key for key, item in self.items.items() if item.package_id == package_id]
        for key in keys:
            del self.items[key]
        return len(keys)


class DraftStore:
    def __init__(self, items: list[IntakeDraft]) -> None:
        self.items = {item.draft_id: item for item in items}

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        return next((item for item in self.items.values() if item.case_id == case_id), None)

    def delete_by_package(self, package_id: str) -> int:
        case_prefix = f"case-{package_id.split('-', 1)[-1]}"
        keys = [key for key, item in self.items.items() if item.case_id.startswith(case_prefix)]
        for key in keys:
            del self.items[key]
        return len(keys)


class FakeStorage:
    def __init__(self) -> None:
        self.deleted: list[str] = []

    def delete_package(self, package_id: str) -> bool:
        self.deleted.append(package_id)
        return True


def _package(
    package_id: str,
    *,
    created_at: str | None = None,
    updated_at: str | None = None,
) -> IntakePackage:
    return IntakePackage(
        package_id=package_id,
        source_type=IntakePackageSourceType.OUTLOOK_MSG,
        status=IntakePackageStatus.READY_FOR_REVIEW,
        source_original_name="request.msg",
        source_stored_path=Path(f"data/intake/{package_id}/source/request.msg"),
        created_at=created_at,
        updated_at=updated_at,
    )


def _email_asset(asset_id: str, package_id: str, *, sha256: str) -> IntakeAsset:
    return IntakeAsset(
        asset_id=asset_id,
        package_id=package_id,
        original_name="request.msg",
        stored_path=Path(f"data/intake/{package_id}/source/request.msg"),
        extension=".msg",
        mime_type="application/vnd.ms-outlook",
        size_bytes=2048,
        sha256=sha256,
        asset_role=IntakeAssetRole.EMAIL_SOURCE,
    )


def _case(case_id: str, package_id: str) -> IntakeCase:
    return IntakeCase(
        case_id=case_id,
        package_id=package_id,
        selected_form_asset_id=None,
        status=IntakeCaseStatus.NEEDS_REVIEW,
    )


def _draft(draft_id: str, case_id: str) -> IntakeDraft:
    return IntakeDraft(
        draft_id=draft_id,
        case_id=case_id,
        parsed_fields_json="{}",
        parser_warnings_json="[]",
        updated_at="2026-05-11T08:00:00+00:00",
    )
