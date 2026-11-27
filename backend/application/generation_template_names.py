"""Shared filename rules for generation and non-overwriting template setup."""
from pathlib import Path

from backend.application.ir_dwv_template_discovery import is_ir_dwv_template_name


def matches_generation_template(path: Path, purpose: str) -> bool:
    name = path.name.upper()
    suffix = path.suffix.lower()
    if purpose == "test_record":
        return suffix == ".docx" and "FDQF-E-036" in name and "TEST RECORD" in name
    if purpose == "customer_feedback":
        return suffix == ".xlsx" and "E-4243" in name
    if purpose == "ir_dwv":
        return is_ir_dwv_template_name(path)
    suffix_expected, token = {
        "internal_report": (".docx", "E-3707_H"),
        "customer_report": (".docx", "E-4515"),
        "fee_evaluation": (".xlsx", "FDQF-E-176"),
    }[purpose]
    return suffix == suffix_expected and token in name and not name.startswith("~$")


def matching_generation_templates(folder: Path, purpose: str) -> list[Path]:
    return sorted(path for path in folder.iterdir() if matches_generation_template(path, purpose) and path.is_file())
