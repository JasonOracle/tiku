<template>
	<view class="question-card">
		<view class="question-card__meta">
			<text class="question-card__seq">第 {{ index + 1 }} / {{ total }} 题</text>
			<text class="question-card__sep">·</text>
			<text class="question-card__type">{{ typeLabel }}</text>
			<text class="question-card__sep">·</text>
			<text class="question-card__score">{{ question.score }} 分</text>
		</view>

		<text class="question-card__stem">{{ stem }}</text>

		<!-- 单选 -->
		<view v-if="questionKind === 'single'" class="question-card__options">
			<view
				v-for="option in visibleOptions"
				:key="option.key"
				class="option-card"
				:class="{ 'option-card--active': singleValue === option.key }"
				hover-class="option-card--pressed"
				@click="selectSingle(option.key)"
			>
				<view class="option-card__badge" :class="{ 'option-card__badge--active': singleValue === option.key }">
					<text class="option-card__badge-text">{{ option.key }}</text>
				</view>
				<text class="option-card__text">{{ option.text }}</text>
			</view>
		</view>

		<!-- 多选 -->
		<view v-else-if="questionKind === 'multiple'" class="question-card__options">
			<view
				v-for="option in visibleOptions"
				:key="option.key"
				class="option-card"
				:class="{ 'option-card--active': multipleValue.includes(option.key) }"
				hover-class="option-card--pressed"
				@click="toggleMultiple(option.key)"
			>
				<view class="option-card__badge option-card__badge--square" :class="{ 'option-card__badge--active': multipleValue.includes(option.key) }">
					<text class="option-card__badge-text">{{ option.key }}</text>
				</view>
				<text class="option-card__text">{{ option.text }}</text>
			</view>
		</view>

		<!-- 判断：正确 / 错误 两枚胶囊 -->
		<view v-else-if="questionKind === 'judge'" class="question-card__judge">
			<view
				v-for="option in visibleOptions"
				:key="option.key"
				class="judge-pill"
				:class="{ 'judge-pill--active': singleValue === option.key }"
				hover-class="judge-pill--pressed"
				@click="selectSingle(option.key)"
			>
				<text class="judge-pill__text">{{ option.text }}</text>
			</view>
		</view>

		<!-- 填空：空位数量由题干下划线推导，多空逐个输入 -->
		<view v-else-if="questionKind === 'fill'" class="question-card__fills">
			<view v-for="blank in blankCount" :key="blank" class="fill-row">
				<text v-if="blankCount > 1" class="fill-row__label">第 {{ blank }} 空</text>
				<wd-input
					:model-value="fillValues[blank - 1] ?? ''"
					:placeholder="blankCount > 1 ? `请输入第 ${blank} 空答案` : '请输入答案'"
					clearable
					@update:model-value="handleFillInput(blank - 1, $event)"
				/>
			</view>
		</view>

		<!-- 简答 -->
		<view v-else class="question-card__short">
			<wd-textarea
				v-model="shortValue"
				placeholder="请在此作答，可分段书写要点"
				:maxlength="500"
				show-word-limit
				:rows="6"
				no-border
			/>
		</view>
	</view>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { ExamQuestion, QuestionOption } from "@/api/exam";

/** 归一化后的选项：key 为提交给后端的选项标识，text 为展示文案 */
type NormalizedOption = { key: string; text: string };

/** 五类题型，把后端可能出现的枚举别名统一收敛到这里 */
type QuestionKind = "single" | "multiple" | "judge" | "fill" | "short";

type AnswerValue = string | string[];

const props = defineProps<{
	/** 单题数据，服务端已剥离正确答案与解析 */
	question: ExamQuestion;
	/** 当前答案：单选 / 判断 / 简答 / 单空填空为 string，多选 / 多空填空为 string[] */
	modelValue: AnswerValue;
	/** 当前题序，从 0 开始 */
	index: number;
	/** 题目总数 */
	total: number;
}>();

const emit = defineEmits<{
	"update:modelValue": [value: AnswerValue];
}>();

/** 后端题型枚举别名映射：不同批次的存量数据用过不同写法，必须全部兼容 */
const KIND_MAP: Record<string, QuestionKind> = {
	single: "single",
	single_choice: "single",
	multiple: "multiple",
	multiple_choice: "multiple",
	judge: "judge",
	true_false: "judge",
	fill: "fill",
	fill_in: "fill",
	short: "short",
	short_answer: "short",
};

const TYPE_LABELS: Record<QuestionKind, string> = {
	single: "单选",
	multiple: "多选",
	judge: "判断",
	fill: "填空",
	short: "简答",
};

/** 匹配 "A. 文本" / "A、文本" / "A:文本" 这类带选项标识的写法 */
const OPTION_PREFIX_PATTERN = /^([A-Za-z])\s*[.、．:：)]\s*(.+)$/;
/** 匹配题干中的填空下划线，两个及以上视为一个空位 */
const BLANK_PATTERN = /_{2,}/g;

/** 判断题兜底选项：题干未携带 options 时使用，key 必须与后端判分口径一致 */
const JUDGE_FALLBACK: NormalizedOption[] = [
	{ key: "A", text: "正确" },
	{ key: "B", text: "错误" },
];

function indexToLetter(index: number): string {
	return String.fromCharCode(65 + index);
}

/**
 * 选项三形态归一化：
 * 1) { key, text } 对象 → 直接取用；
 * 2) 带前缀的字符串（如 "A. 锁屏"）→ 拆出 key 与 text；
 * 3) 无前缀的纯文本 → 按数组下标生成 key。
 */
function normalizeOptions(raw: QuestionOption[] | undefined): NormalizedOption[] {
	if (!raw || raw.length === 0) return [];
	return raw.map((option, index) => {
		if (typeof option === "object" && option !== null) {
			const key = String(option.key ?? "").trim().toUpperCase();
			return { key: key || indexToLetter(index), text: String(option.text ?? "").trim() };
		}
		const text = String(option ?? "").trim();
		const matched = text.match(OPTION_PREFIX_PATTERN);
		if (matched) return { key: matched[1].toUpperCase(), text: matched[2].trim() };
		return { key: indexToLetter(index), text };
	});
}

const stem = computed(() => props.question.content || props.question.title || "");

const normalizedOptions = computed(() => normalizeOptions(props.question.options));

/** 题型判定：客观题缺选项时退化为文本作答，避免出现无法作答的死题；判断题始终使用内置双选项 */
const questionKind = computed<QuestionKind>(() => {
	const mapped = KIND_MAP[props.question.type] ?? "single";
	if (mapped === "judge") return "judge";
	if (mapped === "single" || mapped === "multiple") {
		return normalizedOptions.value.length > 0 ? mapped : "short";
	}
	return mapped;
});

const typeLabel = computed(() => TYPE_LABELS[questionKind.value]);

const visibleOptions = computed<NormalizedOption[]>(() => {
	if (questionKind.value === "judge") {
		return normalizedOptions.value.length >= 2 ? normalizedOptions.value.slice(0, 2) : JUDGE_FALLBACK;
	}
	return normalizedOptions.value;
});

/** 填空空位数量：从题干下划线推导，推导不到则按单空处理，与后端宽松比对的单空口径对齐 */
const blankCount = computed(() => {
	const matched = stem.value.match(BLANK_PATTERN);
	return matched && matched.length > 0 ? matched.length : 1;
});

const singleValue = computed(() => (typeof props.modelValue === "string" ? props.modelValue : ""));

const multipleValue = computed<string[]>(() => (Array.isArray(props.modelValue) ? props.modelValue.map((item) => String(item)) : []));

const fillValues = computed<string[]>(() => {
	const raw = props.modelValue;
	if (Array.isArray(raw)) return raw.map((item) => String(item ?? ""));
	return raw ? [String(raw)] : [];
});

const shortValue = computed({
	get: () => (typeof props.modelValue === "string" ? props.modelValue : ""),
	set: (value: string) => emit("update:modelValue", value),
});

function selectSingle(key: string): void {
	emit("update:modelValue", key);
}

function toggleMultiple(key: string): void {
	const next = multipleValue.value.includes(key)
		? multipleValue.value.filter((item) => item !== key)
		: [...multipleValue.value, key].sort();
	emit("update:modelValue", next);
}

/** 多空填空：始终按空位总数补齐数组，避免稀疏数组被序列化成 null 导致后端比对失败 */
function handleFillInput(blankIndex: number, value: string | number): void {
	const size = blankCount.value;
	const next: string[] = [];
	for (let i = 0; i < size; i += 1) {
		next.push(i === blankIndex ? String(value ?? "") : (fillValues.value[i] ?? ""));
	}
	emit("update:modelValue", size > 1 ? next : (next[0] ?? ""));
}
</script>

<style lang="scss" scoped>
.question-card {
	padding: 36rpx 32rpx;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
}

.question-card__meta {
	display: flex;
	align-items: center;
}

.question-card__seq,
.question-card__type,
.question-card__score {
	font-size: 24rpx;
	color: #a8b2c4;
}

.question-card__type {
	color: #1d63ff;
	font-weight: 600;
}

.question-card__sep {
	margin: 0 10rpx;
	font-size: 24rpx;
	color: #d5dcea;
}

.question-card__stem {
	display: block;
	margin-top: 22rpx;
	font-size: 32rpx;
	font-weight: 600;
	line-height: 1.62;
	color: #1c2331;
}

.question-card__options {
	margin-top: 34rpx;
}

.option-card {
	display: flex;
	align-items: flex-start;
	padding: 26rpx 24rpx;
	margin-bottom: 20rpx;
	background-color: #f6f8fc;
	border: 2rpx solid transparent;
	border-radius: 20rpx;
	transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.option-card--pressed {
	transform: scale(0.98);
	opacity: 0.92;
}

.option-card--active {
	background-color: #e8f0ff;
	border-color: #1d63ff;
}

.option-card__badge {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 44rpx;
	height: 44rpx;
	border-radius: 50%;
	border: 2rpx solid #c9d4e8;
	background-color: #ffffff;
}

.option-card__badge--square {
	border-radius: 10rpx;
}

.option-card__badge--active {
	border-color: #1d63ff;
	background-color: #1d63ff;
}

.option-card__badge-text {
	font-size: 24rpx;
	font-weight: 600;
	color: #748094;
}

.option-card__badge--active .option-card__badge-text {
	color: #ffffff;
}

.option-card__text {
	flex: 1;
	margin-left: 20rpx;
	font-size: 28rpx;
	line-height: 1.55;
	color: #1c2331;
}

.option-card--active .option-card__text {
	color: #0045d8;
	font-weight: 500;
}

.question-card__judge {
	display: flex;
	margin-top: 34rpx;
}

.judge-pill {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	height: 108rpx;
	margin-right: 24rpx;
	background-color: #f6f8fc;
	border: 2rpx solid transparent;
	border-radius: 999rpx;
	transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.judge-pill:last-child {
	margin-right: 0;
}

.judge-pill--pressed {
	transform: scale(0.97);
	opacity: 0.92;
}

.judge-pill--active {
	background-color: #e8f0ff;
	border-color: #1d63ff;
}

.judge-pill__text {
	font-size: 30rpx;
	font-weight: 600;
	color: #748094;
}

.judge-pill--active .judge-pill__text {
	color: #1d63ff;
}

.question-card__fills {
	margin-top: 30rpx;
}

.fill-row {
	display: flex;
	align-items: center;
	margin-bottom: 18rpx;
}

.fill-row__label {
	width: 120rpx;
	font-size: 26rpx;
	color: #748094;
}

.question-card__short {
	margin-top: 30rpx;
	padding: 20rpx 24rpx;
	background-color: #f6f8fc;
	border-radius: 20rpx;
}
</style>
