# PageState 页面状态占位组件

## 💡 核心思想

任何**真实**的数据页面都有三种非正常态：正在加载、确实没数据、加载失败。工程里最容易出问题的地方不是这三种态「做没做」，而是它们**经常被漏做**——于是用户看到一个永远转不出来的白屏，或者一次网络抖动后页面就再也没恢复。

把三种态收敛成一个组件，页面只需表达「我现在是什么状态」，不必再各写一套骨架与插画：

```
loading  →  流光滑块骨架卡（数量可配，默认 3 张）
empty    →  手绘矢量空态插画 + 标题 + 说明
error    →  手绘矢量错误插画 + 标题 + 说明 + 「重新加载」按钮
```

三个必须记住的防坑点：

1. **三种态必须互斥且穷尽**。页面的 `status` 只允许是 `loading` / `empty` / `error` 三者之一，数据正常时不渲染本组件。这样就不可能出现「骨架屏和数据同时显示」或「请求回来了但骨架还在」的错乱。
2. **请求必须有 `finally`**。骨架屏卡死最常见的原因不是组件问题，而是业务侧 `loading` 没在异常分支复位。凡是驱动本组件 `status` 的请求，都要写成 `try / catch / finally`，在 `finally` 里兜底把状态落到 `empty` 或 `error`。
3. **插画是纯手写 SVG，不含任何图片资源**。空态与错误态的两张插画内联在组件里，不依赖 `static` 目录、不依赖字体图标，因此不会因为资源路径写错而在真机上裂图。

文案有默认值：错误态默认「加载失败 / 网络异常或服务暂时不可用，请稍后重试」，空态默认「暂无内容 / 这里暂时还没有可展示的内容」。业务侧传了 `title` / `description` 就以传入的为准。

## 💻 使用示例

### 基础用法：三态驱动

```vue
<template>
	<view class="page">
		<CustomHeader title="我的测试" />

		<view class="page__body">
			<PageState
				v-if="status !== 'ready'"
				:status="status"
				action-text="重新加载"
				@action="loadRecords"
			/>

			<view v-else class="page__list">
				<view v-for="item in records" :key="item.record_id" class="card">{{ item.task_title }}</view>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { onShow } from "@dcloudio/uni-app";
import { ref } from "vue";
import CustomHeader from "@/components/CustomHeader.vue";
import PageState from "@/components/PageState.vue";
import { fetchMyRecords, type MyRecordItem } from "@/api/exam";

const status = ref<"loading" | "empty" | "error" | "ready">("loading");
const records = ref<MyRecordItem[]>([]);

async function loadRecords(): Promise<void> {
	status.value = "loading";
	try {
		const data = await fetchMyRecords();
		records.value = data.items;
		status.value = data.items.length ? "ready" : "empty";
	} catch {
		// request 层已经弹过轻提示，这里只负责把页面切到错误态，避免白屏
		status.value = "error";
	}
}

onShow(() => {
	loadRecords();
});
</script>
```

### 自定义文案与骨架数量

```vue
<template>
	<PageState :status="status" skeleton-count="5" :title="'还没有历史记录'" :description="'完成第一次测评后，成绩会显示在这里'" />
</template>
```

### 仅错误态 + 重试

```vue
<template>
	<PageState status="error" title="加载失败" description="请检查网络后重试" action-text="重新加载" @action="reload" />
</template>
```
