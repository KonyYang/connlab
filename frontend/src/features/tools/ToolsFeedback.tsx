import { createContext, useContext, type ReactNode } from "react";
import { createPortal } from "react-dom";

export const ToolsFeedbackTarget = createContext<HTMLElement | null>(null);

/** Keep each tool's state local while its feedback follows every action in DOM order. */
export function ToolsFeedback({ children }: { children: ReactNode }) {
  const target = useContext(ToolsFeedbackTarget);
  return target ? createPortal(children, target) : <>{children}</>;
}
