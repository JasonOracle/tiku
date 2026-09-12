# AnswerSheet 半屏答题卡抽屉组件

## 💡 核心思想

答题卡的本质是「**一眼看清全场作答进度，并一键跳回任意一题**」。它必须快、必须准，而最容易出问题的地方是**判定规则被写了两遍**。

如果考场页里写一份「这题算不算已作答」，答题卡里再写一份，两处迟早会漂移：多选只选了一个选项算不算已答？填空只填了半个空算不算已答？一旦两边口径不一致，就会出现「考场页显示已答 3 题，答题卡却只高亮 2 格」这种让人抓狂的错位。

所以本组件的边界划得非常死：

```
父级（唯一判定者）── answeredIds: number[] ──→ 本组件（纯渲染）
父级（唯一状态源）── currentIndex: number  ──→ 本组件（纯渲染）
```

**本组件不做任何「是否已作答」的判断**，它只接收一个已经算好的 ID 数组，把它渲染成三种颜色。判定规则永远只有父级那一处。

三个必须记住的防坑点：

1. **点击题号只上报、不自闭。** 点击事件只 `emit('select', index)`，抽屉的关闭由父级统一控制。这样「点题号跳题」和「点遮罩关闭」两条路径不会各写一套关闭逻辑。
2. **三态是「可叠加」而不是「三选一」。** 一道题可以同时是「已作答」且「当前题」，此时应当显示极客蓝填充 + 深蓝描边。CSS 里 `.sheet-cell--done.sheet-cell--current` 必须显式写，否则会退化成其中一种。
3. **必须挂在弹层容器里渲染，且自身限定高度。** 界面高度写死在组件根节点的 `60vh` 上（由 `wd-popup` 的 `custom-style` 承载），而**不是**依赖弹层自适应内容高度——否则题量一多，面板会一路顶到屏幕顶部，把题干区压没。

抽屉的懒渲染交给 `wd-popup` 的 `lazyRender`（默认开启）：未打开时不产生任何节点，几十道题的网格也不会给考场首屏增加负担。

## 💻 使用示例

### 基础用法：接入考场页

```vue
<template>
	<view class="exam">
		<!-- 底部操作条上的入口 -->
		<view class="exam__sheet-entry" @click="sheetVisible = true">
			<text>{{ currentIndex + 1 }} / {{ questions.length }} · 答题卡</text>
		</view>

		<!-- 半屏答题卡抽屉 -->
		<AnswerSheet
			v-model="sheetVisible"
			:questions="questions"
			:answered-ids="answeredIds"
			:current-index="currentIndex"
			@select="handleJumpTo"
		/>
	</view>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import AnswerSheet from "@/components/AnswerSheet.vue";
import type { ExamQuestion } from "@/api/exam";

const questions = ref<ExamQuestion[]>([]);
const answers = ref<Record<number, string | string[]>>({});
const currentIndex = ref(0);
const sheetVisible = ref(false);

/** 已作答判定规则：全工程唯一一处，答题卡与状态条共用这一个结果 */
const answeredIds = computed(() =>
	questions.value
		.filter((question) => {
			const value = answers.value[question.id];
			if (Array.isArray(value)) return value.some((item) => String(item).trim() !== "");
			return typeof value === "string" && value.trim() !== "";
		})
		.map((question) => question.id)
);

function handleJumpTo(index: number): void {
	currentIndex.value = index;
	// 关闭动作由父级统一控制，组件自身不会自动收起
	sheetVisible.value = false;
}
</script>
```

### 三态视觉一览

| 状态 | 视觉 | CSS 类 |
| --- | --- | --- |
| 未作答 | 浅灰底、灰字 | `.sheet-cell` 默认态 |
| 已作答 | 极客蓝填充、白字 | `.sheet-cell--done` |
| 当前题 | 白底 + 极客蓝描边、蓝字加粗 | `.sheet-cell--current` |
| 已作答且为当前题 | 极客蓝填充 + 深蓝描边、白字 | 两者叠加 |

### 只读展示（不响应跳转）

```vue
<template>
	<AnswerSheet :model-value="true" :questions="questions" :answered-ids="answeredIds" :current-index="0" />
</template>
```

不监听 `@select` 时点击题号不会有任何跳转行为，可用于报告页的作答总览。
