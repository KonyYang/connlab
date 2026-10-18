"""Public numerical contract, checked against the supplied VBA workbook's saved results."""

import json
from pathlib import Path

import pytest

from backend.domain.temperature_rise import (
    Measurement, Coefficients, analyze_temperature_rise, calculate_current, generate_derating, fit_quadratic,
)


def baseline_rows():
    payload = json.loads((Path(__file__).parents[1] / "fixtures/temperature_rise/scanner.json").read_text(encoding="utf-8"))
    return tuple(Measurement(**row) for row in payload["measurements"])


def test_scanner_stages_sample_maxima_and_fits_match_saved_macro():
    result = analyze_temperature_rise(baseline_rows(), thermocouples_per_sample=4, zero_intercept=True)
    assert [point.source_row for point in result.points] == [None, 81, 131, 181, 231, 281, 331]
    assert [point.current for point in result.points] == pytest.approx(
        [0, 17.596362, 30.850749, 39.665046, 43.987415, 66.039286, 75.089058])
    assert [point.maximum for point in result.points] == pytest.approx(
        [0, 3.503, 8.634, 12.952, 15.405, 29.951, 36.545])
    assert [point.average for point in result.points] == pytest.approx(
        [0, 3.1812, 8.1236, 12.1774, 14.4634, 28.5982, 34.968])
    assert result.maximum_fit.coefficients == Coefficients(0.004677, 0.139598, 0)
    assert result.average_fit.coefficients == Coefficients(0.004630, 0.122028, 0)
    # Desktop Excel native polynomial trendline labels, including forced zero intercept.
    assert result.maximum_fit.r_squared == pytest.approx(.9996190754852495)
    assert result.average_fit.r_squared == pytest.approx(.9996219947698262)


def test_current_and_derating_use_effective_six_decimal_coefficients():
    assert calculate_current(Coefficients(.004677, .139598, 0), 30) == pytest.approx(66.54445742154181)
    result = generate_derating(Coefficients(.004630, .122028, 0), max_temperature=105, step=2.5, ambient_point=75)
    assert len(result.points) == 43
    assert result.annotation.ambient == 75
    assert result.annotation.basic == pytest.approx(68.38881593205294)
    assert result.annotation.derated == pytest.approx(54.71105274564235)
    assert result.points[-1].basic == 0
    assert all(a.basic >= b.basic for a, b in zip(result.points, result.points[1:]))


def test_quadratic_fit_can_retain_nonzero_intercept():
    result = fit_quadratic([0, 10, 20, 30], [2, 5, 10, 17], zero_intercept=False)
    assert result.coefficients == Coefficients(.01, .2, 2)
    assert result.r_squared == pytest.approx(1)
    assert calculate_current(result.coefficients, 10) == pytest.approx(20)


@pytest.mark.parametrize('zero_intercept', [False, True])
def test_measured_zero_current_endpoint_preserves_background_rise(zero_intercept):
    rows = [Measurement(1, 0, 20, (29, 28)), Measurement(2, 0, 22, (24, 23))]
    for current in (10, 20, 30):
        for _ in range(2):
            rows.append(Measurement(len(rows) + 1, current, 25,
                (25 + .01 * current ** 2 + .2 * current + 2,
                 25 + .005 * current ** 2 + .1 * current + 1)))
    # A shutdown tail is not the pre-energization background reading.
    rows.extend([Measurement(9, 0, 25, (50, 49)), Measurement(10, 0, 25, (49, 48))])
    result = analyze_temperature_rise(rows, thermocouples_per_sample=1, zero_intercept=zero_intercept)
    assert [point.source_row for point in result.points] == ([None, 4, 6, 8] if zero_intercept else [2, 4, 6, 8])
    assert result.points[0].current == 0
    assert result.points[0].rises == ((0, 0) if zero_intercept else (2, 1))
    assert result.points[0].maximum == (0 if zero_intercept else 2)
    assert result.points[0].average == (0 if zero_intercept else 1.5)
    if not zero_intercept:
        assert result.maximum_fit.coefficients == Coefficients(.01, .2, 2)
        assert result.average_fit.coefficients == Coefficients(.0075, .15, 1.5)
        assert result.maximum_fit.r_squared == pytest.approx(1)
        assert calculate_current(result.maximum_fit.coefficients, 10) == pytest.approx(20)
    else:
        assert result.maximum_fit.coefficients.c == 0
        assert result.average_fit.coefficients.c == 0


def test_free_intercept_without_initial_zero_uses_only_measurements_and_warns():
    rows = [Measurement(i + 1, current, 23, (23 + rise,))
            for i, (current, rise) in enumerate(((10, 3.8), (10, 3.8), (20, 8.8),
                                                (20, 8.8), (30, 15.8), (30, 15.8)))]
    result = analyze_temperature_rise(rows, thermocouples_per_sample=1, zero_intercept=False)
    assert [point.source_row for point in result.points] == [2, 4, 6]
    assert [point.current for point in result.points] == [10, 20, 30]
    assert result.maximum_fit.coefficients == Coefficients(.01, .2, .8)
    assert len(result.warnings) == 1
    assert 'zero-current' in result.warnings[0] and 'extrapolated' in result.warnings[0]
    forced = analyze_temperature_rise(rows, thermocouples_per_sample=1, zero_intercept=True)
    assert [point.source_row for point in forced.points] == [None, 2, 4, 6]
    assert forced.points[0].maximum == 0
    assert forced.warnings == ()


@pytest.mark.parametrize('initial_zero', [False, True])
def test_restart_zero_is_not_reused_as_pre_energization_baseline(initial_zero):
    currents = ([0] if initial_zero else []) + [10, 10, 0, 0, 20, 20, 30, 30, 0]
    rows = [Measurement(i + 1, current, 20, (21 + .01 * current ** 2,))
            for i, current in enumerate(currents)]
    result = analyze_temperature_rise(rows, thermocouples_per_sample=1, zero_intercept=False)
    assert [point.current for point in result.points] == ([0] if initial_zero else []) + [10, 20, 30]
    assert bool(result.warnings) is not initial_zero
    assert all(point.source_row is not None for point in result.points)


def test_missing_baseline_with_too_few_stages_explains_both_problems():
    rows = [Measurement(i + 1, current, 20, (20 + current,))
            for i, current in enumerate((10, 10, 20, 20))]
    with pytest.raises(ValueError, match='zero-current.*three distinct'):
        analyze_temperature_rise(rows, thermocouples_per_sample=1, zero_intercept=False)


def test_single_zero_reading_before_energization_is_a_real_endpoint():
    rows = [Measurement(7, 0, 20, (22,))]
    rows.extend(Measurement(number, current, 20, (rise + 20,))
                for number, current, rise in ((8, 10, 5), (9, 10, 5), (10, 20, 10), (11, 20, 10)))
    result = analyze_temperature_rise(rows, thermocouples_per_sample=1, zero_intercept=False)
    assert [point.source_row for point in result.points] == [7, 9, 11]
    assert result.maximum_fit.coefficients == Coefficients(.01, .2, 2)


def test_derating_includes_end_limit_and_exact_off_grid_annotation():
    result = generate_derating(Coefficients(.01, 0, 0), max_temperature=100, step=30, ambient_point=75)
    assert [point.ambient for point in result.points] == [0, 30, 60, 90, 100]
    assert result.annotation.basic == 50
    assert result.annotation.derated == 40


@pytest.mark.parametrize('coefficients,target', [
    (Coefficients(0, 1, 0), 30), (Coefficients(1, 0, 40), 30),
    (Coefficients(1, 2, 0), -1), (Coefficients(float('nan'), 0, 0), 30),
])
def test_invalid_current_inputs_are_actionable(coefficients, target):
    with pytest.raises(ValueError):
        calculate_current(coefficients, target)


def test_incomplete_samples_or_insufficient_stages_cannot_be_plotted():
    with pytest.raises(ValueError, match='complete samples'):
        analyze_temperature_rise(baseline_rows(), thermocouples_per_sample=3, zero_intercept=True)
    with pytest.raises(ValueError, match='distinct current'):
        analyze_temperature_rise([Measurement(1, 10, 20, (25,)), Measurement(2, 10, 20, (25,))],
                                 thermocouples_per_sample=1, zero_intercept=True)


def test_missing_measurement_does_not_become_zero():
    with pytest.raises(ValueError, match='Row 17'):
        analyze_temperature_rise([Measurement(17, 10, 20, (None,))],
                                 thermocouples_per_sample=1, zero_intercept=True)


def test_unrepresentable_current_scale_is_rejected_with_guidance():
    with pytest.raises(ValueError, match='scale'):
        fit_quadratic([0, 1e-200, 2e-200], [0, 5, 10], zero_intercept=True)
