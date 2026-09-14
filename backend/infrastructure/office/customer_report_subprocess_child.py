"""Child entry point for isolated standalone customer-report generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from backend.infrastructure.office.customer_report_document_gateway import (
    CustomerReportDocumentGateway,
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = _parse_args(argv)
    result = _execute(args.command_json)
    print(json.dumps(result, ensure_ascii=False), end="")
    return 0 if result.get("status") == "success" else 1


def _execute(command_json: Path) -> dict[str, Any]:
    try:
        payload = json.loads(command_json.read_text(encoding="utf-8"))
        source = Path(payload["source_path"])
        template = Path(payload["template_path"])
        output = Path(payload["output_path"])
        CustomerReportDocumentGateway().generate_customer_report(
            source_path=source,
            template_path=template,
            output_path=output,
        )
        return {"status": "success"}
    except Exception as exc:
        return {
            "status": "failure",
            "error_type": type(exc).__name__,
            "error_message": " ".join(str(exc).split()) or type(exc).__name__,
        }


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one customer report in an isolated Word process."
    )
    parser.add_argument("--command-json", required=True, type=Path)
    return parser.parse_args(argv)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

