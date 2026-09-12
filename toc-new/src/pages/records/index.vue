<template>
	<view class="rc-page">
		<!-- 通顶 Header -->
		<view class="rc-header">
			<view class="rc-header__inner">
				<view class="rc-header__title">我的测试</view>
				<view class="rc-header__count">{{ totalRecordsCount }} 条记录</view>
			</view>
		</view>

		<!-- 毛玻璃吸顶分段控制器（100% 还原 Apple 滑块动效） -->
		<view class="rc-tabs">
			<view class="rc-seg">
				<view class="rc-seg__thumb" :class="'rc-seg__thumb--' + tab" />
				<view
					v-for="t in tabs"
					:key="t.key"
					class="rc-seg__item"
					:class="{ 'rc-seg__item--on': tab === t.key }"
					@click="tab = t.key"
				>
					{{ t.label }}
				</view>
			</view>
		</view>

		<!-- 状态占位：加载中/异常/空态 -->
		<view v-if="pageStatus === 'loading'" class="rc-loading-wrap">
			<PageState status="loading" />
		</view>

		<view v-else-if="pageStatus === 'error'" class="rc-loading-wrap">
			<PageState status="error" action-text="重新加载" @action="loadTasks" />
		</view>

		<!-- 1. 进行中列表 -->
		<view v-else-if="tab === 'doing'" class="rc-list">
			<view v-if="doingList.length === 0" class="rc-empty">
				<PageState status="empty" description="暂无正在进行中的测评" />
			</view>
			<view
				v-for="c in doingList"
				:key="c.task_id"
				class="rc-card"
				@click="goExam(c)"
			>
				<view class="rc-card__title">{{ c.title }}</view>
				<view class="rc-progress">
					<view class="rc-progress__track">
						<view class="rc-progress__fill" style="width: 50%;" />
					</view>
					<view class="rc-progress__text">{{ c.question_count }} 题待继续</view>
				</view>
				<view class="rc-card__foot">
					<view class="rc-card__time">
						<view class="rc-card__dot rc-card__dot--live" />
						限时 {{ formatTimeLimit(c.time_limit) }}
					</view>
					<view class="rc-btn">继续答题</view>
				</view>
			</view>
		</view>

		<!-- 2. 未开始列表 -->
		<view v-else-if="tab === 'todo'" class="rc-list">
			<view v-if="todoList.length === 0" class="rc-empty">
				<PageState status="empty" description="暂无未开始的预约测评" />
			</view>
			<view
				v-for="c in todoList"
				:key="c.task_id"
				class="rc-card rc-card--muted"
			>
				<view class="rc-card__top">
					<view class="rc-card__title rc-card__title--soft">{{ c.title }}</view>
					<view class="rc-lock">
						<view class="rc-lock__hole" />
					</view>
				</view>
				<view class="rc-plan">开考时间：{{ formatDateTime(c.start_time) }}</view>
				<view class="rc-card__foot">
					<view class="rc-card__time">截止 {{ formatDeadline(c.deadline) }}</view>
					<view class="rc-btn rc-btn--disabled">未到开考时间</view>
				</view>
			</view>
		</view>

		<!-- 3. 已参加列表（全边界覆盖：高分、及格、未及格、核验中） -->
		<view v-else class="rc-list">
			<view v-if="doneList.length === 0" class="rc-empty">
				<PageState status="empty" description="暂无已完成的测评记录" />
			</view>
			<view
				v-for="r in doneList"
				:key="r.task_id"
				class="rc-card"
				@click="goReport(r)"
			>
				<view class="rc-score-row">
					<view class="rc-score" :class="'rc-score--' + resolveDoneTone(r)">
						<text class="rc-score__num">{{ resolveScoreText(r) }}</text>
						<text v-if="r.status !== 'pending_verification'" class="rc-score__unit">分</text>
					</view>
					<view class="rc-badge" :class="'rc-badge--' + resolveDoneTone(r)">
						{{ resolveBadgeText(r) }}
					</view>
				</view>
				<view class="rc-card__title rc-card__title--tight">{{ r.title }}</view>
				<view class="rc-card__foot">
					<view class="rc-card__time">
						{{ r.submit_time ? `提交于 ${formatDateTime(r.submit_time)}` : "已交卷" }}
					</view>
					<view class="rc-btn rc-btn--ghost">查看报告</view>
				</view>
			</view>
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 100% 像素级对齐 preview-apple/records/index.vue 架构与设计：通顶大字标题 rc-header__title、毛玻璃吸顶三态滑块切换器 rc-seg、Apple 钛金质感做题卡片 rc-card、绿色大号得分 rc-score--ok、预约小锁 rc-lock、闪烁呼吸绿点 rc-card__dot--live; 2. 严密对接真实后端 GET /api/v1/member/member-tasks 并精准分类三大状态]
 */
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchMemberTasks, type MemberTaskItem } from "@/api/exam";
import { formatDateTime, formatDeadline, formatTimeLimit } from "@/utils/format";

type RecordTab = "doing" | "todo" | "done";

const tab = ref<RecordTab>("done");
const tabs: { key: RecordTab; label: string }[] = [
	{ key: "doing", label: "进行中" },
	{ key: "todo", label: "未开始" },
	{ key: "done", label: "已参加" },
];

const pageStatus = ref<"loading" | "ready" | "error">("loading");
const allTasks = ref<MemberTaskItem[]>([]);

/** 数据分类映射 */
const doingList = computed(() => {
	const now = Date.now();
	return allTasks.value.filter((t) => {
		const isNotDone = !["submitted", "verified", "pending_verification"].includes(t.status);
		const started = !t.start_time || new Date(t.start_time).getTime() <= now;
		return isNotDone && started;
	});
});

const todoList = computed(() => {
	const now = Date.now();
	return allTasks.value.filter((t) => {
		const isNotDone = !["submitted", "verified", "pending_verification"].includes(t.status);
		const notStarted = t.start_time && new Date(t.start_time).getTime() > now;
		return isNotDone && notStarted;
	});
});

const doneList = computed(() => {
	return allTasks.value.filter((t) => {
		return ["submitted", "verified", "pending_verification"].includes(t.status);
	});
});

const totalRecordsCount = computed(() => {
	if (tab.value === "doing") return doingList.value.length;
	if (tab.value === "todo") return todoList.value.length;
	return doneList.value.length;
});

function resolveDoneTone(item: MemberTaskItem): "ok" | "warn" | "danger" {
	if (item.status === "pending_verification") return "warn";
	const score = item.score ?? 0;
	return score >= (item.pass_score || 60) ? "ok" : "danger";
}

function resolveScoreText(item: MemberTaskItem): string {
	if (item.status === "pending_verification") return "核验中";
	return String(item.score ?? 0);
}

function resolveBadgeText(item: MemberTaskItem): string {
	if (item.status === "pending_verification") return "主观题批阅中";
	const score = item.score ?? 0;
	if (score >= 90) return "优秀 · 已核验";
	if (score >= (item.pass_score || 60)) return "及格 · 已核验";
	return "未及格 · 待努力";
}

async function loadTasks(): Promise<void> {
	pageStatus.value = "loading";
	try {
		const res = await fetchMemberTasks();
		allTasks.value = res.items || [];
		pageStatus.value = "ready";
	} catch {
		pageStatus.value = "error";
	}
}

function goExam(item: MemberTaskItem) {
	uni.navigateTo({
		url: `/pages/exam/index?task_id=${item.task_id}&title=${encodeURIComponent(item.title)}`
	});
}

function goReport(item: MemberTaskItem) {
	const recordId = item.record_id || item.task_id;
	uni.navigateTo({
		url: `/pages/report/index?record_id=${recordId}`
	});
}

onShow(() => {
	loadTasks();
});
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.rc-page {
	min-height: 100vh;
	background: $bg;
	padding-bottom: 80rpx;
	box-sizing: border-box;
}

.rc-header {
	background: linear-gradient(180deg, rgba(24, 82, 224, 0.07), transparent);
}

.rc-header__inner {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 44rpx 44rpx 24rpx;
}

.rc-header__title {
	font-size: 44rpx;
	font-weight: 800;
	color: $ink;
}

.rc-header__count {
	font-size: 22rpx;
	color: $muted;
}

/* 毛玻璃吸顶分段控制器 */
.rc-tabs {
	position: sticky;
	top: 0;
	z-index: 20;
	padding: 16rpx 44rpx 20rpx;
	background: rgba(251, 251, 253, 0.78);
	backdrop-filter: $glass-blur;
	border-bottom: 1px solid $line;
}

.rc-seg {
	position: relative;
	display: flex;
	background: rgba(20, 30, 60, 0.05);
	border-radius: 22rpx;
	padding: 6rpx;
}

.rc-seg__thumb {
	position: absolute;
	top: 6rpx;
	bottom: 6rpx;
	width: calc((100% - 12rpx) / 3);
	background: #ffffff;
	border-radius: 18rpx;
	box-shadow: 0 4rpx 16rpx rgba(20, 30, 60, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.8);
	transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
}

.rc-seg__thumb--doing {
	transform: translateX(0);
}

.rc-seg__thumb--todo {
	transform: translateX(100%);
}

.rc-seg__thumb--done {
	transform: translateX(200%);
}

.rc-seg__item {
	position: relative;
	flex: 1;
	text-align: center;
	font-size: 27rpx;
	color: $muted;
	padding: 20rpx 0;
	transition: color 0.25s, font-weight 0.25s;
}

.rc-seg__item--on {
	color: $ink;
	font-weight: 700;
}

/* 卡片列表 */
.rc-list {
	padding: 36rpx 44rpx 0;
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.rc-card {
	background: $surface;
	border-radius: $radius-card;
	padding: 38rpx 36rpx;
	box-shadow: $shadow-card;
	transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.rc-card:active {
	transform: scale(0.982);
}

.rc-card--muted {
	background: linear-gradient(170deg, #f7f7fa, #eef0f5);
	box-shadow: none;
}

.rc-card__top {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
}

.rc-card__title {
	font-size: 30rpx;
	font-weight: 700;
	color: $ink;
	line-height: 1.5;
}

.rc-card__title--soft {
	color: $ink-2;
	flex: 1;
	margin-right: 20rpx;
}

.rc-card__title--tight {
	margin-top: 26rpx;
}

/* 灰色小锁 */
.rc-lock {
	position: relative;
	width: 40rpx;
	height: 32rpx;
	background: #c7c7cc;
	border-radius: 9rpx;
	margin-top: 6rpx;
	flex-shrink: 0;
}

.rc-lock::before {
	content: "";
	position: absolute;
	top: -18rpx;
	left: 50%;
	transform: translateX(-50%);
	width: 22rpx;
	height: 22rpx;
	border: 4rpx solid #c7c7cc;
	border-bottom: none;
	border-radius: 12rpx 12rpx 0 0;
}

.rc-lock__hole {
	display: none;
}

/* 进度条 */
.rc-progress {
	display: flex;
	align-items: center;
	gap: 20rpx;
	margin: 28rpx 0;
}

.rc-progress__track {
	flex: 1;
	height: 10rpx;
	border-radius: 5rpx;
	background: rgba(20, 30, 60, 0.06);
	overflow: hidden;
}

.rc-progress__fill {
	height: 100%;
	border-radius: 5rpx;
	background: $gradient;
	transition: width 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

.rc-progress__text {
	font-size: 22rpx;
	color: $muted;
}

/* 预约计划 */
.rc-plan {
	font-size: 24rpx;
	color: $ink-2;
	margin: 22rpx 0;
}

/* 分数区 */
.rc-score-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 10rpx;
}

.rc-score__num {
	font-size: 64rpx;
	font-weight: 800;
	letter-spacing: -0.02em;
	line-height: 1;
}

.rc-score--ok .rc-score__num {
	color: $ok;
	text-shadow: 0 8rpx 24rpx rgba(52, 199, 89, 0.3);
}

.rc-score--warn .rc-score__num {
	font-size: 36rpx;
	color: $warn;
}

.rc-score--danger .rc-score__num {
	color: $danger;
	text-shadow: 0 8rpx 24rpx rgba(255, 59, 48, 0.25);
}

.rc-score__unit {
	font-size: 22rpx;
	margin-left: 8rpx;
	color: $muted;
}

.rc-badge {
	font-size: 20rpx;
	font-weight: 600;
	padding: 10rpx 22rpx;
	border-radius: $radius-pill;
}

.rc-badge--ok {
	color: #1e8e3e;
	background: $ok-soft;
}

.rc-badge--warn {
	color: #b26a00;
	background: $warn-soft;
	box-shadow: 0 4rpx 16rpx rgba(245, 166, 35, 0.2);
}

.rc-badge--danger {
	color: #d70015;
	background: $danger-soft;
}

/* 底部操作 */
.rc-card__foot {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: 30rpx;
	padding-top: 26rpx;
	border-top: 1px solid $line;
}

.rc-card__time {
	display: flex;
	align-items: center;
	gap: 10rpx;
	font-size: 22rpx;
	color: $muted;
}

.rc-card__dot--live {
	width: 12rpx;
	height: 12rpx;
	border-radius: 50%;
	background: $ok;
	animation: dot-live 1.6s ease-in-out infinite;
}

@keyframes dot-live {
	0%,
	100% {
		opacity: 1;
	}
	50% {
		opacity: 0.35;
	}
}

.rc-btn {
	font-size: 24rpx;
	font-weight: 700;
	color: #ffffff;
	background: $gradient;
	padding: 16rpx 38rpx;
	border-radius: $radius-pill;
	box-shadow: 0 8rpx 24rpx rgba(24, 82, 224, 0.3);
}

.rc-btn--ghost {
	color: $accent;
	background: $accent-soft;
	box-shadow: none;
}

.rc-btn--disabled {
	color: #aeaeb2;
	background: rgba(20, 30, 60, 0.06);
	box-shadow: none;
}

.rc-loading-wrap {
	padding-top: 60rpx;
}

.rc-empty {
	padding: 40rpx 0;
}
</style>
