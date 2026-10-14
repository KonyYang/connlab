import { useSyncExternalStore } from 'react';
import { getIdentitySession, loginIdentity, logoutIdentity, registerIdentity,
  type LocalUser, type LoginInput, type RegisterInput } from './api/localIdentity';

// Compatibility fallback, not an authenticated identity.
export const CURRENT_USER_DISPLAY_NAME = "Lab User";
type IdentityState = { user: LocalUser | null; loaded: boolean; busy: boolean; error: string | null };
let state: IdentityState = { user: null, loaded: false, busy: false, error: null };
let generation = 0;
let refreshing: Promise<void> | null = null;
const listeners = new Set<() => void>();
const publish = (patch: Partial<IdentityState>) => { state = { ...state, ...patch }; listeners.forEach(listener => listener()); };
export function getCurrentUserDisplayName() { return state.user?.display_name ?? CURRENT_USER_DISPLAY_NAME; }
export function useCurrentIdentity() {
  return useSyncExternalStore(listener => { listeners.add(listener); return () => listeners.delete(listener); }, () => state);
}
export function refreshCurrentIdentity(): Promise<void> {
  if (state.busy) return Promise.resolve();
  if (refreshing) return refreshing;
  const version = generation;
  refreshing = getIdentitySession().then(result => {
    if (version === generation) publish({ user: result.user, loaded: true, error: null });
  }).catch(() => {
    if (version === generation) publish({ loaded: true, error: 'Could not check the local login. Try again.' });
  }).finally(() => { refreshing = null; });
  return refreshing;
}
export function bootstrapCurrentIdentity() { return state.loaded ? Promise.resolve() : refreshCurrentIdentity(); }
async function mutate(operation: () => Promise<{ user: LocalUser | null }>) {
  if (state.busy) throw new Error('An account operation is already running.');
  const version = ++generation;
  publish({ busy: true, error: null });
  try {
    const result = await operation();
    if (version === generation) publish({ user: result.user, loaded: true });
  } catch (error) {
    publish({ error: error instanceof Error ? error.message : 'The account operation failed.' });
    throw error;
  } finally { if (version === generation) publish({ busy: false }); }
}
export const registerCurrentIdentity = (input: RegisterInput) => mutate(() => registerIdentity(input));
export const loginCurrentIdentity = (input: LoginInput) => mutate(() => loginIdentity(input));
export const logoutCurrentIdentity = () => mutate(logoutIdentity);
