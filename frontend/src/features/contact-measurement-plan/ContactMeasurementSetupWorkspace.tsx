import { ProjectPointProfileEditor } from "./ProjectPointProfileEditor";
import { useProjectPointProfileModel } from "./useProjectPointProfileModel";

type ContactMeasurementSetupWorkspaceProps = {
  projectId: string;
  onBackToMatrix: () => void;
};

export function ContactMeasurementSetupWorkspace({ projectId, onBackToMatrix }: ContactMeasurementSetupWorkspaceProps) {
  const model = useProjectPointProfileModel({ projectId });

  return <section className="contact-measurement-setup-page" aria-label="Test points setup">
    {model.loading ? <p aria-busy="true">Loading project point profile...</p> : <ProjectPointProfileEditor model={model} onCancel={onBackToMatrix} onConfirmed={onBackToMatrix} />}
  </section>;
}
