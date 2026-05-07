from __future__ import annotations

from pathlib import Path

from backend.application.lookup_options_service import (
    INTAKE_PRECHECK_LOOKUP_GROUPS,
    PROJECT_SETUP_LOOKUP_GROUPS,
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


def test_project_setup_options_backfill_required_defaults() -> None:
    store = _FakeLookupOptionStore(
        (
            LookupOption(
                option_id="custom-bu",
                group_key="business_unit",
                value="Custom BU",
                label="Custom BU",
                sort_order=1,
            ),
        )
    )

    groups = LookupOptionService(store).project_setup_options()

    assert tuple(groups) == PROJECT_SETUP_LOOKUP_GROUPS
    assert "AIPG Guangzhou" in [option.value for option in groups["project_setup_location"]]
    assert "Qualification" in [
        option.value for option in groups["project_setup_test_type_in_sheet"]
    ]


def test_import_from_config_backs_up_and_disables_without_deleting(tmp_path: Path) -> None:
    database_path = tmp_path / "connlab.sqlite3"
    database_path.write_text("database", encoding="utf-8")
    config_path = tmp_path / "lookup-options.toml"
    config_path.write_text(
        """
[lookup_options]
project_setup_location = [
  "Nantong Lab",
  { value = "Old Location", active = false, sort_order = 5 },
]
project_setup_test_type_in_sheet = [
  { value = "Qualification", label = "Qualification", sort_order = 2 },
]
""".strip(),
        encoding="utf-8",
    )
    store = _FakeLookupOptionStore(
        (
            LookupOption(
                option_id="old",
                group_key="project_setup_location",
                value="Old Location",
                label="Old Location",
                sort_order=1,
            ),
        )
    )

    result = LookupOptionService(store).import_from_config(
        config_path,
        database_path=database_path,
        backup_dir=tmp_path / "backups",
    )

    assert result.imported_count == 3
    assert result.disabled_count == 1
    assert result.backup_path is not None
    assert result.backup_path.read_text(encoding="utf-8") == "database"
    active = store.list_active_by_groups(PROJECT_SETUP_LOOKUP_GROUPS)
    assert [option.value for option in active["project_setup_location"]] == ["Nantong Lab"]
    assert [option.value for option in active["project_setup_test_type_in_sheet"]] == [
        "Qualification"
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

    def upsert_many(self, options: tuple[LookupOption, ...]) -> None:
        """Create or update options in memory."""
        existing = {
            (option.group_key, option.value): index
            for index, option in enumerate(self.options)
        }
        for option in options:
            index = existing.get((option.group_key, option.value))
            if index is None:
                self.options.append(option)
            else:
                self.options[index] = option
