import { expect, it, vi } from 'vitest';
import { getIdentitySession, registerIdentity, logoutIdentity } from './localIdentity';
it('sends credentials only through bounded same-origin JSON requests', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async () => new Response('{"user":null}', { headers: { 'Content-Type': 'application/json' } }));
  await registerIdentity({ username: 'alice', display_name: 'Alice', password: 'password 123', remember: true });
  expect(fetchMock).toHaveBeenLastCalledWith('/api/local-identity/register', expect.objectContaining({ credentials: 'same-origin',
    headers: expect.objectContaining({ 'X-ConnLab-Identity': '1' }), method: 'POST' }));
  await getIdentitySession();
  expect(fetchMock).toHaveBeenLastCalledWith('/api/local-identity/session', expect.objectContaining({ cache: 'no-store' }));
  await logoutIdentity();
  expect(fetchMock).toHaveBeenLastCalledWith('/api/local-identity/logout', expect.objectContaining({ body: '{}' }));
  fetchMock.mockRestore();
});
