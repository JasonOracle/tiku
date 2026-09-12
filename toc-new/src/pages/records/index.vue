<template>
	<view class="records-apple">
		<!-- 漫反射暮光背景 -->
		<view class="rc-aurora">
			<view class="rc-aurora__blob rc-aurora__blob--1" />
			<view class="rc-aurora__blob rc-aurora__blob--2" />
		</view>

		<!-- 钛金通顶导航栏 -->
		<view class="rc-header">
			<text class="rc-header__title">我的测试</text>
			<text class="rc-header__sub">记录你的每一次成长与突破</text>
		</view>

		<!-- Apple 柔和三态微胶囊 Tab -->
		<view class="rc-tabs-wrap">
			<view class="rc-tabs">
				<view
					v-for="tab in tabs"
					:key="tab.key"
					class="rc-tab"
					:class="{ 'rc-tab--active': activeKey === tab.key }"
					@click="switchTab(tab.key)"
				>
					<text class="rc-tab__label">{{ tab.label }}</text>
					<view v-if="badgeCount(tab.key) > 0" class="rc-tab__badge">
						<text class="rc-tab__badge-text">{{ badgeCount(tab.key) }}</text>
					</view>
				</view>
			</view>
		</view>

		<view class="rc-body">
			<!-- 状态占位 -->
			<PageState
				v-if="viewState !== 'ready'"
				:status="viewState"
				:description="viewState === 'empty' ? emptyDescription : ''"
				:action-text="viewState === 'error' ? '重新加载' : ''"
				@action="loadTasks()"
			/>

			<!-- 钛金卡片流 -->
			<view v-else class="rc-list">
				<view
					v-for="item in currentList"
					:key="item.task_id"
					class="rc-card"
					:class="{ 'rc-card--disabled': activeKey === 'upcoming' }"
					hover-class="rc-card--pressed"
					@click="handleCardClick(item)"
				>
					<view class="rc-card__head">
						<text class="rc-card__title">{{ item.title }}</text>
						<view class="rc-status-pill" :class="`rc-status-pill--${resolveTagClass(item)}`">
							<text class="rc-status-pill__text">{{ resolveStatusText(item) }}</text>
						</view>
					</view>

					<view class="rc-card__meta">
						<text class="rc-card__meta-item">总分 {{ item.total_score }}</text>
						<text class="rc-card__meta-dot">·</text>
						<text class="rc-card__meta-item">{{ item.question_count }} 题</text>
						<text class="rc-card__meta-dot">·</text>
						<text class="rc-card__meta-item">限时 {{ formatTimeLimit(item.time_limit) }}</text>
					</view>

					<!-- 底部动作与信息区 -->
					<view class="rc-card__foot">
						<!-- 已参加态：左侧提交时间，右侧显赫得分与复盘按钮 -->
						<template v-if="activeKey === 'completed'">
							<view class="rc-card__foot-left">
								<text class="rc-card__time">
									{{ item.submit_time ? `提交于 ${formatDateTime(item.submit_time)}` : "已交卷" }}
								</text>
							</view>
							<view class="rc-card__foot-right">
								<view v-if="item.status === 'pending_verification'" class="rc-card__audit-pill">
									<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
										<circle cx="12" cy="12" r="10" stroke="#F59E0B" stroke-width="2"/>
										<polyline points="12 6 12 12 16 14" stroke="#F59E0B" stroke-width="2" stroke-linecap="round"/>
									</svg>
									<text class="rc-card__audit-text">批阅核验中</text>
								</view>
								<view v-else class="rc-card__score-box">
									<text class="rc-card__score-num">{{ item.score ?? 0 }}</text>
									<text class="rc-card__score-unit">分</text>
								</view>
								<view class="rc-card__entry-btn">
									<text class="rc-card__entry-text">复盘</text>
									<svg width="11" height="11" viewBox="0 0 24 24" fill="none">
										<path d="M9 18l6-6-6-6" stroke="#1852E0" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
									</svg>
								</view>
							</view>
						</template>

						<!-- 未开始态：预计开考时间与锁定标签 -->
						<template v-else-if="activeKey === 'upcoming'">
							<text class="rc-card__time">
								{{ item.start_time ? `预约开考：${formatDateTime(item.start_time)}` : "尚未开始" }}
							</text>
							<view class="rc-card__lock-pill">
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
									<rect x="5" y="11" width="14" height="10" rx="2" stroke="#86868b" stroke-width="2"/>
									<path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="#86868b" stroke-width="2"/>
								</svg>
								<text class="rc-card__lock-text">未到时间</text>
							</view>
						</template>

						<!-- 进行中态：截止时间与进入作答按钮 -->
						<template v-else>
							<text class="rc-card__time">
								{{ item.deadline ? `截止：${formatDeadline(item.deadline)}` : "长期有效" }}
							</text>
							<view class="rc-card__action-btn">
								<text class="rc-card__action-text">进入作答</text>
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
									<path d="M9 18l6-6-6-6" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</view>
						</template>
					</view>
				</view>
			</view>

			<!-- 底部占位安全区 -->
			<view class="rc-bottom-space" />
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 全面升级我的测试页面为 Apple 钛金微光风，采用拟物微胶囊 Tab 与大圆角卡片; 2. 真实对接后端 GET /api/v1/member/member-tasks，严格执行「进行中/未开始/已参加」三态归类]
 */
import { computed, ref, reactive } from "vue";
import { onShow } from "@dcloudio/uni-app";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchMemberTasks, type MemberTaskItem } from "@/api/exam";
import { formatDateTime, formatDeadline, formatTimeLimit } from "@/utils/format";

type RequestStatus = "loading" | "empty" | "error" | "ready";
type TabKey = "ongoing" | "upcoming" | "completed";

const tabs: Array<{ key: TabKey; label: string }> = [
	{ key: "ongoing", label: "进行中" },
	{ key: "upcoming", label: "未开始" },
	{ key: "completed", label: "已参加" },
];

const activeKey = ref<TabKey>("ongoing");
const requestStatus = ref<RequestStatus>("loading");

const grouped = reactive<Record<TabKey, MemberTaskItem[]>>({
	ongoing: [],
	upcoming: [],
	completed: [],
});

const currentList = computed(() => grouped[activeKey.value]);

function badgeCount(key: TabKey): number {
	return grouped[key].length;
}

function switchTab(key: TabKey): void {
	activeKey.value = key;
}

const viewState = computed<RequestStatus>(() => {
	if (requestStatus.value !== "ready") return requestStatus.value;
	return currentList.value.length ? "ready" : "empty";
});

const emptyDescription = computed(() => {
	if (activeKey.value === "ongoing") return "当前没有正在进行中的测评";
	if (activeKey.value === "upcoming") return "暂无未开始的计划测评";
	return "暂无已参加的测评记录，快去完成一次测评吧";
});

function resolveTagClass(item: MemberTaskItem): "success" | "warning" | "primary" | "default" {
	if (activeKey.value === "completed") {
		return item.status === "pending_verification" ? "warning" : "success";
	}
	if (activeKey.value === "upcoming") return "default";
	return "primary";
}

function resolveStatusText(item: MemberTaskItem): string {
	if (activeKey.value === "completed") {
		return item.status === "pending_verification" ? "审核中" : "已完成";
	}
	if (activeKey.value === "upcoming") return "未开始";
	return item.status === "pending" ? "作答中" : "可开考";
}

const DONE_STATUSES = ["submitted", "verified", "pending_verification"];

async function loadTasks(silent = false): Promise<void> {
	if (!silent) requestStatus.value = "loading";
	try {
		const res = await fetchMemberTasks();
		const items = res.items || [];
		const now = new Date();

		const ongoingList: MemberTaskItem[] = [];
		const upcomingList: MemberTaskItem[] = [];
		const completedList: MemberTaskItem[] = [];

		for (const item of items) {
			// 1. 已参加
			if (DONE_STATUSES.includes(item.status)) {
				completedList.push(item);
				continue;
			}

			// 2. 未开始
			if (item.start_time) {
				const start = new Date(item.start_time);
				if (!Number.isNaN(start.getTime()) && start > now) {
					upcomingList.push(item);
					continue;
				}
			}

			// 3. 进行中
			ongoingList.push(item);
		}

		grouped.ongoing = ongoingList;
		grouped.upcoming = upcomingList;
		grouped.completed = completedList;

		requestStatus.value = "ready";
	} catch {
		requestStatus.value = "error";
	}
}

function handleCardClick(item: MemberTaskItem): void {
	if (activeKey.value === "completed") {
		if (item.record_id) {
			uni.navigateTo({ url: `/pages/report/index?record_id=${item.record_id}` });
		}
		return;
	}

	if (activeKey.value === "upcoming") {
		uni.showToast({ title: "该测评尚未开始", icon: "none" });
		return;
	}

	uni.navigateTo({
		url: `/pages/exam/index?task_id=${item.task_id}&title=${encodeURIComponent(item.title)}`,
	});
}

onShow(() => {
	loadTasks(true);
});
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.records-apple {
	position: relative;
	min-height: 100vh;
	background: $bg;
	overflow: hidden;
}

/* 漫反射微光晕 */
.rc-aurora {
	position: absolute;
	inset: 0;
	pointer-events: none;
	overflow: hidden;

	&__blob {
		position: absolute;
		border-radius: 50%;
		filter: blur(80px);
		opacity: 0.4;

		&--1 {
			width: 500rpx;
			height: 500rpx;
			top: -140rpx;
			right: -100rpx;
			background: radial-gradient(circle, rgba(24, 82, 224, 0.38), rgba(24, 82, 224, 0));
		}

		&--2 {
			width: 440rpx;
			height: 440rpx;
			top: 360rpx;
			left: -120rpx;
			background: radial-gradient(circle, rgba(124, 92, 255, 0.28), rgba(124, 92, 255, 0));
		}
	}
}

/* 顶部标题区 */
.rc-header {
	position: relative;
	z-index: 2;
	padding: 44rpx 36rpx 16rpx;

	&__title {
		font-size: 40rpx;
		font-weight: 800;
		color: $ink;
		letter-spacing: -0.3px;
	}

	&__sub {
		display: block;
		font-size: 22rpx;
		color: $muted;
		margin-top: 6rpx;
	}
}

/* 钛金微胶囊 Tab */
.rc-tabs-wrap {
	position: relative;
	z-index: 2;
	padding: 10rpx 32rpx 20rpx;
}

.rc-tabs {
	background: rgba(255, 255, 255, 0.75);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: $radius-pill;
	padding: 6rpx;
	display: flex;
	box-shadow: $shadow-card;
}

.rc-tab {
	flex: 1;
	height: 68rpx;
	border-radius: $radius-pill;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8rpx;
	transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

	&--active {
		background: #ffffff;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);

		.rc-tab__label {
			color: $accent;
			font-weight: 700;
		}

		.rc-tab__badge {
			background: $accent-soft;
			.rc-tab__badge-text {
				color: $accent;
			}
		}
	}

	&__label {
		font-size: 26rpx;
		font-weight: 500;
		color: $ink-2;
	}

	&__badge {
		background: $surface-sunken;
		padding: 2rpx 12rpx;
		border-radius: 999rpx;
	}

	&__badge-text {
		font-size: 20rpx;
		font-weight: 700;
		color: $muted;
	}
}

.rc-body {
	position: relative;
	z-index: 2;
	padding: 10rpx 32rpx 40rpx;
}

.rc-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

/* 钛金测试卡片 */
.rc-card {
	background: rgba(255, 255, 255, 0.92);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: $radius-card;
	padding: 32rpx 36rpx;
	box-shadow: $shadow-card;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
	transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

	&--pressed {
		transform: scale(0.985);
		background: #ffffff;
	}

	&--disabled {
		opacity: 0.65;
	}

	&__head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 16rpx;
	}

	&__title {
		font-size: 30rpx;
		font-weight: 700;
		color: $ink;
		line-height: 1.45;
		flex: 1;
	}

	&__meta {
		display: flex;
		align-items: center;
		gap: 10rpx;
		font-size: 24rpx;
		color: $muted;
	}

	&__meta-dot {
		color: $line-strong;
	}

	&__foot {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-top: 20rpx;
		border-top: 1px solid $line;
	}

	&__foot-left {
		display: flex;
		align-items: center;
	}

	&__foot-right {
		display: flex;
		align-items: center;
		gap: 16rpx;
	}

	&__time {
		font-size: 22rpx;
		color: $muted;
	}

	&__score-box {
		display: flex;
		align-items: baseline;
		gap: 4rpx;
	}

	&__score-num {
		font-size: 36rpx;
		font-weight: 800;
		color: $ok;
		line-height: 1;
		font-feature-settings: "tnum";
	}

	&__score-unit {
		font-size: 22rpx;
		font-weight: 600;
		color: $ok;
	}

	&__audit-pill {
		display: flex;
		align-items: center;
		gap: 6rpx;
		background: $warn-soft;
		padding: 6rpx 14rpx;
		border-radius: 10rpx;
	}

	&__audit-text {
		font-size: 22rpx;
		font-weight: 600;
		color: $warn;
	}

	&__entry-btn {
		display: flex;
		align-items: center;
		gap: 4rpx;
		background: $accent-soft;
		border-radius: $radius-pill;
		padding: 8rpx 18rpx;
	}

	&__entry-text {
		font-size: 22rpx;
		font-weight: 600;
		color: $accent;
	}

	&__lock-pill {
		display: flex;
		align-items: center;
		gap: 6rpx;
		background: $surface-sunken;
		padding: 8rpx 18rpx;
		border-radius: $radius-pill;
	}

	&__lock-text {
		font-size: 22rpx;
		font-weight: 600;
		color: $muted;
	}

	&__action-btn {
		background: $gradient;
		border-radius: $radius-pill;
		padding: 10rpx 24rpx;
		display: flex;
		align-items: center;
		gap: 6rpx;
		box-shadow: 0 6rpx 16rpx rgba(24, 82, 224, 0.25);
	}

	&__action-text {
		font-size: 22rpx;
		font-weight: 600;
		color: #ffffff;
	}
}

/* 状态徽章 */
.rc-status-pill {
	padding: 4rpx 14rpx;
	border-radius: 10rpx;
	flex-shrink: 0;

	&__text {
		font-size: 20rpx;
		font-weight: 600;
	}

	&--success {
		background: $ok-soft;
		.rc-status-pill__text {
			color: $ok;
		}
	}

	&--warning {
		background: $warn-soft;
		.rc-status-pill__text {
			color: $warn;
		}
	}

	&--primary {
		background: $accent-soft;
		.rc-status-pill__text {
			color: $accent;
		}
	}

	&--default {
		background: $surface-sunken;
		.rc-status-pill__text {
			color: $muted;
		}
	}
}

.rc-bottom-space {
	height: calc(100rpx + env(safe-area-inset-bottom));
}
</style>
