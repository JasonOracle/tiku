<template>
	<view class="home-apple">
		<!-- 通顶 Header：左侧问候语与机构名，右侧微光头像与待考胶囊 -->
		<view class="hm-header">
			<view class="hm-header__inner">
				<view class="hm-header__info">
					<view class="hm-header__hello">{{ greetingText }}</view>
					<view class="hm-header__org">{{ institutionName }}</view>
				</view>
				<view class="hm-header__right">
					<view class="hm-avatar">{{ avatarLetter }}</view>
				</view>
			</view>
		</view>

		<!-- Apple 风格圆角 Banner 轮播（微微漫反射阴影 + 钛金遮罩） -->
		<view class="hm-banner-wrap">
			<swiper
				v-if="bannerList.length > 0"
				class="hm-banner"
				circular
				autoplay
				:interval="bannerInterval * 1000"
				:duration="560"
				@change="onSwiperChange"
			>
				<swiper-item v-for="b in bannerList" :key="b.id">
					<view class="hm-banner__item">
						<image class="hm-banner__img" :src="b.image_url" mode="aspectFill" />
						<view class="hm-banner__mask" />
						<view class="hm-banner__text">
							<view class="hm-banner__tag">能力认证</view>
							<view class="hm-banner__title">{{ b.title }}</view>
							<view class="hm-banner__sub">专业能力校验 · 在线实时测评</view>
						</view>
					</view>
				</swiper-item>
			</swiper>

			<swiper
				v-else
				class="hm-banner"
				circular
				autoplay
				:interval="4200"
				:duration="560"
				@change="onSwiperChange"
			>
				<swiper-item v-for="b in defaultBanners" :key="b.id">
					<view class="hm-banner__item">
						<image class="hm-banner__img" :src="b.image" mode="aspectFill" />
						<view class="hm-banner__mask" />
						<view class="hm-banner__text">
							<view class="hm-banner__tag">{{ b.tag }}</view>
							<view class="hm-banner__title">{{ b.title }}</view>
							<view class="hm-banner__sub">{{ b.sub }}</view>
						</view>
					</view>
				</swiper-item>
			</swiper>

			<!-- 钛金动效轮播指示条（长短胶囊动画） -->
			<view class="hm-dots">
				<view
					v-for="i in (bannerList.length || defaultBanners.length)"
					:key="i"
					class="hm-dot"
					:class="{ 'hm-dot--on': i - 1 === bannerIndex }"
				/>
			</view>
		</view>

		<!-- 区块标题：为你推荐 / 待参加测评 -->
		<view class="hm-section">
			<view class="hm-section__title">为你推荐</view>
			<view class="hm-section__count">{{ uncompletedCards.length }} 项进行中</view>
		</view>

		<!-- 骨架屏态 -->
		<view v-if="status === 'loading'">
			<view v-for="n in 3" :key="n" class="hm-skel">
				<view class="hm-skel__bar hm-skel__bar--wide" />
				<view class="hm-skel__bar" />
				<view class="hm-skel__row">
					<view class="hm-skel__chip" />
					<view class="hm-skel__chip" />
					<view class="hm-skel__btn" />
				</view>
			</view>
		</view>

		<!-- 清空成就态：Apple 琉璃勋章插画 -->
		<view v-else-if="status === 'empty'" class="hm-empty">
			<view class="hm-medal">
				<view class="hm-medal__halo" />
				<view class="hm-medal__ribbon" />
				<view class="hm-medal__disc">
					<view class="hm-medal__star" />
				</view>
			</view>
			<view class="hm-empty__title">当前待办测评已全部完成</view>
			<view class="hm-empty__sub">太棒了！你已顺利交卷，前往「我的测试」可复盘已测成绩</view>
			<view class="hm-empty__btn-wrap">
				<view class="hm-empty__btn" @click="goRecords">查看已测记录</view>
			</view>
		</view>

		<!-- 错误异常态 -->
		<view v-else-if="status === 'error'" class="hm-error-wrap">
			<PageState
				status="error"
				title="数据加载失败"
				description="网络连接异常，请点击重新尝试"
				action-text="重新加载"
				@action="loadData"
			/>
		</view>

		<!-- 100% 还原 Apple 钛金微光风卡片列表流 -->
		<view v-else class="hm-cards">
			<view
				v-for="(c, idx) in uncompletedCards"
				:key="c.task_id"
				class="hm-card"
				:class="{ 'hm-card--urgent': isUrgent(c) }"
				@click="goExam(c)"
			>
				<!-- 右上角漫反射微光（红 / 蓝 / 橙交替多姿态） -->
				<view class="hm-card__glow" :class="'hm-card__glow--' + resolveKindKey(c, idx)" />

				<view class="hm-card__top">
					<view class="hm-card__kind" :class="'hm-card__kind--' + resolveKindKey(c, idx)">
						{{ c.category_name || resolveCategoryFallback(idx) }}
					</view>
					<view v-if="isUrgent(c)" class="hm-card__alert">
						<view class="hm-card__pulse" />
						<text>{{ deadlineAlertText(c) }}</text>
					</view>
				</view>

				<view class="hm-card__title">{{ c.title }}</view>

				<!-- 三联指标栏：题量、限时、总分 -->
				<view class="hm-card__meta">
					<view class="hm-meta">
						<text class="hm-meta__num">{{ c.question_count }}</text>
						<text class="hm-meta__label">题量</text>
					</view>
					<view class="hm-meta">
						<text class="hm-meta__num">{{ formatTimeLimit(c.time_limit) }}</text>
						<text class="hm-meta__label">限时</text>
					</view>
					<view class="hm-meta">
						<text class="hm-meta__num">{{ c.total_score }}</text>
						<text class="hm-meta__label">总分</text>
					</view>
				</view>

				<!-- 卡片底栏：截止时间 + Apple 钛金按钮 -->
				<view class="hm-card__foot">
					<view class="hm-deadline" :class="{ 'hm-deadline--hot': isUrgent(c) }">
						截止 {{ formatDeadline(c.deadline) }}
					</view>
					<view class="hm-card__btn">
						{{ isUrgent(c) ? "立即开考" : "去参加" }}
					</view>
				</view>
			</view>
		</view>

		<view class="hm-bottom-space" />
		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 100% 像素级对齐 preview-apple/index/index.vue：深空漫反射暮光问候顶栏 hm-header、首字母头像 hm-avatar、指示条动画 hm-dots、Apple 钛金试卷卡片 hm-card、三联指标栏 hm-meta 及清空态琉璃勋章插画 hm-medal; 2. 严密绑定后端 GET /api/v1/member/banners 与 GET /api/v1/member/member-tasks 真实数据并保持已提交试卷精准过滤]
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
const bannerList = ref<BannerItem[]>([]);
const bannerInterval = ref(4);
const allTasks = ref<MemberTaskItem[]>([]);
const bannerIndex = ref(0);

function onSwiperChange(e: { detail: { current: number } }): void {
	bannerIndex.value = e.detail.current;
}

const defaultBanners = [
	{ id: 1, image: "/static/preview/banner-apple.png", tag: "季度合规", title: "2026 企业安全与能力认证", sub: "专业能力校验 · 在线实时测评" },
	{ id: 2, image: "/static/preview/banner-apple.png", tag: "能力认证", title: "教学质量标准化认证测试", sub: "100 题综合金标测评体系" },
	{ id: 3, image: "/static/preview/banner-apple.png", tag: "AI 实操", title: "大模型应用实操能力评估", sub: "前沿大模型考核 · 专项技能达标" },
];

/** 动态问候语 */
const greetingText = computed(() => {
	const hour = new Date().getHours();
	if (hour < 6) return "凌晨好";
	if (hour < 12) return "上午好";
	if (hour < 14) return "中午好";
	if (hour < 18) return "下午好";
	return "晚上好";
});

/** 当前所属机构名称 */
const institutionName = computed(() => {
	const matched = userStore.joinedTenants.find((tenant) => tenant.tenant_id === userStore.tenantId);
	return matched?.tenant_name || "星雅教育 · 教务中心";
});

/** 首字母头像 */
const avatarLetter = computed(() => {
	const name = userStore.userInfo?.display_name || userStore.userInfo?.phone || "学";
	return name.slice(0, 1);
});

/** 首页仅展示未提交/未作答试卷 */
const DONE_STATUSES = ["submitted", "verified", "pending_verification"];
const uncompletedCards = computed(() => {
	return allTasks.value.filter((item) => !DONE_STATUSES.includes(item.status));
});

function resolveKindKey(item: MemberTaskItem, index: number): "timed" | "mixed" | "special" {
	// 如果分类名包含明确倾向，优先匹配
	const cat = (item.category_name || "").toLowerCase();
	if (cat.includes("模拟") || cat.includes("限时") || cat.includes("安全")) return "timed";
	if (cat.includes("综合") || cat.includes("质量") || cat.includes("认证")) return "mixed";
	if (cat.includes("专项") || cat.includes("技能") || cat.includes("趣味") || cat.includes("调查")) return "special";

	// 否则根据卡片自然序号轮换调色盘（红、蓝、橙交替，与 preview-apple 完全一致）
	const palette: ("timed" | "mixed" | "special")[] = ["timed", "mixed", "special"];
	return palette[index % palette.length];
}

function resolveCategoryFallback(index: number): string {
	const labels = ["严苛限时", "综合测评", "专项技能"];
	return labels[index % labels.length];
}

function isUrgent(item: MemberTaskItem): boolean {
	if (!item.deadline) return false;
	const deadlineMs = new Date(item.deadline).getTime();
	const nowMs = Date.now();
	const diffHours = (deadlineMs - nowMs) / (1000 * 60 * 60);
	return diffHours > 0 && diffHours <= 24;
}

function deadlineAlertText(item: MemberTaskItem): string {
	if (!item.deadline) return "即将截止";
	const deadlineMs = new Date(item.deadline).getTime();
	const nowMs = Date.now();
	const diffHours = Math.max(1, Math.round((deadlineMs - nowMs) / (1000 * 60 * 60)));
	if (diffHours <= 24) {
		return `剩余 ${diffHours} 小时截止`;
	}
	return "即将截止";
}

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

function goExam(item: MemberTaskItem) {
	uni.navigateTo({
		url: `/pages/exam/index?task_id=${item.task_id}&title=${encodeURIComponent(item.title)}`
	});
}

function goRecords() {
	uni.switchTab({ url: "/pages/records/index" });
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
	min-height: 100vh;
	background: $bg;
	padding-bottom: 80rpx;
	box-sizing: border-box;
}

/* 顶部通顶问候栏 */
.hm-header {
	background: linear-gradient(180deg, rgba(24, 82, 224, 0.08), transparent);
}

.hm-header__inner {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 44rpx 44rpx 24rpx;
}

.hm-header__hello {
	font-size: 23rpx;
	color: $muted;
}

.hm-header__org {
	margin-top: 10rpx;
	font-size: 38rpx;
	font-weight: 800;
	color: $ink;
}

.hm-avatar {
	width: 84rpx;
	height: 84rpx;
	border-radius: 30rpx;
	background: $gradient;
	color: #ffffff;
	font-size: 32rpx;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 12rpx 32rpx rgba(10, 50, 153, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

/* Banner 轮播区 */
.hm-banner-wrap {
	position: relative;
}

.hm-banner {
	height: 300rpx;
	margin: 16rpx 44rpx 0;
	border-radius: 32rpx;
	overflow: hidden;
	box-shadow: $shadow-float;
}

.hm-banner__item {
	position: relative;
	height: 100%;
	border-radius: 32rpx;
	overflow: hidden;
}

.hm-banner__img {
	width: 100%;
	height: 100%;
}

.hm-banner__mask {
	position: absolute;
	inset: 0;
	background: linear-gradient(115deg, rgba(10, 50, 153, 0.75) 0%, rgba(24, 82, 224, 0.25) 55%, rgba(255, 255, 255, 0) 100%);
}

.hm-banner__text {
	position: absolute;
	left: 40rpx;
	bottom: 36rpx;
	right: 40rpx;
	color: #ffffff;
}

.hm-banner__tag {
	display: inline-block;
	font-size: 20rpx;
	color: rgba(255, 255, 255, 0.92);
	background: rgba(255, 255, 255, 0.18);
	backdrop-filter: blur(8px);
	border: 1px solid rgba(255, 255, 255, 0.3);
	border-radius: $radius-pill;
	padding: 6rpx 20rpx;
	margin-bottom: 14rpx;
}

.hm-banner__title {
	font-size: 36rpx;
	font-weight: 800;
}

.hm-banner__sub {
	margin-top: 10rpx;
	font-size: 23rpx;
	opacity: 0.85;
}

/* 轮播动效指示胶囊 */
.hm-dots {
	display: flex;
	justify-content: center;
	gap: 12rpx;
	margin-top: 20rpx;
}

.hm-dot {
	width: 12rpx;
	height: 12rpx;
	border-radius: 50%;
	background: rgba(20, 30, 60, 0.14);
	transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.hm-dot--on {
	width: 36rpx;
	border-radius: 6rpx;
	background: $accent;
}

/* 区块标题 */
.hm-section {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 52rpx 44rpx 24rpx;
}

.hm-section__title {
	font-size: 34rpx;
	font-weight: 800;
	color: $ink;
}

.hm-section__count {
	font-size: 22rpx;
	color: $muted;
}

/* 试卷卡片流（100% 还原 Apple 风格） */
.hm-cards {
	padding: 0 44rpx;
	display: flex;
	flex-direction: column;
	gap: 32rpx;
}

.hm-card {
	position: relative;
	background: $surface;
	border-radius: $radius-card;
	padding: 40rpx 36rpx 36rpx;
	box-shadow: $shadow-card;
	overflow: hidden;
	transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.hm-card:active {
	transform: scale(0.98);
}

.hm-card__glow {
	position: absolute;
	top: -80rpx;
	right: -60rpx;
	width: 280rpx;
	height: 280rpx;
	border-radius: 50%;
	filter: blur(60rpx);
	opacity: 0.35;
	pointer-events: none;
}

.hm-card__glow--timed {
	background: #ff3b30;
}

.hm-card__glow--mixed {
	background: #1852e0;
}

.hm-card__glow--special {
	background: #f5a623;
}

.hm-card--urgent {
	box-shadow: 0 1px 2px rgba(20, 30, 60, 0.05), 0 12px 36px rgba(255, 59, 48, 0.16);
}

.hm-card__top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 22rpx;
	position: relative;
}

.hm-card__kind {
	font-size: 21rpx;
	font-weight: 600;
	padding: 10rpx 22rpx;
	border-radius: $radius-pill;
}

.hm-card__kind--timed {
	color: #c62b22;
	background: $danger-soft;
}

.hm-card__kind--mixed {
	color: $accent;
	background: $accent-soft;
}

.hm-card__kind--special {
	color: #b26a00;
	background: $warn-soft;
}

.hm-card__alert {
	display: flex;
	align-items: center;
	gap: 10rpx;
	font-size: 21rpx;
	color: #c62b22;
	font-weight: 600;
}

.hm-card__pulse {
	width: 14rpx;
	height: 14rpx;
	border-radius: 50%;
	background: #ff3b30;
	animation: card-pulse 1.2s ease-in-out infinite;
}

@keyframes card-pulse {
	0%,
	100% {
		box-shadow: 0 0 0 0 rgba(255, 59, 48, 0.4);
	}
	50% {
		box-shadow: 0 0 0 12rpx rgba(255, 59, 48, 0);
	}
}

.hm-card__title {
	position: relative;
	font-size: 32rpx;
	font-weight: 700;
	color: $ink;
	line-height: 1.5;
}

.hm-card__meta {
	position: relative;
	display: flex;
	gap: 56rpx;
	margin-top: 30rpx;
	padding: 24rpx 0;
	border-top: 1px solid $line;
	border-bottom: 1px solid $line;
}

.hm-meta__num {
	font-size: 32rpx;
	font-weight: 800;
	color: $ink;
}

.hm-meta__label {
	margin-left: 10rpx;
	font-size: 20rpx;
	color: $muted;
}

.hm-card__foot {
	position: relative;
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: 28rpx;
}

.hm-deadline {
	font-size: 23rpx;
	color: $muted;
}

.hm-deadline--hot {
	color: #c62b22;
	font-weight: 600;
}

.hm-card__btn {
	font-size: 25rpx;
	font-weight: 700;
	color: #ffffff;
	background: $gradient;
	border-radius: $radius-pill;
	padding: 18rpx 44rpx;
	box-shadow: 0 10rpx 28rpx rgba(24, 82, 224, 0.32), inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

/* 骨架屏态 */
.hm-skel {
	background: $surface;
	border-radius: $radius-card;
	padding: 40rpx 36rpx;
	margin: 0 44rpx 32rpx;
	box-shadow: $shadow-card;
}

.hm-skel__bar {
	height: 26rpx;
	border-radius: 13rpx;
	background: linear-gradient(90deg, #f0f0f4 25%, #f9f9fc 50%, #f0f0f4 75%);
	background-size: 400% 100%;
	animation: skel-shimmer 1.5s ease infinite;
	margin-bottom: 20rpx;
	width: 62%;
}

.hm-skel__bar--wide {
	width: 92%;
	height: 34rpx;
}

.hm-skel__row {
	display: flex;
	gap: 16rpx;
	margin-top: 26rpx;
}

.hm-skel__chip {
	width: 130rpx;
	height: 44rpx;
	border-radius: 22rpx;
	background: #f0f0f4;
}

.hm-skel__btn {
	margin-left: auto;
	width: 170rpx;
	height: 56rpx;
	border-radius: 28rpx;
	background: linear-gradient(90deg, #f0f0f4 25%, #f9f9fc 50%, #f0f0f4 75%);
	background-size: 400% 100%;
}

@keyframes skel-shimmer {
	0% {
		background-position: 100% 0;
	}
	100% {
		background-position: -100% 0;
	}
}

/* 清空成就态：琉璃勋章 */
.hm-empty {
	padding: 88rpx 60rpx 40rpx;
	text-align: center;
}

.hm-medal {
	position: relative;
	width: 200rpx;
	height: 240rpx;
	margin: 0 auto 44rpx;
}

.hm-medal__halo {
	position: absolute;
	left: 50%;
	top: 60rpx;
	transform: translateX(-50%);
	width: 200rpx;
	height: 200rpx;
	border-radius: 50%;
	background: radial-gradient(circle, rgba(24, 82, 224, 0.25), transparent 70%);
	animation: halo-breathe 3.2s ease-in-out infinite;
}

@keyframes halo-breathe {
	0%,
	100% {
		transform: translateX(-50%) scale(1);
		opacity: 0.7;
	}
	50% {
		transform: translateX(-50%) scale(1.18);
		opacity: 1;
	}
}

.hm-medal__ribbon {
	position: absolute;
	left: 50%;
	top: 0;
	transform: translateX(-50%);
	width: 60rpx;
	height: 100rpx;
	background: linear-gradient(180deg, #1852e0 50%, #0a3299 50%);
	clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 78%, 0 100%);
}

.hm-medal__disc {
	position: absolute;
	left: 50%;
	top: 78rpx;
	transform: translateX(-50%);
	width: 132rpx;
	height: 132rpx;
	border-radius: 50%;
	background: $gradient;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 20rpx 48rpx rgba(10, 50, 153, 0.4), inset 0 2rpx 6rpx rgba(255, 255, 255, 0.45);
}

.hm-medal__star {
	width: 56rpx;
	height: 56rpx;
	background: #ffd76a;
	clip-path: polygon(50% 0%, 63% 35%, 98% 35%, 70% 57%, 79% 91%, 50% 70%, 21% 91%, 30% 57%, 2% 35%, 37% 35%);
}

.hm-empty__title {
	font-size: 34rpx;
	font-weight: 800;
	color: $ink;
}

.hm-empty__sub {
	margin: 16rpx auto 0;
	font-size: 24rpx;
	color: $muted;
	max-width: 480rpx;
	line-height: 1.7;
}

.hm-empty__btn-wrap {
	margin-top: 40rpx;
}

.hm-empty__btn {
	display: inline-block;
	padding: 18rpx 44rpx;
	border-radius: $radius-pill;
	background: $surface;
	border: 1px solid $line;
	font-size: 26rpx;
	font-weight: 600;
	color: $accent;
	box-shadow: $shadow-card;
}

.hm-bottom-space {
	height: calc(40rpx + env(safe-area-inset-bottom));
}
</style>
