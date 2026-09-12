import { createPinia } from "pinia";
import { createPersistedState } from "pinia-plugin-persistedstate";

/**
 * uni-app 跨端同步存储适配。
 * 说明：pinia-plugin-persistedstate 默认走浏览器 localStorage，在小程序 / App 端不存在，
 * 因此统一改走 uni 存储 API，保证三端持久化行为一致。
 */
const uniStorage = {
  getItem: (key: string): string | null => {
    const value = uni.getStorageSync(key);
    // uni 在键不存在时返回空串而非 null，需显式归一化，否则 JSON.parse 会抛异常
    return value === "" || value === null || value === undefined ? null : String(value);
  },
  setItem: (key: string, value: string): void => {
    uni.setStorageSync(key, value);
  },
};

/** 全局唯一的 Pinia 实例：导出后供 main.ts 装配，也供纯 TS 模块复用，避免重复 createPinia */
export const pinia = createPinia();

pinia.use(
  createPersistedState({
    storage: uniStorage,
  })
);
