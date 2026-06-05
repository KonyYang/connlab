from __future__ import annotations

import os
from pathlib import Path

import pytest

from backend.infrastructure.office.excel_com_smoke_harness import (
    ExcelComSmokeCommand,
    run_excel_com_smoke,
)


pytestmark = pytest.mark.skipif(
    os.environ.get("CONNLAB_RUN_EXCEL_COM_SMOKE") != "1",
    reason="Manual Windows host Excel COM smoke; skipped in normal CI/test runs.",
)


def test_excel_com_smoke_harness_manual_host(tmp_path: Path) -> None:
    result = run_excel_com_smoke(
        ExcelComSmokeCommand(
            template_path=Path(
                "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls"
            ),
            output_root=tmp_path / "task_290a_excel_com_smoke",
            timeout_seconds=90.0,
        )
    )

    assert result.timed_out is False
    assert result.status == "success"
    assert result.output_path is not None
    assert result.output_path.suffix.lower() == ".xls"
    assert result.output_size is not None
    assert result.output_size > 0
    assert [step["name"] for step in result.steps] == [
        "start",
        "open_template",
        "build_request",
        "export",
        "save_output",
        "close_excel",
        "verify_output",
    ]
