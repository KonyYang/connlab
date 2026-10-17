import { expect, it } from 'vitest';
import { formatCurrent } from './currentPrecision';

it.each([
  [0.4123, 0, '0'], [0.5, 0, '1'], [0.04, 1, '0.0'], [0.05, 1, '0.1'],
  [0.15, 1, '0.2'], [0.0087, 2, '0.01'], [1.005, 2, '1.01'], [-0.04, 1, '0.0'],
])('formats %s A at %s places with decimal half-up rounding', (value, decimals, expected) => {
  expect(formatCurrent(value as number, decimals as number)).toBe(expected);
});
