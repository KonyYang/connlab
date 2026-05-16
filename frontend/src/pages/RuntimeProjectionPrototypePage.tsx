import type { ReactElement } from "react";
import { RuntimeProjectionPrototypeView } from "../features/runtime-projection-read-only/RuntimeProjectionPrototypeView";
import "../runtime-projection-prototype.css";

export function RuntimeProjectionPrototypePage(): ReactElement {
  return <RuntimeProjectionPrototypeView />;
}
