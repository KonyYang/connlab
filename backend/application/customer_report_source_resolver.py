"""Select a customer-report source without changing current-report authority."""
from typing import Protocol

from backend.application.current_report_update_service import CurrentReportArtifact


class DownloadedInternalReportUnavailable(ValueError):
    """Downloaded candidates cannot safely identify one current-project draft."""


class DownloadedInternalReportReader(Protocol):
    def latest(self, dl_number: str) -> CurrentReportArtifact | None: ...


class CustomerReportSourceResolver:
    def __init__(self, *, current_reports, basic_information, workspaces,
                 downloaded_drafts: DownloadedInternalReportReader):
        self._current = current_reports
        self._basic = basic_information
        self._workspaces = workspaces
        self._downloads = downloaded_drafts

    def get_current_report(self, project_id: str) -> CurrentReportArtifact:
        current = self._current.get_current_report(project_id)
        if current.status == "ambiguous" or (current.status == "ready" and current.mode == "official"):
            return current
        workspace = self._workspaces.get_by_project(project_id)
        basic = self._basic.get_latest_confirmed(project_id)
        confirmed_dl = basic.values.get("dl_number", "").strip() if basic else ""
        registered_dl = workspace.dl_number.strip() if workspace else ""
        if registered_dl and confirmed_dl and registered_dl.casefold() != confirmed_dl.casefold():
            return CurrentReportArtifact("missing", None, None, None, None, None)
        dl_number = registered_dl or confirmed_dl
        if dl_number:
            try:
                downloaded = self._downloads.latest(dl_number)
            except DownloadedInternalReportUnavailable:
                # Do not silently substitute an older managed source for an unsafe latest draft.
                return CurrentReportArtifact("missing", None, None, None, None, None)
            if downloaded is not None:
                return downloaded
        return current
