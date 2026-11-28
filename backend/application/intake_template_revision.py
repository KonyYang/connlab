"""Compare the received request's revision with the approved Word form in Settings."""

from functools import lru_cache
import logging
from pathlib import Path
import re

from backend.modules.intake import ApplicationFormParser


logger = logging.getLogger(__name__)
_FORM_NUMBER = re.compile(r"(?<![a-z0-9])E-3718(?![a-z0-9])", re.IGNORECASE)


def request_revision_warning(
    folder: Path | None, received_number: str | None, received_revision: str | None,
) -> str | None:
    if folder is None:
        return "Cannot check the request revision. Set Template folder in Settings and place the approved E-3718 Word template there."
    try:
        candidates = sorted(
            (
                file for file in folder.iterdir()
                if file.suffix.lower() == ".docx" and not file.name.startswith("~$")
                and _FORM_NUMBER.search(file.stem) and file.is_file()
            ),
            key=lambda file: file.name.casefold(),
        )
    except OSError:
        return f"Cannot read Template folder {folder} to check the E-3718 revision. Check the folder path and access in Settings."
    if not candidates:
        return f"Cannot check the request revision. Place the approved E-3718 .docx directly in Template folder {folder}."
    if len(candidates) > 1:
        names = ", ".join(file.name for file in candidates)
        return f"Multiple E-3718 templates in {folder}: {names}. Keep the approved one in Template folder to check the revision."

    template = candidates[0]
    try:
        stamp = template.stat()
        form_no, expected = _template_identity(template, stamp.st_ino, stamp.st_mtime_ns, stamp.st_size)
    except Exception:
        # Invalid, locked or protected Word files must not stop an otherwise valid import.
        logger.warning("Cannot read intake template %s", template, exc_info=True)
        return f"Cannot read E-3718 template {template}. Check that the approved Word file opens, then retry the revision check."
    if (form_no or "").upper() != "E-3718" or not expected:
        return f"Cannot verify the revision in {template}. Check the form number (E-3718) and revision inside the approved Word template."
    if (received_number or "").strip().upper() != "E-3718":
        number = received_number or "not found"
        return f"Cannot compare request revisions. Form number in the request: {number}. The template {template.name} is E-3718 Rev {expected}."
    if not received_revision:
        return f"The request has no readable revision. Check its form number and revision against {template.name} (E-3718 Rev {expected})."
    if received_revision.strip().casefold() != expected.casefold():
        return f"Request is E-3718 Rev {received_revision}. The approved template {template.name} is Rev {expected}. Confirm the revision with the requester."
    return None


@lru_cache(maxsize=16)
def _template_identity(path: Path, file_id: int, modified_ns: int, size: int) -> tuple[str | None, str | None]:
    # Autosave re-reads the review. Reuse only metadata for this exact template version.
    return ApplicationFormParser().read_form_identity(path)
