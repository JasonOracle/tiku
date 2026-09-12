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
						<wd-tag :type="resolveTagType(item)" plain round>
							{{ resolveStatusText(item) }}
						</wd-tag>
					</view>

					<view class="record-card__meta">
						<text class="record-card__meta-item">总分 {{ item.total_score }}</text>
						<text class="record-card__meta-dot">·</text>
						<text class="record-card__meta-item">{{ item.question_count }} 题</text>
						<text class="record-card__meta-dot">·</text>
						<text class="record-card__meta-item">限时 {{ formatTimeLimit(item.time_limit) }}</text>
					</view>

					<!-- 底部动作与信息区 -->
					<view class="record-card__foot">
						<!-- 已参加态：展示提交时间与得分 -->
						<template v-if="activeKey === 'completed'">
							<text class="record-card__time">
								{{ item.submit_time ? `提交于 ${formatDateTime(item.submit_time)}` : "已交卷" }}
							</text>
							<view class="record-card__score-wrap">
								<text class="record-card__score" :class="{ 'record-card__score--pending': item.status === 'pending_verification' }">
									{{ item.status === 'pending_verification' ? '审核中' : `${item.score ?? 0} 分` }}
								</text>
								<view class="record-card__report-link">
									<text class="record-card__report-text">查看报告</text>
									<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
										<path d="M9 18l6-6-6-6" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
									</svg>
								</view>
							</view>
						</template>

						<!-- 未开始态：展示预计开考时间 -->
						<template v-else-if="activeKey === 'upcoming'">
							<text class="record-card__time">
								{{ item.start_time ? `开考时间：${formatDateTime(item.start_time)}` : "尚未开始" }}
							</text>
							<text class="record-card__upcoming-badge">未到时间</text>
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

function resolveTagType(item: MemberTaskItem): TagType {
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
	padding: 16px 18px;
	border: 1px solid rgba(226, 232, 240, 0.8);
	box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
	display: flex;
	flex-direction: column;
	gap: 10px;
	transition: all 0.15s ease;

	&--pressed {
		transform: scale(0.985);
		background-color: #F8FAFC;
	}

	&--disabled {
		opacity: 0.65;
	}

	&__head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 10px;
	}

	&__title {
		font-size: 15px;
		font-weight: 700;
		color: #0F172A;
		line-height: 1.4;
		flex: 1;
	}

	&__meta {
		display: flex;
		align-items: center;
		gap: 6px;
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
		padding-top: 10px;
		border-top: 1px dashed #F1F5F9;
	}

	&__time {
		font-size: 12px;
		color: #94A3B8;
	}

	&__score-wrap {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	&__score {
		font-size: 16px;
		font-weight: 800;
		color: #10B981;

		&--pending {
			font-size: 13px;
			font-weight: 600;
			color: #F59E0B;
		}
	}

	&__report-link {
		display: flex;
		align-items: center;
		gap: 2px;
		color: #1D63FF;
		font-size: 12px;
		font-weight: 600;
	}

	&__upcoming-badge {
		font-size: 12px;
		font-weight: 600;
		color: #94A3B8;
	}

	&__action-btn {
		background: #1D63FF;
		border-radius: 999px;
		padding: 5px 12px;
		display: flex;
		align-items: center;
		gap: 3px;
	}

	&__action-text {
		font-size: 12px;
		font-weight: 600;
		color: #FFFFFF;
	}
}
</style>
