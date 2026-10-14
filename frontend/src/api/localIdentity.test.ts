import { expect, it, vi } from 'vitest';
import { getLocalProfile, saveLocalProfile } from './localIdentity';
it('reads and saves only the local display profile without authentication or cookies in JSON', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async () => new Response('{"profile":null}', { headers: { 'Content-Type': 'application/json' } }));
  await saveLocalProfile('张三');
  expect(fetchMock).toHaveBeenLastCalledWith('/api/local-identity/profile', expect.objectContaining({ credentials: 'same-origin',
    headers: expect.objectContaining({ 'X-ConnLab-Identity': '1' }), method: 'PUT', body: '{"display_name":"张三"}' }));
  await getLocalProfile();
  expect(fetchMock).toHaveBeenLastCalledWith('/api/local-identity/profile', expect.objectContaining({ cache: 'no-store' }));
  fetchMock.mockRestore();
});
