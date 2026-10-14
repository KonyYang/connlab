import { ApiRequestError, requestJson } from './client';

export class LocalProfileSaveError extends Error {
  constructor(message: string, readonly nameField = false) { super(message); }
}

export function profileSaveError(error: unknown): LocalProfileSaveError {
  if (error instanceof LocalProfileSaveError) return error;
  if (error instanceof ApiRequestError) {
    const detail = error.detail;
    if (error.status === 400 && detail && typeof detail === 'object' && 'field' in detail
      && detail.field === 'display_name' && 'message' in detail && typeof detail.message === 'string') {
      const fieldMessages: Record<string, string> = {
        '请填写项目负责人姓名。': '请填写负责人姓名。',
        '姓名不能包含控制字符或无效字符。': '姓名不能包含控制字符或无效字符。',
        '姓名最多为 80 个字符。': '姓名最多为 80 个字符。',
      };
      if (Object.prototype.hasOwnProperty.call(fieldMessages, detail.message)) {
        return new LocalProfileSaveError(fieldMessages[detail.message], true);
      }
    }
    if (error.status === 403) return new LocalProfileSaveError('保存失败，请刷新页面重试。');
    if (error.status >= 500) return new LocalProfileSaveError('保存失败，请稍后重试。');
    return new LocalProfileSaveError('保存失败，请重试。');
  }
  return new LocalProfileSaveError('服务连接异常，请重试。');
}

export type LocalProfile = { display_name: string };
export type ProfileResponse = { profile: LocalProfile | null };
const path = '/api/local-identity/profile';
export const getLocalProfile = () => requestJson<ProfileResponse>(path, { cache: 'no-store', credentials: 'same-origin' });
export const saveLocalProfile = (displayName: string) => requestJson<ProfileResponse>(path, {
  method: 'PUT', credentials: 'same-origin',
  headers: { 'Content-Type': 'application/json', 'X-ConnLab-Identity': '1' },
  body: JSON.stringify({ display_name: displayName }),
});
