import { CURRENT_USER_DISPLAY_NAME } from "../../currentUser";

export const DEFAULT_BASIC_INFORMATION_CONFIRMED_BY = CURRENT_USER_DISPLAY_NAME;

export function getBasicInformationConfirmedBy(): string {
  return DEFAULT_BASIC_INFORMATION_CONFIRMED_BY;
}
