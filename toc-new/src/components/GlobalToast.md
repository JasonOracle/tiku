# GlobalToast 全局轻提示组件

## 💡 核心思想

`wot-design-uni` 的 Toast 是**函数式组件**，官方约定必须先有 `<wd-toast />` 挂载点，再在 setup 上下文中 `useToast()` 才能调用。而本项目大量提示发生在 `src/utils/request.ts` 这类**纯 TS 文件**中（拦截器没有 setup 上下文），直接调用必然失败。

本组件用一个最薄的「Pinia 中转站」把这条链路打通：

```
纯 TS 文件（拦截器 / 守卫）
        │  写入状态
        ▼
  stores/toast.ts  （current: ToastPayload | null）
        │  watch 监听引用变化
        ▼
  GlobalToast.vue  （持有 wd-toast 实例）
        │  调用 toast[type]({ msg, duration, position })
        ▼
    真实弹窗
```

三个必须记住的防坑点：

1. **必须挂载在页面上**。uni-app 的 `App.vue` 不渲染模板，无法承载 `<wd-toast />`。任何需要弹提示的页面，模板里都要放一个 `<GlobalToast />`。
2. **selector 必须成对**。模板上写 `selector="global-toast"`，setup 里就必须 `useToast("global-toast")`。`useToast` 底层是 `provide/inject`，selector 不一致等于注入了两个互不相干的配置对象，表现为「调用不报错但永远不弹窗」。
3. **弹完立即复位**。派发后立刻调 `consume()` 清空状态，否则页面重建（切走再切回）会重复弹出同一条历史提示。
4. **没挂载也不会丢错误**。组件在 `onMounted` / `onUnmounted` 时向 store 登记挂载数量；当数量为 0（当前页面漏放挂载点）时，`useGlobalToast()` 自动降级为 `uni.showToast`，保证错误永远可见而不是静默消失。
5. **提示必须归属到触发它的那个页面**。`uni.navigateTo` 之后，上一页仍然留在页面栈里、其 `GlobalToast` 依然挂载着，两个实例共用同一个 store。若不做归属区分，**后台页面的实例会抢先 `consume()` 掉提示**，用户在当前页面完全看不到任何反馈（这一条在阶段三的考场切屏警告上真实踩到过）。因此：`useGlobalToast()` 投递时会带上当前栈顶路由，组件在 `onMounted` 时锁存自己的路由，**只有两者一致的挂载点才派发**；归属路由为空时视为全局提示，人人可派发。

`selector` 单独命名还有一个好处：后续新增 `GlobalLoading` 时，只要换一个 selector，两者就不会互相覆盖。

## 💻 使用示例

### 第一步：在页面模板中挂载（每个需要提示的页面都要放一次）

```vue
<template>
  <view class="page">
    <text>页面内容</text>

    <!-- 全局轻提示挂载点，一个页面只需一个 -->
    <GlobalToast />
  </view>
</template>

<script setup lang="ts">
import GlobalToast from "@/components/GlobalToast.vue";
</script>
```

### 第二步：在任意位置调用（无需 setup 上下文）

```ts
import { useGlobalToast } from "@/stores/toast";

const toast = useGlobalToast();

// 常规提示
toast.show("已保存");
// 成功提示（默认 1.5 秒）
toast.success("交卷成功");
// 错误提示（垂直排布，带 error 图标）
toast.error("账号或密码错误");
// 警告与信息提示
toast.warning("考试时间仅剩 5 分钟");
toast.info("暂无更多测评");

// 加载提示默认常驻，必须手动关闭
toast.loading("正在提交...");
toast.close();
```

### 典型场景：请求拦截器中的业务错误提示

```ts
import { useGlobalToast } from "@/stores/toast";

const toast = useGlobalToast();

// 后端返回业务失败码时
toast.error(res.message || "请求失败，请稍后重试");
```
