import pytest

from backend.modules.temperature_rise.calculation import fit_curve, inverse_current, summarize, stage_endpoints


def test_sample_constrained_fit_and_full_precision_inverse():
    current = [17.596362, 30.850749, 39.665046, 43.987415, 66.039286, 75.089058]
    maximum = [3.503, 8.634, 12.952, 15.405, 29.951, 36.545]
    average = [3.1812, 8.1236, 12.1774, 14.4634, 28.5982, 34.968]
    curve = fit_curve(current, maximum, zero_intercept=True, include_origin=True)
    assert curve.a == pytest.approx(0.004676764445955003)
    assert curve.b == pytest.approx(0.13959770191574522)
    assert curve.c == 0
    assert inverse_current(curve, 30) == pytest.approx(66.545852, abs=1e-6)
    assert curve.r_squared == pytest.approx(0.999603, abs=1e-6)
    avg = fit_curve(current, average, zero_intercept=True, include_origin=True)
    assert avg.a == pytest.approx(0.004629983852724594)
    assert avg.b == pytest.approx(0.12202753907878668)


def test_single_max_uses_selected_row_not_stage_or_channel_average():
    result = summarize(20, [("A", "HS", 22), ("A", "C", 26), ("B", "only", 24)])
    assert result["single_max"] == {"A": 6, "B": 4}
    assert result["maximum"] == 6
    assert result["average_of_max"] == 5


def test_stage_suggestions_are_last_rows_with_one_percent_current_range():
    assert stage_endpoints([10, 10.05, 10.09, 20, 20, 30]) == [2, 4, 5]


def test_free_intercept_is_retained_in_inverse_and_degenerate_input_fails():
    curve = fit_curve([1, 2, 3, 4], [4, 9, 16, 25], zero_intercept=False)
    assert (curve.a, curve.b, curve.c) == pytest.approx((1, 2, 1))
    assert inverse_current(curve, 36) == pytest.approx(5)
    with pytest.raises(ValueError, match="distinct"):
        fit_curve([10, 10], [3, 4], zero_intercept=True)
    with pytest.raises(ValueError, match="non-negative"):
        inverse_current(curve, 0)


def test_small_quadratic_coefficient_is_not_discarded_for_large_currents():
    curve = fit_curve([1e9, 2e9, 3e9], [1, 4, 9])
    assert inverse_current(curve, 16) == pytest.approx(4e9)


def test_zero_intercept_curve_returns_zero_current_at_zero_allowable_rise_even_with_negative_b():
    curve = fit_curve([10, 20, 30], [1, 8, 21])
    assert (curve.a, curve.b, curve.c) == pytest.approx((.03, -.2, 0))
    assert inverse_current(curve, 0) == 0
