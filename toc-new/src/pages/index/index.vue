<template>
	<view class="home">
		<!-- 通顶 Header：展示当前机构名称 -->
		<CustomHeader variant="solid" :title="institutionName">
			<template #right>
				<view class="home__header-badge">
					<text class="home__header-badge-text">{{ uncompletedCards.length }} 场可考</text>
				</view>
			</template>
		</CustomHeader>

		<view class="home__body">
			<!-- 滚动 Banner 轮播区 -->
			<view class="banner-section">
				<swiper
					v-if="bannerList.length > 0"
					class="banner-swiper"
					:indicator-dots="bannerList.length > 1"
					indicator-color="rgba(255, 255, 255, 0.4)"
					indicator-active-color="#1D63FF"
					autoplay
					circular
					:interval="bannerInterval * 1000"
				>
					<swiper-item v-for="b in bannerList" :key="b.id" class="banner-item">
						<image :src="b.image_url" mode="aspectFill" class="banner-img" />
						<view v-if="b.title" class="banner-title-mask">
							<text class="banner-title">{{ b.title }}</text>
						</view>
					</swiper-item>
				</swiper>

				<!-- 默认极客蓝特色 Banner（未配置自定义轮播图时展示） -->
				<view v-else class="default-banner">
					<view class="default-banner__content">
						<view class="default-banner__tag">
							<text class="default-banner__tag-text">OFFICIAL</text>
						</view>
						<text class="default-banner__title">企业在线测评与能力认证</text>
						<text class="default-banner__desc">聚焦专业知识体系，沉浸式在线考核</text>
					</view>
					<view class="default-banner__deco">
						<svg width="72" height="72" viewBox="0 0 24 24" fill="none" opacity="0.15">
							<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</view>
				</view>
			</view>

			<!-- 标题栏 -->
			<view class="home__section-head">
				<view class="home__section-title-wrap">
					<view class="home__section-bar" />
					<text class="home__section-title">待参加测评</text>
				</view>
				<text class="home__section-tip">只展示未作答试卷</text>
			</view>

			<!-- 加载/空态/错误态 -->
			<PageState
				v-if="status !== 'ready'"
				:status="status"
				empty-text="太棒了！当前没有待作答的测评试卷"
				action-text="重新加载"
				@action="loadData()"
			/>

			<!-- 待答试卷卡片列表 -->
			<view v-else class="home__list">
				<view
					v-for="item in uncompletedCards"
					:key="item.task_id"
					class="exam-card"
					hover-class="exam-card--active"
					@click="goExam(item)"
				>
					<view class="exam-card__head">
						<text class="exam-card__title">{{ item.title }}</text>
						<view class="exam-card__tag">
							<text class="exam-card__tag-text">{{ item.category_name || "综合" }}</text>
						</view>
					</view>

					<view class="exam-card__meta">
						<text class="exam-card__meta-item">总分 {{ item.total_score }}</text>
						<text class="exam-card__meta-dot">·</text>
						<text class="exam-card__meta-item">{{ item.question_count }} 题</text>
						<text class="exam-card__meta-dot">·</text>
						<text class="exam-card__meta-item">限时 {{ formatTimeLimit(item.time_limit) }}</text>
					</view>

					<view class="exam-card__foot">
						<view class="exam-card__deadline">
							<svg width="13" height="13" viewBox="0 0 24 24" fill="none" class="exam-card__clock-icon">
								<circle cx="12" cy="12" r="10" stroke="#94A3B8" stroke-width="2"/>
								<polyline points="12 6 12 12 16 14" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/>
							</svg>
							<text class="exam-card__deadline-text">截止 {{ formatDeadline(item.deadline) }}</text>
						</view>

						<view class="exam-card__btn">
							<text class="exam-card__btn-text">开始测试</text>
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none">
								<path d="M9 18l6-6-6-6" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
							</svg>
						</view>
					</view>
				</view>
			</view>

			<!-- 底部占位 -->
			<view class="home__bottom-space" />
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 彻底移除假大空的「晚上好/统计大色块」，恢复滚动 Banner 轮播卡片; 2. 严格按 v1.4 规则过滤首页试卷列表，仅保留未提交/待作答试卷，已交卷试卷一律隐去（去我的测试查看）]
 */
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
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

/** 所属机构名称 */
const institutionName = computed(() => {
	const matched = userStore.joinedTenants.find((tenant) => tenant.tenant_id === userStore.tenantId);
	return matched?.tenant_name || "智题库企业空间";
});

/**
 * 核心过滤规则（严格遵循 v1.4）：
 * 首页只呈现「未作答」的测评试卷。
 * 已交卷 (submitted)、审核中 (pending_verification)、已核验 (verified) 统一从首页隐藏，前往「我的测试」查看成绩。
 */
const DONE_STATUSES = ["submitted", "verified", "pending_verification"];
const uncompletedCards = computed(() => {
	return allTasks.value.filter((item) => !DONE_STATUSES.includes(item.status));
});

async function loadData(silent = false): Promise<void> {
	if (!silent) status.value = "loading";
	try {
		// 并发拉取 Banner 与 试卷列表
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
			// 基于过滤后的有效可考列表判定空态
			status.value = uncompletedCards.value.length ? "ready" : "empty";
		} else {
			status.value = "error";
		}
	} catch {
		status.value = "error";
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
.home {
	min-height: 100vh;
	background-color: #F8FAFC;

	&__header-badge {
		background: rgba(29, 99, 255, 0.08);
		border: 1px solid rgba(29, 99, 255, 0.2);
		padding: 4px 10px;
		border-radius: 999px;
	}

	&__header-badge-text {
		font-size: 12px;
		font-weight: 600;
		color: #1D63FF;
	}

	&__body {
		padding: 14px 16px;
	}

	&__section-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin: 20px 0 12px;
	}

	&__section-title-wrap {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	&__section-bar {
		width: 4px;
		height: 16px;
		background: #1D63FF;
		border-radius: 2px;
	}

	&__section-title {
		font-size: 17px;
		font-weight: 700;
		color: #0F172A;
	}

	&__section-tip {
		font-size: 12px;
		color: #94A3B8;
	}

	&__list {
		display: flex;
		flex-direction: column;
		gap: 14px;
	}

	&__bottom-space {
		height: 32px;
	}
}

/* 轮播 Banner 模块 */
.banner-section {
	margin-bottom: 8px;
}

.banner-swiper {
	height: 146px;
	border-radius: 16px;
	overflow: hidden;
	box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
}

.banner-item {
	position: relative;
	width: 100%;
	height: 100%;
}

.banner-img {
	width: 100%;
	height: 100%;
}

.banner-title-mask {
	position: absolute;
	left: 0;
	right: 0;
	bottom: 0;
	padding: 8px 14px;
	background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.65) 100%);
}

.banner-title {
	font-size: 13px;
	font-weight: 600;
	color: #FFFFFF;
}

/* 默认极客蓝特色 Banner */
.default-banner {
	height: 136px;
	background: linear-gradient(135deg, #1D63FF 0%, #0045D8 100%);
	border-radius: 16px;
	padding: 20px;
	box-sizing: border-box;
	display: flex;
	justify-content: space-between;
	align-items: center;
	position: relative;
	overflow: hidden;
	box-shadow: 0 8px 24px rgba(29, 99, 255, 0.28);

	&__content {
		position: relative;
		z-index: 2;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	&__tag {
		align-self: flex-start;
		background: rgba(255, 255, 255, 0.22);
		border-radius: 4px;
		padding: 2px 6px;
	}

	&__tag-text {
		font-size: 10px;
		font-weight: 800;
		color: #FFFFFF;
		letter-spacing: 0.5px;
	}

	&__title {
		font-size: 18px;
		font-weight: 800;
		color: #FFFFFF;
		letter-spacing: 0.3px;
	}

	&__desc {
		font-size: 12px;
		color: rgba(255, 255, 255, 0.85);
	}

	&__deco {
		position: absolute;
		right: 12px;
		bottom: 8px;
		z-index: 1;
	}
}

/* 试卷大卡片 */
.exam-card {
	background: #FFFFFF;
	border-radius: 16px;
	padding: 16px 18px;
	border: 1px solid rgba(226, 232, 240, 0.8);
	box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
	display: flex;
	flex-direction: column;
	gap: 10px;
	transition: transform 0.15s ease;

	&--active {
		transform: scale(0.985);
		background-color: #F8FAFC;
	}

	&__head {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 12px;
	}

	&__title {
		font-size: 16px;
		font-weight: 700;
		color: #0F172A;
		line-height: 1.4;
		flex: 1;
	}

	&__tag {
		background: #EFF6FF;
		border-radius: 6px;
		padding: 3px 8px;
		flex-shrink: 0;
	}

	&__tag-text {
		font-size: 11px;
		font-weight: 600;
		color: #1D63FF;
	}

	&__meta {
		display: flex;
		align-items: center;
		gap: 6px;
		font-size: 13px;
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

	&__deadline {
		display: flex;
		align-items: center;
		gap: 5px;
	}

	&__deadline-text {
		font-size: 12px;
		color: #94A3B8;
	}

	&__btn {
		background: #1D63FF;
		border-radius: 999px;
		padding: 6px 14px;
		display: flex;
		align-items: center;
		gap: 4px;
		box-shadow: 0 3px 8px rgba(29, 99, 255, 0.25);
	}

	&__btn-text {
		font-size: 12px;
		font-weight: 600;
		color: #FFFFFF;
	}
}
</style>
