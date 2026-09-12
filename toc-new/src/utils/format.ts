/**
 * 展示文案格式化工具。
 * 只做纯函数转换，不依赖任何第三方库，也不持有状态。
 */

/**
 * 将后端返回的时间字符串格式化为 "YYYY-MM-DD HH:mm"。
 * 兼容 "2026-09-12T17:05:22" 与 "2026-09-12 17:05:22" 两种写法，无法解析时返回兜底文案。
 */
export function formatDateTime(value: string | null | undefined, fallback = "--"): string {
  if (!value) return fallback;
  // iOS 对 "YYYY-MM-DD HH:mm:ss" 解析不稳定，统一替换为 ISO 的 T 分隔
  const date = new Date(value.replace(" ", "T"));
  if (Number.isNaN(date.getTime())) return fallback;
  const pad = (num: number): string => String(num).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

/** 截止时间专用：后端返回空值代表长期开放 */
export function formatDeadline(value: string | null | undefined): string {
  return value ? formatDateTime(value) : "长期开放";
}

/** 限时文案：后端以分钟为单位，0 或空值代表不限时 */
export function formatTimeLimit(minutes: number | null | undefined): string {
  if (!minutes || minutes <= 0) return "不限时";
  return `${minutes} 分钟`;
}

/** 手机号脱敏，便于在个人名片等公开区域展示 */
export function maskPhone(phone: string | null | undefined): string {
  if (!phone) return "--";
  if (phone.length < 7) return phone;
  return `${phone.slice(0, 3)}****${phone.slice(-4)}`;
}

/** 作答记录状态 → 中文展示文案（后端 TaskRecord.status 枚举） */
export function formatRecordStatus(status: string): string {
  const statusMap: Record<string, string> = {
    pending: "进行中",
    submitted: "已定稿",
    pending_verification: "核验中",
    verified: "已核验",
  };
  return statusMap[status] ?? "状态未知";
}

/** 租户角色 → 中文展示文案，禁止直接暴露英文枚举 */
export function formatRole(role: string | null | undefined): string {
  const roleMap: Record<string, string> = {
    owner: "企业负责人",
    admin: "企业管理员",
    member: "学员",
  };
  return roleMap[role ?? ""] ?? "成员";
}
