"""Select a customer-report source without changing current-report authority."""
from typing import Protocol

from backend.application.current_report_update_service import CurrentReportArtifact


class DownloadedInternalReportUnavailable(ValueError):
    """Downloaded candidates cannot safely identify one current-project draft."""


class DownloadedInternalReportReader(Protocol):
    def latest(self, dl_number: str) -> CurrentReportArtifact | None: ...


class CustomerReportSourceResolver:
    def __init__(self, *, current_reports, basic_information, workspaces,
                 downloaded_drafts: DownloadedInternalReportReader, working_drafts=None):
        self._current = current_reports
        self._basic = basic_information
        self._workspaces = workspaces
        self._downloads = downloaded_drafts
        self._working = working_drafts

    def get_current_report(self, project_id: str) -> CurrentReportArtifact:
        current = self._current.get_current_report(project_id)
        if current.status == "ambiguous" or (current.status == "ready" and current.mode == "official"):
            return current
        dl_number = self.project_dl_number(project_id)
        if dl_number:
            try:
                if self._working is not None:
                    working = self._working.latest(project_id, dl_number)
                    if working is not None:
                        return working
                downloaded = self._downloads.latest(dl_number)
            except ValueError:
                # Never silently replace an unsafe latest draft with an older managed source.
                return CurrentReportArtifact("missing", None, None, None, None, None)
            if downloaded is not None:
                return downloaded
        elif dl_number is None:
            return CurrentReportArtifact("missing", None, None, None, None, None)
        return current

    def project_dl_number(self, project_id):
        workspace = self._workspaces.get_by_project(project_id)
        basic = self._basic.get_latest_confirmed(project_id)
        confirmed_dl = basic.values.get("dl_number", "").strip() if basic else ""
        registered_dl = workspace.dl_number.strip() if workspace else ""
        if registered_dl and confirmed_dl and registered_dl.casefold() != confirmed_dl.casefold():
            return None
        return registered_dl or confirmed_dl
