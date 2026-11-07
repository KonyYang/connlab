"""Per-output failures that leave the approved publication boundary untouched."""

from backend.shared.operation_diagnostics import safe_text


class ProjectFolderOutputUnavailable(Exception):
    """A source artifact could not be prepared; no final-file publish was attempted."""

    def __init__(self, key: str, label: str, reason: str):
        self.key, self.label, self.reason = key, label, safe_text(reason)
        super().__init__(self.reason)


def record_output_issue(state: dict, key: str, label: str, reason: str) -> None:
    issue = {"key": key, "label": label, "message": safe_text(reason)}
    issues = state.setdefault("issues", [])
    if issue not in issues:
        issues.append(issue)
