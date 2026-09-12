<template>
	<view class="home-apple">
		<!-- 漫反射暮光背景 -->
		<view class="hm-aurora">
			<view class="hm-aurora__blob hm-aurora__blob--1" />
			<view class="hm-aurora__blob hm-aurora__blob--2" />
		</view>

		<!-- 钛金通顶导航栏 -->
		<view class="hm-header">
			<view class="hm-header__info">
				<text class="hm-header__brand">智题库</text>
				<text class="hm-header__org">{{ institutionName }}</text>
			</view>
			<view class="hm-header__pill">
				<text class="hm-header__pill-text">{{ uncompletedCards.length }} 场待考</text>
			</view>
		</view>

		<view class="hm-body">
			<!-- Apple 风格圆角 Banner 轮播 -->
			<view class="hm-banner-wrap">
				<swiper
					v-if="bannerList.length > 0"
					class="hm-swiper"
					:indicator-dots="bannerList.length > 1"
					indicator-color="rgba(255, 255, 255, 0.45)"
					indicator-active-color="#FFFFFF"
					autoplay
					circular
					:interval="bannerInterval * 1000"
				>
					<swiper-item v-for="b in bannerList" :key="b.id" class="hm-swiper-item">
						<image :src="b.image_url" mode="aspectFill" class="hm-banner-img" />
						<view v-if="b.title" class="hm-banner-mask">
							<text class="hm-banner-title">{{ b.title }}</text>
						</view>
					</swiper-item>
				</swiper>

				<!-- 未配置自定义图时的 Apple 钛金微光兜底卡片 -->
				<view v-else class="hm-default-banner">
					<view class="hm-default-banner__content">
						<view class="hm-default-banner__badge">
							<text class="hm-default-banner__badge-text">OFFICIAL</text>
						</view>
						<text class="hm-default-banner__title">企业在线测评与能力认证</text>
						<text class="hm-default-banner__desc">沉浸式在线考核，专业能力体系校验</text>
					</view>
					<view class="hm-default-banner__glow" />
				</view>
			</view>

			<!-- 标题栏 -->
			<view class="hm-section-head">
				<view class="hm-section-title-wrap">
					<view class="hm-section-dot" />
					<text class="hm-section-title">待参加测评</text>
				</view>
				<text class="hm-section-tip">只展示未提交试卷</text>
			</view>

			<!-- 加载/空态/错误态 -->
			<PageState
				v-if="status !== 'ready'"
				:status="status"
				:variant="status === 'empty' ? 'celebrate' : 'default'"
				:title="status === 'empty' ? '待办任务已清空' : '数据加载失败'"
				:description="status === 'empty' ? '太棒了！当前没有待作答试卷，可前往「我的测试」复盘成绩' : '网络连接异常，请点击重新尝试'"
				:action-text="status === 'empty' ? '查看已测记录' : '重新加载'"
				:action-variant="status === 'empty' ? 'ghost' : 'primary'"
				@action="handleStateAction"
			/>

			<!-- 钛金试卷卡片流 -->
			<view v-else class="hm-list">
				<view
					v-for="item in uncompletedCards"
					:key="item.task_id"
					class="exam-card-apple"
					hover-class="exam-card-apple--pressed"
					@click="goExam(item)"
				>
					<view class="exam-card-apple__head">
						<text class="exam-card-apple__title">{{ item.title }}</text>
						<view class="exam-card-apple__tag">
							<text class="exam-card-apple__tag-text">{{ item.category_name || "综合" }}</text>
						</view>
					</view>

					<view class="exam-card-apple__meta">
						<text class="exam-card-apple__meta-item">总分 {{ item.total_score }}</text>
						<text class="exam-card-apple__meta-dot">·</text>
						<text class="exam-card-apple__meta-item">{{ item.question_count }} 题</text>
						<text class="exam-card-apple__meta-dot">·</text>
						<text class="exam-card-apple__meta-item">限时 {{ formatTimeLimit(item.time_limit) }}</text>
					</view>

					<view class="exam-card-apple__foot">
						<view class="exam-card-apple__deadline">
							<svg width="13" height="13" viewBox="0 0 24 24" fill="none">
								<circle cx="12" cy="12" r="10" stroke="#86868b" stroke-width="2"/>
								<polyline points="12 6 12 12 16 14" stroke="#86868b" stroke-width="2" stroke-linecap="round"/>
							</svg>
							<text class="exam-card-apple__deadline-text">截止 {{ formatDeadline(item.deadline) }}</text>
						</view>

						<view class="exam-card-apple__btn">
							<text class="exam-card-apple__btn-text">开始测试</text>
							<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
								<path d="M9 18l6-6-6-6" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
							</svg>
						</view>
					</view>
				</view>
			</view>

			<!-- 底部占位安全区 -->
			<view class="hm-bottom-space" />
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 全面升级首页为 Apple 钛金微光风，采用漫反射光晕与大圆角呼吸感排版; 2. 严格对接真实后端 GET /api/v1/member/banners 与 GET /api/v1/member/member-tasks; 3. 严格遵循 v1.4 规则过滤已作答试卷]
 */
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchMemberTasks, fetchMemberBanners, type MemberTaskItem, type BannerItem } from "@/api/exam";
import { useUserStore } from "@/stores/user";
import { formatDeadline, formatTimeLimit } from "@/utils/format";

type PageStatus = "loading" | "empty" | "error" | "ready";

const userStore = useUserStore();

const status = ref<PageStatus>("loading");
const allTasks = ref<MemberTaskItem[]>([]);
const bannerList = ref<BannerItem[]>([]);
const bannerInterval = ref(4);

/** 当前所属机构名称 */
const institutionName = computed(() => {
	const matched = userStore.joinedTenants.find((tenant) => tenant.tenant_id === userStore.tenantId);
	return matched?.tenant_name || "智题库认证空间";
});

/** 首页仅展示未提交/未作答试卷 */
const DONE_STATUSES = ["submitted", "verified", "pending_verification"];
const uncompletedCards = computed(() => {
	return allTasks.value.filter((item) => !DONE_STATUSES.includes(item.status));
});

async function loadData(silent = false): Promise<void> {
	if (!silent) status.value = "loading";
	try {
		const [bannerRes, taskRes] = await Promise.allSettled([
			fetchMemberBanners(),
			fetchMemberTasks()
		]);

		if (bannerRes.status === "fulfilled") {
			bannerList.value = bannerRes.value.items || [];
			bannerInterval.value = bannerRes.value.interval_seconds || 4;
		}

		if (taskRes.status === "fulfilled") {
			allTasks.value = taskRes.value.items || [];
			status.value = uncompletedCards.value.length ? "ready" : "empty";
		} else {
			status.value = "error";
		}
	} catch {
		status.value = "error";
	}
}

function handleStateAction() {
	if (status.value === "empty") {
		uni.switchTab({ url: "/pages/records/index" });
	} else {
		loadData();
	}
}

function goExam(item: MemberTaskItem) {
	uni.navigateTo({
		url: `/pages/exam/index?task_id=${item.task_id}&title=${encodeURIComponent(item.title)}`
	});
}

onShow(() => {
	if (!userStore.token) {
		uni.reLaunch({ url: "/pages/login/index" });
		return;
	}
	loadData(true);
});
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.home-apple {
	position: relative;
	min-height: 100vh;
	background: $bg;
	overflow: hidden;
}

/* 漫反射微光晕 */
.hm-aurora {
	position: absolute;
	inset: 0;
	pointer-events: none;
	overflow: hidden;

	&__blob {
		position: absolute;
		border-radius: 50%;
		filter: blur(80px);
		opacity: 0.45;

		&--1 {
			width: 520rpx;
			height: 520rpx;
			top: -160rpx;
			left: -120rpx;
			background: radial-gradient(circle, rgba(24, 82, 224, 0.4), rgba(24, 82, 224, 0));
		}

		&--2 {
			width: 480rpx;
			height: 480rpx;
			top: 300rpx;
			right: -140rpx;
			background: radial-gradient(circle, rgba(124, 92, 255, 0.3), rgba(124, 92, 255, 0));
		}
	}
}

/* 通顶导航条 */
.hm-header {
	position: relative;
	z-index: 2;
	padding: 44rpx 36rpx 20rpx;
	display: flex;
	align-items: center;
	justify-content: space-between;

	&__brand {
		font-size: 38rpx;
		font-weight: 800;
		color: $ink;
		letter-spacing: -0.3px;
	}

	&__org {
		display: block;
		font-size: 22rpx;
		color: $muted;
		margin-top: 4rpx;
	}

	&__pill {
		background: rgba(255, 255, 255, 0.85);
		border: 1px solid $glass-border;
		backdrop-filter: $glass-blur;
		padding: 8rpx 20rpx;
		border-radius: $radius-pill;
		box-shadow: $shadow-card;
	}

	&__pill-text {
		font-size: 22rpx;
		font-weight: 600;
		color: $accent;
	}
}

.hm-body {
	position: relative;
	z-index: 2;
	padding: 10rpx 32rpx 40rpx;
}

/* Banner 轮播区 */
.hm-banner-wrap {
	margin-bottom: 24rpx;
}

.hm-swiper {
	height: 280rpx;
	border-radius: $radius-card;
	overflow: hidden;
	box-shadow: $shadow-card;
}

.hm-swiper-item {
	position: relative;
	width: 100%;
	height: 100%;
}

.hm-banner-img {
	width: 100%;
	height: 100%;
	display: block;
}

.hm-banner-mask {
	position: absolute;
	left: 0;
	right: 0;
	bottom: 0;
	padding: 24rpx 28rpx 18rpx;
	background: linear-gradient(180deg, transparent, rgba(0, 0, 0, 0.65));
}

.hm-banner-title {
	font-size: 28rpx;
	font-weight: 700;
	color: #ffffff;
}

/* 默认 Banner */
.hm-default-banner {
	height: 260rpx;
	background: $gradient;
	border-radius: $radius-card;
	padding: 36rpx;
	box-sizing: border-box;
	display: flex;
	align-items: center;
	position: relative;
	overflow: hidden;
	box-shadow: 0 12rpx 36rpx rgba(24, 82, 224, 0.28);

	&__content {
		position: relative;
		z-index: 2;
		display: flex;
		flex-direction: column;
		gap: 10rpx;
	}

	&__badge {
		align-self: flex-start;
		background: rgba(255, 255, 255, 0.22);
		border-radius: 6rpx;
		padding: 4rpx 10rpx;
	}

	&__badge-text {
		font-size: 18rpx;
		font-weight: 800;
		color: #ffffff;
		letter-spacing: 0.5px;
	}

	&__title {
		font-size: 34rpx;
		font-weight: 800;
		color: #ffffff;
	}

	&__desc {
		font-size: 22rpx;
		color: rgba(255, 255, 255, 0.85);
	}

	&__glow {
		position: absolute;
		right: -40rpx;
		bottom: -40rpx;
		width: 200rpx;
		height: 200rpx;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.15);
	}
}

/* 栏目标题区 */
.hm-section-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin: 28rpx 8rpx 18rpx;
}

.hm-section-title-wrap {
	display: flex;
	align-items: center;
	gap: 12rpx;
}

.hm-section-dot {
	width: 8rpx;
	height: 26rpx;
	border-radius: 4rpx;
	background: $gradient;
}

.hm-section-title {
	font-size: 32rpx;
	font-weight: 800;
	color: $ink;
}

.hm-section-tip {
	font-size: 22rpx;
	color: $muted;
}

.hm-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

/* 试卷大卡片 */
.exam-card-apple {
	background: rgba(255, 255, 255, 0.92);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: $radius-card;
	padding: 32rpx 36rpx;
	box-shadow: $shadow-card;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
	transition: all 0.2s ease;

	&--pressed {
		transform: scale(0.985);
		background: #ffffff;
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
		line-height: 1.4;
		flex: 1;
	}

	&__tag {
		background: $accent-soft;
		border-radius: 10rpx;
		padding: 4rpx 14rpx;
		flex-shrink: 0;
	}

	&__tag-text {
		font-size: 20rpx;
		font-weight: 600;
		color: $accent;
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

	&__deadline {
		display: flex;
		align-items: center;
		gap: 8rpx;
	}

	&__deadline-text {
		font-size: 22rpx;
		color: $muted;
	}

	&__btn {
		background: $gradient;
		border-radius: $radius-pill;
		padding: 10rpx 24rpx;
		display: flex;
		align-items: center;
		gap: 6rpx;
		box-shadow: 0 6rpx 16rpx rgba(24, 82, 224, 0.25);
	}

	&__btn-text {
		font-size: 22rpx;
		font-weight: 600;
		color: #ffffff;
	}
}

.hm-bottom-space {
	height: calc(100rpx + env(safe-area-inset-bottom));
}
</style>
