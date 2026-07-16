import type { ProjectPointProfileModel } from "./projectPointProfileModelTypes";

type ProjectPointProfileEditorProps = {
  model: ProjectPointProfileModel;
  onCancel: () => void;
  onConfirmed: () => void;
};

export function ProjectPointProfileEditor({ model, onCancel, onConfirmed }: ProjectPointProfileEditorProps) {
  return <section className="project-point-profile-editor" aria-label="LLCR test point confirmation">
    <div className="project-point-profile-card">
      <header className="project-point-profile-header"><div><h2>LLCR Test Point Confirmation</h2><p>{`${model.total} points / sample`}</p></div></header>
      {model.error ? <p className="contact-measurement-setup-alert is-error" role="alert">{model.error}</p> : null}
      <table className="project-point-profile-table"><thead><tr><th scope="col">Prefix</th><th scope="col">Test points</th><th scope="col" className="project-point-profile-action"><button className="contact-measurement-button is-compact" type="button" disabled={model.busy || model.rows.length >= 256} onClick={model.addCategory}>Add row</button></th></tr></thead>
        <tbody>{model.rows.map((row, index) => <tr key={row.category_id ?? `new-${index}`}><td><label className="sr-only" htmlFor={`point-prefix-${index}`}>Prefix {index + 1}</label><textarea rows={1} id={`point-prefix-${index}`} value={row.prefix} disabled={model.busy} onChange={(event) => model.updateRow(index, { prefix: event.target.value })} /></td><td><label className="sr-only" htmlFor={`point-expression-${index}`}>Test points {index + 1}</label><textarea rows={1} id={`point-expression-${index}`} value={row.point_expression} disabled={model.busy} onChange={(event) => model.updateRow(index, { point_expression: event.target.value })} /></td><td className="project-point-profile-action"><button className="contact-measurement-button is-compact project-point-profile-delete" type="button" title="Delete row" aria-label={`Delete point profile row ${row.prefix || index + 1}`} disabled={model.busy} onClick={() => model.removeCategory(index)} onKeyDown={(event) => {
        if (!model.busy && (event.key === "Enter" || event.key === " ")) {
          event.preventDefault();
          model.removeCategory(index);
        }
        }}><span aria-hidden="true">🗑</span></button></td></tr>)}</tbody>
      </table>
    </div>
    <footer className="contact-measurement-setup-actions"><button className="contact-measurement-button is-secondary" type="button" disabled={model.busy} onClick={onCancel}>Cancel</button><button className="contact-measurement-button is-primary" type="button" disabled={model.busy || Boolean(model.validation)} onClick={() => void model.confirm().then((confirmed) => { if (confirmed) onConfirmed(); })}>Confirm point profile</button></footer>
  </section>;
}
