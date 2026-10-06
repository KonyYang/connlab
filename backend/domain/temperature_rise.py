"""Temperature-rise statistics and current derating, independent of Excel and transport."""

from __future__ import annotations

from dataclasses import dataclass
from math import fsum, isfinite, sqrt
from collections.abc import Sequence


@dataclass(frozen=True)
class Measurement:
    source_row: int
    current: float
    ambient: float
    temperatures: tuple[float, ...]


@dataclass(frozen=True)
class Coefficients:
    a: float
    b: float
    c: float

    def evaluate(self, current: float) -> float:
        return (self.a * current + self.b) * current + self.c


@dataclass(frozen=True)
class PolynomialFit:
    coefficients: Coefficients
    r_squared: float
    # Chart rendering uses the fitted curve; editable fields use the rounded coefficients.
    fitted_coefficients: Coefficients


@dataclass(frozen=True)
class RisePoint:
    source_row: int | None
    current: float
    rises: tuple[float, ...]
    sample_maxima: tuple[float, ...]
    maximum: float
    average: float


@dataclass(frozen=True)
class TemperatureRiseAnalysis:
    points: tuple[RisePoint, ...]
    maximum_fit: PolynomialFit
    average_fit: PolynomialFit
    zero_intercept: bool
    thermocouples_per_sample: int


@dataclass(frozen=True)
class DeratingPoint:
    ambient: float
    basic: float
    derated: float


@dataclass(frozen=True)
class DeratingAnalysis:
    points: tuple[DeratingPoint, ...]
    annotation: DeratingPoint
    coefficients: Coefficients
    max_temperature: float
    step: float


def analyze_temperature_rise(
    rows: Sequence[Measurement], *, thermocouples_per_sample: int, zero_intercept: bool,
) -> TemperatureRiseAnalysis:
    _validate_measurements(rows, thermocouples_per_sample)
    endpoints = stable_stage_endpoints(rows)
    points = [_rise_point(row, thermocouples_per_sample) for row in endpoints]
    if not points:
        raise ValueError("No stable current stages. Each stage needs at least two successive readings within 1%.")
    if points[0].current != 0:
        count = len(rows[0].temperatures)
        points.insert(0, RisePoint(None, 0, (0.,) * count, (0.,) * (count // thermocouples_per_sample), 0, 0))
    currents = [point.current for point in points]
    return TemperatureRiseAnalysis(
        tuple(points), fit_quadratic(currents, [p.maximum for p in points], zero_intercept=zero_intercept),
        fit_quadratic(currents, [p.average for p in points], zero_intercept=zero_intercept),
        zero_intercept, thermocouples_per_sample,
    )


def _validate_measurements(rows: Sequence[Measurement], count: int) -> None:
    if not rows or not isinstance(count, int) or count < 1:
        raise ValueError("Confirm data and a positive thermocouple count first.")
    width = len(rows[0].temperatures)
    if width == 0 or width % count:
        raise ValueError("Temperature channels must form complete samples with the same thermocouple count.")
    for row in rows:
        if len(row.temperatures) != width:
            raise ValueError(f"Row {row.source_row}: temperature channel count does not match.")
        values = (row.current, row.ambient, *row.temperatures)
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not isfinite(v) for v in values):
            raise ValueError(f"Row {row.source_row}: replace or exclude missing/non-numeric readings.")
        if row.current < 0:
            raise ValueError(f"Row {row.source_row}: current must be nonnegative. Confirm its unit and scale.")


def stable_stage_endpoints(rows: Sequence[Measurement]) -> tuple[Measurement, ...]:
    """VBA's adjacent 1% current rule, applied only to human-confirmed rows."""
    endpoints: list[Measurement] = []
    stable = False
    for previous, current in zip(rows, rows[1:]):
        if previous.current != 0:
            if abs((current.current - previous.current) / previous.current) <= .01:
                stable = True
            else:
                if stable:
                    endpoints.append(previous)
                stable = False
        else:
            # The macro retains the last zero-current reading before energization.
            # Background heating from other currents must not become a synthetic (0, 0).
            if current.current != 0:
                endpoints.append(previous)
            # A shutdown tail has no following energized reading and is not a baseline.
            stable = False
    if stable:
        endpoints.append(rows[-1])
    return tuple(endpoints)


def _rise_point(row: Measurement, count: int) -> RisePoint:
    rises = tuple(value - row.ambient for value in row.temperatures)
    maxima = tuple(max(rises[start:start + count]) for start in range(0, len(rises), count))
    return RisePoint(row.source_row, row.current, rises, maxima, max(maxima), fsum(maxima) / len(maxima))


def fit_quadratic(currents: Sequence[float], rises: Sequence[float], *, zero_intercept: bool) -> PolynomialFit:
    degree_count = 2 if zero_intercept else 3
    if (len(currents) != len(rises) or len(set(currents)) < degree_count
            or (zero_intercept and len({x for x in currents if x != 0}) < 2)):
        raise ValueError("Not enough distinct current stages to fit a quadratic curve.")
    scale = max(abs(x) for x in currents)
    if scale == 0:
        raise ValueError("Nonzero current stages are needed to fit the curve.")
    squared_scale = scale * scale
    if not isfinite(squared_scale) or squared_scale == 0:
        raise ValueError("Current scale is outside the numerical range. Check the unit and scale to amperes.")
    normalized = [x / scale for x in currents]
    columns = [[x * x for x in normalized], normalized]
    if not zero_intercept:
        columns.append([1.] * len(currents))
    # Small scaled QR solve avoids squaring the condition number and adds no runtime dependency.
    orthogonal: list[list[float]] = []
    triangular = [[0.] * degree_count for _ in range(degree_count)]
    for j, column in enumerate(columns):
        residual = list(column)
        for _ in range(2):
            for i, basis in enumerate(orthogonal):
                projection = fsum(a * b for a, b in zip(basis, residual))
                triangular[i][j] += projection
                residual = [a - projection * b for a, b in zip(residual, basis)]
        norm = sqrt(fsum(v * v for v in residual))
        if norm < 1e-10:
            raise ValueError("Current stages are too close together for a reliable quadratic fit.")
        triangular[j][j] = norm
        orthogonal.append([v / norm for v in residual])
    rhs = [fsum(a * b for a, b in zip(basis, rises)) for basis in orthogonal]
    solution = [0.] * degree_count
    for i in reversed(range(degree_count)):
        solution[i] = (rhs[i] - fsum(triangular[i][j] * solution[j] for j in range(i + 1, degree_count))) / triangular[i][i]
    coefficients = Coefficients(solution[0] / squared_scale, solution[1] / scale, 0. if zero_intercept else solution[2])
    fitted = [coefficients.evaluate(x) for x in currents]
    mean, fit_mean = fsum(rises) / len(rises), fsum(fitted) / len(fitted)
    total = fsum((y - mean) ** 2 for y in rises)
    fit_total = fsum((y - fit_mean) ** 2 for y in fitted)
    # Excel polynomial chart labels use squared correlation, including forced-intercept fits.
    covariance = fsum((y - mean) * (f - fit_mean) for y, f in zip(rises, fitted))
    error = fsum((y - f) ** 2 for y, f in zip(rises, fitted))
    r_squared = min(1., covariance ** 2 / (total * fit_total)) if total and fit_total else (1. if error < 1e-20 else 0.)
    effective = Coefficients(*(round(value, 6) for value in (coefficients.a, coefficients.b, coefficients.c)))
    return PolynomialFit(effective, r_squared, coefficients)


def calculate_current(coefficients: Coefficients, target_rise: float) -> float:
    a, b, c = coefficients.a, coefficients.b, coefficients.c
    if any(not isfinite(v) for v in (a, b, c, target_rise)) or target_rise < 0:
        raise ValueError("Enter finite coefficients and a nonnegative temperature rise.")
    if a == 0:
        raise ValueError("Coefficient a must be nonzero. Get or correct the coefficients first.")
    discriminant = b * b - 4 * a * (c - target_rise)
    if not isfinite(discriminant) or discriminant < 0:
        raise ValueError("These coefficients have no real current at the requested temperature rise.")
    root = (-b + sqrt(discriminant)) / (2 * a)
    if not isfinite(root) or root < 0:
        raise ValueError("These coefficients do not give a nonnegative current at the requested rise.")
    return root


def generate_derating(
    coefficients: Coefficients, *, max_temperature: float, step: float, ambient_point: float,
) -> DeratingAnalysis:
    if coefficients.c != 0:
        raise ValueError("Derating requires zero-intercept AVG coefficients.")
    if not all(isfinite(v) for v in (max_temperature, step, ambient_point)):
        raise ValueError("Enter finite Derating parameters.")
    if max_temperature <= 0 or step <= 0 or max_temperature / step > 10000:
        raise ValueError("Use a positive maximum temperature and step, with at most 10,000 intervals.")
    if not 0 <= ambient_point <= max_temperature:
        raise ValueError("The ambient point must be between 0 and the maximum working temperature.")

    def point(ambient: float) -> DeratingPoint:
        basic = calculate_current(coefficients, max_temperature - ambient)
        return DeratingPoint(ambient, basic, .8 * basic)

    # Compute endpoints explicitly so fractional steps cannot overshoot the working limit.
    ambients = [i * step for i in range(int(max_temperature / step) + 1)]
    if ambients[-1] < max_temperature:
        ambients.append(max_temperature)
    points = tuple(point(value) for value in ambients)
    if any(a.basic < b.basic for a, b in zip(points, points[1:])):
        raise ValueError("AVG coefficients must produce a decreasing current as ambient temperature rises.")
    return DeratingAnalysis(points, point(ambient_point), coefficients, max_temperature, step)
