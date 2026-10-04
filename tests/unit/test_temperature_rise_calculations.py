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
