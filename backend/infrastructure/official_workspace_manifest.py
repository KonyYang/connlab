"""Portable manifest gateway for local official project workspaces."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class OfficialWorkspaceManifest:
    """Portable local workspace manifest payload."""

    schema_version: int
    project_id: str
    dl_number: str
    local_workspace_path: str
    source_book_path: str
    official_project_folder_path: str
    template_source_path: str
    created_at: str


class OfficialWorkspaceManifestGateway:
    """Read and write official workspace manifest JSON files."""

    def read(self, path: Path) -> dict[str, object]:
        """Read a manifest JSON file as a dictionary."""
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, path: Path, manifest: OfficialWorkspaceManifest) -> None:
        """Write a manifest JSON file in UTF-8."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(asdict(manifest), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
