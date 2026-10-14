import { requestJson } from './client';

export type LocalProfile = { display_name: string };
export type ProfileResponse = { profile: LocalProfile | null };
const path = '/api/local-identity/profile';
export const getLocalProfile = () => requestJson<ProfileResponse>(path, { cache: 'no-store', credentials: 'same-origin' });
export const saveLocalProfile = (displayName: string) => requestJson<ProfileResponse>(path, {
  method: 'PUT', credentials: 'same-origin',
  headers: { 'Content-Type': 'application/json', 'X-ConnLab-Identity': '1' },
  body: JSON.stringify({ display_name: displayName }),
});
