<template>
	<view class="home">
		<!-- 通顶渐变区：Header 透明融入，向下延伸出欢迎区与统计，底边圆角收口 -->
		<view class="home__hero">
			<CustomHeader variant="transparent" :title="institutionName">
				<template #right>
					<text class="home__hero-badge">{{ availableCount }} 场可考</text>
				</template>
			</CustomHeader>

			<view class="home__welcome">
				<text class="home__greeting">{{ greeting }}</text>
				<text class="home__slogan">保持节奏，稳步提分</text>

				<view class="home__stats">
					<view class="home__stat">
						<text class="home__stat-value">{{ cards.length }}</text>
						<text class="home__stat-label">全部测评</text>
					</view>
					<view class="home__stat-split" />
					<view class="home__stat">
						<text class="home__stat-value">{{ availableCount }}</text>
						<text class="home__stat-label">待参与</text>
					</view>
					<view class="home__stat-split" />
					<view class="home__stat">
						<text class="home__stat-value">{{ finishedCount }}</text>
						<text class="home__stat-label">已参与</text>
					</view>
				</view>
			</view>
		</view>

		<view class="home__body">
			<view class="home__section">
				<text class="home__section-title">可参与的测评</text>
				<text class="home__section-count">{{ cards.length }} 项</text>
			</view>

			<PageState v-if="status !== 'ready'" :status="status" action-text="重新加载" @action="loadTasks()" />

			<view v-else class="home__list">
				<view
					v-for="item in cards"
					:key="item.task_id"
					class="exam-card"
					hover-class="exam-card--active"
					@click="goExam(item)"
				>
					<view class="exam-card__head">
						<text class="exam-card__title">{{ item.title }}</text>
						<wd-tag :type="item.tagType" plain round>{{ item.statusText }}</wd-tag>
					</view>

					<text class="exam-card__meta">
						总分 {{ item.total_score }} · {{ item.question_count }} 题 · 限时 {{ formatTimeLimit(item.time_limit) }}
					</text>
					<text class="exam-card__deadline">截止 {{ formatDeadline(item.deadline) }}</text>

					<view class="exam-card__foot">
						<text class="exam-card__category">{{ item.category_name || "综合测评" }}</text>
						<view class="exam-card__go">
							<text class="exam-card__go-text" :class="{ 'exam-card__go-text--scored': item.score !== null }">
								{{ item.score !== null ? `得分 ${item.score}` : "进入考场" }}
							</text>
							<svg class="exam-card__go-icon" viewBox="0 0 24 24" fill="none">
								<path d="m9.5 5 7 7-7 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
							</svg>
						</view>
					</view>
				</view>
			</view>

			<!-- 原生 tabBar 与底部安全区占位 -->
			<view class="home__bottom-space" />
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 由模板示例页重写为首页：通顶渐变 Header 展示机构名、欢迎统计区、测评卡片流; 2. 接入真实测评列表接口并补齐加载/空/错误三态]
 */
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchMemberTasks, type MemberTaskItem } from "@/api/exam";
import { useUserStore } from "@/stores/user";
import { formatDeadline, formatRecordStatus, formatTimeLimit } from "@/utils/format";

type TagType = "default" | "primary" | "success" | "warning" | "danger";
type PageStatus = "loading" | "empty" | "error" | "ready";

/** 卡片视图模型：在接口字段之上派生展示文案与标签色 */
type ExamCardView = MemberTaskItem & {
	statusText: string;
	tagType: TagType;
};

const userStore = useUserStore();

const status = ref<PageStatus>("loading");
const taskList = ref<MemberTaskItem[]>([]);

/** 所属机构名称：从已加入租户中匹配当前生效租户，未匹配到时回退默认空间名 */
const institutionName = computed(() => {
	const matched = userStore.joinedTenants.find((tenant) => tenant.tenant_id === userStore.tenantId);
	return matched?.tenant_name || "智题库企业空间";
});

const greeting = computed(() => {
	const hour = new Date().getHours();
	if (hour < 6) return "夜深了";
	if (hour < 12) return "早上好";
	if (hour < 14) return "中午好";
	if (hour < 18) return "下午好";
	return "晚上好";
});

function resolveTagType(item: MemberTaskItem): TagType {
	if (item.record_id === null) return "primary";
	if (item.status === "pending_verification") return "warning";
	if (item.status === "verified" || item.status === "submitted") return "success";
	return "default";
}

const cards = computed<ExamCardView[]>(() =>
	taskList.value.map((item) => ({
		...item,
		statusText: item.record_id === null ? "待参与" : formatRecordStatus(item.status),
		tagType: resolveTagType(item),
	}))
);

const availableCount = computed(() => taskList.value.filter((item) => item.record_id === null).length);
const finishedCount = computed(() => taskList.value.filter((item) => item.record_id !== null).length);

/**
 * 拉取可考测评列表。
 * silent 为 true 时不重置为加载态，用于从其它 Tab 切回首页时避免骨架屏闪烁。
 */
async function loadTasks(silent = false): Promise<void> {
	if (!silent) status.value = "loading";
	try {
		const data = await fetchMemberTasks();
		taskList.value = data.items;
		status.value = data.items.length ? "ready" : "empty";
	} catch {
		// 失败信息已由请求层统一轻提示，这里只负责切换到错误态，避免白屏
		status.value = "error";
	}
}

function goExam(item: MemberTaskItem): void {
	// 严禁在此调用入考接口：后端会真实创建作答记录并锁定开考时间，属不可逆副作用
	uni.navigateTo({
		url: `/pages/exam/index?task_id=${item.task_id}&title=${encodeURIComponent(item.title)}`,
	});
}

onShow(() => {
	// 未登录时首页是应用启动页，直接回登录页，避免用无凭证请求触发 401 导致骨架屏空闪
	if (!userStore.isLoggedIn) {
		uni.reLaunch({ url: "/pages/login/index" });
		return;
	}
	// 首次进入展示骨架屏；已有数据时静默刷新，避免每次切回都闪一下
	loadTasks(status.value === "ready");
});
</script>

<style lang="scss" scoped>
.home {
	min-height: 100vh;
	background-color: #f6f8fc;
}

.home__hero {
	padding-bottom: 56rpx;
	background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
	border-bottom-left-radius: 40rpx;
	border-bottom-right-radius: 40rpx;
}

.home__hero-badge {
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.86);
}

.home__welcome {
	padding: 24rpx 32rpx 0;
}

.home__greeting {
	display: block;
	font-size: 46rpx;
	font-weight: 600;
	letter-spacing: 2rpx;
	color: #ffffff;
}

.home__slogan {
	display: block;
	margin-top: 10rpx;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.74);
}

.home__stats {
	display: flex;
	align-items: center;
	margin-top: 40rpx;
	padding: 28rpx 0;
	border-radius: 24rpx;
	background-color: rgba(255, 255, 255, 0.14);
}

.home__stat {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.home__stat-split {
	width: 1rpx;
	height: 48rpx;
	background-color: rgba(255, 255, 255, 0.24);
}

.home__stat-value {
	font-size: 40rpx;
	font-weight: 600;
	color: #ffffff;
}

.home__stat-label {
	margin-top: 8rpx;
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.74);
}

.home__body {
	padding: 0 32rpx;
}

.home__section {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 40rpx 0 24rpx;
}

.home__section-title {
	font-size: 32rpx;
	font-weight: 600;
	color: #1c2331;
}

.home__section-count {
	font-size: 24rpx;
	color: #748094;
}

.home__list {
	display: flex;
	flex-direction: column;
}

.exam-card {
	padding: 32rpx;
	margin-bottom: 24rpx;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.exam-card--active {
	transform: scale(0.98);
	opacity: 0.94;
}

.exam-card__head {
	display: flex;
	align-items: flex-start;
	justify-content: space-between;
}

.exam-card__title {
	flex: 1;
	margin-right: 16rpx;
	font-size: 32rpx;
	font-weight: 600;
	line-height: 1.45;
	color: #1c2331;
}

.exam-card__meta {
	display: block;
	margin-top: 18rpx;
	font-size: 24rpx;
	color: #748094;
}

.exam-card__deadline {
	display: block;
	margin-top: 8rpx;
	font-size: 24rpx;
	color: #748094;
}

.exam-card__foot {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-top: 26rpx;
	padding-top: 24rpx;
	border-top: 1rpx solid #f0f3f9;
}

.exam-card__category {
	font-size: 24rpx;
	color: #a8b2c4;
}

.exam-card__go {
	display: flex;
	align-items: center;
	color: #1d63ff;
}

.exam-card__go-text {
	font-size: 26rpx;
	font-weight: 600;
	color: #1d63ff;
}

.exam-card__go-text--scored {
	color: #00b578;
}

.exam-card__go-icon {
	width: 30rpx;
	height: 30rpx;
	margin-left: 4rpx;
}

.home__bottom-space {
	// 原生 tabBar 会占据底部空间，额外预留安全区
	height: calc(48rpx + constant(safe-area-inset-bottom));
	height: calc(48rpx + env(safe-area-inset-bottom));
}
</style>
