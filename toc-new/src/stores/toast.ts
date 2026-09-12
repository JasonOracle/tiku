/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 提示负载新增触发页路由，解决页面栈中多个挂载点共用同一状态时后台页面抢先消费提示、导致当前页面看不到反馈的缺陷]
 */
import { defineStore } from "pinia";

/** 轻提示类型，与 wot-design-uni Toast 实例上的可用方法一一对应 */
export type ToastType = "show" | "success" | "error" | "warning" | "info" | "loading";

/** 轻提示垂直位置 */
export type ToastPosition = "top" | "middle-top" | "middle" | "bottom";

export interface ToastPayload {
  type: ToastType;
  msg: string;
  /** 持续时间（毫秒），0 表示常驻不自动关闭 */
  duration?: number;
  position?: ToastPosition;
  /** 触发时刻，仅用于排查提示时序问题 */
  triggeredAt: number;
  /**
   * 触发时所在的页面路由。
   * 页面栈里可能同时存在多个挂载了 GlobalToast 的页面（如首页 navigateTo 到考场后首页仍在栈中），
   * 若不做区分，后台页面的实例会抢先消费提示，导致用户在当前页面根本看不到反馈。
   */
  page: string;
}

type ToastState = {
  current: ToastPayload | null;
  /** 当前页面已挂载的 GlobalToast 数量，为 0 时提示降级为 uni.showToast，避免错误静默丢失 */
  mountedCount: number;
};

/**
 * 轻提示状态树。
 * 该 store 只做「状态中转」，真正的渲染由 GlobalToast.vue 内部持有的 wd-toast 完成。
 * 之所以绕这一层，是因为 wot-design-uni 的 useToast() 依赖 provide/inject，
 * 在拦截器、路由守卫等无 setup 上下文的纯 TS 文件中无法直接调用。
 */
/** 读取当前栈顶页面路由，作为提示的归属页面标记 */
function currentRoutePath(): string {
  const pages = getCurrentPages();
  const page = pages[pages.length - 1] as unknown as { route?: string } | undefined;
  return page?.route ?? "";
}

export const useToastStore = defineStore("toast", {
  state: (): ToastState => ({
    current: null,
    mountedCount: 0,
  }),
  actions: {
    /** 投递一条提示，每次投递都会产生新的对象引用，保证监听方可被稳定触发 */
    push(payload: Omit<ToastPayload, "triggeredAt" | "page">): void {
      this.current = { ...payload, triggeredAt: Date.now(), page: currentRoutePath() };
    },
    /** 提示已被消费，立即复位，避免后续进入新页面时重复弹出历史提示 */
    consume(): void {
      this.current = null;
    },
    /** GlobalToast 挂载时登记，用于判断当前页面是否有可用的提示挂载点 */
    markMounted(): void {
      this.mountedCount += 1;
    },
    /** GlobalToast 卸载时注销，计数归零后提示自动降级为 uni.showToast */
    markUnmounted(): void {
      this.mountedCount = Math.max(0, this.mountedCount - 1);
    },
  },
});

/**
 * 全局轻提示调用入口。
 * 可在任意位置直接调用，包括 axios / uni.request 拦截器、路由守卫等纯 TS 环境。
 */
export function useGlobalToast() {
  const toastStore = useToastStore();

  const trigger = (type: ToastType, msg: string, options?: { duration?: number; position?: ToastPosition }): void => {
    // 空文案直接丢弃，避免弹出一个空壳提示
    if (!msg) return;
    // 当前页面没有挂载 GlobalToast 时降级为原生提示，保证错误不静默丢失
    if (toastStore.mountedCount === 0) {
      uni.showToast({ title: msg, icon: "none" });
      return;
    }
    toastStore.push({ type, msg, ...options });
  };

  return {
    /** 普通提示，默认 2 秒自动关闭 */
    show: (msg: string): void => trigger("show", msg),
    success: (msg: string): void => trigger("success", msg),
    error: (msg: string): void => trigger("error", msg),
    warning: (msg: string): void => trigger("warning", msg),
    info: (msg: string): void => trigger("info", msg),
    /** 加载提示默认常驻，需业务侧显式调用 close() 关闭 */
    loading: (msg: string): void => trigger("loading", msg, { duration: 0 }),
    close: (): void => toastStore.consume(),
  };
}
