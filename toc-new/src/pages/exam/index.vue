<template>
	<view class="ex-page">
		<!-- Apple 极简考场顶栏（带交卷按钮、微光倒计时与动态进度条） -->
		<view class="ex-header">
			<view class="ex-header__inner">
				<view class="ex-header__left">
					<view class="ex-header__back" @click="handleBack">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none">
							<path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</view>
					<view class="ex-header__titles">
						<view class="ex-header__title">{{ paperTitle }}</view>
						<view class="ex-header__sub">
							第 {{ currentIndex + 1 }} / {{ questions.length }} 题 · 已答 {{ answeredIds.length }}/{{ questions.length }}
						</view>
					</view>
				</view>

				<!-- 右侧倒计时药丸胶囊 -->
				<view class="ex-clock" :class="{ 'ex-clock--hot': isUrgent }">
					<view class="ex-clock__icon" :class="{ 'ex-clock__icon--pulse': isUrgent }" />
					<text class="ex-clock__text">{{ countdownText }}</text>
				</view>
			</view>

			<!-- 顶部细线作答进度条 -->
			<view class="ex-timebar">
				<view class="ex-timebar__fill" :style="{ width: answeredRatio + '%' }" />
			</view>
		</view>

		<!-- 状态判断：加载中 / 已提交拦截 / 正常做题 -->
		<view v-if="pageStatus === 'loading'" class="ex-center-wrap">
			<PageState status="loading" />
		</view>

		<view v-else-if="pageStatus === 'error'" class="ex-center-wrap">
			<PageState status="error" :title="stateTitle" :description="stateDescription" action-text="重新加载" @action="startExam" />
		</view>

		<view v-else-if="pageStatus === 'blocked'" class="ex-center-wrap">
			<PageState
				status="empty"
				title="该试卷你已提交过"
				description="每份试卷每人仅可作答一次，请前往「我的测试」查看作答记录"
				action-text="前往我的测试"
				@action="goMyRecords"
			/>
		</view>

		<!-- 100% 像素级对齐 preview-apple 原生考场题目滑动区 -->
		<swiper
			v-else
			class="ex-swiper"
			:current="currentIndex"
			duration="380"
			@change="handleSwiperChange"
		>
			<swiper-item v-for="(q, qi) in formattedQuestions" :key="q.id">
				<scroll-view class="ex-qscroll" scroll-y>
					<view class="ex-question">
						<view class="ex-question__head">
							<view class="ex-question__no">Q{{ qi + 1 }}</view>
							<view class="ex-question__type">{{ q.typeLabel }} · {{ q.score }}分</view>
							<view
								class="ex-question__flag"
								:class="{ 'ex-question__flag--on': flags.has(q.id) }"
								@click="toggleFlag(q.id)"
							>
								{{ flags.has(q.id) ? "已标记" : "标记本题" }}
							</view>
						</view>

						<view class="ex-question__title">{{ q.stem }}</view>

						<!-- 1. 单选 -->
						<view v-if="q.kind === 'single'" class="ex-options">
							<view
								v-for="o in q.normalizedOptions"
								:key="o.key"
								class="ex-option"
								:class="{ 'ex-option--on': answers[q.id] === o.key }"
								@click="selectSingle(q.id, o.key)"
							>
								<view class="ex-option__key" :class="{ 'ex-option__key--on': answers[q.id] === o.key }">
									{{ o.key }}
								</view>
								<view class="ex-option__text">{{ o.text }}</view>
							</view>
						</view>

						<!-- 2. 多选 -->
						<view v-else-if="q.kind === 'multiple'" class="ex-options">
							<view
								v-for="o in q.normalizedOptions"
								:key="o.key"
								class="ex-option"
								:class="{ 'ex-option--on': isMultiPicked(q.id, o.key) }"
								@click="toggleMulti(q.id, o.key)"
							>
								<view class="ex-option__check" :class="{ 'ex-option__check--on': isMultiPicked(q.id, o.key) }" />
								<view class="ex-option__text">{{ o.text }}</view>
							</view>
						</view>

						<!-- 3. 判断题：对 / 错 双大胶囊按钮 -->
						<view v-else-if="q.kind === 'judge'" class="ex-judge">
							<view
								class="ex-judge__btn"
								:class="{ 'ex-judge__btn--on': answers[q.id] === 'A', 'ex-judge__btn--yes': answers[q.id] === 'A' }"
								@click="answers[q.id] = 'A'"
							>
								<text class="ex-judge__mark">对</text>
								<text class="ex-judge__label">正确</text>
							</view>
							<view
								class="ex-judge__btn"
								:class="{ 'ex-judge__btn--on': answers[q.id] === 'B', 'ex-judge__btn--no': answers[q.id] === 'B' }"
								@click="answers[q.id] = 'B'"
							>
								<text class="ex-judge__mark">错</text>
								<text class="ex-judge__label">错误</text>
							</view>
						</view>

						<!-- 4. 填空题 -->
						<view v-else-if="q.kind === 'fill'" class="ex-blanks">
							<view v-for="b in q.blankCount" :key="b" class="ex-blank">
								<view class="ex-blank__label">空位 {{ b }}</view>
								<input
									class="ex-blank__input"
									:value="getFillValue(q.id, b - 1)"
									placeholder="请输入作答内容"
									placeholder-class="ex-ph"
									@input="handleFillInput(q.id, b - 1, $event)"
								/>
							</view>
						</view>

						<!-- 5. 简答题 -->
						<view v-else class="ex-essay">
							<textarea
								class="ex-essay__area"
								:value="typeof answers[q.id] === 'string' ? String(answers[q.id]) : ''"
								:maxlength="500"
								placeholder="请结合实际要求在此作答，注意条理与要点完整"
								placeholder-class="ex-ph"
								@input="handleEssayInput(q.id, $event)"
							/>
							<view class="ex-essay__count">
								<text :class="{ 'ex-essay__count--hot': (answers[q.id] ? String(answers[q.id]).length : 0) > 480 }">
									{{ answers[q.id] ? String(answers[q.id]).length : 0 }}
								</text>
								/ 500
							</view>
						</view>
					</view>
				</scroll-view>
			</swiper-item>
		</swiper>

		<!-- 底部极简悬浮操作栏 -->
		<view v-if="pageStatus === 'ready'" class="ex-footer">
			<view class="ex-footer__drawer" @click="drawerOpen = true">
				<view class="ex-footer__grid">
					<view v-for="n in 4" :key="n" class="ex-footer__cell" />
				</view>
				<text>答题卡</text>
			</view>
			<view class="ex-footer__nav">
				<view class="ex-nav" :class="{ 'ex-nav--disabled': currentIndex === 0 }" @click="prevQuestion">上一题</view>
				<view class="ex-nav ex-nav--primary" @click="nextQuestion">
					{{ currentIndex === questions.length - 1 ? "去交卷" : "下一题" }}
				</view>
			</view>
		</view>

		<!-- 60vh 玻璃答题卡抽屉（100% 还原 Apple 抽屉） -->
		<view v-if="drawerOpen" class="ex-drawer-mask" @click="drawerOpen = false" />
		<view class="ex-drawer" :class="{ 'ex-drawer--open': drawerOpen }">
			<view class="ex-drawer__grabber" />
			<view class="ex-drawer__head">
				<view class="ex-drawer__title">答题卡</view>
				<view class="ex-drawer__legend">
					<view class="lg-item"><view class="lg-chip lg-chip--cur" />当前题</view>
					<view class="lg-item"><view class="lg-chip lg-chip--done" />已作答</view>
					<view class="lg-item"><view class="lg-chip lg-chip--flag" />已标记</view>
					<view class="lg-item"><view class="lg-chip lg-chip--todo" />未作答</view>
				</view>
			</view>
			<scroll-view class="ex-drawer__scroll" scroll-y>
				<view class="ex-matrix">
					<view
						v-for="i in questions.length"
						:key="i"
						class="ex-cell"
						:class="cellClass(i - 1)"
						@click="jumpTo(i - 1)"
					>
						{{ i }}
					</view>
				</view>
			</scroll-view>
			<view class="ex-drawer__foot">
				<view class="ex-submit" :class="{ 'ex-submit--loading': submitting }" @click="askSubmit">
					{{ submitting ? "交卷中..." : "确认交卷" }}
				</view>
			</view>
		</view>

		<!-- 切屏告警弹窗 -->
		<view v-if="cheatOpen" class="ex-modal-mask">
			<view class="ex-modal">
				<view class="ex-modal__alert">!</view>
				<view class="ex-modal__title">切屏警告</view>
				<view class="ex-modal__body">
					检测到离开考场！已记录 {{ switchScreenCount }} 次切屏行为，累计切屏 {{ MAX_SWITCH_LIMIT }} 次将被强制收卷并记录考纪违规。
				</view>
				<view class="ex-modal__btns">
					<view class="ex-modal__btn ex-modal__btn--primary" @click="cheatOpen = false">我知道了，继续作答</view>
				</view>
			</view>
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-13
 * AI模型：Gemini 系列
 * 修改内容：[1. 100% 像素级将 preview-apple/exam/index.vue 原生模板完整移植到主项目，告别白屏和外层 QuestionCard 丢失; 2. 单选、多选、判断题（双大胶囊）、填空题、简答题全部原生直接内联展开; 3. 完美承接真实接口 GET /api/v1/member/tasks/{id}/entry 与 POST /api/v1/member/task-records/submit 并完整校验题干 content 与 title]
 */
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { onLoad, onHide } from "@dcloudio/uni-app";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import {
	fetchExamEntry,
	submitExam,
	type ExamQuestion,
	type QuestionOption,
	type UserAnswerItem,
} from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";
import { formatDuration } from "@/utils/format";

type PageStatus = "loading" | "ready" | "error" | "blocked";

const toast = useGlobalToast();

const taskId = ref(0);
const recordId = ref(0);
const paperTitle = ref("在线测评");
const pageStatus = ref<PageStatus>("loading");
const stateTitle = ref("正在准备考场");
const stateDescription = ref("正在安全同步考卷与基准时间...");

const questions = ref<ExamQuestion[]>([]);
const answers = reactive<Record<number, string | string[]>>({});
const flags = reactive(new Set<number>());

const currentIndex = ref(0);
const drawerOpen = ref(false);
const cheatOpen = ref(false);
const submitting = ref(false);

const remainingSeconds = ref(0);
let timerHandle: number | null = null;
const isUrgent = computed(() => remainingSeconds.value > 0 && remainingSeconds.value <= 300);

const switchScreenCount = ref(0);
const MAX_SWITCH_LIMIT = 3;

function indexToLetter(idx: number): string {
	return String.fromCharCode(65 + (idx % 26));
}

const OPTION_PREFIX_PATTERN = /^([A-Z])[\.、\s\-\:：]+(.*)$/i;

function normalizeOptions(raw: QuestionOption[] | undefined): { key: string; text: string }[] {
	if (!raw || !Array.isArray(raw) || raw.length === 0) return [];
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

type QuestionKind = "single" | "multiple" | "judge" | "fill" | "short";

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
	single: "单选题",
	multiple: "多选题",
	judge: "判断题",
	fill: "填空题",
	short: "简答题",
};

/** 对后端下发的每道题目进行安全归一化处理 */
const formattedQuestions = computed(() => {
	return questions.value.map((q) => {
		const rawType = String(q.type || "single").toLowerCase();
		const kind = KIND_MAP[rawType] || "single";
		const stem = q.content || q.title || "题目加载中...";
		const normalizedOpts = normalizeOptions(q.options);

		let blankCount = 1;
		if (kind === "fill") {
			const matched = stem.match(/_{2,}/g);
			blankCount = matched && matched.length > 0 ? matched.length : 1;
		}

		return {
			...q,
			stem,
			kind,
			typeLabel: TYPE_LABELS[kind] || "测评试题",
			normalizedOptions: normalizedOpts,
			blankCount,
		};
	});
});

const answeredIds = computed(() => {
	return questions.value
		.filter((q) => {
			const val = answers[q.id];
			if (Array.isArray(val)) return val.length > 0 && val.some((v) => String(v).trim().length > 0);
			return typeof val === "string" && val.trim().length > 0;
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

function toggleFlag(id: number): void {
	if (flags.has(id)) flags.delete(id);
	else flags.add(id);
}

function selectSingle(qId: number, key: string): void {
	answers[qId] = key;
}

function isMultiPicked(qId: number, key: string): boolean {
	const current = answers[qId];
	return Array.isArray(current) && current.includes(key);
}

function toggleMulti(qId: number, key: string): void {
	const current = Array.isArray(answers[qId]) ? [...(answers[qId] as string[])] : [];
	const index = current.indexOf(key);
	if (index >= 0) {
		current.splice(index, 1);
	} else {
		current.push(key);
		current.sort();
	}
	answers[qId] = current;
}

function getFillValue(qId: number, blankIdx: number): string {
	const current = answers[qId];
	if (Array.isArray(current)) return current[blankIdx] || "";
	return blankIdx === 0 && typeof current === "string" ? current : "";
}

function handleFillInput(qId: number, blankIdx: number, e: unknown): void {
	const text = (e as { detail: { value: string } })?.detail?.value || "";
	const targetQ = formattedQuestions.value.find((it) => it.id === qId);
	const count = targetQ ? targetQ.blankCount : 1;
	let current: string[] = [];
	if (Array.isArray(answers[qId])) {
		current = [...(answers[qId] as string[])];
	} else if (typeof answers[qId] === "string" && answers[qId]) {
		current = [String(answers[qId])];
	}
	while (current.length < count) current.push("");
	current[blankIdx] = text;
	answers[qId] = current;
}

function handleEssayInput(qId: number, e: unknown): void {
	const text = (e as { detail: { value: string } })?.detail?.value || "";
	answers[qId] = text;
}

function handleSwiperChange(event: { detail: { current: number } }): void {
	currentIndex.value = event.detail.current;
}

function prevQuestion(): void {
	if (currentIndex.value > 0) currentIndex.value -= 1;
}

function nextQuestion(): void {
	if (currentIndex.value < questions.value.length - 1) {
		currentIndex.value += 1;
	} else {
		askSubmit();
	}
}

function jumpTo(index: number): void {
	currentIndex.value = index;
	drawerOpen.value = false;
}

function cellClass(idx: number): string {
	const q = questions.value[idx];
	if (!q) return "";
	if (idx === currentIndex.value) return "ex-cell--cur";
	if (flags.has(q.id)) return "ex-cell--flag";
	if (answeredIds.value.includes(q.id)) return "ex-cell--done";
	return "ex-cell--todo";
}

function startTimer(): void {
	stopTimer();
	if (remainingSeconds.value <= 0) return;
	timerHandle = setInterval(() => {
		if (remainingSeconds.value > 1) {
			remainingSeconds.value -= 1;
		} else {
			remainingSeconds.value = 0;
			stopTimer();
			toast.warning("答题时间已到，系统正在自动为您提交试卷");
			doSubmit(true);
		}
	}, 1000) as unknown as number;
}

function stopTimer(): void {
	if (timerHandle !== null) {
		clearInterval(timerHandle);
		timerHandle = null;
	}
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
			for (const ans of res.my_answers) {
				answers[ans.resource_id] = ans.answer;
			}
		}

		// 根据服务端权威时刻推算剩余秒数
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

function askSubmit(): void {
	const unansCount = questions.value.length - answeredIds.value.length;
	const content = unansCount > 0
		? `还有 ${unansCount} 道题未作答，提交后将不可修改，确定交卷吗？`
		: "已全部作答完毕，确认立即提交试卷吗？";

	uni.showModal({
		title: "确认交卷",
		content,
		confirmText: "确认交卷",
		confirmColor: "#1852E0",
		cancelText: "检查一下",
		success(res) {
			if (res.confirm) {
				doSubmit(false);
			}
		},
	});
}

async function doSubmit(auto = false): Promise<void> {
	if (submitting.value) return;
	submitting.value = true;
	stopTimer();

	const answersPayload: UserAnswerItem[] = Object.keys(answers).map((idStr) => {
		const rid = Number(idStr);
		return { resource_id: rid, answer: answers[rid] };
	});

	try {
		const result = await submitExam({
			task_id: taskId.value,
			time_spent: 0,
			answers: answersPayload,
		});

		toast.success(auto ? "超时自动交卷成功" : "交卷成功！正在生成报告...");
		setTimeout(() => {
			uni.redirectTo({
				url: `/pages/report/index?record_id=${result.record_id || recordId.value || taskId.value}`,
			});
		}, 800);
	} catch (error) {
		const msg = error instanceof Error && error.message ? error.message : "交卷失败，请稍后重试";
		toast.error(msg);
	} finally {
		submitting.value = false;
	}
}

function handleBack(): void {
	uni.showModal({
		title: "离开考场确认",
		content: "测评正在进行中，退出后倒计时不会暂停，确定暂时离开吗？",
		confirmText: "暂时离开",
		confirmColor: "#86868B",
		cancelText: "继续作答",
		success(res) {
			if (res.confirm) {
				stopTimer();
				uni.navigateBack();
			}
		},
	});
}

function goMyRecords(): void {
	uni.switchTab({ url: "/pages/records/index" });
}

onHide(() => {
	if (pageStatus.value === "ready") {
		switchScreenCount.value += 1;
		if (switchScreenCount.value >= MAX_SWITCH_LIMIT) {
			toast.error("切屏超限，系统已自动收卷");
			doSubmit(true);
		} else {
			cheatOpen.value = true;
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

.ex-page {
	height: 100vh;
	display: flex;
	flex-direction: column;
	background: $bg;
	overflow: hidden;
	box-sizing: border-box;
}

/* 考场顶栏 */
.ex-header {
	background: linear-gradient(180deg, rgba(24, 82, 224, 0.07), transparent);
	border-bottom: 1px solid $line;
	flex-shrink: 0;
}

.ex-header__inner {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 28rpx 36rpx 20rpx;
}

.ex-header__left {
	display: flex;
	align-items: center;
	gap: 16rpx;
	flex: 1;
	min-width: 0;
}

.ex-header__back {
	width: 56rpx;
	height: 56rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	color: $ink;
	background: rgba(20, 30, 60, 0.05);
	cursor: pointer;
}

.ex-header__titles {
	flex: 1;
	min-width: 0;
}

.ex-header__title {
	font-size: 30rpx;
	font-weight: 800;
	color: $ink;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.ex-header__sub {
	margin-top: 4rpx;
	font-size: 22rpx;
	color: $muted;
}

.ex-clock {
	display: flex;
	align-items: center;
	gap: 12rpx;
	background: $gradient;
	border-radius: $radius-pill;
	padding: 14rpx 28rpx;
	box-shadow: 0 10rpx 28rpx rgba(10, 50, 153, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.ex-clock--hot {
	background: linear-gradient(135deg, #ff5f57 0%, #d70015 100%);
	box-shadow: 0 10rpx 28rpx rgba(255, 59, 48, 0.35);
}

.ex-clock__icon {
	width: 14rpx;
	height: 14rpx;
	border-radius: 50%;
	background: #9ef0b6;
}

.ex-clock--hot .ex-clock__icon {
	background: #ffd6d4;
}

.ex-clock__icon--pulse {
	animation: clock-pulse 1s ease-in-out infinite;
}

@keyframes clock-pulse {
	0%, 100% { transform: scale(1); opacity: 1; }
	50% { transform: scale(0.75); opacity: 0.35; }
}

.ex-clock__text {
	color: #ffffff;
	font-size: 26rpx;
	font-weight: 700;
	font-variant-numeric: tabular-nums;
	letter-spacing: 0.04em;
}

.ex-timebar {
	height: 6rpx;
	background: rgba(20, 30, 60, 0.06);
}

.ex-timebar__fill {
	height: 100%;
	background: $gradient;
	border-radius: 0 4rpx 4rpx 0;
	transition: width 0.3s ease;
}

/* 题目主体区 */
.ex-swiper {
	flex: 1;
	min-height: 0;
}

.ex-qscroll {
	height: 100%;
}

.ex-question {
	background: $surface;
	border-radius: 28rpx;
	margin: 28rpx 36rpx 140rpx;
	padding: 38rpx 34rpx;
	box-shadow: $shadow-card;
	border: 1px solid $line;
}

.ex-question__head {
	display: flex;
	align-items: center;
	gap: 16rpx;
	margin-bottom: 24rpx;
}

.ex-question__no {
	font-size: 24rpx;
	font-weight: 800;
	color: #ffffff;
	background: $gradient;
	padding: 8rpx 20rpx;
	border-radius: $radius-pill;
	box-shadow: 0 8rpx 20rpx rgba(24, 82, 224, 0.28);
}

.ex-question__type {
	font-size: 22rpx;
	color: $muted;
}

.ex-question__flag {
	margin-left: auto;
	font-size: 22rpx;
	color: $muted;
	background: rgba(20, 30, 60, 0.05);
	border-radius: $radius-pill;
	padding: 10rpx 24rpx;
	cursor: pointer;
	transition: all 0.22s;
}

.ex-question__flag--on {
	color: #b26a00;
	background: $warn-soft;
	box-shadow: 0 4rpx 16rpx rgba(245, 166, 35, 0.25);
}

.ex-question__title {
	font-size: 31rpx;
	font-weight: 700;
	color: $ink;
	line-height: 1.65;
}

/* 单选 / 多选选项 */
.ex-options {
	margin-top: 32rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.ex-option {
	display: flex;
	align-items: center;
	gap: 22rpx;
	border: 1px solid transparent;
	background: rgba(20, 30, 60, 0.04);
	border-radius: 22rpx;
	padding: 24rpx;
	cursor: pointer;
	transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.ex-option:active {
	transform: scale(0.98);
}

.ex-option--on {
	border-color: rgba(24, 82, 224, 0.35);
	background: $accent-soft;
	box-shadow: 0 8rpx 28rpx rgba(24, 82, 224, 0.14);
}

.ex-option__key {
	width: 52rpx;
	height: 52rpx;
	border-radius: 50%;
	background: #ffffff;
	box-shadow: 0 2rpx 8rpx rgba(20, 30, 60, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 26rpx;
	font-weight: 700;
	color: $muted;
	flex-shrink: 0;
	transition: all 0.22s;
}

.ex-option__key--on {
	background: $gradient;
	color: #ffffff;
	box-shadow: 0 8rpx 20rpx rgba(24, 82, 224, 0.35);
}

.ex-option__text {
	font-size: 28rpx;
	color: $ink-2;
	line-height: 1.55;
}

/* 多选方角复选框 */
.ex-option__check {
	width: 36rpx;
	height: 36rpx;
	border-radius: 10rpx;
	border: 2px solid rgba(20, 30, 60, 0.18);
	background: #ffffff;
	flex-shrink: 0;
	position: relative;
	transition: all 0.22s;
}

.ex-option__check--on {
	border-color: transparent;
	background: $gradient;
	box-shadow: 0 6rpx 16rpx rgba(24, 82, 224, 0.3);
}

.ex-option__check--on::after {
	content: "";
	position: absolute;
	left: 11rpx;
	top: 4rpx;
	width: 8rpx;
	height: 16rpx;
	border: solid #ffffff;
	border-width: 0 3px 3px 0;
	transform: rotate(45deg);
}

/* 判断题双大胶囊 */
.ex-judge {
	display: flex;
	gap: 24rpx;
	margin-top: 36rpx;
}

.ex-judge__btn {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 10rpx;
	background: rgba(20, 30, 60, 0.04);
	border: 1px solid transparent;
	border-radius: 26rpx;
	padding: 36rpx 0;
	cursor: pointer;
	transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.ex-judge__btn:active {
	transform: scale(0.96);
}

.ex-judge__btn--on.ex-judge__btn--yes {
	background: $ok-soft;
	border-color: rgba(52, 199, 89, 0.4);
	box-shadow: 0 8rpx 28rpx rgba(52, 199, 89, 0.18);
}

.ex-judge__btn--on.ex-judge__btn--no {
	background: $danger-soft;
	border-color: rgba(255, 59, 48, 0.4);
	box-shadow: 0 8rpx 28rpx rgba(255, 59, 48, 0.18);
}

.ex-judge__mark {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	background: #ffffff;
	box-shadow: 0 4rpx 14rpx rgba(20, 30, 60, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 34rpx;
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
	font-size: 27rpx;
	font-weight: 600;
	color: $ink-2;
}

/* 填空题 */
.ex-blanks {
	margin-top: 32rpx;
	display: flex;
	flex-direction: column;
	gap: 26rpx;
}

.ex-blank__label {
	font-size: 24rpx;
	color: $muted;
	margin-bottom: 12rpx;
}

.ex-blank__input {
	width: 100%;
	height: 88rpx;
	box-sizing: border-box;
	background: rgba(20, 30, 60, 0.04);
	border: 1px solid transparent;
	border-radius: 20rpx;
	padding: 0 28rpx;
	font-size: 28rpx;
	color: $ink;
}

.ex-ph {
	color: $faint;
}

/* 简答题 */
.ex-essay {
	margin-top: 32rpx;
}

.ex-essay__area {
	width: 100%;
	height: 320rpx;
	box-sizing: border-box;
	background: rgba(20, 30, 60, 0.04);
	border: 1px solid transparent;
	border-radius: 22rpx;
	padding: 24rpx;
	font-size: 28rpx;
	line-height: 1.6;
	color: $ink;
}

.ex-essay__count {
	margin-top: 14rpx;
	text-align: right;
	font-size: 22rpx;
	color: $faint;
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
	background: rgba(251, 251, 253, 0.88);
	backdrop-filter: $glass-blur;
	border-top: 1px solid $line;
	padding: 20rpx 36rpx calc(20rpx + env(safe-area-inset-bottom));
}

.ex-footer__drawer {
	display: flex;
	align-items: center;
	gap: 16rpx;
	font-size: 26rpx;
	color: $ink-2;
	padding: 16rpx 28rpx;
	border-radius: $radius-pill;
	background: rgba(20, 30, 60, 0.05);
	cursor: pointer;
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
	background: $muted;
}

.ex-footer__nav {
	display: flex;
	align-items: center;
	gap: 18rpx;
}

.ex-nav {
	font-size: 25rpx;
	font-weight: 600;
	padding: 16rpx 34rpx;
	border-radius: $radius-pill;
	color: $ink-2;
	background: rgba(20, 30, 60, 0.06);
	cursor: pointer;
}

.ex-nav--disabled {
	opacity: 0.35;
	pointer-events: none;
}

.ex-nav--primary {
	color: #ffffff;
	background: $gradient;
	box-shadow: 0 6rpx 20rpx rgba(24, 82, 224, 0.32);
}

/* 答题卡抽屉 */
.ex-drawer-mask {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.4);
	backdrop-filter: blur(8px);
	z-index: 100;
}

.ex-drawer {
	position: fixed;
	left: 0;
	right: 0;
	bottom: 0;
	height: 60vh;
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: $glass-blur;
	border-radius: 36rpx 36rpx 0 0;
	z-index: 101;
	display: flex;
	flex-direction: column;
	transform: translateY(100%);
	transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.ex-drawer--open {
	transform: translateY(0);
}

.ex-drawer__grabber {
	width: 72rpx;
	height: 8rpx;
	border-radius: 4rpx;
	background: rgba(20, 30, 60, 0.16);
	margin: 16rpx auto 8rpx;
}

.ex-drawer__head {
	padding: 24rpx 40rpx 20rpx;
	border-bottom: 1px solid $line;
}

.ex-drawer__title {
	font-size: 32rpx;
	font-weight: 800;
	color: $ink;
}

.ex-drawer__legend {
	display: flex;
	gap: 28rpx;
	margin-top: 14rpx;
}

.lg-item {
	display: flex;
	align-items: center;
	gap: 8rpx;
	font-size: 22rpx;
	color: $muted;
}

.lg-chip {
	width: 18rpx;
	height: 18rpx;
	border-radius: 6rpx;
}

.lg-chip--cur { background: $gradient; }
.lg-chip--done { background: $ok; }
.lg-chip--flag { background: $warn; }
.lg-chip--todo { background: rgba(20, 30, 60, 0.08); }

.ex-drawer__scroll {
	flex: 1;
	padding: 28rpx 40rpx;
}

.ex-matrix {
	display: grid;
	grid-template-columns: repeat(5, 1fr);
	gap: 20rpx;
}

.ex-cell {
	aspect-ratio: 1;
	border-radius: 18rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 26rpx;
	font-weight: 700;
	background: rgba(20, 30, 60, 0.06);
	color: $ink;
	cursor: pointer;
}

.ex-cell--cur {
	background: $gradient;
	color: #ffffff;
	box-shadow: 0 8rpx 20rpx rgba(24, 82, 224, 0.3);
}

.ex-cell--done {
	background: $ok-soft;
	color: $ok;
}

.ex-cell--flag {
	background: $warn-soft;
	color: $warn;
}

.ex-drawer__foot {
	padding: 20rpx 40rpx calc(24rpx + env(safe-area-inset-bottom));
	border-top: 1px solid $line;
}

.ex-submit {
	background: $gradient;
	color: #ffffff;
	font-size: 28rpx;
	font-weight: 700;
	border-radius: $radius-pill;
	padding: 24rpx 0;
	text-align: center;
	box-shadow: 0 8rpx 24rpx rgba(24, 82, 224, 0.35);
	cursor: pointer;
}

.ex-submit--loading {
	opacity: 0.65;
	pointer-events: none;
}

/* 异常态居中居顶容器 */
.ex-center-wrap {
	padding-top: 80rpx;
}

/* 切屏告警弹窗 */
.ex-modal-mask {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.5);
	backdrop-filter: blur(12px);
	z-index: 200;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 60rpx;
}

.ex-modal {
	width: 100%;
	background: #ffffff;
	border-radius: 32rpx;
	padding: 52rpx 44rpx 40rpx;
	text-align: center;
	box-shadow: 0 24rpx 72rpx rgba(0, 0, 0, 0.25);
}

.ex-modal__alert {
	width: 100rpx;
	height: 100rpx;
	border-radius: 50%;
	background: $danger-soft;
	color: $danger;
	font-size: 52rpx;
	font-weight: 800;
	display: flex;
	align-items: center;
	justify-content: center;
	margin: 0 auto 24rpx;
}

.ex-modal__title {
	font-size: 36rpx;
	font-weight: 800;
	color: $ink;
}

.ex-modal__body {
	margin-top: 18rpx;
	font-size: 26rpx;
	color: $ink-2;
	line-height: 1.65;
}

.ex-modal__btns {
	margin-top: 36rpx;
}

.ex-modal__btn--primary {
	background: $gradient;
	color: #ffffff;
	font-size: 27rpx;
	font-weight: 700;
	padding: 22rpx 0;
	border-radius: $radius-pill;
	box-shadow: 0 8rpx 24rpx rgba(24, 82, 224, 0.35);
	cursor: pointer;
}
</style>
