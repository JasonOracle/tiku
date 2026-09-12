<template>
	<view class="records">
		<!-- Header + 经典三态 Tabs 整体吸顶 -->
		<view class="records__sticky">
			<CustomHeader title="我的测试" />

			<view class="records__tabs">
				<view
					v-for="tab in tabs"
					:key="tab.key"
					class="records__tab"
					@click="handleTabChange(tab.key)"
				>
					<view class="records__tab-content">
						<text class="records__tab-text" :class="{ 'records__tab-text--active': activeKey === tab.key }">
							{{ tab.label }}
						</text>
						<text class="records__tab-badge" :class="{ 'records__tab-badge--active': activeKey === tab.key }">
							{{ grouped[tab.key].length }}
						</text>
					</view>
				</view>
				<!-- 极客蓝滑动指示器 -->
				<view class="records__indicator" :style="{ transform: `translateX(${activeIndex * 100}%)` }" />
			</view>
		</view>

		<view class="records__body">
			<!-- 加载/空态/错误态 -->
			<PageState
				v-if="viewState !== 'ready'"
				:status="viewState"
				:description="viewState === 'empty' ? emptyDescription : ''"
				:action-text="viewState === 'error' ? '重新加载' : ''"
				@action="loadTasks()"
			/>

			<!-- 试卷卡片流 -->
			<view v-else class="records__list">
				<view
					v-for="item in currentList"
					:key="item.task_id"
					class="record-card"
					:class="{ 'record-card--disabled': activeKey === 'upcoming' }"
					hover-class="record-card--pressed"
					@click="handleCardClick(item)"
				>
					<view class="record-card__head">
						<text class="record-card__title">{{ item.title }}</text>
						<view class="status-badge" :class="`status-badge--${resolveTagClass(item)}`">
							<text class="status-badge__text">{{ resolveStatusText(item) }}</text>
						</view>
					</view>

					<view class="record-card__meta">
						<text class="record-card__meta-item">满分 {{ item.total_score }}</text>
						<text class="record-card__meta-dot">·</text>
						<text class="record-card__meta-item">{{ item.question_count }} 题</text>
						<text class="record-card__meta-dot">·</text>
						<text class="record-card__meta-item">限时 {{ formatTimeLimit(item.time_limit) }}</text>
					</view>

					<!-- 底部信息与动作区 -->
					<view class="record-card__foot">
						<!-- 已参加态：左侧提交时间，右侧显赫得分与查看报告轻按钮 -->
						<template v-if="activeKey === 'completed'">
							<view class="record-card__foot-left">
								<text class="record-card__time">
									{{ item.submit_time ? `提交于 ${formatDateTime(item.submit_time)}` : "已交卷" }}
								</text>
							</view>
							<view class="record-card__foot-right">
								<view v-if="item.status === 'pending_verification'" class="record-card__audit-pill">
									<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
										<circle cx="12" cy="12" r="10" stroke="#F59E0B" stroke-width="2"/>
										<polyline points="12 6 12 12 16 14" stroke="#F59E0B" stroke-width="2" stroke-linecap="round"/>
									</svg>
									<text class="record-card__audit-text">批阅核验中</text>
								</view>
								<view v-else class="record-card__score-box">
									<text class="record-card__score-num">{{ item.score ?? 0 }}</text>
									<text class="record-card__score-unit">分</text>
								</view>
								<view class="record-card__entry-btn">
									<text class="record-card__entry-text">复盘</text>
									<svg width="11" height="11" viewBox="0 0 24 24" fill="none">
										<path d="M9 18l6-6-6-6" stroke="#1D63FF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
									</svg>
								</view>
							</view>
						</template>

						<!-- 未开始态：展示预计开考时间与锁定胶囊 -->
						<template v-else-if="activeKey === 'upcoming'">
							<text class="record-card__time">
								{{ item.start_time ? `预约开考：${formatDateTime(item.start_time)}` : "尚未开始" }}
							</text>
							<view class="record-card__lock-pill">
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
									<rect x="5" y="11" width="14" height="10" rx="2" stroke="#94A3B8" stroke-width="2"/>
									<path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="#94A3B8" stroke-width="2"/>
								</svg>
								<text class="record-card__lock-text">未到时间</text>
							</view>
						</template>

						<!-- 进行中态：展示截止时间与进入考场按钮 -->
						<template v-else>
							<text class="record-card__time">
								{{ item.deadline ? `截止：${formatDeadline(item.deadline)}` : "长期有效" }}
							</text>
							<view class="record-card__action-btn">
								<text class="record-card__action-text">进入作答</text>
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
									<path d="M9 18l6-6-6-6" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
								</svg>
							</view>
						</template>
					</view>
				</view>
			</view>

			<!-- 底部占位 -->
			<view class="records__bottom-space" />
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[彻底恢复 v1.4 经典三态架构：进行中 / 未开始 / 已参加，严格按考情生命周期进行数据归类与状态流转]
 */
import { computed, ref, reactive } from "vue";
import { onShow } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchMemberTasks, type MemberTaskItem } from "@/api/exam";
import { formatDateTime, formatDeadline, formatTimeLimit, formatRecordStatus } from "@/utils/format";

type TagType = "default" | "primary" | "success" | "warning" | "danger";
type RequestStatus = "loading" | "empty" | "error" | "ready";
type TabKey = "ongoing" | "upcoming" | "completed";

// 严格对齐 v1.4 经典三态
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
	completed: []
});

const activeIndex = computed(() => tabs.findIndex((tab) => tab.key === activeKey.value));
const currentList = computed(() => grouped[activeKey.value]);

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
			// 1. 已参加：已交卷 / 审核中 / 已核验
			if (DONE_STATUSES.includes(item.status)) {
				completedList.push(item);
				continue;
			}

			// 2. 未开始：未作答且明确配置了尚未到达的 start_time
			if (item.start_time) {
				const startTime = new Date(item.start_time);
				if (now < startTime) {
					upcomingList.push(item);
					continue;
				}
			}

			// 3. 其余均为进行中（随时可考或作答中）
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

function handleTabChange(key: TabKey): void {
	activeKey.value = key;
}

function handleCardClick(item: MemberTaskItem): void {
	// 未开始态置灰不可点
	if (activeKey.value === "upcoming") return;

	// 已参加态：直接跳往成绩复盘报告页（携带 record_id）
	if (activeKey.value === "completed" || DONE_STATUSES.includes(item.status)) {
		if (item.record_id) {
			uni.navigateTo({ url: `/pages/report/index?record_id=${item.record_id}` });
		}
		return;
	}

	// 进行中态：进入考场
	uni.navigateTo({
		url: `/pages/exam/index?task_id=${item.task_id}&title=${encodeURIComponent(item.title)}`
	});
}

onShow(() => {
	loadTasks(requestStatus.value === "ready");
});
</script>

<style lang="scss" scoped>
.records {
	min-height: 100vh;
	background-color: #F8FAFC;

	&__sticky {
		position: sticky;
		top: 0;
		z-index: 20;
		background: #FFFFFF;
		box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
	}

	&__tabs {
		position: relative;
		display: flex;
		height: 46px;
		background: #FFFFFF;
		border-bottom: 1px solid #F1F5F9;
	}

	&__tab {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	&__tab-content {
		display: flex;
		align-items: center;
		gap: 5px;
	}

	&__tab-text {
		font-size: 14px;
		font-weight: 500;
		color: #64748B;
		transition: all 0.2s ease;

		&--active {
			font-size: 15px;
			font-weight: 700;
			color: #1D63FF;
		}
	}

	&__tab-badge {
		font-size: 11px;
		font-weight: 600;
		color: #94A3B8;
		background: #F1F5F9;
		padding: 1px 6px;
		border-radius: 999px;

		&--active {
			color: #1D63FF;
			background: rgba(29, 99, 255, 0.1);
		}
	}

	&__indicator {
		position: absolute;
		bottom: 0;
		left: 0;
		width: 33.3333%;
		height: 2px;
		background: #1D63FF;
		transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
	}

	&__body {
		padding: 14px 16px;
	}

	&__list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	&__bottom-space {
		height: 32px;
	}
}

.record-card {
	background: #FFFFFF;
	border-radius: 16px;
	padding: 18px 20px;
	border: 1px solid rgba(226, 232, 240, 0.7);
	box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
	display: flex;
	flex-direction: column;
	gap: 12px;
	transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

	&--pressed {
		transform: translateY(1px);
		box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
		background-color: #F8FAFC;
	}

	&--disabled {
		opacity: 0.7;
	}

	&__head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
	}

	&__title {
		font-size: 15px;
		font-weight: 700;
		color: #0F172A;
		line-height: 1.45;
		flex: 1;
		letter-spacing: -0.2px;
	}

	&__meta {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 12px;
		color: #64748B;
	}

	&__meta-dot {
		color: #CBD5E1;
	}

	&__foot {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding-top: 12px;
		border-top: 1px solid #F1F5F9;
	}

	&__foot-left {
		display: flex;
		align-items: center;
	}

	&__foot-right {
		display: flex;
		align-items: center;
		gap: 12px;
	}

	&__time {
		font-size: 12px;
		color: #94A3B8;
	}

	&__score-box {
		display: flex;
		align-items: baseline;
		gap: 2px;
	}

	&__score-num {
		font-size: 20px;
		font-weight: 800;
		color: #059669;
		line-height: 1;
		font-feature-settings: "tnum";
	}

	&__score-unit {
		font-size: 12px;
		font-weight: 600;
		color: #10B981;
	}

	&__audit-pill {
		display: flex;
		align-items: center;
		gap: 4px;
		background: #FFFBEB;
		padding: 4px 8px;
		border-radius: 6px;
	}

	&__audit-text {
		font-size: 12px;
		font-weight: 600;
		color: #D97706;
	}

	&__entry-btn {
		display: flex;
		align-items: center;
		gap: 2px;
		background: #EFF6FF;
		border-radius: 999px;
		padding: 4px 10px;
		transition: background 0.15s ease;

		&:active {
			background: #DBEAFE;
		}
	}

	&__entry-text {
		font-size: 12px;
		font-weight: 600;
		color: #1D63FF;
	}

	&__lock-pill {
		display: flex;
		align-items: center;
		gap: 4px;
		background: #F1F5F9;
		padding: 4px 10px;
		border-radius: 999px;
	}

	&__lock-text {
		font-size: 11px;
		font-weight: 600;
		color: #64748B;
	}

	&__action-btn {
		background: linear-gradient(135deg, #1D63FF 0%, #0045D8 100%);
		border-radius: 999px;
		padding: 6px 14px;
		display: flex;
		align-items: center;
		gap: 4px;
		box-shadow: 0 4px 12px rgba(29, 99, 255, 0.25);
	}

	&__action-text {
		font-size: 12px;
		font-weight: 600;
		color: #FFFFFF;
	}
}

/* 状态徽章微系统 */
.status-badge {
	padding: 3px 8px;
	border-radius: 6px;
	flex-shrink: 0;

	&__text {
		font-size: 11px;
		font-weight: 600;
	}

	&--success {
		background: #ECFDF5;
		.status-badge__text {
			color: #059669;
		}
	}

	&--warning {
		background: #FFFBEB;
		.status-badge__text {
			color: #D97706;
		}
	}

	&--primary {
		background: #EFF6FF;
		.status-badge__text {
			color: #1D63FF;
		}
	}

	&--default {
		background: #F1F5F9;
		.status-badge__text {
			color: #64748B;
		}
	}
}
</style>
