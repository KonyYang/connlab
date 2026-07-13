import { ApiRequestError } from "../../api/client";

export function contactMeasurementPlanMessageFor(cause: unknown, fallback: string): string {
  if (cause instanceof ApiRequestError && cause.status === 409) {
    return "Contact measurement plan changed. Reload before continuing.";
  }
  return cause instanceof Error ? cause.message : fallback;
}

export function isStaleContactMeasurementPlanError(
  cause: unknown
): cause is ApiRequestError {
  return cause instanceof ApiRequestError && cause.status === 409;
}
