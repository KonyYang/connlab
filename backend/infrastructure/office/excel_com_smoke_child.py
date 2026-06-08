"""Child entry point for manual Excel COM Matrix basic-fill smoke runs."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

from backend.application.confirmed_matrix_fee_template_basic_fill_service import (
    MatrixBasicFillGroup,
    MatrixBasicFillHeader,
    MatrixBasicFillLine,
    MatrixBasicFillWorkbook,
)
from backend.infrastructure.office.fee_evaluation_workbook_gateway import (
    FeeEvaluationWorkbookGateway,
)
from backend.infrastructure.office.office_lifecycle import OfficeAutomationUnavailable


@dataclass(frozen=True, slots=True)
class SmokeStep:
    """One child smoke execution step."""

    name: str
    timestamp: str
    message: str


def main(argv: list[str] | None = None) -> int:
    """Run one Excel COM smoke export and emit exactly one JSON result."""
    args = _parse_args(argv)
    steps: list[SmokeStep] = []
    warnings: list[str] = []
    try:
        _step(steps, "start", "Starting Excel COM Matrix basic-fill smoke.")
        template_path = args.template_path.resolve()
        output_dir = args.output_dir.resolve()
        output_path = output_dir / args.output_name
        _step(steps, "open_template", f"Template path: {template_path}")
        if not template_path.is_file():
            raise FileNotFoundError(f"Template does not exist: {template_path}")
        output_dir.mkdir(parents=True, exist_ok=True)
        _step(steps, "build_request", "Building minimal Matrix basic-fill workbook.")
        basic_fill = _basic_fill_workbook()
        _step(steps, "export", "Calling FeeEvaluationWorkbookGateway.")
        result = FeeEvaluationWorkbookGateway().generate_matrix_basic_fill(
            template_path=template_path,
            output_path=output_path,
            basic_fill=basic_fill,
            review_required=True,
            prepared_by="TASK_290A smoke",
            approved_by=None,
        )
        warnings.extend(result.warnings)
        _step(steps, "save_output", f"Output path: {result.output_path}")
        _step(steps, "close_excel", "Gateway returned after workbook close/quit.")
        output_size = _verify_output(result.output_path)
        _step(steps, "verify_output", f"Output size: {output_size}")
        _emit(
            {
                "status": "success",
                "output_path": str(result.output_path),
                "output_size": output_size,
                "steps": [asdict(step) for step in steps],
                "warnings": warnings,
                "manual_cleanup_warning": None,
            }
        )
        return 0
    except OfficeAutomationUnavailable as exc:
        _emit(
            {
                "status": "unavailable",
                "output_path": None,
                "output_size": None,
                "steps": [asdict(step) for step in steps],
                "warnings": warnings,
                "error_message": str(exc),
                "manual_cleanup_warning": None,
            }
        )
        return 2
    except Exception as exc:
        _emit(
            {
                "status": "execution_failure",
                "output_path": None,
                "output_size": None,
                "steps": [asdict(step) for step in steps],
                "warnings": warnings,
                "error_message": f"{type(exc).__name__}: {exc}",
                "manual_cleanup_warning": None,
            }
        )
        return 1


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a manual Excel COM Matrix basic-fill smoke export."
    )
    parser.add_argument("--template-path", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--output-name", required=True)
    return parser.parse_args(argv)


def _step(steps: list[SmokeStep], name: str, message: str) -> None:
    steps.append(
        SmokeStep(
            name=name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            message=message,
        )
    )


def _basic_fill_workbook() -> MatrixBasicFillWorkbook:
    return MatrixBasicFillWorkbook(
        header=MatrixBasicFillHeader(
            project_id="TASK_290A_SMOKE",
            confirmed_matrix_id="cmv-task290a-smoke",
            confirmed_revision=1,
            generated_at=datetime.now(timezone.utc).isoformat(),
        ),
        status="ready",
        groups=(
            MatrixBasicFillGroup(
                group_key="g1",
                group_label="Group 1",
                confirmed_group_id="cmg-task290a-1",
                sample_quantity_expression="5",
                lines=(
                    MatrixBasicFillLine(
                        line_id="cmv-task290a-smoke:g1:cmr-visual",
                        group_key="g1",
                        group_label="Group 1",
                        confirmed_group_id="cmg-task290a-1",
                        confirmed_row_id="cmr-visual",
                        source_row_id="smr-visual",
                        row_order=1,
                        step_index=0,
                        test_item="Visual Examination",
                        cell_value="1 X",
                        step_tokens=(),
                    ),
                ),
            ),
            MatrixBasicFillGroup(
                group_key="g2",
                group_label="Group 2",
                confirmed_group_id="cmg-task290a-2",
                sample_quantity_expression="3",
                lines=(
                    MatrixBasicFillLine(
                        line_id="cmv-task290a-smoke:g2:cmr-llcr",
                        group_key="g2",
                        group_label="Group 2",
                        confirmed_group_id="cmg-task290a-2",
                        confirmed_row_id="cmr-llcr",
                        source_row_id="smr-llcr",
                        row_order=2,
                        step_index=0,
                        test_item="LLCR",
                        cell_value="abc",
                        step_tokens=(),
                    ),
                ),
            ),
        ),
    )


def _verify_output(output_path: Path) -> int:
    if output_path.suffix.lower() != ".xls":
        raise ValueError(f"Smoke output must be .xls: {output_path}")
    if not output_path.is_file():
        raise FileNotFoundError(f"Smoke output was not created: {output_path}")
    output_size = output_path.stat().st_size
    if output_size <= 0:
        raise ValueError(f"Smoke output is empty: {output_path}")
    return output_size


def _emit(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    raise SystemExit(main())
