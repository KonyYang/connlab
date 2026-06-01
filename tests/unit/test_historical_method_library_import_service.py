from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from backend.application.historical_method_library_import_service import (
    HistoricalMethodLibraryImportService,
)
from backend.infrastructure.office.historical_test_report_method_extractor import (
    HistoricalMethodExtractResult,
    HistoricalMethodRow,
)
from backend.infrastructure.storage.repositories.historical_method_library_index import (
    HistoricalMethodLibraryIndexRepository,
)


def test_import_service_writes_index_records(tmp_path: Path) -> None:
    source = tmp_path / "report.docx"
    source.write_bytes(b"docx-bytes")
    repository = HistoricalMethodLibraryIndexRepository(index_path=tmp_path / "index.json")
    service = HistoricalMethodLibraryImportService(
        extractor=_FakeExtractor(
            HistoricalMethodExtractResult(
                source_path=source,
                source_table_index=2,
                rows=(
                    HistoricalMethodRow(
                        table_index=2,
                        row_index=5,
                        test_item="LLCR",
                        method="EIA-364-23D",
                        condition="20mV max, 100mA max",
                        requirement="Initial <= 0.25 mΩ; ΔR <= 0.17 mΩ",
                    ),
                ),
            )
        ),
        repository=repository,
    )

    result = service.import_files((source,))
    saved = repository.list_all()

    assert result.imported_files == 1
    assert result.imported_rows == 1
    assert result.file_summaries[0].extracted_row_count == 1
    assert len(saved) == 1
    assert saved[0].test_item == "LLCR"


def test_import_service_reports_skipped_when_no_rows(tmp_path: Path) -> None:
    source = tmp_path / "report.docx"
    source.write_bytes(b"docx-bytes")
    repository = HistoricalMethodLibraryIndexRepository(index_path=tmp_path / "index.json")
    service = HistoricalMethodLibraryImportService(
        extractor=_FakeExtractor(
            HistoricalMethodExtractResult(
                source_path=source,
                source_table_index=None,
                rows=(),
                warnings=("No methods/requirements table detected.",),
            )
        ),
        repository=repository,
    )

    result = service.import_files((source,))

    assert result.imported_files == 0
    assert result.imported_rows == 0
    assert result.file_summaries[0].skipped_reason == "No extractable methods table rows."


@dataclass
class _FakeExtractor:
    result: HistoricalMethodExtractResult

    def extract(self, source_path: Path) -> HistoricalMethodExtractResult:
        return self.result

