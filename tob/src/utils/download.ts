/**
 * 试卷 Word 导出下载（B端共用）：试卷管理行级导出 + AI 助手 exam_card 下载卡共用。
 * 后端：GET /api/v1/admin/tasks/{id}/export（标准试卷排版 .docx，异常降级 .txt）。
 */
import { ElMessage } from 'element-plus';

const getApiBase = (): string => {
  if ((import.meta as any).env?.VITE_API_BASE_URL) {
    return (import.meta as any).env.VITE_API_BASE_URL;
  }
  return '/api';
};

const pickFileName = (disposition: string, fallback: string): string => {
  if (disposition) {
    const star = disposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (star && star[1]) {
      try {
        return decodeURIComponent(star[1]);
      } catch (e) { /* 保留默认 */ }
    }
    const plain = disposition.match(/filename="?([^";]+)"?/i);
    if (plain && plain[1]) return plain[1];
  }
  return fallback;
};

export const downloadTaskExport = async (examId: string | number, title?: string): Promise<void> => {
  if (!examId) throw new Error('该试卷缺少编号，无法下载');
  const token = localStorage.getItem('tiku_tob_token') || '';
  const headers: Record<string, string> = { Authorization: `Bearer ${token}` };
  const tenantId = localStorage.getItem('tiku_tob_tenant') || '';
  if (tenantId) headers['X-Tenant-ID'] = tenantId;
  const res = await fetch(`${getApiBase()}/v1/admin/tasks/${examId}/export`, { headers });
  if (!res.ok) throw new Error('下载失败');
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = pickFileName(res.headers.get('Content-Disposition') || '', `${title || '试卷'}.docx`);
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
  ElMessage.success(`《${title || '试卷'}》已成功下载`);
};
