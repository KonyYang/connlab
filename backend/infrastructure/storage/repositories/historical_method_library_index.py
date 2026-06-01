"""Workspace-local JSON index for historical method library candidates."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class HistoricalMethodCandidateRecord:
    source_file_name: str
    source_path: str
    source_sha256: str
    source_size_bytes: int
    source_modified_at: str
    source_table_index: int
    source_row_index: int
    test_item: str
    method: str
    condition: str
    requirement: str
    imported_at: str


class HistoricalMethodLibraryIndexRepository:
    """Read/write a deterministic JSON candidate index."""

    def __init__(self, *, index_path: Path) -> None:
        self._index_path = index_path

    def upsert_for_source(
        self,
        *,
        source_sha256: str,
        records: tuple[HistoricalMethodCandidateRecord, ...],
    ) -> int:
        payload = self._load()
        current = payload.get("candidates", [])
        filtered = [item for item in current if item.get("source_sha256") != source_sha256]
        filtered.extend(_record_to_dict(record) for record in records)
        payload["candidates"] = filtered
        payload["updated_at"] = datetime.now(UTC).isoformat()
        self._save(payload)
        return len(records)

    def list_all(self) -> tuple[HistoricalMethodCandidateRecord, ...]:
        payload = self._load()
        return tuple(_dict_to_record(item) for item in payload.get("candidates", []))

    def _load(self) -> dict:
        if not self._index_path.is_file():
            return {"schema_version": "1", "updated_at": None, "candidates": []}
        with self._index_path.open("r", encoding="utf-8") as handle:
            parsed = json.load(handle)
        if not isinstance(parsed, dict):
            raise ValueError("Historical method index must be a JSON object.")
        if "candidates" not in parsed or not isinstance(parsed["candidates"], list):
            raise ValueError("Historical method index must contain a candidates array.")
        return parsed

    def _save(self, payload: dict) -> None:
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        with self._index_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")


def _record_to_dict(record: HistoricalMethodCandidateRecord) -> dict:
    return {
        "source_file_name": record.source_file_name,
        "source_path": record.source_path,
        "source_sha256": record.source_sha256,
        "source_size_bytes": record.source_size_bytes,
        "source_modified_at": record.source_modified_at,
        "source_table_index": record.source_table_index,
        "source_row_index": record.source_row_index,
        "test_item": record.test_item,
        "method": record.method,
        "condition": record.condition,
        "requirement": record.requirement,
        "imported_at": record.imported_at,
    }


def _dict_to_record(item: dict) -> HistoricalMethodCandidateRecord:
    return HistoricalMethodCandidateRecord(
        source_file_name=str(item.get("source_file_name", "")),
        source_path=str(item.get("source_path", "")),
        source_sha256=str(item.get("source_sha256", "")),
        source_size_bytes=int(item.get("source_size_bytes", 0)),
        source_modified_at=str(item.get("source_modified_at", "")),
        source_table_index=int(item.get("source_table_index", 0)),
        source_row_index=int(item.get("source_row_index", 0)),
        test_item=str(item.get("test_item", "")),
        method=str(item.get("method", "")),
        condition=str(item.get("condition", "")),
        requirement=str(item.get("requirement", "")),
        imported_at=str(item.get("imported_at", "")),
    )

