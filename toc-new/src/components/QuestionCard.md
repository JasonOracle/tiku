# QuestionCard 单题作答卡片组件

## 💡 核心思想

考场里最脏的活不是「滑动切题」，而是**同一道题可能以五种完全不同的形态出现，且每种形态的数据格式都不统一**。本组件把这部分脏活全部吃进内部，对外只暴露一个答案值：

```
props.question ──┐
                 ├─→ 题型归一化 ─→ 选项归一化 ─→ 渲染对应作答控件
props.modelValue ┘                                      │
                                                        ▼
                                        emit('update:modelValue', 答案值)
```

组件本身**完全无状态**：不持有任何内部答案副本，答案一律由父级持有并通过 `modelValue` 回传。这样「已答判定」「交卷收集答案」「续答回填」三处都只认父级那一份数据，不会出现组件内外答案不一致。

四个必须记住的防坑点：

1. **判断题必须提交选项 key，不能提交「正确 / 错误」。** 后端判分只把 `correct_answer` 里的「正确/对/TRUE/YES」归一化成 `'A'`，**绝不转换用户提交值**。所以选中「正确」时提交的必须是 `'A'`，提交中文字符串会直接被判错。组件的做法是：判断题统一渲染成「正确 / 错误」两枚胶囊，但胶囊绑定的仍是选项的 `key`。
2. **选项有三种真实存在过的形态**，必须归一化，否则会出现「选项全是空白」或「A. A. 文本」这类重复前缀：
   - `{ key, text }` 对象 → 直接取用；
   - 带前缀的字符串 `"A. 锁屏"` → 用 `/^([A-Za-z])\s*[.、．:：)]\s*(.+)$/` 拆出 key 与 text；
   - 无前缀的纯文本 → 按数组下标生成 key（0→A、1→B…）。
3. **题型枚举别名字段必须全部兼容**：真实库里出现过 `single_choice|single`、`multiple_choice|multiple`、`judge|true_false`、`fill_in|fill`、`short_answer|short` 两套写法，照抄其中一套会让另一套的题整片渲染不出来。同时做了兜底：客观题若一个选项都没有，退化为文本作答，避免出现「无法作答的死题」。
4. **填空的空位数量只能从题干下划线推导**。服务端为保证防泄题，响应里已经剥离了 `correct_answer`，前端无法得知标准答案有几个空，只能用 `/_{2,}/g` 数题干里的下划线；一个都数不到时按「单空」处理，与后端把字符串包成单元素列表的宽松比对口径一致。多空提交时**始终补齐为等长数组**，绝不产生稀疏数组（稀疏数组序列化后会变成 `null`，导致后端逐空比对直接失败）。

## 💻 使用示例

### 基础用法：在考场里渲染一题

```vue
<template>
	<QuestionCard
		:question="currentQuestion"
		:model-value="answers[currentQuestion.id] ?? ''"
		:index="currentIndex"
		:total="questions.length"
		@update:model-value="(value) => (answers[currentQuestion.id] = value)"
	/>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import QuestionCard from "@/components/QuestionCard.vue";
import type { ExamQuestion } from "@/api/exam";

const questions = ref<ExamQuestion[]>([]);
const currentIndex = ref(0);
const answers = reactive<Record<number, string | string[]>>({});

const currentQuestion = computed(() => questions.value[currentIndex.value]);
</script>
```

### 各题型回传的答案形态

| 题型 | 回传类型 | 示例值 | 说明 |
| --- | --- | --- | --- |
| 单选 | `string` | `"B"` | 选项 key |
| 多选 | `string[]` | `["A","B","D"]` | 选项 key 数组，已按字典序排序，便于比对 |
| 判断 | `string` | `"A"` | `A` = 正确，`B` = 错误，**不是中文** |
| 填空题（单空） | `string` | `"2"` | 后端会把字符串包成单元素列表比对 |
| 填空题（多空） | `string[]` | `["北京","上海"]` | 顺序与题干空位一一对应，长度必定等于空位数 |
| 简答 | `string` | `"..."` | 后端跳过自动评分，进人工 / AI 核验 |

### 只读回显（如报告页复用同一套渲染）

```vue
<template>
	<QuestionCard :question="question" :model-value="savedAnswer" :index="0" :total="1" />
</template>
```

不监听 `@update:model-value` 即为只读回显，组件不会自行修改任何数据。
