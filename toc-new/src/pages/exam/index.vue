<template>
	<view class="exam">
		<CustomHeader :title="paperTitle" show-back variant="gradient" @back="handleBack">
			<template #right>
				<view class="exam__submit" hover-class="exam__submit--pressed" @click="handleSubmitTap">
					<text class="exam__submit-text">{{ submitting ? "交卷中" : "交卷" }}</text>
				</view>
			</template>
		</CustomHeader>

		<!-- 考场状态条：已答进度 + 倒计时 -->
		<view v-if="pageStatus === 'ready'" class="exam__status">
			<text class="exam__status-text">已答 {{ answeredIds.length }} / {{ questions.length }}</text>
			<view class="exam__progress">
				<view class="exam__progress-inner" :style="{ width: `${answeredRatio}%` }" />
			</view>
			<view class="exam__timer" :class="{ 'exam__timer--urgent': isUrgent }">
				<text class="exam__timer-text">{{ countdownText }}</text>
			</view>
		</view>

		<!-- 就绪态：单题聚焦 swiper -->
		<block v-if="pageStatus === 'ready'">
			<swiper class="exam__swiper" :current="currentIndex" :duration="260" @change="handleSwiperChange">
				<swiper-item v-for="(question, index) in questions" :key="question.id" class="exam__swiper-item">
					<scroll-view class="exam__scroll" scroll-y>
						<view class="exam__card-wrap">
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

			<view class="exam__footer">
				<view
					class="exam__nav"
					:class="{ 'exam__nav--disabled': currentIndex === 0 }"
					hover-class="exam__nav--pressed"
					@click="goPrev"
				>
					<text class="exam__nav-text">上一题</text>
				</view>

				<view class="exam__sheet-entry" hover-class="exam__sheet-entry--pressed" @click="openSheet">
					<text class="exam__sheet-index">{{ currentIndex + 1 }} / {{ questions.length }}</text>
					<text class="exam__sheet-label">答题卡</text>
				</view>

				<view
					class="exam__nav"
					:class="{ 'exam__nav--disabled': currentIndex >= questions.length - 1 }"
					hover-class="exam__nav--pressed"
					@click="goNext"
				>
					<text class="exam__nav-text">下一题</text>
				</view>
			</view>
		</block>

		<!-- 加载 / 加载失败 / 已提交不可重入 -->
		<view v-else class="exam__state">
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

		<!-- 交卷成功后的过渡遮罩，点击可立即前往记录页 -->
		<view v-if="finished" class="exam__finish-mask" @click="goReport">
			<view class="exam__finish-card">
				<text class="exam__finish-title">交卷成功</text>
				<text class="exam__finish-score">{{ finishedScoreText }}</text>
				<text class="exam__finish-tip">正在前往成绩报告</text>
			</view>
		</view>

		<AnswerSheet
			v-model="sheetVisible"
			:questions="questions"
			:answered-ids="answeredIds"
			:current-index="currentIndex"
			@select="handleJumpTo"
		/>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 交卷成功后由「跳我的测试」改为 redirectTo 成绩报告页并携带 record_id（redirectTo 出栈替换，避免返回退回到已交卷的考场）; 2. 已提交不可重入态仍保留前往「我的测试」的引导]
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 由占位页完全重写为真实考场：入考拉题与续答回填、单题聚焦 swiper、半屏答题卡跳题、服务端权威倒计时、切屏防作弊; 2. 交卷二次确认与归零自动交卷，成功后跳「我的测试」; 3. 补齐加载/失败/已提交不可重入三种状态分支]
 */
import { computed, onMounted, onUnmounted, ref } from "vue";
import { onHide, onLoad, onShow, onUnload } from "@dcloudio/uni-app";
import AnswerSheet from "@/components/AnswerSheet.vue";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import QuestionCard from "@/components/QuestionCard.vue";
import { fetchExamEntry, submitExam, type ExamEntryResult, type ExamQuestion, type ExamSubmitPayload, type UserAnswerItem } from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";
import { parseServerTime } from "@/utils/format";

type PageStatus = "loading" | "ready" | "error" | "blocked";
type AnswerValue = string | string[];
type SwiperChangeEvent = { detail: { current: number } };

/** 倒计时刷新间隔（毫秒） */
const TICK_INTERVAL = 1000;
/** 切屏警告节流窗口：H5 端 visibilitychange 与 onHide 会先后触发，必须避免连弹两次 */
const WARN_THROTTLE_MS = 1500;
/** 剩余时间进入最后五分钟转为警示态 */
const URGENT_THRESHOLD_SECONDS = 300;
/** 交卷成功后停留多久再跳转记录页，留给轻提示展示时间 */
const REDIRECT_DELAY_MS = 1400;

const toast = useGlobalToast();

const pageStatus = ref<PageStatus>("loading");
const questions = ref<ExamQuestion[]>([]);
const answers = ref<Record<number, AnswerValue>>({});
const currentIndex = ref(0);
const sheetVisible = ref(false);
const submitting = ref(false);
const finished = ref(false);
const offscreenWarnings = ref(0);
const remainingSeconds = ref(0);
const hasCountdown = ref(false);
const submittedScore = ref<number | null>(null);
const submittedStatus = ref("");
const submittedRecordId = ref(0);
const stateTitle = ref("");
const stateDescription = ref("");

const taskId = ref(0);
const paperTitle = ref("考场");
const localDeadlineTs = ref(0);

let tickTimer: ReturnType<typeof setInterval> | null = null;
let redirectTimer: ReturnType<typeof setTimeout> | null = null;
let lastWarnAt = 0;
/** 开考接口返回时服务端已经走过的秒数，用于拼出真实用时 */
let entryElapsedSeconds = 0;
/** 收到开考响应的本地时刻，与 entryElapsedSeconds 相加得到当前用时 */
let entryLoadedAt = 0;

const answeredIds = computed<number[]>(() =>
	questions.value
		.filter((question) => {
			const value = answers.value[question.id];
			if (Array.isArray(value)) return value.some((item) => String(item).trim() !== "");
			return typeof value === "string" && value.trim() !== "";
		})
		.map((question) => question.id)
);

const unansweredCount = computed(() => questions.value.length - answeredIds.value.length);

const answeredRatio = computed(() => {
	if (questions.value.length === 0) return 0;
	return Math.round((answeredIds.value.length / questions.value.length) * 100);
});

const countdownText = computed(() => {
	if (!hasCountdown.value) return "不限时";
	const total = Math.max(0, remainingSeconds.value);
	const pad = (num: number): string => String(num).padStart(2, "0");
	const hours = Math.floor(total / 3600);
	const minutes = Math.floor((total % 3600) / 60);
	const seconds = total % 60;
	return hours > 0 ? `${pad(hours)}:${pad(minutes)}:${pad(seconds)}` : `${pad(minutes)}:${pad(seconds)}`;
});

const isUrgent = computed(() => hasCountdown.value && remainingSeconds.value <= URGENT_THRESHOLD_SECONDS);

const finishedScoreText = computed(() => (submittedStatus.value === "pending_verification" ? "等待核验" : `${submittedScore.value ?? 0} 分`));

onLoad((query) => {
	const rawId = query?.task_id;
	taskId.value = Number(rawId) || 0;
	const rawTitle = query?.title;
	if (typeof rawTitle === "string" && rawTitle) {
		paperTitle.value = rawTitle;
	}
	startExam();
});

onShow(() => {
	// 从后台切回时立即按墙钟补算一次，抵消定时器被节流造成的滞后
	refreshRemaining();
});

onHide(() => {
	warnOffscreen("检测到离开考场");
});

onMounted(() => {
	if (typeof document !== "undefined") {
		document.addEventListener("visibilitychange", handleVisibilityChange);
	}
});

onUnmounted(() => {
	removeVisibilityListener();
});

onUnload(() => {
	// 本页两类副作用的唯一收口点：轮询定时器与跳转延时器、以及全局事件监听
	stopTick();
	clearRedirectTimer();
	removeVisibilityListener();
});

function removeVisibilityListener(): void {
	if (typeof document !== "undefined") {
		document.removeEventListener("visibilitychange", handleVisibilityChange);
	}
}

function handleVisibilityChange(): void {
	if (typeof document !== "undefined" && document.visibilityState === "hidden") {
		warnOffscreen("检测到切出考场");
	}
}

/**
 * 切屏防作弊警告。
 * 以 visibilitychange 为主路径、页面 onHide 为兜底，两者共用同一个节流窗口，
 * 保证一次切屏只警告并计数一次，不会连弹两条提示。
 */
function warnOffscreen(reason: string): void {
	if (pageStatus.value !== "ready" || finished.value) return;
	const now = Date.now();
	if (now - lastWarnAt < WARN_THROTTLE_MS) return;
	lastWarnAt = now;
	offscreenWarnings.value += 1;
	toast.warning(`${reason}，已记录 ${offscreenWarnings.value} 次`);
}

async function startExam(): Promise<void> {
	if (!taskId.value) {
		pageStatus.value = "error";
		stateTitle.value = "缺少测评编号";
		stateDescription.value = "未能从上一页获取到测评信息，请返回列表后重新进入";
		return;
	}

	pageStatus.value = "loading";
	stateTitle.value = "";
	stateDescription.value = "";

	try {
		const data: ExamEntryResult = await fetchExamEntry(taskId.value);
		paperTitle.value = data.exam_title || data.title || paperTitle.value;
		questions.value = data.questions ?? [];
		answers.value = buildAnswerMap(data.my_answers ?? []);
		setupCountdown(data);

		// 已提交过的试卷不可重入，直接拦截并引导到记录页
		if (data.my_status && data.my_status !== "pending") {
			stopTick();
			pageStatus.value = "blocked";
			return;
		}

		if (questions.value.length === 0) {
			stopTick();
			pageStatus.value = "error";
			stateTitle.value = "试卷暂无题目";
			stateDescription.value = "该试卷尚未配置题目，请联系企业管理员处理";
			return;
		}

		// 先切就绪态再立刻刷新一次倒计时，否则首帧会显示 00:00 空窗
		pageStatus.value = "ready";
		refreshRemaining();
		startTick();
	} catch {
		// 失败原因已由请求层统一轻提示，这里只负责切换到错误态，避免白屏
		stopTick();
		pageStatus.value = "error";
	}
}

/** 续答回填：仅「继续测试」把记录退回 pending 后 my_answers 才非空 */
function buildAnswerMap(list: UserAnswerItem[]): Record<number, AnswerValue> {
	const map: Record<number, AnswerValue> = {};
	list.forEach((item) => {
		if (!item || item.resource_id === undefined || item.resource_id === null) return;
		map[Number(item.resource_id)] = Array.isArray(item.answer) ? item.answer.map((value) => String(value)) : String(item.answer ?? "");
	});
	return map;
}

/**
 * 换算倒计时基准。
 * 服务端下发的时间串同源同格式，先用「服务端截止时刻 - 服务端当前时刻」求出剩余时长，
 * 再叠加到本地时钟上，避免本地与服务端存在时钟偏差时倒计时整体偏移。
 */
function setupCountdown(data: ExamEntryResult): void {
	const serverNow = parseServerTime(data.server_now) || Date.now();
	const startedAt = parseServerTime(data.started_at) || serverNow;
	const paperDeadline = parseServerTime(data.deadline);
	const limitSeconds = data.is_timed ? (data.time_limit ?? 0) * 60 : 0;

	const candidates: number[] = [];
	if (limitSeconds > 0) candidates.push(startedAt + limitSeconds * 1000);
	if (paperDeadline > 0) candidates.push(paperDeadline);

	if (candidates.length === 0) {
		hasCountdown.value = false;
		localDeadlineTs.value = 0;
		remainingSeconds.value = 0;
		return;
	}

	// 记录服务端口径的已用时长，用于交卷时填充 time_spent（后端会忽略该值，仅按契约要求携带）
	entryElapsedSeconds = Math.max(0, Math.round((serverNow - startedAt) / 1000));
	entryLoadedAt = Date.now();

	const serverDeadline = Math.min(...candidates);
	hasCountdown.value = true;
	localDeadlineTs.value = entryLoadedAt + Math.max(0, serverDeadline - serverNow);
	refreshRemaining();
}

/** 每次都用墙钟差值重算剩余秒数，后台被节流也不会累积误差 */
function refreshRemaining(): void {
	if (!hasCountdown.value) return;
	const remain = Math.max(0, Math.round((localDeadlineTs.value - Date.now()) / 1000));
	remainingSeconds.value = remain;
	// 仅在正式开考后触发自动交卷，避免加载阶段或已交卷后被重复触发
	if (remain <= 0 && pageStatus.value === "ready") {
		handleTimeUp();
	}
}

function startTick(): void {
	stopTick();
	tickTimer = setInterval(refreshRemaining, TICK_INTERVAL);
}

function stopTick(): void {
	if (tickTimer !== null) {
		clearInterval(tickTimer);
		tickTimer = null;
	}
}

function clearRedirectTimer(): void {
	if (redirectTimer !== null) {
		clearTimeout(redirectTimer);
		redirectTimer = null;
	}
}

function handleTimeUp(): void {
	if (finished.value || submitting.value) return;
	stopTick();
	toast.warning("考试时间已结束，正在自动交卷");
	submitPaper(true);
}

/**
 * 写入某一题的答案。
 * 必须按题序下标定位（而非取 currentIndex），因为 swiper 的滑动动画期间 currentIndex 尚未更新，
 * 用 currentIndex 会把答案写到上一题上。
 */
function handleAnswerUpdate(index: number, value: AnswerValue): void {
	const question = questions.value[index];
	if (!question) return;
	answers.value[question.id] = value;
}

function handleSwiperChange(event: SwiperChangeEvent): void {
	currentIndex.value = event.detail.current;
}

function goPrev(): void {
	if (currentIndex.value <= 0) return;
	currentIndex.value -= 1;
}

function goNext(): void {
	if (currentIndex.value >= questions.value.length - 1) return;
	currentIndex.value += 1;
}

function openSheet(): void {
	sheetVisible.value = true;
}

function handleJumpTo(index: number): void {
	currentIndex.value = index;
	sheetVisible.value = false;
}

function handleBack(): void {
	if (finished.value) {
		goReport();
		return;
	}
	uni.showModal({
		title: "退出考场",
		content: "退出后本次作答不会保存，确定离开吗？",
		confirmColor: "#1D63FF",
		success: (res) => {
			if (res.confirm) {
				uni.navigateBack({ delta: 1 });
			}
		},
	});
}

function handleSubmitTap(): void {
	if (finished.value || submitting.value || pageStatus.value !== "ready") return;
	const unanswered = unansweredCount.value;
	uni.showModal({
		title: "交卷",
		content: unanswered > 0 ? `尚有 ${unanswered} 题未作答，交卷后不可修改，确定现在交卷吗？` : "交卷后不可修改，确定现在交卷吗？",
		confirmColor: "#1D63FF",
		success: (res) => {
			if (res.confirm) {
				submitPaper(false);
			}
		},
	});
}

/**
 * 交卷。
 * answers 必须为对象数组，且为每一道题都生成一项（未作答传空值），
 * 否则后端生成逐题复盘时会丢失未作答题目。
 */
async function submitPaper(auto: boolean): Promise<void> {
	if (submitting.value || finished.value) return;
	submitting.value = true;
	stopTick();

	try {
		const payload: ExamSubmitPayload = {
			task_id: taskId.value,
			// 后端完全忽略客户端上报的用时，按服务端开考时刻自行结算，此处仅按契约填充
			time_spent: computeTimeSpent(),
			answers: questions.value.map((question) => {
				const value = answers.value[question.id];
				if (Array.isArray(value)) return { resource_id: question.id, answer: value };
				return { resource_id: question.id, answer: typeof value === "string" ? value : "" };
			}),
		};

		const result = await submitExam(payload);
		finished.value = true;
		submittedScore.value = result.score;
		submittedStatus.value = result.status;
		submittedRecordId.value = result.record_id;

		if (result.status === "pending_verification") {
			toast.success(auto ? "时间已到，已自动交卷，等待核验" : "交卷成功，等待核验");
		} else {
			toast.success(auto ? `时间已到，已自动交卷，得分 ${result.score} 分` : `交卷成功，得分 ${result.score} 分`);
		}

		// 用 redirectTo 出栈替换考场页：若用 navigateTo，考生从报告页返回会退回已交卷的考场。
		// 报告页非 tabBar 页，redirectTo 合法。
		redirectTimer = setTimeout(() => {
			redirectTimer = null;
			uni.redirectTo({ url: `/pages/report/index?record_id=${result.record_id}` });
		}, REDIRECT_DELAY_MS);
	} catch (error) {
		// 交卷失败必须保留当前作答并恢复倒计时，允许考生重试，绝不跳页
		if (!auto) startTick();
		const message = error instanceof Error && error.message ? error.message : "交卷失败，请稍后重试";
		toast.error(message);
	} finally {
		submitting.value = false;
	}
}

/**
 * 本次作答用时（秒）= 开考接口返回时服务端已走时长 + 进入考场后的本地时长。
 * 后端 submit_task 会完全忽略该字段并自行按 created_at 结算，此处仅为满足入参契约。
 */
function computeTimeSpent(): number {
	if (!entryLoadedAt) return 0;
	const localElapsed = Math.max(0, Math.round((Date.now() - entryLoadedAt) / 1000));
	return entryElapsedSeconds + localElapsed;
}

/** 已提交过的试卷：引导前往「我的测试」查看历史记录 */
function goMyRecords(): void {
	clearRedirectTimer();
	uni.switchTab({ url: "/pages/records/index" });
}

/** 交卷成功后前往本次作答的成绩报告页 */
function goReport(): void {
	clearRedirectTimer();
	if (submittedRecordId.value) {
		uni.redirectTo({ url: `/pages/report/index?record_id=${submittedRecordId.value}` });
		return;
	}
	goMyRecords();
}
</script>

<style lang="scss" scoped>
.exam {
	display: flex;
	flex-direction: column;
	height: 100vh;
	overflow: hidden;
	background-color: #f6f8fc;
}

.exam__submit {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 56rpx;
	padding: 0 26rpx;
	border: 2rpx solid rgba(255, 255, 255, 0.7);
	border-radius: 999rpx;
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.exam__submit--pressed {
	transform: scale(0.96);
	opacity: 0.86;
}

.exam__submit-text {
	font-size: 24rpx;
	font-weight: 600;
	color: #ffffff;
}

.exam__status {
	display: flex;
	align-items: center;
	padding: 20rpx 32rpx;
	background-color: #ffffff;
}

.exam__status-text {
	font-size: 24rpx;
	color: #748094;
}

.exam__progress {
	flex: 1;
	height: 10rpx;
	margin: 0 20rpx;
	border-radius: 5rpx;
	background-color: #eef2f9;
	overflow: hidden;
}

.exam__progress-inner {
	height: 100%;
	border-radius: 5rpx;
	background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
	transition: width 0.3s ease;
}

.exam__timer {
	padding: 8rpx 18rpx;
	border-radius: 999rpx;
	background-color: #e8f0ff;
}

.exam__timer--urgent {
	background-color: #fa4350;
}

.exam__timer-text {
	font-size: 24rpx;
	font-weight: 600;
	color: #1d63ff;
}

.exam__timer--urgent .exam__timer-text {
	color: #ffffff;
}

.exam__swiper {
	flex: 1;
	min-height: 0;
}

.exam__swiper-item {
	overflow: hidden;
}

.exam__scroll {
	height: 100%;
}

.exam__card-wrap {
	padding: 28rpx 32rpx 40rpx;
}

.exam__footer {
	display: flex;
	align-items: center;
	padding: 18rpx 32rpx;
	padding-bottom: calc(18rpx + constant(safe-area-inset-bottom));
	padding-bottom: calc(18rpx + env(safe-area-inset-bottom));
	background-color: #ffffff;
	box-shadow: 0 -4rpx 20rpx rgba(29, 99, 255, 0.06);
}

.exam__nav {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 168rpx;
	height: 84rpx;
	border-radius: 999rpx;
	background-color: #eef2f9;
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.exam__nav--pressed {
	transform: scale(0.96);
	opacity: 0.88;
}

.exam__nav--disabled {
	opacity: 0.42;
}

.exam__nav-text {
	font-size: 28rpx;
	font-weight: 600;
	color: #748094;
}

.exam__sheet-entry {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	margin: 0 24rpx;
	transition: opacity 0.2s ease;
}

.exam__sheet-entry--pressed {
	opacity: 0.6;
}

.exam__sheet-index {
	font-size: 32rpx;
	font-weight: 600;
	color: #1d63ff;
}

.exam__sheet-label {
	margin-top: 2rpx;
	font-size: 20rpx;
	color: #a8b2c4;
}

.exam__state {
	flex: 1;
	min-height: 0;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0 32rpx;
}

.exam__finish-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	z-index: 200;
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: rgba(28, 35, 49, 0.5);
}

.exam__finish-card {
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 480rpx;
	padding: 56rpx 40rpx;
	background-color: #ffffff;
	border-radius: 32rpx;
}

.exam__finish-title {
	font-size: 30rpx;
	color: #748094;
}

.exam__finish-score {
	margin-top: 16rpx;
	font-size: 72rpx;
	font-weight: 600;
	color: #1d63ff;
}

.exam__finish-tip {
	margin-top: 20rpx;
	font-size: 24rpx;
	color: #a8b2c4;
}
</style>
