import { useSyncExternalStore } from 'react';
import { getLocalProfile, saveLocalProfile, profileSaveError, type LocalProfile } from './api/localIdentity';

// A display/default setting, not authentication or proof of who performed a test.
export const CURRENT_USER_DISPLAY_NAME = "Lab User";
type ProfileState = { profile: LocalProfile | null; loaded: boolean; busy: boolean; error: string | null };
let state: ProfileState = { profile: null, loaded: false, busy: false, error: null };
let generation = 0;
let refreshing: Promise<void> | null = null;
const listeners = new Set<() => void>();
const publish = (patch: Partial<ProfileState>) => { state = { ...state, ...patch }; listeners.forEach(listener => listener()); };
export function getCurrentUserDisplayName() { return state.profile?.display_name ?? CURRENT_USER_DISPLAY_NAME; }
export function useCurrentProfile() {
  return useSyncExternalStore(listener => { listeners.add(listener); return () => listeners.delete(listener); }, () => state);
}
export function refreshCurrentProfile(): Promise<void> {
  if (state.busy) return Promise.resolve();
  if (refreshing) return refreshing;
  const version = generation;
  refreshing = Promise.resolve().then(getLocalProfile).then(result => {
    if (version === generation) publish({ profile: result.profile, loaded: true, error: null });
  }).catch(() => {
    if (version === generation) publish({ loaded: true, error: '无法读取本机姓名设置，请重试。' });
  }).finally(() => { refreshing = null; });
  return refreshing;
}
export function bootstrapCurrentProfile() { return state.loaded ? Promise.resolve() : refreshCurrentProfile(); }
export async function saveCurrentProfile(displayName: string) {
  if (state.busy) throw new Error('正在保存姓名，请稍候。');
  const version = ++generation;
  publish({ busy: true, error: null });
  try {
    const result = await saveLocalProfile(displayName);
    if (version === generation) publish({ profile: result.profile, loaded: true });
  } catch (error) {
    // Save feedback belongs to the active form; reopening must not replay a completed attempt.
    throw profileSaveError(error);
  } finally { if (version === generation) publish({ busy: false }); }
}
