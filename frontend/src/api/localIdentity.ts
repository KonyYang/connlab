import { requestJson } from './client';

export type LocalUser = { user_id: string; username: string; display_name: string };
export type IdentitySession = { user: LocalUser | null };
export type LoginInput = { username: string; password: string; remember: boolean };
export type RegisterInput = LoginInput & { display_name: string };
const base = '/api/local-identity';
const mutation = (body: unknown): RequestInit => ({ method: 'POST', credentials: 'same-origin',
  headers: { 'Content-Type': 'application/json', 'X-ConnLab-Identity': '1' }, body: JSON.stringify(body) });
export const getIdentitySession = () => requestJson<IdentitySession>(`${base}/session`, { cache: 'no-store', credentials: 'same-origin' });
export const registerIdentity = (input: RegisterInput) => requestJson<IdentitySession>(`${base}/register`, mutation(input));
export const loginIdentity = (input: LoginInput) => requestJson<IdentitySession>(`${base}/login`, mutation(input));
export const logoutIdentity = () => requestJson<IdentitySession>(`${base}/logout`, mutation({}));
