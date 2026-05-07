"""Service for frozen-field revision request recording."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import uuid4

from backend.application.intake_case_review_service import (
    IntakeCaseReviewNotFoundError,
    IntakeCaseReviewService,
)
from backend.domain import FrozenFieldRevisionRequest, FrozenFieldRevisionRequestStatus, LtrRecord, LtrStatus


class FrozenFieldRevisionRequestValidationError(ValueError):
    """Raised when a revision request payload fails validation."""


class FrozenFieldRevisionRequestNotFoundError(LookupError):
    """Raised when a revision request cannot be found."""


@dataclass(frozen=True)
class FrozenFieldRevisionChange:
    """One requested field change for a frozen base field."""

    field_key: str
    current_value: Any
    proposed_value: Any
    field_label: str | None = None


class FrozenFieldRevisionRequestStore(Protocol):
    """Persistence port for request records."""

    def create(self, request: FrozenFieldRevisionRequest) -> FrozenFieldRevisionRequest: ...

    def get(self, request_id: str) -> FrozenFieldRevisionRequest | None: ...

    def list_by_case(self, case_id: str) -> list[FrozenFieldRevisionRequest]: ...

    def list_by_project(self, project_id: str) -> list[FrozenFieldRevisionRequest]: ...


class LtrRecordStore(Protocol):
    """Read port for project LTR records."""

    def list_by_project(self, project_id: str) -> list[LtrRecord]: ...


class FrozenFieldRevisionRequestService:
    """Create and read frozen-field revision requests."""

    def __init__(
        self,
        request_store: FrozenFieldRevisionRequestStore,
        review_service: IntakeCaseReviewService,
        ltr_store: LtrRecordStore,
    ) -> None:
        self._requests = request_store
        self._review = review_service
        self._ltrs = ltr_store

    def create_request(
        self,
        case_id: str,
        *,
        reason: str,
        requested_by: str | None,
        changes: list[dict[str, Any]],
    ) -> FrozenFieldRevisionRequest:
        """Persist one frozen-field revision request after validation."""
        review_item = self._review.get_case_review_item(case_id)
        if not review_item.base_editing_frozen:
            raise FrozenFieldRevisionRequestValidationError(
                "Intake case is not frozen by registered LTR state."
            )
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise FrozenFieldRevisionRequestValidationError("Reason is required.")
        if not changes:
            raise FrozenFieldRevisionRequestValidationError("At least one field change is required.")
        allowed_keys = set(self._review.frozen_field_keys())
        normalized_changes: list[FrozenFieldRevisionChange] = []
        for index, change in enumerate(changes):
            if not isinstance(change, dict):
                raise FrozenFieldRevisionRequestValidationError(
                    f"Invalid change entry at index {index}."
                )
            field_key = str(change.get("field_key", "")).strip()
            if not field_key:
                raise FrozenFieldRevisionRequestValidationError(
                    f"Field key is required at index {index}."
                )
            if field_key not in allowed_keys:
                raise FrozenFieldRevisionRequestValidationError(
                    f"Field '{field_key}' is not an allowed frozen field."
                )
            normalized_changes.append(
                FrozenFieldRevisionChange(
                    field_key=field_key,
                    current_value=review_item.parsed_fields.get(field_key),
                    proposed_value=change.get("proposed_value"),
                    field_label=self._field_label_from_review(review_item, field_key),
                )
            )
        deduped_changes = self._dedupe_changes(normalized_changes)
        now = datetime.now(UTC).isoformat()
        ltr_record = self._registered_ltr_for_project(review_item.case.confirmed_project_id)
        request = FrozenFieldRevisionRequest(
            request_id=f"ffrr-{uuid4().hex}",
            intake_case_id=review_item.case.case_id,
            project_id=review_item.case.confirmed_project_id,
            ltr_record_id=ltr_record.ltr_id if ltr_record else None,
            ltr_number=ltr_record.ltr_number if ltr_record else None,
            status=FrozenFieldRevisionRequestStatus.REQUESTED,
            requested_by=self._normalized_text(requested_by),
            reason=normalized_reason,
            field_changes_json=json.dumps(
                [
                    {
                        "field_key": change.field_key,
                        "field_label": change.field_label,
                        "current_value": change.current_value,
                        "proposed_value": change.proposed_value,
                    }
                    for change in deduped_changes
                ],
                ensure_ascii=False,
                sort_keys=True,
            ),
            created_at=now,
            updated_at=now,
        )
        return self._requests.create(request)

    def list_by_case(self, case_id: str) -> list[FrozenFieldRevisionRequest]:
        """List requests for one intake case."""
        return self._requests.list_by_case(case_id)

    def list_by_project(self, project_id: str) -> list[FrozenFieldRevisionRequest]:
        """List requests for one confirmed project."""
        return self._requests.list_by_project(project_id)

    def get(self, request_id: str) -> FrozenFieldRevisionRequest:
        """Get one request by id."""
        item = self._requests.get(request_id)
        if item is None:
            raise FrozenFieldRevisionRequestNotFoundError(
                f"Frozen-field revision request not found: {request_id}"
            )
        return item

    def _field_label_from_review(self, review_item: Any, field_key: str) -> str | None:
        for field in getattr(review_item, "fields", []):
            if isinstance(field, dict) and field.get("key") == field_key:
                label = field.get("label")
                return str(label) if label else None
        return None

    def _registered_ltr_for_project(self, project_id: str | None) -> LtrRecord | None:
        if not project_id:
            return None
        records = self._ltrs.list_by_project(project_id)
        for record in records:
            if record.status is LtrStatus.REGISTERED:
                return record
        return records[0] if records else None

    def _normalized_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        text = value.strip()
        return text or None

    def _dedupe_changes(self, changes: list[FrozenFieldRevisionChange]) -> list[FrozenFieldRevisionChange]:
        seen: dict[str, FrozenFieldRevisionChange] = {}
        for change in changes:
            seen[change.field_key] = change
        return list(seen.values())
