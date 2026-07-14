import { ContactMeasurementSetupWorkspace } from "../features/contact-measurement-plan/ContactMeasurementSetupWorkspace";
import "../contact-measurement-plan.css";

export function ProjectContactMeasurementSetupPage({
  projectId,
  onBackToMatrix,
}: {
  projectId: string;
  onBackToMatrix: () => void;
}) {
  return <ContactMeasurementSetupWorkspace projectId={projectId} onBackToMatrix={onBackToMatrix} />;
}
