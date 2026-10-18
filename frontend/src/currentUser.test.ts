import { beforeEach, describe, expect, it, vi } from 'vitest';
vi.mock('./api/localIdentity', async original => ({ ...await original<typeof import('./api/localIdentity')>(),
  getLocalProfile: vi.fn(), saveLocalProfile: vi.fn() }));
import * as api from './api/localIdentity';
import { ApiRequestError } from './api/client';
import { act, renderHook } from '@testing-library/react';

describe('local current profile', () => {
  beforeEach(() => { vi.resetModules(); vi.resetAllMocks(); });
  it('returns concise safe save guidance without persisting a completed form error in shared state', async () => {
    const store = await import('./currentUser');
    vi.mocked(api.saveLocalProfile).mockRejectedValue(new ApiRequestError('Raw origin header /api/local-identity/profile D:/private traceback', 403, null));
    const view = renderHook(() => store.useCurrentProfile());
    await act(async () => {
      await expect(store.saveCurrentProfile('Alice')).rejects.toThrow('Could not save. Refresh the page and retry.');
    });
    expect(view.result.current.error).toBeNull();
  });
  it('keeps fallback available when the profile adapter fails synchronously and can recover', async () => {
    const store = await import('./currentUser');
    vi.mocked(api.getLocalProfile).mockImplementation(() => { throw new Error('Unavailable'); });
    await expect(store.bootstrapCurrentProfile()).resolves.toBeUndefined();
    expect(store.getCurrentUserDisplayName()).toBe('Lab User');
    vi.mocked(api.getLocalProfile).mockResolvedValue({ profile: { display_name: '张三' } });
    await store.refreshCurrentProfile();
    expect(store.getCurrentUserDisplayName()).toBe('张三');
  });
  it('does not let a stale profile read overwrite a newly saved name', async () => {
    const store = await import('./currentUser');
    let complete!: (value: api.ProfileResponse) => void;
    vi.mocked(api.getLocalProfile).mockReturnValue(new Promise(resolve => { complete = resolve; }));
    const stale = store.refreshCurrentProfile();
    vi.mocked(api.saveLocalProfile).mockResolvedValue({ profile: { display_name: '张三' } });
    await store.saveCurrentProfile('张三');
    complete({ profile: { display_name: 'Old name' } }); await stale;
    expect(store.getCurrentUserDisplayName()).toBe('张三');
  });
  it('retains the old profile after a failed save and permits retry', async () => {
    const store = await import('./currentUser');
    vi.mocked(api.saveLocalProfile).mockResolvedValue({ profile: { display_name: 'Alice' } });
    await store.saveCurrentProfile('Alice');
    vi.mocked(api.saveLocalProfile).mockRejectedValue(new Error('Storage unavailable'));
    await expect(store.saveCurrentProfile('Bob')).rejects.toThrow('Could not connect. Please retry.');
    expect(store.getCurrentUserDisplayName()).toBe('Alice');
    vi.mocked(api.saveLocalProfile).mockResolvedValue({ profile: { display_name: 'Bob' } });
    await store.saveCurrentProfile('Bob');
    expect(store.getCurrentUserDisplayName()).toBe('Bob');
  });
});
