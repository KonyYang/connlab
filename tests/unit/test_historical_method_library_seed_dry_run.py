from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from backend.application.historical_method_library_import_service import (
    HistoricalMethodLibraryImportService,
)
from backend.infrastructure.office.historical_test_report_method_extractor import (
    HistoricalTestReportMethodExtractor,
)
from backend.infrastructure.storage.repositories.historical_method_library_index import (
    HistoricalMethodLibraryIndexRepository,
)


def test_matrix_fill_seed_folder_dry_run_inventory_driven(tmp_path: Path) -> None:
    inventory_path = Path("docs/task_283c_matrix_fill_seed_inventory.md")
    if not inventory_path.is_file():
        pytest.skip("Seed inventory markdown is not available.")
    entries = _load_inventory(inventory_path)
    if len(entries) != 8:
        pytest.skip("Expected 8 seed inventory entries.")
    for path, expected_hash in entries:
        if not path.is_file():
            pytest.skip(f"Inventory file missing in environment: {path}")
        if _sha256(path) != expected_hash:
            pytest.skip(f"Inventory hash mismatch in environment: {path.name}")

    service = HistoricalMethodLibraryImportService(
        extractor=HistoricalTestReportMethodExtractor(),
        repository=HistoricalMethodLibraryIndexRepository(index_path=tmp_path / "seed_index.json"),
    )
    result = service.import_files(tuple(path for path, _ in entries))

    summaries = {Path(summary.source_path): summary for summary in result.file_summaries}
    assert set(summaries) == {path for path, _ in entries}
    for path, expected_hash in entries:
        summary = summaries[path]
        assert summary.source_sha256 == expected_hash
        assert summary.extracted_row_count >= 0
        if summary.extracted_row_count == 0:
            assert summary.skipped_reason is not None

    artifact = tmp_path / "seed_dry_run_result.json"
    artifact.write_text(
        json.dumps(
            {
                "imported_files": result.imported_files,
                "imported_rows": result.imported_rows,
                "summaries": [
                    {
                        "file": Path(summary.source_path).name,
                        "sha256": summary.source_sha256,
                        "extracted_row_count": summary.extracted_row_count,
                        "skipped_reason": summary.skipped_reason,
                    }
                    for summary in result.file_summaries
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    assert artifact.is_file()


def _load_inventory(path: Path) -> list[tuple[Path, str]]:
    entries: list[tuple[Path, str]] = []
    pattern = re.compile(r"\| \d+ \| .* \| `([^`]+)` \| .* \| `([0-9a-f]{64})` \|")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.search(line)
        if not match:
            continue
        file_path = Path(match.group(1))
        if file_path.name.startswith("~$"):
            continue
        entries.append((file_path, match.group(2)))
    return entries


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

