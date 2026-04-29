"""Deterministic evidence placement rules for generated project folders."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from backend.domain import FileAsset, FileAssetType


class EvidencePlacementCategory(StrEnum):
    """Supported evidence placement categories."""

    EMAIL = "email"
    APPLICATION_FORM = "application_form"
    SUPPORTING_ATTACHMENT = "supporting_attachment"
    SPECIFICATION = "specification"
    PHOTO = "photo"
    LTR_EVIDENCE = "ltr_evidence"
    CORRECTION = "correction"


@dataclass(frozen=True, slots=True)
class EvidencePlacementItem:
    """One planned evidence copy operation."""

    asset_id: str
    category: EvidencePlacementCategory
    source_path: Path
    target_path: Path
    missing_source: bool
    target_exists: bool
    duplicate_target: bool = False

    @property
    def conflict(self) -> bool:
        """Return whether this item cannot be safely copied."""
        return self.missing_source or self.target_exists or self.duplicate_target


@dataclass(frozen=True, slots=True)
class EvidencePlacementPlan:
    """Preview plan for all evidence files of one project."""

    project_id: str
    project_folder_path: Path
    evidence_root_path: Path
    items: tuple[EvidencePlacementItem, ...]
    conflicts: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def conflict(self) -> bool:
        """Return whether the plan contains any blocking conflict."""
        return bool(self.conflicts) or any(item.conflict for item in self.items)


class EvidencePlacementPlanner:
    """Build placement plans from project file assets and generated folder shape."""

    _IMAGE_EXTENSIONS = {
        ".bmp",
        ".gif",
        ".heic",
        ".jpeg",
        ".jpg",
        ".png",
        ".tif",
        ".tiff",
        ".webp",
    }
    _SPEC_KEYWORDS = (
        "spec",
        "规格",
        "standard",
        "requirement",
        "req",
        "drawing",
        "图纸",
        "sor",
    )
    _CORRECTION_KEYWORDS = (
        "correction",
        "corrected",
        "revise",
        "revised",
        "更正",
        "修正",
        "补充",
    )
    _LTR_KEYWORDS = (
        "ltr",
        "registration",
        "readiness",
        "preview",
        "commit",
        "audit",
    )

    def preview(
        self,
        project_id: str,
        project_folder_path: Path,
        assets: list[FileAsset],
    ) -> EvidencePlacementPlan:
        """Return a safe copy preview for project evidence assets."""
        evidence_root = self._evidence_root(project_folder_path)
        warnings = self._folder_warnings(project_folder_path, evidence_root)
        items = [
            self._item_for_asset(asset, evidence_root)
            for asset in assets
            if asset.asset_type is not FileAssetType.GENERATED_FOLDER
            and asset.asset_type is not FileAssetType.FOLDER_TEMPLATE
        ]
        items = self._mark_duplicate_targets(items)
        return EvidencePlacementPlan(
            project_id=project_id,
            project_folder_path=project_folder_path,
            evidence_root_path=evidence_root,
            items=tuple(items),
            warnings=tuple(warnings),
        )

    def _item_for_asset(
        self,
        asset: FileAsset,
        evidence_root: Path,
    ) -> EvidencePlacementItem:
        """Build one placement item for a file asset."""
        category = self._classify(asset)
        target_dir = self._target_dir(evidence_root, category)
        target_name = self._target_name(asset)
        target_path = target_dir / target_name
        return EvidencePlacementItem(
            asset_id=asset.asset_id,
            category=category,
            source_path=asset.path,
            target_path=target_path,
            missing_source=not asset.path.exists(),
            target_exists=target_path.exists(),
        )

    def _classify(self, asset: FileAsset) -> EvidencePlacementCategory:
        """Classify one project asset into a deterministic evidence category."""
        name = self._search_name(asset)
        suffix = asset.path.suffix.lower()
        if self._has_any(name, self._CORRECTION_KEYWORDS):
            return EvidencePlacementCategory.CORRECTION
        if asset.asset_type is FileAssetType.APPLICATION_FORM:
            return EvidencePlacementCategory.APPLICATION_FORM
        if suffix == ".msg" or "outlook" in name or "email" in name:
            return EvidencePlacementCategory.EMAIL
        if suffix in self._IMAGE_EXTENSIONS:
            return EvidencePlacementCategory.PHOTO
        if asset.asset_type is FileAssetType.LTR or self._has_any(
            name, self._LTR_KEYWORDS
        ):
            return EvidencePlacementCategory.LTR_EVIDENCE
        if self._has_any(name, self._SPEC_KEYWORDS):
            return EvidencePlacementCategory.SPECIFICATION
        return EvidencePlacementCategory.SUPPORTING_ATTACHMENT

    def _target_dir(
        self,
        evidence_root: Path,
        category: EvidencePlacementCategory,
    ) -> Path:
        """Return the target directory for an evidence category."""
        if category is EvidencePlacementCategory.EMAIL:
            return evidence_root / "E-mail"
        if category is EvidencePlacementCategory.PHOTO:
            return evidence_root / "Photos"
        if category is EvidencePlacementCategory.SPECIFICATION:
            return evidence_root / "Submitted Material" / "Specifications"
        if category is EvidencePlacementCategory.LTR_EVIDENCE:
            return evidence_root / "Submitted Material" / "LTR Evidence"
        if category is EvidencePlacementCategory.CORRECTION:
            return evidence_root / "Submitted Material" / "Corrections"
        return evidence_root / "Submitted Material"

    def _evidence_root(self, project_folder_path: Path) -> Path:
        """Return the primary title folder used by real generated projects."""
        if not project_folder_path.exists() or not project_folder_path.is_dir():
            return project_folder_path
        children = sorted(path for path in project_folder_path.iterdir() if path.is_dir())
        project_stem = project_folder_path.name.lower()
        title_dirs = [
            child
            for child in children
            if child.name.lower() != "source book"
            and child.name.lower().startswith(project_stem)
        ]
        if title_dirs:
            return title_dirs[0]
        non_source_dirs = [child for child in children if child.name.lower() != "source book"]
        return non_source_dirs[0] if non_source_dirs else project_folder_path

    def _folder_warnings(
        self,
        project_folder_path: Path,
        evidence_root: Path,
    ) -> list[str]:
        """Return non-blocking folder shape warnings."""
        warnings: list[str] = []
        if not project_folder_path.exists():
            warnings.append(f"Project folder does not exist yet: {project_folder_path}")
        elif evidence_root == project_folder_path:
            warnings.append(
                "Project title folder was not detected; evidence targets use project root."
            )
        return warnings

    def _target_name(self, asset: FileAsset) -> str:
        """Return the file name to use at the target location."""
        candidate = (asset.original_name or asset.path.name).strip()
        return candidate if candidate else asset.path.name

    def _search_name(self, asset: FileAsset) -> str:
        """Return normalized text used for deterministic classification."""
        return f"{asset.original_name or ''} {asset.path.name}".lower()

    def _has_any(self, value: str, keywords: tuple[str, ...]) -> bool:
        """Return whether any configured keyword appears in a normalized value."""
        return any(keyword in value for keyword in keywords)

    def _mark_duplicate_targets(
        self,
        items: list[EvidencePlacementItem],
    ) -> list[EvidencePlacementItem]:
        """Mark items whose target path is repeated in the same plan."""
        counts: dict[Path, int] = {}
        for item in items:
            counts[item.target_path] = counts.get(item.target_path, 0) + 1
        return [
            EvidencePlacementItem(
                asset_id=item.asset_id,
                category=item.category,
                source_path=item.source_path,
                target_path=item.target_path,
                missing_source=item.missing_source,
                target_exists=item.target_exists,
                duplicate_target=counts[item.target_path] > 1,
            )
            for item in items
        ]
