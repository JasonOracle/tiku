<template>
	<view class="exam-apple">
		<!-- 沉浸式微渐变通顶 Header -->
		<CustomHeader :title="paperTitle" show-back variant="gradient" @back="handleBack">
			<template #right>
				<view class="ex-submit-pill" hover-class="ex-submit-pill--pressed" @click="handleSubmitTap">
					<text class="ex-submit-pill__text">{{ submitting ? "交卷中" : "交卷" }}</text>
				</view>
			</template>
		</CustomHeader>

		<!-- 钛金考场状态条：已答进度 + 倒计时 -->
		<view v-if="pageStatus === 'ready'" class="ex-status">
			<view class="ex-status__info">
				<text class="ex-status__text">已答 {{ answeredIds.length }} / {{ questions.length }}</text>
				<view class="ex-timer" :class="{ 'ex-timer--urgent': isUrgent }">
					<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
						<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
						<polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
					</svg>
					<text class="ex-timer__text">{{ countdownText }}</text>
				</view>
			</view>
			<view class="ex-progress">
				<view class="ex-progress__inner" :style="{ width: `${answeredRatio}%` }" />
			</view>
		</view>

		<!-- 就绪态：单题聚焦 swiper -->
		<block v-if="pageStatus === 'ready'">
			<swiper class="ex-swiper" :current="currentIndex" :duration="260" @change="handleSwiperChange">
				<swiper-item v-for="(question, index) in questions" :key="question.id" class="ex-swiper-item">
					<scroll-view class="ex-scroll" scroll-y>
						<view class="ex-card-wrap">
							<QuestionCard
								:question="question"
								:model-value="answers[question.id] ?? ''"
								:index="index"
								:total="questions.length"
								@update:model-value="handleAnswerUpdate(index, $event)"
							/>
						</view>
					</scroll-view>
				</swiper-item>
			</swiper>

			<!-- 底部悬浮控制台 -->
			<view class="ex-footer">
				<view
					class="ex-nav-btn"
					:class="{ 'ex-nav-btn--disabled': currentIndex === 0 }"
					hover-class="ex-nav-btn--pressed"
					@click="goPrev"
				>
					<text class="ex-nav-btn__text">上一题</text>
				</view>

				<view class="ex-sheet-btn" hover-class="ex-sheet-btn--pressed" @click="openSheet">
					<text class="ex-sheet-btn__index">{{ currentIndex + 1 }} / {{ questions.length }}</text>
					<text class="ex-sheet-btn__label">答题卡</text>
				</view>

				<view
					class="ex-nav-btn"
					:class="{ 'ex-nav-btn--disabled': currentIndex >= questions.length - 1 }"
					hover-class="ex-nav-btn--pressed"
					@click="goNext"
				>
					<text class="ex-nav-btn__text">下一题</text>
				</view>
			</view>
		</block>

		<!-- 加载 / 加载失败 / 已提交不可重入 -->
		<view v-else class="ex-state">
			<PageState
				v-if="pageStatus === 'blocked'"
				status="empty"
				title="该试卷你已提交过"
				description="每份试卷每人仅可作答一次，可前往「我的测试」查看作答记录"
				action-text="前往我的测试"
				@action="goMyRecords"
			/>
			<PageState
				v-else
				:status="pageStatus === 'loading' ? 'loading' : 'error'"
				:title="stateTitle"
				:description="stateDescription"
				action-text="重新加载"
				@action="startExam"
			/>
		</view>

		<!-- 交卷成功后的过渡遮罩 -->
		<view v-if="finished" class="ex-finish-mask" @click="goReport">
			<view class="ex-finish-card">
				<text class="ex-finish-card__title">交卷成功</text>
				<text class="ex-finish-card__score">{{ finishedScoreText }}</text>
				<text class="ex-finish-card__tip">点击立即前往成绩报告</text>
			</view>
		</view>

		<!-- 答题卡抽屉 -->
		<AnswerSheet
			v-model="sheetVisible"
			:questions="questions"
			:answered-ids="answeredIds"
			:current-index="currentIndex"
			@select="handleJumpTo"
		/>

		<!-- 防作弊告警弹窗 -->
		<wd-message-box />
		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 全面升级在线考场为 Apple 钛金微光风，采用微渐变顶栏、柔和进度指示器与立体控制台; 2. 严格对接真实后端 GET /api/v1/member/tasks/{id}/entry 与 POST /api/v1/member/task-records/submit; 3. 包含完整防切屏告警与倒计时物理递减机制]
 */
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { onLoad, onHide } from "@dcloudio/uni-app";
import { useMessage } from "wot-design-uni";
import AnswerSheet from "@/components/AnswerSheet.vue";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import QuestionCard from "@/components/QuestionCard.vue";
import {
	fetchExamEntry,
	submitExam,
	type ExamQuestion,
	type UserAnswerItem,
} from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";
import { formatDuration } from "@/utils/format";

type PageStatus = "loading" | "ready" | "error" | "blocked";

const message = useMessage();
const toast = useGlobalToast();

const taskId = ref(0);
const recordId = ref(0);
const paperTitle = ref("在线测评");
const pageStatus = ref<PageStatus>("loading");
const stateTitle = ref("正在准备考场");
const stateDescription = ref("正在安全同步服务端考卷与倒计时基准...");

const questions = ref<ExamQuestion[]>([]);
const answers = ref<Record<number, string | string[]>>({});
const currentIndex = ref(0);
const sheetVisible = ref(false);
const submitting = ref(false);
const finished = ref(false);
const finishedScore = ref<number | null>(null);

const remainingSeconds = ref(0);
let timerHandle: number | null = null;
const isUrgent = computed(() => remainingSeconds.value > 0 && remainingSeconds.value <= 300);

const switchScreenCount = ref(0);
const MAX_SWITCH_LIMIT = 3;

const answeredIds = computed(() => {
	const currentAnswers = answers.value;
	return questions.value
		.filter((q) => {
			const value = currentAnswers[q.id];
			if (Array.isArray(value)) return value.length > 0 && value.some((v) => String(v).trim().length > 0);
			return typeof value === "string" && value.trim().length > 0;
		})
		.map((q) => q.id);
});

const answeredRatio = computed(() => {
	if (questions.value.length === 0) return 0;
	return Math.min(100, Math.round((answeredIds.value.length / questions.value.length) * 100));
});

const countdownText = computed(() => {
	if (remainingSeconds.value <= 0) return "已截止";
	return formatDuration(remainingSeconds.value);
});

const finishedScoreText = computed(() => {
	return finishedScore.value !== null ? `${finishedScore.value} 分` : "成绩正在安全核验中";
});

function startTimer(): void {
	stopTimer();
	if (remainingSeconds.value <= 0) return;
	timerHandle = setInterval(() => {
		if (remainingSeconds.value > 1) {
			remainingSeconds.value -= 1;
		} else {
			remainingSeconds.value = 0;
			stopTimer();
			handleTimeUp();
		}
	}, 1000) as unknown as number;
}

function stopTimer(): void {
	if (timerHandle !== null) {
		clearInterval(timerHandle);
		timerHandle = null;
	}
}

function handleTimeUp(): void {
	toast.warning("答题时间已到，系统正在自动为您提交试卷");
	doSubmit(true);
}

async function startExam(): Promise<void> {
	if (taskId.value <= 0) {
		pageStatus.value = "error";
		stateTitle.value = "试卷不存在";
		stateDescription.value = "缺少有效的测评任务参数，无法开考";
		return;
	}

	pageStatus.value = "loading";
	stateTitle.value = "正在加载试卷";
	stateDescription.value = "安全同步服务端考卷与倒计时中...";

	try {
		const res = await fetchExamEntry(taskId.value);
		recordId.value = res.my_record_id || 0;
		paperTitle.value = res.title || res.exam_title || paperTitle.value;
		questions.value = res.questions || [];

		// 恢复暂存答案
		if (res.my_answers && Array.isArray(res.my_answers)) {
			const restored: Record<number, string | string[]> = {};
			for (const ans of res.my_answers) {
				restored[ans.resource_id] = ans.answer;
			}
			answers.value = restored;
		}

		// 根据服务端时间差推导权威倒计时
		if (res.is_timed && res.time_limit > 0) {
			const startedAt = new Date(res.started_at).getTime();
			const serverNow = new Date(res.server_now).getTime();
			const elapsedSec = Math.max(0, Math.floor((serverNow - startedAt) / 1000));
			remainingSeconds.value = Math.max(0, res.time_limit * 60 - elapsedSec);
		} else {
			remainingSeconds.value = 0;
		}

		pageStatus.value = "ready";
		startTimer();
	} catch (error) {
		const msg = error instanceof Error && error.message ? error.message : "";
		if (msg.includes("已完成") || msg.includes("已提交") || msg.includes("不可重入")) {
			pageStatus.value = "blocked";
		} else {
			pageStatus.value = "error";
			stateTitle.value = "考卷加载失败";
			stateDescription.value = msg || "无法连接至考场服务器，请重试";
		}
	}
}

function handleSwiperChange(event: { detail: { current: number } }): void {
	currentIndex.value = event.detail.current;
}

function handleAnswerUpdate(questionIndex: number, value: string | string[]): void {
	const targetQuestion = questions.value[questionIndex];
	if (!targetQuestion) return;
	answers.value = { ...answers.value, [targetQuestion.id]: value };
}

function goPrev(): void {
	if (currentIndex.value > 0) currentIndex.value -= 1;
}

function goNext(): void {
	if (currentIndex.value < questions.value.length - 1) currentIndex.value += 1;
}

function openSheet(): void {
	sheetVisible.value = true;
}

function handleJumpTo(index: number): void {
	currentIndex.value = index;
}

function handleBack(): void {
	message.confirm({
		title: "离开考场确认",
		msg: "作答正在进行中，退出后倒计时不会暂停，确定暂时离开吗？",
		confirmButtonText: "离开",
		cancelButtonText: "继续作答",
	}).then(() => {
		stopTimer();
		uni.navigateBack({ delta: 1 });
	}).catch(() => {});
}

function handleSubmitTap(): void {
	if (submitting.value) return;
	const total = questions.value.length;
	const answered = answeredIds.value.length;
	const unAnswered = total - answered;

	const msg = unAnswered > 0
		? `当前尚有 ${unAnswered} 道题目未作答，确定交卷吗？交卷后将不可更改。`
		: "所有题目均已完成，确认现在提交试卷吗？";

	message.confirm({
		title: "交卷确认",
		msg,
		confirmButtonText: "确认交卷",
		cancelButtonText: "再检查一下",
	}).then(() => {
		doSubmit(false);
	}).catch(() => {});
}

async function doSubmit(force = false): Promise<void> {
	if (submitting.value) return;
	submitting.value = true;

	const payloadAnswers: UserAnswerItem[] = [];
	for (const q of questions.value) {
		const raw = answers.value[q.id];
		if (raw !== undefined && raw !== null && raw !== "") {
			payloadAnswers.push({ resource_id: q.id, answer: raw });
		}
	}

	try {
		const result = await submitExam({
			task_id: taskId.value,
			time_spent: 0,
			answers: payloadAnswers,
		});

		stopTimer();
		finishedScore.value = result.score;
		finished.value = true;
		toast.success("交卷成功");

		setTimeout(() => {
			goReport();
		}, 1200);
	} catch (error) {
		const msg = error instanceof Error && error.message ? error.message : "交卷失败，请检查网络重试";
		toast.error(msg);
	} finally {
		submitting.value = false;
	}
}

function goReport(): void {
	if (recordId.value > 0) {
		uni.redirectTo({ url: `/pages/report/index?record_id=${recordId.value}` });
	} else {
		uni.switchTab({ url: "/pages/records/index" });
	}
}

function goMyRecords(): void {
	uni.switchTab({ url: "/pages/records/index" });
}

// 模拟防切屏监控
onHide(() => {
	if (pageStatus.value === "ready" && !finished.value) {
		switchScreenCount.value += 1;
		if (switchScreenCount.value >= MAX_SWITCH_LIMIT) {
			toast.error("切屏次数超限，系统已强制自动交卷");
			doSubmit(true);
		} else {
			toast.warning(`检测到离开考场，已记录警告 (${switchScreenCount.value}/${MAX_SWITCH_LIMIT})`);
		}
	}
});

onLoad((query) => {
	if (query?.task_id) taskId.value = Number(query.task_id);
	if (query?.title) paperTitle.value = decodeURIComponent(query.title);
	startExam();
});

onBeforeUnmount(() => {
	stopTimer();
});
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.exam-apple {
	position: relative;
	min-height: 100vh;
	background: $bg;
	display: flex;
	flex-direction: column;
}

.ex-submit-pill {
	background: rgba(255, 255, 255, 0.9);
	border-radius: $radius-pill;
	padding: 8rpx 24rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);

	&--pressed {
		opacity: 0.8;
	}

	&__text {
		font-size: 24rpx;
		font-weight: 700;
		color: $accent;
	}
}

/* 考场状态条 */
.ex-status {
	background: rgba(255, 255, 255, 0.88);
	backdrop-filter: $glass-blur;
	border-bottom: 1px solid $line;
	padding: 16rpx 32rpx 20rpx;

	&__info {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 12rpx;
	}

	&__text {
		font-size: 24rpx;
		font-weight: 600;
		color: $ink-2;
	}
}

.ex-timer {
	display: flex;
	align-items: center;
	gap: 8rpx;
	color: $accent;

	&--urgent {
		color: $danger;
		animation: blink 1.2s ease-in-out infinite;
	}

	&__text {
		font-size: 24rpx;
		font-weight: 700;
		font-feature-settings: "tnum";
	}
}

@keyframes blink {
	0%, 100% { opacity: 1; }
	50% { opacity: 0.45; }
}

.ex-progress {
	height: 8rpx;
	border-radius: 4rpx;
	background: $surface-sunken;
	overflow: hidden;

	&__inner {
		height: 100%;
		background: $gradient;
		border-radius: 4rpx;
		transition: width 0.3s ease;
	}
}

.ex-swiper {
	flex: 1;
	height: calc(100vh - 300rpx);
}

.ex-swiper-item {
	width: 100%;
	height: 100%;
}

.ex-scroll {
	width: 100%;
	height: 100%;
}

.ex-card-wrap {
	padding: 24rpx 32rpx 140rpx;
}

/* 底部悬浮控制台 */
.ex-footer {
	position: fixed;
	left: 32rpx;
	right: 32rpx;
	bottom: calc(24rpx + env(safe-area-inset-bottom));
	height: 100rpx;
	background: rgba(255, 255, 255, 0.92);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: $radius-pill;
	padding: 8rpx 24rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;
	box-shadow: $shadow-float;
	z-index: 10;
}

.ex-nav-btn {
	padding: 14rpx 28rpx;
	border-radius: $radius-pill;
	background: $surface-sunken;

	&--disabled {
		opacity: 0.35;
		pointer-events: none;
	}

	&--pressed {
		background: #e2e8f0;
	}

	&__text {
		font-size: 24rpx;
		font-weight: 600;
		color: $ink-2;
	}
}

.ex-sheet-btn {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 6rpx 24rpx;

	&--pressed {
		opacity: 0.7;
	}

	&__index {
		font-size: 22rpx;
		font-weight: 800;
		color: $accent;
	}

	&__label {
		font-size: 18rpx;
		color: $muted;
	}
}

.ex-finish-mask {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.65);
	backdrop-filter: blur(16px);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 99;
}

.ex-finish-card {
	width: 540rpx;
	background: #ffffff;
	border-radius: 36rpx;
	padding: 48rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 16rpx;
	box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.25);

	&__title {
		font-size: 36rpx;
		font-weight: 800;
		color: $ink;
	}

	&__score {
		font-size: 48rpx;
		font-weight: 900;
		color: $ok;
	}

	&__tip {
		font-size: 22rpx;
		color: $muted;
	}
}
</style>
