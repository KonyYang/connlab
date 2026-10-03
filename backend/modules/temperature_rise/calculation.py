"""Pure full-precision temperature rise and current calculations (no Office I/O)."""
from dataclasses import dataclass
from math import copysign, fsum, isfinite, sqrt


@dataclass(frozen=True)
class Curve:
    a: float
    b: float
    c: float
    r_squared: float

    def evaluate(self, current: float) -> float:
        return (self.a * current + self.b) * current + self.c


def number(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label}: enter a finite number.")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}: enter a finite number.") from exc
    if not isfinite(result):
        raise ValueError(f"{label}: enter a finite number.")
    return result


def summarize(ambient: float, channels: list[tuple[str, str, float]]) -> dict:
    if not channels:
        raise ValueError("Map at least one sample temperature channel.")
    rises = [(sample, point, number(value, point) - number(ambient, "Ambient"))
             for sample, point, value in channels]
    maxima = {}
    for sample, _, rise in rises:
        maxima[sample] = max(maxima.get(sample, rise), rise)
    return {"rises": rises, "single_max": maxima, "maximum": max(maxima.values()),
            "average_of_max": fsum(maxima.values()) / len(maxima)}


def stage_endpoints(currents: list[float]) -> list[int]:
    """Last row of each contiguous 1% current range; this does not assess thermal stability."""
    if not currents:
        return []
    result = []
    low = high = number(currents[0], "Current")
    for index, value in enumerate(currents[1:], 1):
        value = number(value, "Current")
        next_low, next_high = min(low, value), max(high, value)
        if next_high - next_low > 0.01 * max(abs(low), abs(high), 1e-12):
            result.append(index - 1)
            low = high = value
        else:
            low, high = next_low, next_high
    return result + [len(currents) - 1]


def fit_curve(currents: list[float], rises: list[float], *, zero_intercept: bool = True,
              include_origin: bool = False) -> Curve:
    x = [number(value, "Current") for value in currents]
    y = [number(value, "Temperature rise") for value in rises]
    size = 2 if zero_intercept else 3
    if len(x) != len(y) or len(set(x)) < size:
        raise ValueError(f"Fit requires at least {size} distinct measured current levels.")
    if any(value < 0 for value in x):
        raise ValueError("Current must be non-negative.")
    scale = max(x)
    if scale == 0:
        raise ValueError("Fit is degenerate: no positive measured current.")
    rows = [[(value / scale) ** 2, value / scale] + ([] if zero_intercept else [1.0]) for value in x]
    # Normal equations are scaled and pivoted; rank is explicitly checked.
    matrix = [[fsum(row[i] * row[j] for row in rows) for j in range(size)] +
              [fsum(row[i] * value for row, value in zip(rows, y))] for i in range(size)]
    tolerance = max(abs(value) for row in matrix for value in row[:size]) * 1e-12
    for column in range(size):
        pivot = max(range(column, size), key=lambda index: abs(matrix[index][column]))
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        if abs(matrix[column][column]) <= tolerance:
            raise ValueError("Fit is degenerate; select separated positive current levels.")
        divisor = matrix[column][column]
        matrix[column] = [value / divisor for value in matrix[column]]
        for index in range(size):
            if index != column:
                factor = matrix[index][column]
                matrix[index] = [value - factor * other for value, other in zip(matrix[index], matrix[column])]
    a, b = matrix[0][-1] / scale ** 2, matrix[1][-1] / scale
    c = 0.0 if zero_intercept else matrix[2][-1]
    # Origin is non-measured display data. Including it changes centered R² only,
    # never the regression observations or the explicit intercept constraint.
    metric_x = x + ([0.0] if include_origin else [])
    metric_y = y + ([0.0] if include_origin else [])
    mean = fsum(metric_y) / len(metric_y)
    total = fsum((value - mean) ** 2 for value in metric_y)
    if total <= 1e-20:
        raise ValueError("Fit is degenerate: temperature rise has no variation.")
    error = fsum((value - ((a * current + b) * current + c)) ** 2 for current, value in zip(metric_x, metric_y))
    return Curve(a, b, c, 1 - error / total)


def inverse_current(curve: Curve, rise: float) -> float:
    target = number(rise, "Target temperature rise")
    if target < 0:
        raise ValueError("Allowable temperature rise must be non-negative.")
    if target == 0 and curve.c == 0:
        # Preserve the explicit zero-intercept boundary even when the fitted
        # linear term is negative and another positive root also exists.
        return 0.0
    a, b, d = curve.a, curve.b, curve.c - target
    if a == 0:
        roots = [-d / b] if b != 0 else []
    else:
        discriminant = b * b - 4 * a * d
        if discriminant < 0:
            roots = []
        else:
            q = -0.5 * (b + copysign(sqrt(discriminant), b))
            roots = [q / a, d / q] if q else [-b / (2 * a)]
    valid = sorted(value for value in roots if isfinite(value) and value >= 0 and 2 * a * value + b >= 0)
    if not valid:
        raise ValueError("Curve has no non-negative current on its increasing branch for this temperature rise.")
    return valid[0]
