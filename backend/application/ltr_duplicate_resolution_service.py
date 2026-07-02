"""Local LTR duplicate ownership conflict and confirmation service."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol
from uuid import uuid4

from backend.domain import (
    LtrAssociationEvent,
    LtrDuplicateResolutionToken,
    LtrRecord,
    Project,
)


class LocalLtrDuplicateConflictError(ValueError):
    """Raised when a local LTR number is owned by another current project."""

    def __init__(self, detail: dict[str, object]) -> None:
        super().__init__(str(detail.get("message") or "Local LTR duplicate conflict."))
        self.detail = detail


class LocalLtrDuplicateTokenError(ValueError):
    """Raised when duplicate-resolution confirmation is stale or invalid."""


@dataclass(frozen=True, slots=True)
class DuplicateResolutionCommand:
    """Operator confirmation for local LTR duplicate ownership replacement."""

    action: str
    token: str
    acknowledged: bool
    reason: str | None = None


class LtrRecordStore(Protocol):
    """LTR record store behavior required by duplicate resolution."""

    def find_current_by_ltr_number(self, ltr_number: str) -> LtrRecord | None:
        """Return current registered owner for one LTR number."""

    def update(self, ltr: LtrRecord) -> LtrRecord:
        """Update one LTR record."""


class ProjectStore(Protocol):
    """Project lookup behavior required by duplicate resolution."""

    def get(self, project_id: str) -> Project | None:
        """Return a project by id."""


class TokenStore(Protocol):
    """Token store behavior required by duplicate resolution."""

    def create(self, token: LtrDuplicateResolutionToken) -> LtrDuplicateResolutionToken:
        """Create one token."""

    def get(self, token_id: str) -> LtrDuplicateResolutionToken | None:
        """Return one token."""

    def update(self, token: LtrDuplicateResolutionToken) -> LtrDuplicateResolutionToken:
        """Update one token."""


class EventStore(Protocol):
    """Audit store behavior required by duplicate resolution."""

    def create(self, event: LtrAssociationEvent) -> LtrAssociationEvent:
        """Create one audit event."""


class LocalLtrDuplicateResolutionService:
    """Build, validate, and apply local LTR duplicate owner confirmations."""

    def __init__(
        self,
        *,
        ltr_store: LtrRecordStore,
        project_store: ProjectStore,
        token_store: TokenStore,
        event_store: EventStore,
        token_ttl_minutes: int = 30,
    ) -> None:
        self._ltrs = ltr_store
        self._projects = project_store
        self._tokens = token_store
        self._events = event_store
        self._token_ttl_minutes = token_ttl_minutes

    def ensure_no_conflict_or_valid_confirmation(
        self,
        *,
        ltr_number: str,
        current_project: Project,
        current_case_id: str,
        resolution: DuplicateResolutionCommand | None,
    ) -> LtrRecord | None:
        """Return existing owner when confirmation is valid, or raise conflict."""
        existing = self._ltrs.find_current_by_ltr_number(ltr_number)
        if existing is None or existing.project_id == current_project.project_id:
            return None
        if resolution is None:
            raise LocalLtrDuplicateConflictError(
                self._conflict_detail(ltr_number, existing, current_project, current_case_id)
            )
        self._validate_resolution(
            ltr_number=ltr_number,
            existing=existing,
            current_project=current_project,
            current_case_id=current_case_id,
            resolution=resolution,
        )
        return existing

    def apply_confirmed_replacement(
        self,
        *,
        old_owner: LtrRecord | None,
        new_owner: LtrRecord,
        resolution: DuplicateResolutionCommand | None,
        operator: str | None,
    ) -> None:
        """Retire old local current owner and audit the new local owner."""
        if old_owner is None or resolution is None:
            return
        now = _now()
        reason = (resolution.reason or "").strip() or "Operator confirmed local LTR owner."
        token = self._tokens.get(resolution.token)
        if token is not None:
            self._tokens.update(_replace_token(token, used_at=now))
        self._events.create(
            LtrAssociationEvent(
                event_id=uuid4().hex,
                ltr_number=new_owner.ltr_number,
                event_type="local_ltr_duplicate_override",
                old_ltr_id=old_owner.ltr_id,
                old_project_id=old_owner.project_id,
                new_ltr_id=new_owner.ltr_id,
                new_project_id=new_owner.project_id,
                operator=operator,
                reason=reason,
                token_id=resolution.token,
                created_at=now,
                metadata_json=json.dumps(
                    {
                        "source": "new_project_apply_ltr",
                        "old_owner_version": old_owner.owner_version,
                        "new_owner_version": new_owner.owner_version,
                    },
                    ensure_ascii=True,
                    sort_keys=True,
                ),
            )
        )

    def retire_old_owner_before_replacement(
        self,
        *,
        old_owner: LtrRecord | None,
        new_ltr_id: str,
        resolution: DuplicateResolutionCommand | None,
    ) -> None:
        """Retire an old owner before inserting the replacement current owner."""
        if old_owner is None or resolution is None:
            return
        reason = (resolution.reason or "").strip() or "Operator confirmed local LTR owner."
        self._ltrs.update(
            _replace_ltr(
                old_owner,
                is_current_owner=False,
                superseded_at=_now(),
                superseded_by_ltr_id=new_ltr_id,
                superseded_reason=reason,
            )
        )

    def _conflict_detail(
        self,
        ltr_number: str,
        existing: LtrRecord,
        current_project: Project,
        current_case_id: str,
    ) -> dict[str, object]:
        existing_project = self._projects.get(existing.project_id)
        token = self._tokens.create(
            LtrDuplicateResolutionToken(
                token_id=uuid4().hex,
                ltr_number=ltr_number,
                existing_ltr_id=existing.ltr_id,
                existing_project_id=existing.project_id,
                current_case_id=current_case_id,
                current_project_id=current_project.project_id,
                conflict_fingerprint=_fingerprint(
                    ltr_number,
                    existing.ltr_id,
                    existing.project_id,
                    current_case_id,
                    current_project.project_id,
                ),
                expires_at=_future(self._token_ttl_minutes),
                created_at=_now(),
                created_by=current_project.requestor,
            )
        )
        return {
            "code": "LOCAL_LTR_DUPLICATE",
            "message": "This LTR number already has a local ConnLab owner.",
            "ltr_number": ltr_number,
            "existing": {
                "ltr_id": existing.ltr_id,
                "project_id": existing.project_id,
                "display_project_id": (
                    existing_project.project_no if existing_project else existing.ltr_number
                )
                or existing.ltr_number,
                "project_name": existing_project.product_name if existing_project else None,
                "product_name": existing_project.product_name if existing_project else None,
                "requester": existing_project.requestor if existing_project else None,
                "registered_on": (
                    existing.registered_on.isoformat() if existing.registered_on else None
                ),
                "project_status": existing_project.status.value if existing_project else None,
                "lifecycle_state": (
                    existing_project.lifecycle_state.value if existing_project else None
                ),
                "has_local_folder": False,
                "has_matrix": False,
                "has_outputs": False,
            },
            "current": {
                "case_id": current_case_id,
                "project_id": current_project.project_id,
                "project_name": current_project.product_name,
                "requester": current_project.requestor,
            },
            "resolution": {
                "token": token.token_id,
                "expires_at": token.expires_at,
                "allowed_actions": [
                    "open_existing",
                    "cancel",
                    "replace_local_association",
                ],
                "requires_second_confirmation": True,
            },
        }

    def _validate_resolution(
        self,
        *,
        ltr_number: str,
        existing: LtrRecord,
        current_project: Project,
        current_case_id: str,
        resolution: DuplicateResolutionCommand,
    ) -> None:
        if resolution.action != "replace_local_association":
            raise LocalLtrDuplicateTokenError("Unsupported local LTR duplicate action.")
        if not resolution.acknowledged:
            raise LocalLtrDuplicateTokenError("Local LTR duplicate confirmation is required.")
        if not (resolution.reason or "").strip():
            raise LocalLtrDuplicateTokenError("Local LTR duplicate confirmation note is required.")
        token = self._tokens.get(resolution.token)
        expected = _fingerprint(
            ltr_number,
            existing.ltr_id,
            existing.project_id,
            current_case_id,
            current_project.project_id,
        )
        if token is None or token.used_at:
            raise LocalLtrDuplicateTokenError("Local LTR duplicate confirmation has expired.")
        if token.conflict_fingerprint != expected:
            raise LocalLtrDuplicateTokenError("Local LTR duplicate confirmation is stale.")
        if token.expires_at < _now():
            raise LocalLtrDuplicateTokenError("Local LTR duplicate confirmation has expired.")


def _fingerprint(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _future(minutes: int) -> str:
    return (
        datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=minutes)
    ).isoformat()


def _replace_ltr(ltr: LtrRecord, **changes) -> LtrRecord:
    from dataclasses import replace

    return replace(ltr, **changes)


def _replace_token(
    token: LtrDuplicateResolutionToken,
    *,
    used_at: str,
) -> LtrDuplicateResolutionToken:
    from dataclasses import replace

    return replace(token, used_at=used_at)
