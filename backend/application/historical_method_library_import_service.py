"""Import historical Test Report method rows into workspace-local candidate index."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from backend.infrastructure.office.historical_test_report_method_extractor import (
    HistoricalTestReportMethodExtractor,
)
from backend.infrastructure.storage.repositories.historical_method_library_index import (
    HistoricalMethodCandidateRecord,
    HistoricalMethodLibraryIndexRepository,
)


@dataclass(frozen=True, slots=True)
class HistoricalMethodFileImportSummary:
    source_path: str
    source_sha256: str
    extracted_row_count: int
    skipped_reason: str | None = None
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HistoricalMethodImportResult:
    imported_files: int
    imported_rows: int
    file_summaries: tuple[HistoricalMethodFileImportSummary, ...]


class HistoricalMethodLibraryImportService:
    """Orchestrate deterministic extraction and index writes for report files."""

    def __init__(
        self,
        *,
        extractor: HistoricalTestReportMethodExtractor,
        repository: HistoricalMethodLibraryIndexRepository,
    ) -> None:
        self._extractor = extractor
        self._repository = repository

    def import_files(self, source_paths: tuple[Path, ...]) -> HistoricalMethodImportResult:
        summaries: list[HistoricalMethodFileImportSummary] = []
        imported_files = 0
        imported_rows = 0
        for source_path in source_paths:
            if source_path.name.startswith("~$"):
                continue
            if source_path.suffix.lower() != ".docx":
                summaries.append(
                    HistoricalMethodFileImportSummary(
                        source_path=str(source_path),
                        source_sha256="",
                        extracted_row_count=0,
                        skipped_reason="Unsupported file extension.",
                    )
                )
                continue
            if not source_path.is_file():
                summaries.append(
                    HistoricalMethodFileImportSummary(
                        source_path=str(source_path),
                        source_sha256="",
                        extracted_row_count=0,
                        skipped_reason="File does not exist.",
                    )
                )
                continue
            source_sha256 = _sha256_file(source_path)
            extract = self._extractor.extract(source_path)
            if extract.source_table_index is None or not extract.rows:
                summaries.append(
                    HistoricalMethodFileImportSummary(
                        source_path=str(source_path),
                        source_sha256=source_sha256,
                        extracted_row_count=0,
                        skipped_reason="No extractable methods table rows.",
                        warnings=extract.warnings,
                    )
                )
                continue
            now = datetime.now(UTC).isoformat()
            stat = source_path.stat()
            records = tuple(
                HistoricalMethodCandidateRecord(
                    source_file_name=source_path.name,
                    source_path=str(source_path),
                    source_sha256=source_sha256,
                    source_size_bytes=stat.st_size,
                    source_modified_at=datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                    source_table_index=row.table_index,
                    source_row_index=row.row_index,
                    test_item=row.test_item,
                    method=row.method,
                    condition=row.condition,
                    requirement=row.requirement,
                    imported_at=now,
                )
                for row in extract.rows
            )
            written = self._repository.upsert_for_source(
                source_sha256=source_sha256,
                records=records,
            )
            imported_files += 1
            imported_rows += written
            summaries.append(
                HistoricalMethodFileImportSummary(
                    source_path=str(source_path),
                    source_sha256=source_sha256,
                    extracted_row_count=written,
                    warnings=extract.warnings,
                )
            )
        return HistoricalMethodImportResult(
            imported_files=imported_files,
            imported_rows=imported_rows,
            file_summaries=tuple(summaries),
        )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

