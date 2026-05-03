"""Application service for backend-managed lookup options."""

from __future__ import annotations

from typing import Protocol

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
    return tuple(
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
    )
