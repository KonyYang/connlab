import { useEffect, useRef, useState, type FormEvent } from 'react';
import { saveCurrentProfile, useCurrentProfile } from '../../currentUser';
import { profileSaveError } from '../../api/localIdentity';
import './localIdentity.css';

function nameIssue(value: string): string | null {
  if (!value.trim()) return '请填写负责人姓名。';
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
  const [dismissedProfileError, setDismissedProfileError] = useState<string | null>(null);
  const busy = profile.busy || locked;
  const errorMessage = fieldError || saveError || (profile.error !== dismissedProfileError ? profile.error : null);
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
    catch (error) {
      const failure = profileSaveError(error);
      if (failure.nameField) { setFieldError(failure.message); input.current?.focus(); }
      else setSaveError(failure.message);
    }
  }
  return <dialog ref={dialog} className="local-identity-dialog" aria-labelledby="local-profile-title"
    onCancel={event => { event.preventDefault(); if (!busy) onClose(); }}>
    <form noValidate onSubmit={event => void submit(event)}>
      <header><h2 id="local-profile-title">负责人姓名</h2>
        <button type="button" aria-label="关闭姓名设置" disabled={busy} onClick={onClose}>×</button></header>
      <input ref={input} autoFocus autoComplete="name" value={name} disabled={busy} aria-labelledby="local-profile-title"
        aria-invalid={Boolean(fieldError)} aria-describedby={fieldError ? 'local-profile-name-error local-profile-help' : 'local-profile-help'}
        onChange={event => {
          touched.current = true; setName(event.target.value); setSaveError(null); setDismissedProfileError(profile.error);
          if (fieldError) setFieldError(nameIssue(event.target.value));
        }} />
      {errorMessage && <p id="local-profile-name-error" role="alert">{errorMessage}</p>}
      <p id="local-profile-help">用于新项目和报告的默认姓名。</p>
      <footer><button type="button" disabled={busy} onClick={onClose}>取消</button>
        <button type="submit" className="primary-action" disabled={busy}>{busy ? '保存中…' : '保存'}</button></footer>
    </form>
  </dialog>;
}
