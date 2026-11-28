"""Bind portable web business folders once, independently of the installation directory."""

from dataclasses import dataclass, field
import hashlib
import os
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from backend.application.ir_dwv_template_discovery import is_ir_dwv_template_name
from backend.domain import ExternalResource, ExternalResourceType
from backend.infrastructure.files.default_storage_directory import DefaultStorageDirectory
from backend.infrastructure.project_library.files import checked_path
from backend.infrastructure.storage.models_project_library import MaterialReceiptSettingsModel
from backend.infrastructure.storage.repositories.external_resources import ExternalResourceRepository

RESOURCE_KINDS = {
    "Projects": ExternalResourceType.PROJECT_OUTPUT_ROOT,
    "TemporaryProjects": ExternalResourceType.TEMPORARY_MATERIALS_ROOT,
    "Template": ExternalResourceType.PROJECT_FOLDER_TEMPLATE,
}


@dataclass
class BrowserStorage:
    locations: dict[str, Path] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    unavailable: set[str] = field(default_factory=set)
    template_overrides: dict[str, Path] = field(default_factory=dict)

    @property
    def common_root(self) -> Path | None:
        if len(self.locations) != 4:
            return None
        root = self.locations["Projects"].parent
        if root.name.casefold() != "connlabfiles":
            return None
        return root if all(path == root / purpose for purpose, path in self.locations.items()) else None

    def metadata(self):
        return {
            "storage_locations": {key: str(path) for key, path in self.locations.items()},
            "storage_warnings": self.warnings,
            "storage_root": str(self.common_root) if self.common_root else None,
        }


def uses_legacy_defaults(settings) -> bool:
    """Remember a fresh database before schema initialization can make it look like an upgrade."""
    database = os.path.normcase(str(settings.database_path.resolve()))
    key = hashlib.sha256(database.encode()).hexdigest()
    marker = settings.data_dir / f".browser-storage-{key}.new-install"
    if marker.is_file():
        return False
    if settings.database_path.exists():
        return not marker.is_file()  # Another launcher may have initialized the database.
    try:
        # The file's exclusive creation is the entire marker write; it has no payload.
        with marker.open("xb"):
            pass
    except FileExistsError:
        if not marker.is_file():
            raise
    return False


def register_browser_storage(settings, sessions, root: Path, overrides: dict[str, Path], *, upgrading=False) -> BrowserStorage:
    storage = BrowserStorage()
    previous_defaults = {
        "Projects": settings.projects_dir, "Template": settings.templates_dir,
        "Library": settings.output_path("Materials"), "TemporaryProjects": settings.output_path("TemporaryMaterials"),
    }

    def prior_folder(purpose):
        if purpose in overrides:
            return overrides[purpose]
        if upgrading:
            candidate = previous_defaults[purpose]
            # Old launchers created empty per-user template folders on every startup.
            # Retain populated defaults; registered/configured folders always take precedence.
            if candidate.is_dir() and any(candidate.iterdir()):
                return candidate
        return None

    with sessions.begin() as session:
        # Serialize first registrations with another launcher or a maintenance settings save.
        session.execute(text("BEGIN IMMEDIATE"))
        resources = ExternalResourceRepository(session)
        for purpose, kind in RESOURCE_KINDS.items():
            row = resources.get_by_type(kind)
            existing = row.path if row else prior_folder(purpose)
            path = existing or root / purpose
            _prepare_folder(storage, purpose, path, create=existing is None,
                            active=row is None or row.active)
            if row is None:
                resources.create_default_if_absent(ExternalResource(uuid4().hex, kind, path))

        ir = resources.get_by_type(ExternalResourceType.IR_DWV_RECORD_TEMPLATE)
        if ir and ir.active and not (ir.path.parent == storage.locations["Template"] and is_ir_dwv_template_name(ir.path)):
            storage.template_overrides["ir_dwv"] = ir.path
        if settings.test_record.template_path:
            storage.template_overrides["test_record"] = settings.test_record.template_path

        receipt = session.get(MaterialReceiptSettingsModel, "default")
        existing = Path(receipt.root_path) if receipt and receipt.root_path else prior_folder("Library")
        path = existing or root / "Library"
        if not receipt or not receipt.root_path:
            # Reuse the receipt service's ownership limits for a newly assigned root.
            from backend.api.routes_material_receipts import get_material_receipt_service
            service = get_material_receipt_service(session, settings)
            try:
                service.prepare_default_root(path, create=existing is None)
            except (OSError, ValueError) as error:
                raise ValueError(f"Cannot initialize Library at {path}: {error}") from error
            if receipt is None:
                session.add(MaterialReceiptSettingsModel(settings_id="default", root_path=str(path), revision=1))
            else:
                receipt.root_path, receipt.revision = str(path), receipt.revision + 1
        _prepare_folder(storage, "Library", path, create=False)
    if "Template" not in storage.unavailable:
        template = storage.locations["Template"].resolve()
        occupied = [settings.data_dir, *(p for key, p in storage.locations.items() if key != "Template")]
        if any(template.is_relative_to(p.resolve()) or p.resolve().is_relative_to(template) for p in occupied):
            storage.unavailable.add("Template")
            storage.warnings.append(f"Template: {template} overlaps a business or data folder. Review its registration before installing templates.")
    return storage


def _prepare_folder(storage: BrowserStorage, purpose: str, path: Path, *, create: bool, active=True):
    storage.locations[purpose] = path
    if create:
        try:
            DefaultStorageDirectory().create(path)
        except (OSError, ValueError) as error:
            raise ValueError(f"Cannot initialize {purpose} at {path}. Check write access or use a writable installation drive.") from error
        return
    try:
        if not active:
            raise ValueError("registration is disabled")
        if not checked_path(path).is_dir():
            raise ValueError("expected a directory")
    except (OSError, ValueError) as error:
        storage.unavailable.add(purpose)
        storage.warnings.append(f"{purpose}: {path} is unavailable ({error}). Restore access to the registered folder.")
