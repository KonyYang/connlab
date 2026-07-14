import { useEffect, useRef } from "react";
import { ProjectPointProfileEditor } from "./ProjectPointProfileEditor";
import { useProjectPointProfileModel } from "./useProjectPointProfileModel";

type ContactMeasurementSetupWorkspaceProps = {
  projectId: string;
  onBackToMatrix: () => void;
};

export function ContactMeasurementSetupWorkspace({ projectId, onBackToMatrix }: ContactMeasurementSetupWorkspaceProps) {
  const headingRef = useRef<HTMLHeadingElement>(null);
  const model = useProjectPointProfileModel({ projectId });

  useEffect(() => { if (!model.loading) headingRef.current?.focus(); }, [model.loading]);

  return <section className="contact-measurement-setup-page" aria-label="Project point profile setup">
    <header className="contact-measurement-setup-header">
      <button type="button" onClick={onBackToMatrix}>Back to Matrix</button>
      <div><h1 ref={headingRef} tabIndex={-1}>Contact measurement setup</h1><p>Set project-wide contact categories before any Matrix target mapping.</p></div>
    </header>
    {model.loading ? <p aria-busy="true">Loading project point profile...</p> : <ProjectPointProfileEditor model={model} />}
  </section>;
}
