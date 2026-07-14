import type { ProjectPointProfileModel } from "./projectPointProfileModelTypes";

type ProjectPointProfileEditorProps = {
  model: ProjectPointProfileModel;
};

export function ProjectPointProfileEditor({ model }: ProjectPointProfileEditorProps) {
  const disabled = model.busy !== null;
  return <section className="project-point-profile-editor" aria-label="Project point profile">
    <header className="project-point-profile-header">
      <div><h2>Project point profile</h2><p>{`${model.total} points / sample`}</p></div>
      {model.workspace?.has_unconfirmed_draft ? <span role="status">Draft changes are not confirmed.</span> : null}
    </header>
    {model.error ? <p className="contact-measurement-setup-alert is-error" role="alert">{model.error}</p> : null}
    {model.message ? <p className="contact-measurement-setup-alert" role="status">{model.message}</p> : null}
    <div className="project-point-profile-rows">
      {model.rows.map((row, index) => <div className="project-point-profile-row" key={row.category_id ?? `new-${index}`}>
        <label><input type="checkbox" checked={row.included} disabled={disabled} onChange={(event) => model.updateRow(index, { included: event.target.checked })} /> Use</label>
        <label>Category<input value={row.label} disabled={disabled} onChange={(event) => model.updateRow(index, { label: event.target.value })} /></label>
        <label>Count per sample<input type="number" min="0" step="1" value={row.count_per_sample} disabled={disabled} onChange={(event) => model.updateRow(index, { count_per_sample: event.target.value })} /></label>
        <details className="project-point-profile-prefix"><summary>More</summary><label>Prefix<input value={row.record_prefix} disabled={disabled} onChange={(event) => model.updateRow(index, { record_prefix: event.target.value })} /></label></details>
        <div><button type="button" disabled={disabled || index === 0} onClick={() => model.moveCategory(index, -1)}>Up</button><button type="button" disabled={disabled || index === model.rows.length - 1} onClick={() => model.moveCategory(index, 1)}>Down</button><button type="button" disabled={disabled} onClick={() => model.removeCategory(index)}>Remove</button></div>
      </div>)}
    </div>
    <div className="contact-measurement-setup-actions">
      <button type="button" disabled={disabled} onClick={model.addCategory}>Add category</button>
      <button type="button" disabled={disabled} onClick={() => model.addTemplate("high_power")}>High Power template</button>
      <button type="button" disabled={disabled} onClick={() => model.addTemplate("low_power")}>Low Power template</button>
      <button type="button" disabled={disabled} onClick={() => model.addTemplate("signal")}>Signal template</button>
      <button type="button" disabled={disabled} onClick={model.discard}>Discard changes</button>
      <button type="button" disabled={disabled || Boolean(model.validation)} onClick={() => void model.saveDraft()}>Save draft</button>
      <button type="button" disabled={disabled || Boolean(model.validation) || model.total <= 0} onClick={() => void model.confirm()}>Confirm point profile</button>
    </div>
  </section>;
}
