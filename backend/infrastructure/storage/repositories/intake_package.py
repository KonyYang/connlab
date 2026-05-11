"""Repositories for Phase 6 intake package persistence."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

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
from backend.infrastructure.storage.models import (
    IntakeAssetModel,
    IntakeCaseModel,
    IntakeDraftModel,
    IntakePackageModel,
)


class IntakePackageRepository:
    """Persist and load intake package records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, package: IntakePackage) -> IntakePackage:
        """Persist a new intake package."""
        self._session.add(_package_to_model(package))
        self._session.flush()
        return package

    def get(self, package_id: str) -> IntakePackage | None:
        """Return an intake package by ID."""
        row = self._session.get(IntakePackageModel, package_id)
        return _package_to_domain(row) if row else None

    def list(self) -> list[IntakePackage]:
        """Return all intake packages ordered by ID."""
        rows = self._session.scalars(
            select(IntakePackageModel).order_by(IntakePackageModel.package_id)
        ).all()
        return [_package_to_domain(row) for row in rows]

    def update(self, package: IntakePackage) -> IntakePackage:
        """Update an existing intake package."""
        row = self._session.get(IntakePackageModel, package.package_id)
        if row is None:
            raise ValueError(f"Intake package not found: {package.package_id}")
        _assign_package(row, package)
        self._session.flush()
        return package

    def delete(self, package_id: str) -> bool:
        """Delete one intake package row by ID."""
        row = self._session.get(IntakePackageModel, package_id)
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True


class IntakeAssetRepository:
    """Persist and load intake asset records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, asset: IntakeAsset) -> IntakeAsset:
        """Persist a new intake asset."""
        self._session.add(_asset_to_model(asset))
        self._session.flush()
        return asset

    def get(self, asset_id: str) -> IntakeAsset | None:
        """Return an intake asset by ID."""
        row = self._session.get(IntakeAssetModel, asset_id)
        return _asset_to_domain(row) if row else None

    def list_by_package(self, package_id: str) -> list[IntakeAsset]:
        """Return assets for one package."""
        rows = self._session.scalars(
            select(IntakeAssetModel)
            .where(IntakeAssetModel.package_id == package_id)
            .order_by(IntakeAssetModel.asset_id)
        ).all()
        return [_asset_to_domain(row) for row in rows]

    def update(self, asset: IntakeAsset) -> IntakeAsset:
        """Update an existing intake asset."""
        row = self._session.get(IntakeAssetModel, asset.asset_id)
        if row is None:
            raise ValueError(f"Intake asset not found: {asset.asset_id}")
        _assign_asset(row, asset)
        self._session.flush()
        return asset

    def delete_by_package(self, package_id: str) -> int:
        """Delete all intake assets for one package and return the row count."""
        rows = self._session.scalars(
            select(IntakeAssetModel).where(IntakeAssetModel.package_id == package_id)
        ).all()
        for row in rows:
            self._session.delete(row)
        self._session.flush()
        return len(rows)


class IntakeCaseRepository:
    """Persist and load intake case records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, case: IntakeCase) -> IntakeCase:
        """Persist a new intake case."""
        self._session.add(_case_to_model(case))
        self._session.flush()
        return case

    def get(self, case_id: str) -> IntakeCase | None:
        """Return an intake case by ID."""
        row = self._session.get(IntakeCaseModel, case_id)
        return _case_to_domain(row) if row else None

    def list_by_package(self, package_id: str) -> list[IntakeCase]:
        """Return cases for one package."""
        rows = self._session.scalars(
            select(IntakeCaseModel)
            .where(IntakeCaseModel.package_id == package_id)
            .order_by(IntakeCaseModel.case_id)
        ).all()
        return [_case_to_domain(row) for row in rows]

    def update(self, case: IntakeCase) -> IntakeCase:
        """Update an existing intake case."""
        row = self._session.get(IntakeCaseModel, case.case_id)
        if row is None:
            raise ValueError(f"Intake case not found: {case.case_id}")
        _assign_case(row, case)
        self._session.flush()
        return case

    def delete_by_package(self, package_id: str) -> int:
        """Delete all intake cases for one package and return the row count."""
        rows = self._session.scalars(
            select(IntakeCaseModel).where(IntakeCaseModel.package_id == package_id)
        ).all()
        for row in rows:
            self._session.delete(row)
        self._session.flush()
        return len(rows)


class IntakeDraftRepository:
    """Persist and load intake draft records."""

    def __init__(self, session: Session) -> None:
        """Create a repository bound to a SQLAlchemy session."""
        self._session = session

    def create(self, draft: IntakeDraft) -> IntakeDraft:
        """Persist a new intake draft."""
        self._session.add(_draft_to_model(draft))
        self._session.flush()
        return draft

    def get(self, draft_id: str) -> IntakeDraft | None:
        """Return an intake draft by ID."""
        row = self._session.get(IntakeDraftModel, draft_id)
        return _draft_to_domain(row) if row else None

    def get_by_case(self, case_id: str) -> IntakeDraft | None:
        """Return the draft for one intake case."""
        row = self._session.scalars(
            select(IntakeDraftModel).where(IntakeDraftModel.case_id == case_id)
        ).first()
        return _draft_to_domain(row) if row else None

    def update(self, draft: IntakeDraft) -> IntakeDraft:
        """Update an existing intake draft."""
        row = self._session.get(IntakeDraftModel, draft.draft_id)
        if row is None:
            raise ValueError(f"Intake draft not found: {draft.draft_id}")
        _assign_draft(row, draft)
        self._session.flush()
        return draft

    def delete_by_case(self, case_id: str) -> int:
        """Delete draft rows for one case and return row count."""
        rows = self._session.scalars(
            select(IntakeDraftModel).where(IntakeDraftModel.case_id == case_id)
        ).all()
        for row in rows:
            self._session.delete(row)
        self._session.flush()
        return len(rows)

    def delete_by_package(self, package_id: str) -> int:
        """Delete all drafts for cases in one package and return the row count."""
        case_ids = select(IntakeCaseModel.case_id).where(
            IntakeCaseModel.package_id == package_id
        )
        rows = self._session.scalars(
            select(IntakeDraftModel).where(IntakeDraftModel.case_id.in_(case_ids))
        ).all()
        for row in rows:
            self._session.delete(row)
        self._session.flush()
        return len(rows)


def _package_to_model(package: IntakePackage) -> IntakePackageModel:
    """Convert an intake package domain record to an ORM row."""
    row = IntakePackageModel(package_id=package.package_id)
    _assign_package(row, package)
    return row


def _assign_package(row: IntakePackageModel, package: IntakePackage) -> None:
    """Assign package domain fields onto an ORM row."""
    row.source_type = package.source_type.value
    row.status = package.status.value
    row.source_original_name = package.source_original_name
    row.source_stored_path = str(package.source_stored_path)
    row.subject = package.subject
    row.sender_name = package.sender_name
    row.sender_email = package.sender_email
    row.recipients_json = package.recipients_json
    row.cc_json = package.cc_json
    row.received_at = package.received_at
    row.body_text = package.body_text
    row.created_at = package.created_at
    row.updated_at = package.updated_at
    row.notes = package.notes


def _package_to_domain(row: IntakePackageModel) -> IntakePackage:
    """Convert an intake package ORM row to a domain record."""
    return IntakePackage(
        package_id=row.package_id,
        source_type=IntakePackageSourceType(row.source_type),
        status=IntakePackageStatus(row.status),
        source_original_name=row.source_original_name,
        source_stored_path=Path(row.source_stored_path),
        subject=row.subject,
        sender_name=row.sender_name,
        sender_email=row.sender_email,
        recipients_json=row.recipients_json,
        cc_json=row.cc_json,
        received_at=row.received_at,
        body_text=row.body_text,
        created_at=row.created_at,
        updated_at=row.updated_at,
        notes=row.notes,
    )


def _asset_to_model(asset: IntakeAsset) -> IntakeAssetModel:
    """Convert an intake asset domain record to an ORM row."""
    row = IntakeAssetModel(asset_id=asset.asset_id)
    _assign_asset(row, asset)
    return row


def _assign_asset(row: IntakeAssetModel, asset: IntakeAsset) -> None:
    """Assign asset domain fields onto an ORM row."""
    row.package_id = asset.package_id
    row.original_name = asset.original_name
    row.stored_path = str(asset.stored_path)
    row.extension = asset.extension
    row.mime_type = asset.mime_type
    row.size_bytes = asset.size_bytes
    row.sha256 = asset.sha256
    row.asset_role = asset.asset_role.value
    row.candidate_score = asset.candidate_score
    row.content_id = asset.content_id
    row.created_at = asset.created_at


def _asset_to_domain(row: IntakeAssetModel) -> IntakeAsset:
    """Convert an intake asset ORM row to a domain record."""
    return IntakeAsset(
        asset_id=row.asset_id,
        package_id=row.package_id,
        original_name=row.original_name,
        stored_path=Path(row.stored_path),
        extension=row.extension,
        mime_type=row.mime_type,
        size_bytes=row.size_bytes,
        sha256=row.sha256,
        asset_role=IntakeAssetRole(row.asset_role),
        candidate_score=row.candidate_score,
        content_id=row.content_id,
        created_at=row.created_at,
    )


def _case_to_model(case: IntakeCase) -> IntakeCaseModel:
    """Convert an intake case domain record to an ORM row."""
    row = IntakeCaseModel(case_id=case.case_id)
    _assign_case(row, case)
    return row


def _assign_case(row: IntakeCaseModel, case: IntakeCase) -> None:
    """Assign case domain fields onto an ORM row."""
    row.package_id = case.package_id
    row.selected_form_asset_id = case.selected_form_asset_id
    row.status = case.status.value
    row.confirmed_project_id = case.confirmed_project_id
    row.created_at = case.created_at
    row.updated_at = case.updated_at
    row.reviewer_notes = case.reviewer_notes


def _case_to_domain(row: IntakeCaseModel) -> IntakeCase:
    """Convert an intake case ORM row to a domain record."""
    return IntakeCase(
        case_id=row.case_id,
        package_id=row.package_id,
        selected_form_asset_id=row.selected_form_asset_id,
        status=IntakeCaseStatus(row.status),
        confirmed_project_id=row.confirmed_project_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        reviewer_notes=row.reviewer_notes,
    )


def _draft_to_model(draft: IntakeDraft) -> IntakeDraftModel:
    """Convert an intake draft domain record to an ORM row."""
    row = IntakeDraftModel(draft_id=draft.draft_id)
    _assign_draft(row, draft)
    return row


def _assign_draft(row: IntakeDraftModel, draft: IntakeDraft) -> None:
    """Assign draft domain fields onto an ORM row."""
    row.case_id = draft.case_id
    row.parsed_fields_json = draft.parsed_fields_json
    row.sample_rows_json = draft.sample_rows_json
    row.requested_testing_json = draft.requested_testing_json
    row.field_confidence_json = draft.field_confidence_json
    row.parser_warnings_json = draft.parser_warnings_json
    row.manual_overrides_json = draft.manual_overrides_json
    row.updated_at = draft.updated_at


def _draft_to_domain(row: IntakeDraftModel) -> IntakeDraft:
    """Convert an intake draft ORM row to a domain record."""
    return IntakeDraft(
        draft_id=row.draft_id,
        case_id=row.case_id,
        parsed_fields_json=row.parsed_fields_json,
        sample_rows_json=row.sample_rows_json,
        requested_testing_json=row.requested_testing_json,
        field_confidence_json=row.field_confidence_json,
        parser_warnings_json=row.parser_warnings_json,
        manual_overrides_json=row.manual_overrides_json,
        updated_at=row.updated_at,
    )
