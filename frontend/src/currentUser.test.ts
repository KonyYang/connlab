import { beforeEach, describe, expect, it, vi } from 'vitest';
vi.mock('./api/localIdentity', () => ({ getIdentitySession: vi.fn(), loginIdentity: vi.fn(), registerIdentity: vi.fn(), logoutIdentity: vi.fn() }));
import * as api from './api/localIdentity';

describe('local current identity', () => {
  beforeEach(() => { vi.resetModules(); vi.resetAllMocks(); });
  it('keeps anonymous identity available when the session adapter fails synchronously', async () => {
    const store = await import('./currentUser');
    vi.mocked(api.getIdentitySession).mockImplementation(() => { throw new Error('Session adapter unavailable'); });
    await expect(store.bootstrapCurrentIdentity()).resolves.toBeUndefined();
    expect(store.getCurrentUserDisplayName()).toBe('Lab User');
    vi.mocked(api.getIdentitySession).mockResolvedValue({ user: { user_id: '1', username: 'alice', display_name: 'Alice' } });
    await store.refreshCurrentIdentity();
    expect(store.getCurrentUserDisplayName()).toBe('Alice');
  });
  it('remembers the public profile but does not let an earlier session read revive a logged-out user', async () => {
    const store = await import('./currentUser');
    const alice = { user_id: '1', username: 'alice', display_name: 'Alice' };
    let complete!: (value: api.IdentitySession) => void;
    vi.mocked(api.getIdentitySession).mockReturnValue(new Promise(resolve => { complete = resolve; }));
    const stale = store.refreshCurrentIdentity();
    vi.mocked(api.loginIdentity).mockResolvedValue({ user: alice });
    await store.loginCurrentIdentity({ username: 'alice', password: 'password 123', remember: true });
    expect(store.getCurrentUserDisplayName()).toBe('Alice');
    vi.mocked(api.logoutIdentity).mockResolvedValue({ user: null });
    await store.logoutCurrentIdentity();
    complete({ user: alice }); await stale;
    expect(store.getCurrentUserDisplayName()).toBe('Lab User');
  });
  it('does not claim logout succeeded when server revocation fails', async () => {
    const store = await import('./currentUser');
    vi.mocked(api.loginIdentity).mockResolvedValue({ user: { user_id: '1', username: 'alice', display_name: 'Alice' } });
    await store.loginCurrentIdentity({ username: 'alice', password: 'password 123', remember: true });
    vi.mocked(api.logoutIdentity).mockRejectedValue(new Error('Cannot revoke session'));
    await expect(store.logoutCurrentIdentity()).rejects.toThrow('Cannot revoke');
    expect(store.getCurrentUserDisplayName()).toBe('Alice');
  });
});
