"""Application service for native file and folder path selection."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from backend.domain import ExternalResourceType


class LocalPathPickerPort(Protocol):
    """Native path-picker behavior required by the application service."""

    def pick_file(self, resource_type: ExternalResourceType) -> Path | None:
        """Return one selected file path, or None when cancelled."""

    def pick_directory(self, resource_type: ExternalResourceType) -> Path | None:
        """Return one selected directory path, or None when cancelled."""


class LocalPathPickerService:
    """Select a local path for one external resource type."""

    def __init__(self, picker: LocalPathPickerPort) -> None:
        self._picker = picker

    def pick_path(self, resource_type: ExternalResourceType) -> Path | None:
        """Return a selected path for one external resource type."""
        if resource_type in {
            ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
            ExternalResourceType.PROJECT_OUTPUT_ROOT,
            ExternalResourceType.OFFICIAL_PUBLIC_DRIVE_ROOT,
        }:
            return self._picker.pick_directory(resource_type)
        return self._picker.pick_file(resource_type)
