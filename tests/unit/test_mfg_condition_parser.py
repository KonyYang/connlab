import pytest

from backend.modules.test_plan.mfg_condition_parser import extract_mfg_condition


def test_extract_mfg_condition_canonicalizes_labeled_phase_hours() -> None:
    source = (
        "Test Condition: CLASS IIA. Expose the connector to mixed gas in "
        "unmated condition for 224h; after mating, requirements shall be met. "
        "Expose the connector to mixed gas in mated condition for 112h."
    )

    assert extract_mfg_condition(source) == (
        "Class IIA; unmated 224 hours; mated 112 hours"
    )


def test_extract_mfg_condition_accepts_duration_before_phase_label() -> None:
    source = "Class IIA. Duration - 224 hours unmated, 112 hours mated."

    assert extract_mfg_condition(source) == (
        "Class IIA; unmated 224 hours; mated 112 hours"
    )


def test_extract_mfg_condition_keeps_supported_facts_when_phase_is_missing() -> None:
    source = "Test Condition: CLASS IIA. Unmated condition for 224 hr."

    assert extract_mfg_condition(source) == "Class IIA; unmated 224 hours"


@pytest.mark.parametrize("unit", ["h", "hr", "hrs", "hour", "hours"])
def test_extract_mfg_condition_accepts_narrow_hour_spellings(unit: str) -> None:
    source = f"Class IIA; unmated condition for 224{unit}; mated 112 {unit}"

    assert extract_mfg_condition(source) == (
        "Class IIA; unmated 224 hours; mated 112 hours"
    )


def test_extract_mfg_condition_rejects_conflicting_phase_values() -> None:
    source = (
        "Class IIA; unmated 224 hours; unmated 240 hours; mated 112 hours"
    )

    assert extract_mfg_condition(source) == "Class IIA; mated 112 hours"
