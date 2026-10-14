import { expect, it, vi } from 'vitest';
import { getLocalProfile, saveLocalProfile, profileSaveError } from './localIdentity';
import { ApiRequestError } from './client';
it('reads and saves only the local display profile without authentication or cookies in JSON', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async () => new Response('{"profile":null}', { headers: { 'Content-Type': 'application/json' } }));
  await saveLocalProfile('张三');
  expect(fetchMock).toHaveBeenLastCalledWith('/api/local-identity/profile', expect.objectContaining({ credentials: 'same-origin',
    headers: expect.objectContaining({ 'X-ConnLab-Identity': '1' }), method: 'PUT', body: '{"display_name":"张三"}' }));
  await getLocalProfile();
  expect(fetchMock).toHaveBeenLastCalledWith('/api/local-identity/profile', expect.objectContaining({ cache: 'no-store' }));
  fetchMock.mockRestore();
});
it.each([
  [403, '保存失败，请刷新页面重试。'], [500, '保存失败，请稍后重试。'], [422, '保存失败，请重试。'],
])('maps status %s to bounded guidance rather than transport details', (status, message) => {
  expect(profileSaveError(new ApiRequestError('Private path /api trace', status as number, null)).message).toBe(message);
});
it('accepts only recognized name-field reasons and gives an honest network retry message', () => {
  const valid = profileSaveError(new ApiRequestError('raw', 400, { field: 'display_name', message: '姓名最多为 80 个字符。' }));
  expect(valid.message).toBe('姓名最多为 80 个字符。'); expect(valid.nameField).toBe(true);
  const untrusted = profileSaveError(new ApiRequestError('raw', 400, { field: 'display_name', message: '/api private traceback' }));
  expect(untrusted.message).toBe('保存失败，请重试。'); expect(untrusted.nameField).toBe(false);
  expect(profileSaveError(new TypeError('Failed to fetch: private details')).message).toBe('服务连接异常，请重试。');
});
