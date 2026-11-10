"""Per-file source facts for the existing-workspace generation boundary."""

from dataclasses import dataclass
from pathlib import Path


class ProjectFileTargetLockedError(PermissionError):
    """A specific file operation is locked; its frozen effect remains recoverable."""


FILE_DEFINITIONS = (
    ("customer_feedback_form", "Customer Feedback Form", "customer_feedback_form"),
    ("fee_form", "Fee Form", "fee_evaluation"),
    ("test_record", "Test Record", "test_record_form"),
    ("test_status", "Test Status", "test_status"),
    ("application_form", "Application Form", "section2_write_back"),
    ("llcr_record", "LLCR Record", "llcr_record_form"),
    ("cr_record", "CR Record", "cr_record_form"),
    ("ir_dwv_record", "IR/DWV Record", "ir_dwv_record_form"),
)


@dataclass(frozen=True)
class ProjectFileSource:
    key: str
    label: str
    target: Path | None
    source_token: str | None
    output_kind: str
    status: str
    message: str
    warnings: tuple[str, ...] = ()
