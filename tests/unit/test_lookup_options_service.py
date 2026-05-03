from __future__ import annotations

from backend.application.lookup_options_service import (
    INTAKE_PRECHECK_LOOKUP_GROUPS,
    LookupOptionService,
)
from backend.domain.lookup_options import LookupOption


def test_intake_precheck_options_seed_defaults_once() -> None:
    store = _FakeLookupOptionStore()
    service = LookupOptionService(store)

    first = service.intake_precheck_options()
    second = service.intake_precheck_options()

    assert store.seed_count == 1
    assert tuple(first) == INTAKE_PRECHECK_LOOKUP_GROUPS
    assert first["business_unit"][0].value == "AAPG"
    assert any(option.value == "AAL" for option in first["manufacturing_site"])
    assert second["sample_status"][0].value == "Prototype"


def test_intake_precheck_options_return_active_custom_database_values() -> None:
    store = _FakeLookupOptionStore(
        (
            LookupOption(
                option_id="1",
                group_key="business_unit",
                value="Custom BU",
                label="Custom BU",
                sort_order=2,
            ),
            LookupOption(
                option_id="2",
                group_key="business_unit",
                value="Inactive BU",
                label="Inactive BU",
                sort_order=1,
                active=False,
            ),
            LookupOption(
                option_id="3",
                group_key="sample_status",
                value="Custom Status",
                label="Custom Status",
                sort_order=1,
            ),
        )
    )

    groups = LookupOptionService(store).intake_precheck_options()

    assert store.seed_count == 0
    assert [option.value for option in groups["business_unit"]] == ["Custom BU"]
    assert [option.value for option in groups["sample_status"]] == ["Custom Status"]
    assert groups["project_type"] == ()
    assert [option.value for option in groups["post_testing_disposition"]] == [
        "Choose an item.",
        "Send Back to Requestor",
        "Scrap",
        "Keep in the Lab",
    ]


class _FakeLookupOptionStore:
    """In-memory lookup option store for service tests."""

    def __init__(self, options: tuple[LookupOption, ...] = ()) -> None:
        self.options = list(options)
        self.seed_count = 0

    def has_any(self) -> bool:
        """Return whether any option exists."""
        return bool(self.options)

    def add_many(self, options: tuple[LookupOption, ...]) -> None:
        """Persist options in memory."""
        self.seed_count += 1
        self.options.extend(options)

    def add_missing(self, options: tuple[LookupOption, ...]) -> None:
        """Persist options that do not already exist."""
        existing = {(option.group_key, option.value) for option in self.options}
        self.options.extend(
            option
            for option in options
            if (option.group_key, option.value) not in existing
        )

    def list_active_by_groups(self, group_keys: tuple[str, ...]) -> dict[str, list[LookupOption]]:
        """Return active grouped options."""
        grouped: dict[str, list[LookupOption]] = {group_key: [] for group_key in group_keys}
        for option in sorted(self.options, key=lambda item: (item.group_key, item.sort_order)):
            if option.active and option.group_key in grouped:
                grouped[option.group_key].append(option)
        return grouped
