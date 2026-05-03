from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import uuid4

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
from backend.infrastructure.files import IntakeStorage


class ManualIntakeError(ValueError):
    """Raised when manual intake data cannot be stored."""


class IntakePackageStore(Protocol):
    """Persistence port for manual intake packages."""

    def create(self, package: IntakePackage) -> IntakePackage: ...


class IntakeAssetStore(Protocol):
    """Persistence port for manual intake assets."""

    def create(self, asset: IntakeAsset) -> IntakeAsset: ...


class IntakeCaseStore(Protocol):
    """Persistence port for manual intake cases."""

    def create(self, case: IntakeCase) -> IntakeCase: ...


class IntakeDraftStore(Protocol):
    """Persistence port for manual intake drafts."""

    def create(self, draft: IntakeDraft) -> IntakeDraft: ...


@dataclass(frozen=True)
class ManualSampleInput:
    """Manual intake sample row."""

    product_name: str | None = None
    part_number: str | None = None
    revision: str | None = None
    lot_or_traceability: str | None = None
    material: str | None = None
    plating: str | None = None
    housing_material: str | None = None
    quantity: int | None = None


@dataclass(frozen=True)
class ManualIntakeInput:
    """Manual intake fields entered when no email package exists."""

    product_name: str | None = None
    requester: str | None = None
    email: str | None = None
    business_unit: str | None = None
    project_no: str | None = None
    form_no: str | None = None
    revision: str | None = None
    requested_testing: str | None = None
    sample: ManualSampleInput | None = None
    operator_notes: str | None = None


@dataclass(frozen=True)
class ManualIntakeResult:
    """Stored manual intake case and missing field state."""

    package: IntakePackage
    asset: IntakeAsset
    case: IntakeCase
    draft: IntakeDraft
    missing_required_fields: tuple[str, ...]


class ManualIntakeService:
    """Stores no-email manual intake data as a reviewable intake case."""

    _required_fields = ("product_name", "requester")

    def __init__(
        self,
        storage: IntakeStorage,
        package_store: IntakePackageStore,
        asset_store: IntakeAssetStore,
        case_store: IntakeCaseStore,
        draft_store: IntakeDraftStore,
    ) -> None:
        """Create the service from explicit storage and persistence ports."""
        self._storage = storage
        self._packages = package_store
        self._assets = asset_store
        self._cases = case_store
        self._drafts = draft_store

    def create_manual_case(self, data: ManualIntakeInput) -> ManualIntakeResult:
        """Persist manual intake draft data without creating a project."""
        package_id = f"pkg-{uuid4().hex}"
        case_id = f"case-{uuid4().hex}"
        asset_id = f"asset-{uuid4().hex}"
        draft_id = f"draft-{uuid4().hex}"
        draft_payload = self._draft_payload(data)
        missing = self._missing_required(draft_payload)
        snapshot_path = self._write_snapshot(package_id, draft_payload)

        package = self._packages.create(
            IntakePackage(
                package_id=package_id,
                source_type=IntakePackageSourceType.MANUAL,
                status=IntakePackageStatus.READY_FOR_REVIEW,
                source_original_name="manual_intake.json",
                source_stored_path=snapshot_path,
                subject=self._subject(draft_payload),
                sender_name=self._optional_text(draft_payload, "requester"),
                sender_email=self._optional_text(draft_payload, "email"),
                notes=self._optional_text(draft_payload, "operator_notes"),
            )
        )
        asset = self._assets.create(
            IntakeAsset(
                asset_id=asset_id,
                package_id=package.package_id,
                original_name="manual_intake.json",
                stored_path=snapshot_path,
                extension=".json",
                mime_type="application/json",
                size_bytes=snapshot_path.stat().st_size,
                sha256=self._storage.sha256(snapshot_path),
                asset_role=IntakeAssetRole.SELECTED_APPLICATION_FORM,
                candidate_score=100,
            )
        )
        case = self._cases.create(
            IntakeCase(
                case_id=case_id,
                package_id=package.package_id,
                selected_form_asset_id=asset.asset_id,
                status=IntakeCaseStatus.NEEDS_REVIEW,
                reviewer_notes=self._reviewer_notes(missing),
            )
        )
        draft = self._drafts.create(
            IntakeDraft(
                draft_id=draft_id,
                case_id=case.case_id,
                parsed_fields_json=json.dumps(draft_payload, ensure_ascii=False),
                parser_warnings_json=json.dumps(
                    ["Manual no-email intake requires human review before project creation."],
                    ensure_ascii=False,
                ),
            )
        )
        return ManualIntakeResult(
            package=package,
            asset=asset,
            case=case,
            draft=draft,
            missing_required_fields=tuple(missing),
        )

    def _write_snapshot(self, package_id: str, payload: dict[str, object]) -> Path:
        """Write the structured manual intake snapshot under controlled storage."""
        path = self._storage.snapshot_path(package_id, "manual_intake.json")
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def _draft_payload(self, data: ManualIntakeInput) -> dict[str, object]:
        """Convert manual input into draft fields used by confirmation."""
        sample = data.sample or ManualSampleInput()
        return {
            "project_no": self._clean(data.project_no),
            "product_name": self._clean(data.product_name),
            "requester": self._clean(data.requester),
            "email": self._clean(data.email),
            "business_unit": self._clean(data.business_unit),
            "form_no": self._clean(data.form_no),
            "revision": self._clean(data.revision),
            "requested_testing": self._clean(data.requested_testing),
            "operator_notes": self._clean(data.operator_notes),
            "samples": [
                {
                    "product_name": self._clean(sample.product_name) or self._clean(data.product_name),
                    "part_number": self._clean(sample.part_number),
                    "revision": self._clean(sample.revision),
                    "lot_or_traceability": self._clean(sample.lot_or_traceability),
                    "material": self._clean(sample.material),
                    "plating": self._clean(sample.plating),
                    "housing_material": self._clean(sample.housing_material),
                    "quantity": sample.quantity,
                }
            ],
        }

    def _missing_required(self, payload: dict[str, object]) -> list[str]:
        """Return required draft fields that are still blank."""
        return [
            field
            for field in self._required_fields
            if not self._optional_text(payload, field)
        ]

    def _subject(self, payload: dict[str, object]) -> str:
        """Return a readable manual intake subject."""
        product_name = self._optional_text(payload, "product_name")
        requester = self._optional_text(payload, "requester")
        if product_name and requester:
            return f"Manual intake: {product_name} / {requester}"
        return "Manual intake draft"

    def _reviewer_notes(self, missing: list[str]) -> str | None:
        """Return case notes for missing required fields."""
        if not missing:
            return None
        return "Missing required fields: " + ", ".join(missing)

    def _optional_text(self, payload: dict[str, object], key: str) -> str | None:
        """Return a stripped text value from a payload."""
        value = payload.get(key)
        if value in (None, ""):
            return None
        text = str(value).strip()
        return text or None

    def _clean(self, value: object | None) -> str | None:
        """Normalize empty manual input to None."""
        if value is None:
            return None
        text = str(value).strip()
        return text or None
