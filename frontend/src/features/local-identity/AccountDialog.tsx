import { useEffect, useRef, useState, type FormEvent } from 'react';
import { saveCurrentProfile, useCurrentProfile } from '../../currentUser';
import './localIdentity.css';

function nameIssue(value: string): string | null {
  if (!value.trim()) return '请填写项目负责人姓名。';
  if (/[\u0000-\u001f\u007f\ud800-\udfff]/u.test(value)) return '姓名不能包含控制字符或无效字符。';
  if (Array.from(value.trim()).length > 80) return '姓名最多为 80 个字符。';
  return null;
}

export function AccountDialog({ onClose, locked = false, returnFocus }: {
  onClose: () => void; locked?: boolean; returnFocus?: HTMLElement | null;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const input = useRef<HTMLInputElement>(null);
  const profile = useCurrentProfile();
  const touched = useRef(false);
  const [name, setName] = useState(profile.profile?.display_name ?? '');
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const busy = profile.busy || locked;
  useEffect(() => {
    if (!touched.current) setName(profile.profile?.display_name ?? '');
  }, [profile.profile]);
  useEffect(() => {
    const node = dialog.current;
    const previous = document.activeElement as HTMLElement | null;
    node?.showModal();
    return () => { node?.close(); (returnFocus?.isConnected ? returnFocus : previous)?.focus(); };
  }, [returnFocus]);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    const issue = nameIssue(name);
    setFieldError(issue); setSaveError(null);
    if (issue) { input.current?.focus(); return; }
    try { await saveCurrentProfile(name.trim()); onClose(); }
    catch { setSaveError('无法确认保存结果，请重试。'); }
  }
  return <dialog ref={dialog} className="local-identity-dialog" aria-labelledby="local-profile-title"
    onCancel={event => { event.preventDefault(); if (!busy) onClose(); }}>
    <form noValidate onSubmit={event => void submit(event)}>
      <header><h2 id="local-profile-title">Project Leader Name</h2>
        <button type="button" aria-label="Close account dialog" disabled={busy} onClick={onClose}>×</button></header>
      <label>Display Project Leader Name<input ref={input} autoFocus autoComplete="name" value={name} disabled={busy}
        aria-invalid={Boolean(fieldError)} aria-describedby={fieldError ? 'local-profile-name-error local-profile-help' : 'local-profile-help'}
        onChange={event => {
          touched.current = true; setName(event.target.value); setSaveError(null);
          if (fieldError) setFieldError(nameIssue(event.target.value));
        }} /></label>
      {fieldError && <p id="local-profile-name-error" role="alert">{fieldError}</p>}
      <p id="local-profile-help">自动用于新项目和新报告，已有内容不会被覆盖。保存在本机，无需登录。</p>
      {(saveError || profile.error) && <p role="alert">{saveError || profile.error}</p>}
      <footer><button type="button" disabled={busy} onClick={onClose}>Cancel</button>
        <button type="submit" className="primary-action" disabled={busy}>{busy ? 'Saving…' : 'Save'}</button></footer>
    </form>
  </dialog>;
}
