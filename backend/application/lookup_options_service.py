"""Application service for backend-managed lookup options."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from backend.domain.lookup_options import LookupOption


INTAKE_PRECHECK_LOOKUP_GROUPS: tuple[str, ...] = (
    "business_unit",
    "manufacturing_site",
    "results_format",
    "test_type",
    "sample_status",
    "project_type",
    "post_testing_disposition",
)

PROJECT_SETUP_LOOKUP_GROUPS: tuple[str, ...] = (
    "project_setup_location",
    "project_setup_test_type_in_sheet",
)

IMPORTABLE_LOOKUP_GROUPS: tuple[str, ...] = (
    *INTAKE_PRECHECK_LOOKUP_GROUPS,
    *PROJECT_SETUP_LOOKUP_GROUPS,
)


@dataclass(frozen=True, slots=True)
class LookupOptionImportResult:
    """Summary of a lookup option configuration import."""

    backup_path: Path | None
    imported_count: int
    disabled_count: int
    group_keys: tuple[str, ...]


class LookupOptionRepositoryPort(Protocol):
    """Storage behavior required by lookup option service."""

    def has_any(self) -> bool:
        """Return whether any lookup option exists."""

    def add_many(self, options: tuple[LookupOption, ...]) -> None:
        """Persist multiple lookup options."""

    def add_missing(self, options: tuple[LookupOption, ...]) -> None:
        """Persist lookup options that do not already exist."""

    def list_active_by_groups(self, group_keys: tuple[str, ...]) -> dict[str, list[LookupOption]]:
        """Return active lookup options for the requested groups."""

    def upsert_many(self, options: tuple[LookupOption, ...]) -> None:
        """Create or update lookup options by group and value."""


class LookupOptionService:
    """Provide backend-managed lookup options for intake/precheck UI surfaces."""

    def __init__(self, repository: LookupOptionRepositoryPort) -> None:
        """Create a lookup option service."""
        self._repository = repository

    def intake_precheck_options(self) -> dict[str, tuple[LookupOption, ...]]:
        """Return active lookup values required by Intake/Precheck."""
        self._seed_defaults_if_empty()
        self._ensure_required_defaults()
        grouped = self._repository.list_active_by_groups(INTAKE_PRECHECK_LOOKUP_GROUPS)
        return {
            group_key: tuple(grouped.get(group_key, []))
            for group_key in INTAKE_PRECHECK_LOOKUP_GROUPS
        }

    def project_setup_options(self) -> dict[str, tuple[LookupOption, ...]]:
        """Return active lookup values required by New Project setup confirmation."""
        self._seed_defaults_if_empty()
        self._ensure_required_defaults()
        grouped = self._repository.list_active_by_groups(PROJECT_SETUP_LOOKUP_GROUPS)
        return {
            group_key: tuple(grouped.get(group_key, []))
            for group_key in PROJECT_SETUP_LOOKUP_GROUPS
        }

    def import_from_config(
        self,
        config_path: Path,
        *,
        database_path: Path,
        backup_dir: Path,
    ) -> LookupOptionImportResult:
        """Import lookup options from a local TOML file after backing up SQLite."""
        options = _options_from_config(config_path)
        backup_path = _backup_database(database_path, backup_dir)
        self._repository.upsert_many(options)
        return LookupOptionImportResult(
            backup_path=backup_path,
            imported_count=len(options),
            disabled_count=sum(1 for option in options if not option.active),
            group_keys=tuple(dict.fromkeys(option.group_key for option in options)),
        )

    def _seed_defaults_if_empty(self) -> None:
        """Seed initial backend-owned lookup values into an empty store."""
        if self._repository.has_any():
            return
        self._repository.add_many(_default_options())

    def _ensure_required_defaults(self) -> None:
        """Backfill required defaults added after earlier first-run seeds."""
        self._repository.add_missing(_required_default_options())


def _default_options() -> tuple[LookupOption, ...]:
    """Return default lookup options for first-run databases."""
    grouped: dict[str, tuple[str, ...]] = {
        "business_unit": (
            "AAPG", "ACAG", "ACPA", "ACPI", "ACS", "AGIS", "AIMG", "AIPG", "AJET", "Amphenol RF",
            "ANAM", "AORORA", "ARDENT", "ARFOB", "ASTG", "BASICS", "CBS", "CMIO", "Halo",
            "HS Backplane", "HS Cable", "HS Mezzanine", "HSIO", "HSIO CA", "HSIO CN", "HSIO SP",
            "MCP", "MEZZ - AIS", "MEZZ - MegArray", "Multi", "Non-ACS", "None", "Optics", "Other",
            "Positronic", "Power Solutions", "RFOB", "Server & Storage", "Server & Storage IO", "Valley Green", "XGIGA",
        ),
        "manufacturing_site": (
            "AAL", "AAOP Berlin", "AAP", "AAPG-OTHER", "AATK", "ABR", "ACAD", "ACAG-OTHER", "ACC-DT", "ACPA",
            "ACPA - Canada", "ACX Bangalore", "ADCE", "ADS", "AGEC", "AGIS-OTHER", "AGSE", "AHSC", "AHSC-XMN",
            "AHSI", "AHSTNT", "AIMG-OTHER", "AIPG", "AIPG-ATS", "AIPG-NT", "AIPG-OTHER", "AIPG-SZ", "AIS", "AIST",
            "AJET", "AJET-HY", "AJET-HZ", "ALTW", "Amphenol RF", "AMTA", "ANAM-OTHER", "Aorora", "APCD", "ARDENT",
            "ARFOB", "ASAA", "ASCA", "ASCA-SZ", "ASEAN", "AST", "ASTG-OTHER", "ATCS", "ATCS-CZ", "ATCS-MEX",
            "ATCS-NH", "ATPI", "ATZ", "Bangalore", "Berlin", "Besancon", "Changzhou", "Chengdu", "Cochin",
            "Dongguan", "GES", "GPE", "HALO-OTHER", "Hampton", "HSIO CN Canada", "HSIO-CZ", "HSIO-All", "HZP",
            "India", "Japan", "Jurong", "MCP-OTHER", "Multi", "Nantong", "None", "Non-ACS", "Other", "Penang",
            "Positronic Springfield", "RFOB-OTHER", "Senai", "Senjur", "SINE", "Spectra Strip", "TCS-CAA", "TCS-CZ",
            "TCS-MAL", "TCS-USA", "USA", "Valley Green", "Xgiga", "Xiamen",
        ),
        "results_format": ("Data and Observations", "Formal Report (Internal)", "Formal Report (Customer)", "Presentation Summary"),
        "test_type": ("Product/Process Development", "Product/Process Qualification", "Lab/Failure Analysis", "Customer Specific Testing"),
        "sample_status": ("Prototype", "Pre-production", "Production", "Competitor"),
        "project_type": ("New Product Development", "Product Extension", "Innovation", "Lab Activities (Lab Use Only)", "Operational Support", "Cost Reduction"),
        "post_testing_disposition": ("Choose an item.", "Send Back to Requestor", "Scrap", "Keep in the Lab"),
        "project_setup_location": (
            "ACPCD",
            "AFCI DG",
            "AFCI Japan",
            "AFCI NT",
            "AFCI VG",
            "AIPG(NT)",
            "AIPG(amphenol-industrial)",
            "AHSI(Amphenol Canada)",
            "AIPG Guangzhou",
            "AIPG Shenzhen(ATS)",
            "AIPG ZhuHai(ATZ)",
            "AHSC(Xiamen)",
            "AJECT-HY(Haiyan)",
            "AJECT-HZ(Hangzhou)",
            "Amphenol RF",
            "AMTA",
            "Arora",
            "ASCA",
            "ASMI(DZ SuoMing)",
            "AST",
            "ATCS CZ",
            "ATCS Nashua",
            "GFS",
            "GPE",
            "Xigia",
            "AJET",
            "ACIK",
            "ACPA",
            "Non-AICC",
            "Bangalore",
            "ShenZhen",
        ),
        "project_setup_test_type_in_sheet": (
            "Analysis",
            "Chemical",
            "Electrical",
            "Environmental",
            "Failure Analysis",
            "Mechanical",
            "ORT",
            "Other",
            "Partial Qualification",
            "Qualification",
            "Solderability",
            "Whisker",
        ),
    }
    options: list[LookupOption] = []
    for group_key, values in grouped.items():
        for index, value in enumerate(values, start=1):
            options.append(
                LookupOption(
                    option_id=f"default-{group_key}-{index:03d}",
                    group_key=group_key,
                    value=value,
                    label=value,
                    sort_order=index,
                )
            )
    return tuple(options)


def _required_default_options() -> tuple[LookupOption, ...]:
    """Return default options that must be present across existing databases."""
    required = [
        LookupOption(
            option_id=f"required-post_testing_disposition-{index:03d}",
            group_key="post_testing_disposition",
            value=value,
            label=value,
            sort_order=index,
        )
        for index, value in enumerate(
            (
                "Choose an item.",
                "Send Back to Requestor",
                "Scrap",
                "Keep in the Lab",
            ),
            start=1,
        )
    ]
    required.extend(
        LookupOption(
            option_id=f"required-{group_key}-{index:03d}",
            group_key=group_key,
            value=value,
            label=value,
            sort_order=index,
        )
        for group_key, values in {
            key: tuple(option.value for option in _default_options() if option.group_key == key)
            for key in PROJECT_SETUP_LOOKUP_GROUPS
        }.items()
        for index, value in enumerate(values, start=1)
    )
    return tuple(required)


def _options_from_config(config_path: Path) -> tuple[LookupOption, ...]:
    """Read importable lookup options from a TOML configuration file."""
    if not config_path.is_file():
        raise FileNotFoundError(f"Lookup option config file not found: {config_path}")
    with config_path.open("rb") as handle:
        payload = tomllib.load(handle)
    raw_groups = payload.get("lookup_options")
    if not isinstance(raw_groups, dict):
        raise ValueError("Lookup option config must contain a [lookup_options] table.")

    options: list[LookupOption] = []
    for group_key, raw_items in raw_groups.items():
        if group_key not in IMPORTABLE_LOOKUP_GROUPS:
            raise ValueError(f"Unsupported lookup option group: {group_key}")
        if not isinstance(raw_items, list):
            raise ValueError(f"Lookup option group must be a list: {group_key}")
        for index, raw_item in enumerate(raw_items, start=1):
            options.append(_option_from_config_item(group_key, raw_item, index))
    if not options:
        raise ValueError("Lookup option config does not contain any options.")
    return tuple(options)


def _option_from_config_item(
    group_key: str,
    raw_item: Any,
    index: int,
) -> LookupOption:
    """Convert one TOML lookup option item to a domain value."""
    if isinstance(raw_item, str):
        value = raw_item.strip()
        label = value
        active = True
        sort_order = index
    elif isinstance(raw_item, dict):
        raw_value = raw_item.get("value")
        if not isinstance(raw_value, str):
            raise ValueError(f"Lookup option value must be text in group {group_key}.")
        value = raw_value.strip()
        raw_label = raw_item.get("label", value)
        if not isinstance(raw_label, str):
            raise ValueError(f"Lookup option label must be text in group {group_key}.")
        label = raw_label.strip() or value
        active = bool(raw_item.get("active", True))
        sort_order = int(raw_item.get("sort_order", index))
    else:
        raise ValueError(f"Lookup option item must be text or object in group {group_key}.")
    if not value:
        raise ValueError(f"Lookup option value cannot be blank in group {group_key}.")
    return LookupOption(
        option_id=f"import-{group_key}-{uuid4().hex}",
        group_key=group_key,
        value=value,
        label=label,
        sort_order=sort_order,
        active=active,
    )


def _backup_database(database_path: Path, backup_dir: Path) -> Path | None:
    """Copy the SQLite database file before lookup option import."""
    if not database_path.exists():
        return None
    from datetime import datetime
    import shutil

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{database_path.stem}_lookup_options_{timestamp}{database_path.suffix}"
    shutil.copy2(database_path, backup_path)
    return backup_path
