from decimal import Decimal

from backend.modules.fee_evaluation.mfg_duration import resolve_mfg_duration_days


def test_resolve_mfg_duration_days_sums_labeled_phase_hours() -> None:
    assert resolve_mfg_duration_days(
        "Class IIA; unmated 224 hours; mated 112 hours"
    ) == Decimal("14")


def test_resolve_mfg_duration_days_preserves_explicit_days() -> None:
    assert resolve_mfg_duration_days("Class IIA, 14 days") == Decimal("14")


def test_resolve_mfg_duration_days_requires_both_labeled_phases() -> None:
    assert resolve_mfg_duration_days("Class IIA; unmated 224 hours") is None
    assert resolve_mfg_duration_days("Class IIA; mated 112 hours") is None
    assert resolve_mfg_duration_days("Class IIA; 224 hours; 112 hours") is None


def test_resolve_mfg_duration_days_requires_class_iia_for_hour_phases() -> None:
    assert resolve_mfg_duration_days(
        "unmated 224 hours; mated 112 hours"
    ) is None


def test_resolve_mfg_duration_days_rejects_conflicting_phase_values() -> None:
    assert resolve_mfg_duration_days(
        "Class IIA; unmated 224 hours; unmated 240 hours; mated 112 hours"
    ) is None
