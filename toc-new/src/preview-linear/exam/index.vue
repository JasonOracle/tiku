<!--
  风格 A · Linear 极客冷灰风 · 在线考场（静态预览）
  单选 / 多选 / 判断 / 填空 / 简答五大题型全交互，60vh 答题卡抽屉、倒计时微动效与切屏防作弊告警
-->
<template>
	<view class="ex-page">
		<!-- 考场顶栏：标题 + 倒计时 -->
		<view class="ex-header">
			<view class="ex-header__inner">
				<view class="ex-header__left">
					<view class="ex-header__title">安全生产与合规考试</view>
					<view class="ex-header__sub">第 {{ current + 1 }} / {{ questions.length }} 题 · 答题卡 {{ answeredCount }}/{{ questions.length }}</view>
				</view>
				<view class="ex-clock" :class="{ 'ex-clock--hot': remainSeconds < 300 }">
					<view class="ex-clock__icon" :class="{ 'ex-clock__icon--pulse': remainSeconds < 300 }"></view>
					<text class="ex-clock__text">{{ clockText }}</text>
				</view>
			</view>
			<!-- 倒计时进度条：随时间流逝缓慢收缩 -->
			<view class="ex-timebar">
				<view class="ex-timebar__fill" :style="{ width: timePercent + '%' }"></view>
			</view>
		</view>

		<!-- 题目横向滑动区 -->
		<swiper class="ex-swiper" :current="current" @change="onSwiperChange" duration="360">
			<swiper-item v-for="(q, qi) in questions" :key="q.id">
				<scroll-view class="ex-qscroll" scroll-y>
					<view class="ex-question">
						<view class="ex-question__head">
							<view class="ex-question__no">Q{{ qi + 1 }}</view>
							<view class="ex-question__type">{{ q.typeLabel }}</view>
							<view
								class="ex-question__flag"
								:class="{ 'ex-question__flag--on': flags.has(q.id) }"
								@click="toggleFlag(q.id)"
							>
								{{ flags.has(q.id) ? "已标记" : "标记本题" }}
							</view>
						</view>
						<view class="ex-question__title">{{ q.title }}</view>

						<!-- 单选 -->
						<view v-if="q.kind === 'single'" class="ex-options">
							<view
								class="ex-option"
								:class="{ 'ex-option--on': answers[q.id] === o.key }"
								v-for="o in q.options"
								:key="o.key"
								@click="answers[q.id] = o.key"
							>
								<view class="ex-option__key" :class="{ 'ex-option__key--on': answers[q.id] === o.key }">{{ o.key }}</view>
								<view class="ex-option__text">{{ o.text }}</view>
							</view>
						</view>

						<!-- 多选 -->
						<view v-else-if="q.kind === 'multiple'" class="ex-options">
							<view
								class="ex-option"
								:class="{ 'ex-option--on': isMultiPicked(q.id, o.key) }"
								v-for="o in q.options"
								:key="o.key"
								@click="toggleMulti(q.id, o.key)"
							>
								<view class="ex-option__check" :class="{ 'ex-option__check--on': isMultiPicked(q.id, o.key) }"></view>
								<view class="ex-option__text">{{ o.text }}</view>
							</view>
						</view>

						<!-- 判断 -->
						<view v-else-if="q.kind === 'judge'" class="ex-judge">
							<view
								class="ex-judge__btn"
								:class="{ 'ex-judge__btn--on': answers[q.id] === '对', 'ex-judge__btn--yes': answers[q.id] === '对' }"
								@click="answers[q.id] = '对'"
							>
								<text class="ex-judge__mark">对</text>
								<text class="ex-judge__label">正确</text>
							</view>
							<view
								class="ex-judge__btn"
								:class="{ 'ex-judge__btn--on': answers[q.id] === '错', 'ex-judge__btn--no': answers[q.id] === '错' }"
								@click="answers[q.id] = '错'"
							>
								<text class="ex-judge__mark">错</text>
								<text class="ex-judge__label">错误</text>
							</view>
						</view>

						<!-- 填空 -->
						<view v-else-if="q.kind === 'blank'" class="ex-blanks">
							<view class="ex-blank" v-for="(b, bi) in q.blanks" :key="bi">
								<view class="ex-blank__label">空位 {{ bi + 1 }}：{{ b.hint }}</view>
								<input class="ex-blank__input" v-model="blankValues[q.id][bi]" :placeholder="b.placeholder" placeholder-class="ex-ph" />
							</view>
						</view>

						<!-- 简答 -->
						<view v-else class="ex-essay">
							<textarea
								class="ex-essay__area"
								v-model="essayValues[q.id]"
								:maxlength="500"
								placeholder="请结合工作实际作答，注意条理与要点完整"
								placeholder-class="ex-ph"
							></textarea>
							<view class="ex-essay__count">
								<text :class="{ 'ex-essay__count--hot': (essayValues[q.id] || '').length > 480 }">
									{{ (essayValues[q.id] || "").length }}
								</text>
								/ 500
							</view>
						</view>
					</view>
				</scroll-view>
			</swiper-item>
		</swiper>

		<!-- 底部操作条 -->
		<view class="ex-footer">
			<view class="ex-footer__drawer" @click="drawerOpen = true">
				<view class="ex-footer__grid">
					<view class="ex-footer__cell" v-for="n in 4" :key="n"></view>
				</view>
				<text>答题卡</text>
			</view>
			<view class="ex-footer__nav">
				<view class="ex-nav" :class="{ 'ex-nav--disabled': current === 0 }" @click="prevQuestion">上一题</view>
				<view class="ex-nav ex-nav--primary" @click="nextQuestion">{{ current === questions.length - 1 ? "去交卷" : "下一题" }}</view>
			</view>
		</view>

		<!-- 60vh 答题卡抽屉 -->
		<view class="ex-drawer-mask" v-if="drawerOpen" @click="drawerOpen = false"></view>
		<view class="ex-drawer" :class="{ 'ex-drawer--open': drawerOpen }">
			<view class="ex-drawer__grabber"></view>
			<view class="ex-drawer__head">
				<view class="ex-drawer__title">答题卡</view>
				<view class="ex-drawer__legend">
					<view class="lg-item"><view class="lg-chip lg-chip--cur"></view>当前题</view>
					<view class="lg-item"><view class="lg-chip lg-chip--done"></view>已作答</view>
					<view class="lg-item"><view class="lg-chip lg-chip--flag"></view>已标记</view>
					<view class="lg-item"><view class="lg-chip lg-chip--todo"></view>未作答</view>
				</view>
			</view>
			<scroll-view class="ex-drawer__scroll" scroll-y>
				<view class="ex-matrix">
					<view
						class="ex-cell"
						:class="cellClass(i - 1)"
						v-for="i in questions.length"
						:key="i"
						@click="jumpTo(i - 1)"
					>
						{{ i }}
					</view>
				</view>
			</scroll-view>
			<view class="ex-drawer__foot">
				<view class="ex-submit" @click="askSubmit">确认交卷</view>
			</view>
		</view>

		<!-- 切屏防作弊告警弹窗（演示触发按钮在顶栏倒计时左侧长按？此处由答题卡交卷按钮模拟） -->
		<view class="ex-modal-mask" v-if="cheatOpen">
			<view class="ex-modal">
				<view class="ex-modal__alert">!</view>
				<view class="ex-modal__title">切屏警告</view>
				<view class="ex-modal__body">本次考试已记录 2 次切屏行为，累计切屏 3 次将被强制收卷并上报监考端。</view>
				<view class="ex-modal__btns">
					<view class="ex-modal__btn" @click="cheatOpen = false">知道了</view>
					<view class="ex-modal__btn ex-modal__btn--primary" @click="cheatOpen = false">继续作答</view>
				</view>
			</view>
		</view>

		<PreviewFloat current="preview-linear/exam/index" />
	</view>
</template>

<script setup lang="ts">
import { computed, onUnmounted, reactive, ref } from "vue";
import PreviewFloat from "@/components/PreviewFloat.vue";

type QuestionKind = "single" | "multiple" | "judge" | "blank" | "essay";
interface QuestionOption {
	key: string;
	text: string;
}
interface BlankSlot {
	hint: string;
	placeholder: string;
}
interface Question {
	id: number;
	kind: QuestionKind;
	typeLabel: string;
	title: string;
	options?: QuestionOption[];
	blanks?: BlankSlot[];
}

const questions: Question[] = [
	{
		id: 1,
		kind: "single",
		typeLabel: "单选题",
		title: "依据 GB/T 33000-2016，企业安全生产标准化的核心运行模式是？",
		options: [
			{ key: "A", text: "策划、实施、检查、改进的 PDCA 动态循环" },
			{ key: "B", text: "一把手负责、全员签字确认的静态达标" },
			{ key: "C", text: "以年度检查代替日常隐患排查治理" },
			{ key: "D", text: "外包安全机构全权托管运行" },
		],
	},
	{
		id: 2,
		kind: "multiple",
		typeLabel: "多选题",
		title: "下列属于危险作业审批范围的有（多选）？",
		options: [
			{ key: "A", text: "动火作业" },
			{ key: "B", text: "有限空间作业" },
			{ key: "C", text: "临时用电作业" },
			{ key: "D", text: "办公室内纸质文件传阅" },
		],
	},
	{
		id: 3,
		kind: "judge",
		typeLabel: "判断题",
		title: "新员工入职后，可先上岗操作再补做三级安全教育。",
	},
	{
		id: 4,
		kind: "blank",
		typeLabel: "填空题",
		title: "发生生产安全事故后，单位负责人接到报告后，应当于 ____ 小时内向事故发生地监管部门报告；情况紧急时可先 ____ 后补报。",
		blanks: [
			{ hint: "报告时限（数字）", placeholder: "如：1" },
			{ hint: "紧急处置动作", placeholder: "如：电话口头上报" },
		],
	},
	{
		id: 5,
		kind: "essay",
		typeLabel: "简答题",
		title: "结合你所在岗位，简述一次隐患排查的完整流程，并说明闭环管理的关键节点。",
	},
];

const current = ref(0);
const drawerOpen = ref(false);
const cheatOpen = ref(false);

/** 客观题答案：单选存选项键，多选存键数组，判断存「对/错」 */
const answers = reactive<Record<number, string | string[]>>({ 1: "", 2: ["A", "C"], 3: "" });
/** 填空题答案矩阵 */
const blankValues = reactive<Record<number, string[]>>({ 4: ["1", ""] });
/** 简答题答案 */
const essayValues = reactive<Record<number, string>>({ 5: "隐患排查应从人机料法环五个维度展开……" });
/** 标记集合 */
const flags = reactive(new Set<number>([2]));

function isMultiPicked(qid: number, key: string): boolean {
	const v = answers[qid];
	return Array.isArray(v) && v.includes(key);
}

function toggleMulti(qid: number, key: string): void {
	const v = answers[qid];
	if (!Array.isArray(v)) {
		answers[qid] = [key];
		return;
	}
	const idx = v.indexOf(key);
	if (idx >= 0) v.splice(idx, 1);
	else v.push(key);
}

function toggleFlag(qid: number): void {
	if (flags.has(qid)) flags.delete(qid);
	else flags.add(qid);
}

function onSwiperChange(e: { detail: { current: number } }): void {
	current.value = e.detail.current;
}

function prevQuestion(): void {
	if (current.value > 0) current.value -= 1;
}

function nextQuestion(): void {
	if (current.value < questions.length - 1) current.value += 1;
	else cheatOpen.value = true; // 静态演示：末题触发防作弊弹窗展示
}

function jumpTo(idx: number): void {
	current.value = idx;
	drawerOpen.value = false;
}

/** 已作答题数（含填空与简答的非空判定） */
const answeredCount = computed(() => {
	let n = 0;
	for (const q of questions) {
		if (q.kind === "blank") {
			if ((blankValues[q.id] || []).some((s) => s.trim() !== "")) n += 1;
		} else if (q.kind === "essay") {
			if ((essayValues[q.id] || "").trim() !== "") n += 1;
		} else if (q.kind === "multiple") {
			if (Array.isArray(answers[q.id]) && (answers[q.id] as string[]).length > 0) n += 1;
		} else if (answers[q.id]) {
			n += 1;
		}
	}
	return n;
});

/* 倒计时：初始 29 分 41 秒，每秒递减，末 5 分钟进入红色紧急态 */
const remainSeconds = ref(29 * 60 + 41);
const timer = setInterval(() => {
	if (remainSeconds.value > 0) remainSeconds.value -= 1;
}, 1000);
onUnmounted(() => clearInterval(timer));

const clockText = computed(() => {
	const m = Math.floor(remainSeconds.value / 60);
	const s = remainSeconds.value % 60;
	return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
});

/** 倒计时进度：30 分钟总时长 */
const timePercent = computed(() => (remainSeconds.value / (30 * 60)) * 100);

/** 答题卡格子的状态样式 */
function cellClass(idx: number): string {
	const q = questions[idx];
	let state = "todo";
	if (q.kind === "blank") {
		if ((blankValues[q.id] || []).some((s) => s.trim() !== "")) state = "done";
	} else if (q.kind === "essay") {
		if ((essayValues[q.id] || "").trim() !== "") state = "done";
	} else if (q.kind === "multiple") {
		if (Array.isArray(answers[q.id]) && (answers[q.id] as string[]).length > 0) state = "done";
	} else if (answers[q.id]) {
		state = "done";
	}
	if (flags.has(q.id)) state = "flag";
	if (idx === current.value) state = "cur";
	return "ex-cell--" + state;
}

function askSubmit(): void {
	drawerOpen.value = false;
	uni.showToast({ title: "静态演示：交卷不落库", icon: "none" });
}
</script>

<style lang="scss" scoped>
@import "../tokens.scss";

.ex-page {
	height: 100vh;
	display: flex;
	flex-direction: column;
	background: $bg;
}

/* 顶栏 */
.ex-header {
	background: $surface;
	border-bottom: 1px solid $line;
	flex-shrink: 0;
}

.ex-header__inner {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 28rpx 40rpx 20rpx;
}

.ex-header__title {
	font-size: 30rpx;
	font-weight: 800;
	color: $ink;
}

.ex-header__sub {
	margin-top: 6rpx;
	font-size: 22rpx;
	color: $muted;
	font-family: $mono;
}

.ex-clock {
	display: flex;
	align-items: center;
	gap: 12rpx;
	background: $ink;
	border-radius: $radius-inner;
	padding: 14rpx 20rpx;
}

.ex-clock--hot {
	background: $danger;
}

.ex-clock__icon {
	width: 14rpx;
	height: 14rpx;
	border-radius: 50%;
	background: #4ade80;
}

.ex-clock--hot .ex-clock__icon {
	background: #fecaca;
}

.ex-clock__icon--pulse {
	animation: clock-pulse 1s ease-in-out infinite;
}

@keyframes clock-pulse {
	0%,
	100% {
		opacity: 1;
		transform: scale(1);
	}
	50% {
		opacity: 0.4;
		transform: scale(0.8);
	}
}

.ex-clock__text {
	color: #ffffff;
	font-size: 28rpx;
	font-weight: 700;
	font-family: $mono;
	font-variant-numeric: tabular-nums;
}

.ex-timebar {
	height: 4rpx;
	background: $surface-sunken;
}

.ex-timebar__fill {
	height: 100%;
	background: $accent;
	transition: width 1s linear;
}

.ex-clock--hot + .ex-timebar .ex-timebar__fill {
	background: $danger;
}

/* 题目区 */
.ex-swiper {
	flex: 1;
	min-height: 0;
}

.ex-qscroll {
	height: 100%;
}

.ex-question {
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	margin: 24rpx 40rpx;
	padding: 32rpx;
	box-shadow: $shadow-card;
}

.ex-question__head {
	display: flex;
	align-items: center;
	gap: 16rpx;
	margin-bottom: 20rpx;
}

.ex-question__no {
	font-size: 24rpx;
	font-weight: 800;
	color: $accent;
	background: $accent-soft;
	padding: 8rpx 16rpx;
	border-radius: 8rpx;
	font-family: $mono;
}

.ex-question__type {
	font-size: 22rpx;
	color: $muted;
}

.ex-question__flag {
	margin-left: auto;
	font-size: 22rpx;
	color: $muted;
	border: 1px solid $line;
	border-radius: $radius-pill;
	padding: 8rpx 20rpx;
	transition: all 0.2s;
}

.ex-question__flag--on {
	color: #b45309;
	background: $warn-soft;
	border-color: rgba(217, 119, 6, 0.4);
}

.ex-question__title {
	font-size: 30rpx;
	font-weight: 600;
	color: $ink;
	line-height: 1.6;
}

/* 单选 / 多选选项 */
.ex-options {
	margin-top: 28rpx;
	display: flex;
	flex-direction: column;
	gap: 18rpx;
}

.ex-option {
	display: flex;
	align-items: center;
	gap: 20rpx;
	border: 1px solid $line;
	border-radius: $radius-inner;
	padding: 24rpx;
	background: $bg;
	transition: all 0.18s;
}

.ex-option:active {
	transform: scale(0.98);
}

.ex-option--on {
	border-color: $accent-line;
	background: $accent-soft;
}

.ex-option__key {
	width: 52rpx;
	height: 52rpx;
	border-radius: 10rpx;
	background: $surface;
	border: 1px solid $line-strong;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 26rpx;
	font-weight: 700;
	color: $muted;
	font-family: $mono;
	flex-shrink: 0;
}

.ex-option__key--on {
	background: $accent;
	border-color: $accent;
	color: #ffffff;
}

.ex-option__text {
	font-size: 27rpx;
	color: $ink-2;
	line-height: 1.5;
}

/* 多选方角复选框 */
.ex-option__check {
	width: 36rpx;
	height: 36rpx;
	border-radius: 8rpx;
	border: 2px solid $line-strong;
	background: $surface;
	flex-shrink: 0;
	position: relative;
	transition: all 0.18s;
}

.ex-option__check--on {
	border-color: $accent;
	background: $accent;
}

.ex-option__check--on::after {
	content: "";
	position: absolute;
	left: 12rpx;
	top: 5rpx;
	width: 8rpx;
	height: 16rpx;
	border: solid #ffffff;
	border-width: 0 3px 3px 0;
	transform: rotate(45deg);
}

/* 判断题双胶囊 */
.ex-judge {
	display: flex;
	gap: 24rpx;
	margin-top: 32rpx;
}

.ex-judge__btn {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 8rpx;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 32rpx 0;
	background: $bg;
	transition: all 0.18s;
}

.ex-judge__btn:active {
	transform: scale(0.97);
}

.ex-judge__btn--on.ex-judge__btn--yes {
	border-color: rgba(16, 185, 129, 0.5);
	background: $ok-soft;
}

.ex-judge__btn--on.ex-judge__btn--no {
	border-color: rgba(220, 38, 38, 0.5);
	background: $danger-soft;
}

.ex-judge__mark {
	width: 72rpx;
	height: 72rpx;
	border-radius: 50%;
	background: $surface;
	border: 1px solid $line-strong;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	font-weight: 800;
	color: $muted;
}

.ex-judge__btn--yes .ex-judge__mark {
	color: $ok;
}

.ex-judge__btn--no .ex-judge__mark {
	color: $danger;
}

.ex-judge__label {
	font-size: 26rpx;
	font-weight: 600;
	color: $ink-2;
}

/* 填空题 */
.ex-blanks {
	margin-top: 28rpx;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.ex-blank__label {
	font-size: 24rpx;
	color: $muted;
	margin-bottom: 12rpx;
}

.ex-blank__input {
	width: 100%;
	height: 84rpx;
	box-sizing: border-box;
	background: $bg;
	border: 1px solid $line;
	border-radius: $radius-inner;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: $ink;
}

.ex-ph {
	color: $faint;
}

/* 简答题 */
.ex-essay {
	margin-top: 28rpx;
}

.ex-essay__area {
	width: 100%;
	height: 320rpx;
	box-sizing: border-box;
	background: $bg;
	border: 1px solid $line;
	border-radius: $radius-inner;
	padding: 24rpx;
	font-size: 27rpx;
	line-height: 1.6;
	color: $ink;
}

.ex-essay__count {
	margin-top: 12rpx;
	text-align: right;
	font-size: 22rpx;
	color: $faint;
	font-family: $mono;
}

.ex-essay__count--hot {
	color: $danger;
	font-weight: 700;
}

/* 底部操作条 */
.ex-footer {
	flex-shrink: 0;
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 24rpx;
	background: $surface;
	border-top: 1px solid $line;
	padding: 20rpx 40rpx calc(20rpx + env(safe-area-inset-bottom));
}

.ex-footer__drawer {
	display: flex;
	align-items: center;
	gap: 16rpx;
	font-size: 26rpx;
	color: $ink-2;
	padding: 16rpx 24rpx;
	border-radius: $radius-inner;
	border: 1px solid $line;
}

.ex-footer__grid {
	display: grid;
	grid-template-columns: repeat(2, 14rpx);
	gap: 6rpx;
}

.ex-footer__cell {
	width: 14rpx;
	height: 14rpx;
	border-radius: 4rpx;
	background: $accent;
}

.ex-footer__nav {
	display: flex;
	gap: 20rpx;
	flex: 1;
	max-width: 60%;
}

.ex-nav {
	flex: 1;
	text-align: center;
	font-size: 27rpx;
	font-weight: 600;
	padding: 22rpx 0;
	border-radius: $radius-inner;
	border: 1px solid $line;
	color: $ink-2;
}

.ex-nav--disabled {
	opacity: 0.4;
}

.ex-nav--primary {
	background: $accent;
	border-color: $accent;
	color: #ffffff;
}

/* 答题卡抽屉 */
.ex-drawer-mask {
	position: fixed;
	inset: 0;
	background: rgba(15, 23, 42, 0.5);
	z-index: 60;
}

.ex-drawer {
	position: fixed;
	left: 0;
	right: 0;
	bottom: 0;
	height: 60vh;
	background: $surface;
	border-radius: 28rpx 28rpx 0 0;
	z-index: 61;
	display: flex;
	flex-direction: column;
	transform: translateY(100%);
	transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
}

.ex-drawer--open {
	transform: translateY(0);
}

.ex-drawer__grabber {
	width: 72rpx;
	height: 8rpx;
	border-radius: 4rpx;
	background: $line-strong;
	margin: 20rpx auto 0;
	flex-shrink: 0;
}

.ex-drawer__head {
	padding: 24rpx 40rpx 8rpx;
	flex-shrink: 0;
}

.ex-drawer__title {
	font-size: 32rpx;
	font-weight: 800;
	color: $ink;
}

.ex-drawer__legend {
	display: flex;
	gap: 28rpx;
	margin-top: 20rpx;
}

.lg-item {
	display: flex;
	align-items: center;
	gap: 10rpx;
	font-size: 22rpx;
	color: $muted;
}

.lg-chip {
	width: 22rpx;
	height: 22rpx;
	border-radius: 6rpx;
}

.lg-chip--cur {
	background: $accent;
}

.lg-chip--done {
	background: rgba(29, 99, 255, 0.22);
}

.lg-chip--flag {
	background: #fbbf24;
}

.lg-chip--todo {
	background: $surface-sunken;
	border: 1px solid $line-strong;
}

.ex-drawer__scroll {
	flex: 1;
	min-height: 0;
}

.ex-matrix {
	display: grid;
	grid-template-columns: repeat(5, 1fr);
	gap: 20rpx;
	padding: 20rpx 40rpx;
}

.ex-cell {
	aspect-ratio: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: $radius-inner;
	font-size: 28rpx;
	font-weight: 700;
	font-family: $mono;
}

.ex-cell--todo {
	background: $surface-sunken;
	border: 1px solid $line;
	color: $muted;
}

.ex-cell--done {
	background: rgba(29, 99, 255, 0.16);
	color: $accent;
}

.ex-cell--flag {
	background: #fef3c7;
	color: #b45309;
}

.ex-cell--cur {
	background: $accent;
	color: #ffffff;
	box-shadow: 0 8rpx 24rpx rgba(29, 99, 255, 0.35);
}

.ex-drawer__foot {
	padding: 20rpx 40rpx calc(24rpx + env(safe-area-inset-bottom));
	flex-shrink: 0;
}

.ex-submit {
	text-align: center;
	background: $accent;
	color: #ffffff;
	font-size: 30rpx;
	font-weight: 700;
	border-radius: $radius-inner;
	padding: 26rpx 0;
}

/* 防作弊告警弹窗 */
.ex-modal-mask {
	position: fixed;
	inset: 0;
	background: rgba(15, 23, 42, 0.6);
	z-index: 70;
	display: flex;
	align-items: center;
	justify-content: center;
}

.ex-modal {
	width: 580rpx;
	background: $surface;
	border-radius: $radius-card;
	padding: 48rpx 40rpx 40rpx;
	box-shadow: $shadow-float;
}

.ex-modal__alert {
	width: 88rpx;
	height: 88rpx;
	border-radius: 50%;
	background: $danger-soft;
	color: $danger;
	font-size: 44rpx;
	font-weight: 800;
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 auto 24rpx;
}

.ex-modal__title {
	text-align: center;
	font-size: 32rpx;
	font-weight: 800;
	color: $ink;
}

.ex-modal__body {
	margin-top: 16rpx;
	text-align: center;
	font-size: 25rpx;
	color: $muted;
	line-height: 1.65;
}

.ex-modal__btns {
	display: flex;
	gap: 20rpx;
	margin-top: 40rpx;
}

.ex-modal__btn {
	flex: 1;
	text-align: center;
	font-size: 27rpx;
	font-weight: 600;
	padding: 22rpx 0;
	border-radius: $radius-inner;
	border: 1px solid $line;
	color: $ink-2;
}

.ex-modal__btn--primary {
	background: $accent;
	border-color: $accent;
	color: #ffffff;
}
</style>
