// Decimal arithmetic for the fee form, matching Python Decimal ROUND_HALF_UP.
// Keep raw hours until the final display/money boundary; never multiply a label.
type DecimalValue = { units: bigint; scale: number };

function parse(value: string): DecimalValue {
  const text = value.trim().replace(/[$,\s]/g, "");
  const match = /^([+-]?)(\d*)(?:\.(\d*))?(?:e([+-]?\d+))?$/i.exec(text);
  if (!match || !(match[2] || match[3]) || !Number.isFinite(Number(text))) throw new Error("Invalid fee number");
  const exponent = Number(match[4] || "0");
  let scale = (match[3] || "").length - exponent;
  if (Math.abs(scale) > 100 || text.length > 100) throw new Error("Fee number is too large");
  let units = BigInt((match[1] === "-" ? "-" : "") + (match[2] || "0") + (match[3] || ""));
  if (scale < 0) { units *= 10n ** BigInt(-scale); scale = 0; }
  return { units, scale };
}

function add(a: DecimalValue, b: DecimalValue): DecimalValue {
  const scale = Math.max(a.scale, b.scale);
  return {units: a.units * 10n ** BigInt(scale-a.scale) + b.units * 10n ** BigInt(scale-b.scale), scale};
}

function multiply(a: DecimalValue, b: DecimalValue): DecimalValue {
  return {units: a.units * b.units, scale: a.scale + b.scale};
}

function format(value: DecimalValue, places?: number): string {
  const scale = places ?? value.scale;
  let units = value.units;
  if (value.scale > scale) {
    const divisor = 10n ** BigInt(value.scale - scale);
    const sign = units < 0n ? -1n : 1n;
    units = sign * ((sign * units + divisor / 2n) / divisor);
  } else units *= 10n ** BigInt(scale - value.scale);
  const sign = units < 0n ? "-" : "";
  const digits = (units < 0n ? -units : units).toString().padStart(scale + 1, "0");
  const text = sign + (scale ? `${digits.slice(0, -scale)}.${digits.slice(-scale)}` : digits);
  return places === undefined && scale ? text.replace(/\.?0+$/, "") : text;
}

function display(calculate: () => DecimalValue, places?: number): string {
  try { return format(calculate(), places); } catch { return "Pending"; }
}

export function feeDecimalSum(values: string[], places?: number): string {
  return display(() => values.reduce((sum, value) => add(sum, parse(value)), parse("0")), places);
}

export function feeDecimalProduct(left: string, right: string, places: number): string {
  return display(() => multiply(parse(left), parse(right)), places);
}

export function feeRowAmount(price: string, units: string, base: string, discount: string): string {
  return display(() => {
    const reduction = parse(discount.replace(/%/g, "") || "0");
    const factor = add(parse("1"), {units: -reduction.units, scale: reduction.scale + 2});
    return add(multiply(multiply(parse(price), parse(units)), factor), parse(base || "0"));
  }, 0);
}
