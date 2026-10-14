import { useEffect, useRef, useState, type FormEvent } from 'react';
import { loginCurrentIdentity, registerCurrentIdentity, useCurrentIdentity } from '../../currentUser';
import './localIdentity.css';

export function AccountDialog({ onClose, locked = false }: { onClose: () => void; locked?: boolean }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const identity = useCurrentIdentity();
  const [registering, setRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const busy = identity.busy || locked;
  useEffect(() => {
    const node = dialog.current;
    const previous = document.activeElement as HTMLElement | null;
    node?.showModal();
    return () => { node?.close(); previous?.focus(); };
  }, []);
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    if (registering && password !== confirmation) { setError('Passwords do not match.'); return; }
    setError(null);
    try {
      const input = { username, password, remember };
      if (registering) await registerCurrentIdentity({ ...input, display_name: name });
      else await loginCurrentIdentity(input);
      setPassword(''); setConfirmation(''); onClose();
    } catch (failure) { setError(failure instanceof Error ? failure.message : 'Could not sign in.'); }
  }
  return <dialog ref={dialog} className="local-identity-dialog" aria-labelledby="local-identity-title"
    onCancel={event => { event.preventDefault(); if (!busy) onClose(); }}>
    <form onSubmit={event => void submit(event)}>
      <header><h2 id="local-identity-title">{registering ? 'Create local account' : 'Sign in'}</h2>
        <button type="button" aria-label="Close account dialog" disabled={busy} onClick={onClose}>×</button></header>
      <p>Accounts are stored on this computer. No cloud account is required.</p>
      <label>Username<input autoFocus required minLength={3} maxLength={64} pattern="[A-Za-z0-9_.\-]+"
        autoComplete="username" value={username} disabled={busy} onChange={event => setUsername(event.target.value)} /></label>
      {registering && <label>Display name<input required maxLength={80} autoComplete="name" value={name}
        disabled={busy} onChange={event => setName(event.target.value)} /></label>}
      <label>Password<input type="password" required minLength={10} maxLength={128}
        autoComplete={registering ? 'new-password' : 'current-password'} value={password} disabled={busy}
        onChange={event => setPassword(event.target.value)} /></label>
      {registering && <label>Confirm password<input type="password" required minLength={10} maxLength={128}
        autoComplete="new-password" value={confirmation} disabled={busy} onChange={event => setConfirmation(event.target.value)} /></label>}
      <label className="local-identity-remember"><input type="checkbox" checked={remember} disabled={busy}
        onChange={event => setRemember(event.target.checked)} />Remember login on this computer (30 days)</label>
      {error && <p role="alert">{error}</p>}
      <footer><button type="button" disabled={busy} onClick={() => {
        setRegistering(value => !value); setError(null); setPassword(''); setConfirmation('');
      }}>{registering ? 'Already registered? Sign in' : 'Create an account'}</button>
        <button type="submit" className="primary-action" disabled={busy}>{busy ? 'Please wait…' : registering ? 'Register and sign in' : 'Sign in'}</button></footer>
    </form>
  </dialog>;
}
