# PreviewFloat 悬浮球

> 💡 核心思想
>
> 双风格 UI 选型阶段需要一个「永远在手边」的页面直达器。`PreviewFloat` 是一个固定悬浮球组件：
> 点击展开后，以双列面板并列呈现 **A（Linear 极客冷灰）** 与 **B（Apple 钛金微光）** 两套风格的
> 全部 7 个预览页面，点击任意条目即 `navigateTo` 直达，当前页自动高亮。
> 组件仅服务于 `preview-linear/`、`preview-apple/`、`preview-nav/` 预览体系，
> 不读取 store、不调用任何真实接口，正式业务页面不会引入它，选型结束后可整体删除。

**交互说明**

- 悬浮球点击：展开 / 收起导航面板，展开时球体旋转 45 度并切换为极客蓝；
- 面板蒙层点击：收起面板；
- 「返回索引总览」：重定向回 `preview-nav/index` 索引页。

**Props**

| 属性 | 类型 | 说明 |
| --- | --- | --- |
| `current` | `string` | 当前预览页路由路径（如 `preview-linear/exam/index`），用于高亮定位 |

> 💻 使用示例

```vue
<template>
	<view class="page">
		<!-- 页面正常内容 -->
		<PreviewFloat current="preview-linear/exam/index" />
	</view>
</template>

<script setup lang="ts">
import PreviewFloat from "@/components/PreviewFloat.vue";
</script>
```
