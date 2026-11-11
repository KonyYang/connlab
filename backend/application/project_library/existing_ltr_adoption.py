"""Adopt an already-authoritative LTR without writing its workbook."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Protocol

from backend.domain.project_library import ProjectLibraryConflict
from backend.modules.ltr import LtrNumberKind, parse_ltr_number


@dataclass(frozen=True, slots=True)
class ExistingLtrAuthorityRow:
    ltr_number: str
    sheet_name: str
    row_number: int
    values: tuple[object, ...]


class ExistingLtrAuthority(Protocol):
    def find(self, ltr_number: str) -> ExistingLtrAuthorityRow | None: ...


class UnavailableExistingLtrAuthority:
    """Explicit production boundary when the configured workbook cannot be read."""

    def find(self, ltr_number: str) -> ExistingLtrAuthorityRow | None:
        raise ProjectLibraryConflict(
            "The configured LTR workbook is unavailable. Configure it before adding this numbered project."
        )


class ExistingLtrAdoptionService:
    """Review then atomically adopt a workbook-owned LTR in local storage."""

    def __init__(self, store, authority: ExistingLtrAuthority) -> None:
        self._store = store
        self._authority = authority

    def review(self, ltr_number: str) -> dict:
        parsed = parse_ltr_number(ltr_number)
        if parsed.kind is not LtrNumberKind.STANDARD_DL:
            raise ProjectLibraryConflict("Use a complete standard LTR number from the authority workbook.")
        normalized = parsed.normalized
        owner = self._store.current_ltr_owner(normalized)
        if owner is not None:
            raise ProjectLibraryConflict(
                f"{normalized} already belongs to another local project. Open that project instead of importing a duplicate."
            )
        row = self._authority.find(normalized)
        if row is None or row.ltr_number.upper() != normalized:
            raise ProjectLibraryConflict(f"{normalized} was not found in the configured LTR workbook.")
        return {
            "status": "found",
            "ltr_number": normalized,
            "sheet_name": row.sheet_name,
            "row_number": row.row_number,
            "row_fingerprint": _fingerprint(row),
        }

    def adopt(self, project_id: str, proof: dict) -> None:
        normalized = str(proof.get("ltr_number") or "").strip().upper()
        owner = self._store.current_ltr_owner(normalized)
        if owner is not None and owner["project_id"] != project_id:
            raise ProjectLibraryConflict(
                f"{normalized} already belongs to another local project. Nothing was imported."
            )
        if owner is not None:
            return
        self.verify(proof)
        self._store.adopt_existing_ltr(project_id, proof)

    def claim(self, project_id: str, title: str, proof: dict) -> None:
        """Claim local ownership before any project files are copied."""
        normalized = str(proof.get("ltr_number") or "").strip().upper()
        owner = self._store.current_ltr_owner(normalized)
        if owner is not None:
            if owner["project_id"] == project_id:
                return
            raise ProjectLibraryConflict(
                f"{normalized} already belongs to another local project. Nothing was imported."
            )
        self.verify(proof)
        self._store.claim_existing_ltr(project_id, title, proof)

    def verify(self, proof: dict) -> None:
        normalized = str(proof.get("ltr_number") or "").strip().upper()
        owner = self._store.current_ltr_owner(normalized)
        if owner is not None:
            raise ProjectLibraryConflict(
                f"{normalized} already belongs to another local project. Nothing was imported."
            )
        row = self._authority.find(normalized)
        if (
            row is None
            or row.sheet_name != proof.get("sheet_name")
            or row.row_number != proof.get("row_number")
            or _fingerprint(row) != proof.get("row_fingerprint")
        ):
            raise ProjectLibraryConflict("The authoritative LTR row changed after review. Check the project again.")


def _fingerprint(row: ExistingLtrAuthorityRow) -> str:
    payload = {
        "ltr_number": row.ltr_number,
        "sheet_name": row.sheet_name,
        "row_number": row.row_number,
        "values": [_json_value(value) for value in row.values],
    }
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


def _json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)
