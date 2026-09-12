<template>
	<view class="records">
		<!-- Header + 分类栏整体吸顶，仅列表滚动 -->
		<view class="records__sticky">
			<CustomHeader title="我的测试" />

			<view class="records__tabs">
				<view v-for="tab in tabs" :key="tab.key" class="records__tab" @click="handleTabChange(tab.key)">
					<text class="records__tab-text" :class="{ 'records__tab-text--active': activeKey === tab.key }">
						{{ tab.label }}
					</text>
				</view>
				<!-- 极客蓝下划线指示器：按当前激活项滑动 -->
				<view class="records__indicator" :style="{ transform: `translateX(${activeIndex * 100}%)` }" />
			</view>
		</view>

		<view class="records__body">
			<PageState
				v-if="viewState !== 'ready'"
				:status="viewState"
				:description="viewState === 'empty' ? emptyDescription : ''"
				:action-text="viewState === 'error' ? '重新加载' : ''"
				@action="loadRecords()"
			/>

			<view v-else class="records__list">
				<view
				v-for="item in filteredRecords"
				:key="item.record_id"
				class="record-card"
				hover-class="record-card--pressed"
				@click="goReport(item.record_id)"
			>
					<view class="record-card__head">
						<text class="record-card__title">{{ item.task_title }}</text>
						<wd-tag :type="resolveTagType(item.status)" plain round>{{ formatRecordStatus(item.status) }}</wd-tag>
					</view>

					<view class="record-card__foot">
						<text class="record-card__time">提交于 {{ formatDateTime(item.submit_time) }}</text>
						<text class="record-card__score" :class="{ 'record-card__score--pending': item.score === null }">
							{{ item.score === null ? "核验中" : `${item.score} 分` }}
						</text>
					</view>
				</view>
			</view>

			<!-- 原生 tabBar 与底部安全区占位 -->
			<view class="records__bottom-space" />
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 历史作答记录卡片支持点击查看，跳转成绩报告页复盘（携带 record_id）]
 */
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchMyRecords, type MyRecordItem } from "@/api/exam";
import { formatDateTime, formatRecordStatus } from "@/utils/format";

type TagType = "default" | "primary" | "success" | "warning" | "danger";
type RequestStatus = "loading" | "empty" | "error" | "ready";
type TabKey = "all" | "pending" | "done";

const tabs: Array<{ key: TabKey; label: string }> = [
	{ key: "all", label: "全部" },
	{ key: "pending", label: "待核验" },
	{ key: "done", label: "已完成" },
];

const activeKey = ref<TabKey>("all");
const requestStatus = ref<RequestStatus>("loading");
const records = ref<MyRecordItem[]>([]);

const activeIndex = computed(() => tabs.findIndex((tab) => tab.key === activeKey.value));

/** 分类过滤：待核验取核验中，已完成取已核验与已定稿 */
const filteredRecords = computed(() => {
	if (activeKey.value === "pending") {
		return records.value.filter((item) => item.status === "pending_verification");
	}
	if (activeKey.value === "done") {
		return records.value.filter((item) => item.status === "verified" || item.status === "submitted");
	}
	return records.value;
});

/** 请求态优先，请求成功后若当前分类下无数据则视为空态 */
const viewState = computed<RequestStatus>(() => {
	if (requestStatus.value !== "ready") return requestStatus.value;
	return filteredRecords.value.length ? "ready" : "empty";
});

const emptyDescription = computed(() => {
	if (activeKey.value === "pending") return "当前没有等待核验的作答记录";
	if (activeKey.value === "done") return "还没有已完成定稿的测评记录";
	return "完成第一次测评后，作答记录会显示在这里";
});

function resolveTagType(status: string): TagType {
	if (status === "pending_verification") return "warning";
	if (status === "verified" || status === "submitted") return "success";
	return "default";
}

/** 拉取本人历史作答记录；silent 用于切回页面时避免骨架屏闪烁 */
async function loadRecords(silent = false): Promise<void> {
	if (!silent) requestStatus.value = "loading";
	try {
		const data = await fetchMyRecords();
		records.value = data.items;
		requestStatus.value = "ready";
	} catch {
		// 失败信息已由请求层统一轻提示，这里只负责切换到错误态
		requestStatus.value = "error";
	}
}

function handleTabChange(key: TabKey): void {
	activeKey.value = key;
}

/** 进入本次作答的成绩报告页复盘（报告页非 tabBar 页，用 navigateTo） */
function goReport(recordId: number): void {
	uni.navigateTo({ url: `/pages/report/index?record_id=${recordId}` });
}

onShow(() => {
	loadRecords(requestStatus.value === "ready");
});
</script>

<style lang="scss" scoped>
.records {
	min-height: 100vh;
	background-color: #f6f8fc;
}

.records__sticky {
	position: sticky;
	top: 0;
	z-index: 20;
	background-color: #ffffff;
}

.records__tabs {
	position: relative;
	display: flex;
	align-items: center;
	height: 88rpx;
}

.records__tab {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	height: 100%;
}

.records__tab-text {
	font-size: 28rpx;
	color: #748094;
	transition: color 0.2s ease;
}

.records__tab-text--active {
	font-size: 30rpx;
	font-weight: 600;
	color: #1d63ff;
}

.records__indicator {
	position: absolute;
	left: 0;
	bottom: 0;
	width: 33.3333%;
	display: flex;
	justify-content: center;
	transition: transform 0.25s ease;
}

.records__indicator::after {
	content: "";
	width: 48rpx;
	height: 6rpx;
	border-radius: 3rpx;
	background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
}

.records__body {
	padding: 24rpx 32rpx 0;
}

.records__list {
	display: flex;
	flex-direction: column;
}

.record-card {
	padding: 32rpx;
	margin-bottom: 24rpx;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.record-card--pressed {
	transform: scale(0.98);
	opacity: 0.92;
}

.record-card__head {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
}

.record-card__title {
	flex: 1;
	margin-right: 16rpx;
	font-size: 30rpx;
	font-weight: 600;
	line-height: 1.45;
	color: #1c2331;
}

.record-card__foot {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-top: 24rpx;
	padding-top: 22rpx;
	border-top: 1rpx solid #f0f3f9;
}

.record-card__time {
	font-size: 24rpx;
	color: #a8b2c4;
}

.record-card__score {
	font-size: 32rpx;
	font-weight: 600;
	color: #00b578;
}

.record-card__score--pending {
	font-size: 26rpx;
	color: #f0883a;
}

.records__bottom-space {
	height: calc(48rpx + constant(safe-area-inset-bottom));
	height: calc(48rpx + env(safe-area-inset-bottom));
}
</style>
