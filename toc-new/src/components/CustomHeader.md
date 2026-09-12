# CustomHeader 通顶 Header 组件

## 💡 核心思想

uni-app 在 `pages.json` 中把页面的 `navigationStyle` 设为 `custom` 后，系统原生标题栏会被彻底隐藏，页面从状态栏下方开始绘制——这就是「通顶沉浸式」的前提。代价是**标题栏要自己画**，而且必须把手机状态栏那一段高度自己补齐，否则内容会顶到时间、电量图标下面。

本组件就是干这一件事的最小实现，内部只有三段结构：

```
┌──────────────────────────────────────┐
│ 状态栏占位（仅当 statusBarHeight > 0） │  ← 动态高度，H5 端为 0 不占位
├───────┬──────────────────────┬───────┤
│ left  │        标题/副标题      │ right │  ← 固定 88rpx 内容行
└───────┴──────────────────────┴───────┘
```

三个必须记住的防坑点：

1. **状态栏高度不能硬编码**。`uni.getSystemInfoSync().statusBarHeight` 在 **H5 端返回 0**（H5 没有原生状态栏，页面本来就从浏览器视口顶部开始），在 App / 小程序端才返回真实像素值。组件的处理方式是：`> 0` 才插入占位块，`= 0` 时完全不渲染，这样两端都不会多出一块空白。
2. **左右两侧宽度必须固定**。`min-width: 96rpx` 是为了让标题在视觉上真正居中。如果两侧宽度随内容变化，标题会左右摇摆。
3. **返回键的双行为**。点击永远先 `emit('back')`；父组件**没有**监听 `@back` 时才自动 `uni.navigateBack()`。这样「无脑返回上一页」的页面什么都不用写，需要拦截（如未保存提示）的页面只要挂上 `@back` 即可，不会出现「既跳转又执行自定义逻辑」的双跑。

组件本身**不带 `position: sticky`**。需要吸顶的页面（如「我的测试」的 Header + 分类栏），把 `CustomHeader` 和吸顶元素一起包在一个 `position: sticky; top: 0` 的容器里即可，比在组件内写死吸顶更灵活。

`variant` 三态对应三种页面背景：

| variant | 底色 | 文字色 | 典型场景 |
| --- | --- | --- | --- |
| `solid`（默认） | 纯白 + 极轻投影 | `#1C2331` 深色 | 列表类页面 |
| `gradient` | 极客蓝 135° 渐变 | 白色 | 首页等需要氛围的页面 |
| `transparent` | 透明 | 白色 | 自身已有渐变背景、需要 Header 融进去的页面 |

图标全部为手写内联 `<svg>`，`stroke="currentColor"`，颜色由外层 `:style="{ color }"` 统一控制，不绑定任何 SVG 属性，规避模板编译器的属性透传差异。

> ⚠️ 跨端提示：内联 `<svg>` 标签在 **H5 端可正常渲染**，小程序端不支持该标签。若后续需要上小程序，需把内联 SVG 换成 `<image src="/static/icons/xxx.svg" />` 形式。

## 💻 使用示例

### 基础用法：白底标题栏

```vue
<template>
  <view class="page">
    <CustomHeader title="我的测试" />

    <view class="page__body">
      <text>页面内容</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import CustomHeader from "@/components/CustomHeader.vue";
</script>
```

### 首页：极客蓝渐变 + 右侧插槽

```vue
<template>
  <view class="page">
    <CustomHeader title="智题库企业空间" variant="gradient">
      <template #right>
        <text class="page__badge">可考 3 场</text>
      </template>
    </CustomHeader>
  </view>
</template>

<script setup lang="ts">
import CustomHeader from "@/components/CustomHeader.vue";
</script>

<style scoped>
.page__badge {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.86);
}
</style>
```

### 子页面：带返回键并拦截返回行为

```vue
<template>
  <view class="page">
    <CustomHeader title="考场" subtitle="作答中" show-back @back="handleBack" />
  </view>
</template>

<script setup lang="ts">
import CustomHeader from "@/components/CustomHeader.vue";
import { useGlobalToast } from "@/stores/toast";

const toast = useGlobalToast();

function handleBack(): void {
  // 监听了 @back 之后，组件不会再自动 navigateBack，由这里完全接管
  toast.warning("考试进行中，请先交卷再离开");
}
</script>
```

### 吸顶用法：Header + 分类栏一起吸顶

```vue
<template>
  <view class="page">
    <view class="page__sticky">
      <CustomHeader title="我的测试" />
      <view class="page__tabs">分类切换栏</view>
    </view>

    <view class="page__list">成绩列表</view>
  </view>
</template>

<style scoped>
.page__sticky {
  position: sticky;
  top: 0;
  z-index: 20;
  background-color: #ffffff;
}
</style>
```
