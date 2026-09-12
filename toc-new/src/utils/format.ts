/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 新增 parseServerTime：兼容后端带 6 位微秒的 ISO 时间串，统一截断到毫秒后再解析; 2. formatDateTime 改为复用该函数，消除重复的兼容逻辑]
 */

/**
 * 展示文案格式化工具。
 * 只做纯函数转换，不依赖任何第三方库，也不持有状态。
 */

/**
 * 解析服务端时间串为毫秒时间戳，无法解析时返回 0。
 * 后端 datetime.isoformat() 会输出形如 "2026-09-12T17:05:22.000000" 的 6 位微秒串，
 * 部分运行环境（iOS WebView / 旧版内核）对超过 3 位的小数秒解析不稳定，故统一截断到毫秒。
 * 用于倒计时差值计算时，started_at 与 server_now 同源同格式，其差值与时区解释无关，结果依然准确。
 */
export function parseServerTime(value: string | null | undefined): number {
  if (!value) return 0;
  // 空格分隔统一替换为 ISO 的 T 分隔
  const normalized = value.trim().replace(" ", "T").replace(/(\.\d{3})\d+/, "$1");
  const timestamp = new Date(normalized).getTime();
  return Number.isNaN(timestamp) ? 0 : timestamp;
}

/**
 * 将后端返回的时间字符串格式化为 "YYYY-MM-DD HH:mm"。
 * 兼容 "2026-09-12T17:05:22"、"2026-09-12 17:05:22" 与带微秒的三种写法，无法解析时返回兜底文案。
 */
export function formatDateTime(value: string | null | undefined, fallback = "--"): string {
  const timestamp = parseServerTime(value);
  if (!timestamp) return fallback;
  const date = new Date(timestamp);
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

/** 将剩余秒数格式化为 "mm:ss" 或 "hh:mm:ss" */
export function formatDuration(totalSeconds: number): string {
  if (totalSeconds <= 0) return "00:00";
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const pad = (n: number) => String(n).padStart(2, "0");
  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  }
  return `${pad(minutes)}:${pad(seconds)}`;
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
