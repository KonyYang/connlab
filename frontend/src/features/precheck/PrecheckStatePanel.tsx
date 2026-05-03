import type { ReactElement } from "react";

export function PrecheckStatePanel({
  title,
  text,
  tone
}: {
  title: string;
  text: string;
  tone?: "danger";
}): ReactElement {
  return <div className={tone === "danger" ? "precheck-card precheck-state precheck-state-danger" : "precheck-card precheck-state"}><h3>{title}</h3><p>{text}</p></div>;
}
