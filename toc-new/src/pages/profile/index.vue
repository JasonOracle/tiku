<template>
	<view class="profile">
		<!-- 极客蓝通顶名片：Header 透明融入渐变，名片信息紧随其下 -->
		<view class="profile__hero">
			<CustomHeader variant="transparent" title="个人中心" />

			<view class="profile__identity">
				<view class="profile__avatar">
					<text class="profile__avatar-text">{{ avatarText }}</text>
				</view>

				<view class="profile__info">
					<text class="profile__name">{{ displayName }}</text>
					<text class="profile__phone">{{ phoneText }}</text>
				</view>

				<view class="profile__role">
					<text class="profile__role-text">{{ roleText }}</text>
				</view>
			</view>
		</view>

		<view class="profile__body">
			<PageState
				v-if="statsStatus !== 'ready'"
				:status="statsStatus === 'error' ? 'error' : 'loading'"
				:skeleton-count="1"
				action-text="重新加载"
				@action="loadStats()"
			/>

			<view v-else class="stats-card">
				<view v-for="cell in statCells" :key="cell.label" class="stats-card__item">
					<text class="stats-card__value">{{ cell.value }}</text>
					<text class="stats-card__label">{{ cell.label }}</text>
				</view>
			</view>

			<view class="menu-card">
				<view class="menu-item" hover-class="menu-item--active" @click="handleFavorites">
					<text class="menu-item__label">我的收藏</text>
					<view class="menu-item__tail">
						<text class="menu-item__value">{{ favoriteText }}</text>
						<svg class="menu-item__arrow" viewBox="0 0 24 24" fill="none">
							<path d="m9.5 5 7 7-7 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
						</svg>
					</view>
				</view>

				<view class="menu-item menu-item--last" hover-class="menu-item--active" @click="handleAbout">
					<text class="menu-item__label">关于智题库</text>
					<view class="menu-item__tail">
						<svg class="menu-item__arrow" viewBox="0 0 24 24" fill="none">
							<path d="m9.5 5 7 7-7 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
						</svg>
					</view>
				</view>
			</view>

			<view class="profile__logout" hover-class="profile__logout--active" @click="handleLogout">
				<text class="profile__logout-text">退出登录</text>
			</view>

			<!-- 原生 tabBar 与底部安全区占位 -->
			<view class="profile__bottom-space" />
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchMyStats, type MyStatsResult } from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";
import { useUserStore } from "@/stores/user";
import { formatRole, maskPhone } from "@/utils/format";

type StatsStatus = "loading" | "error" | "ready";

const userStore = useUserStore();
const toast = useGlobalToast();

const statsStatus = ref<StatsStatus>("loading");
const stats = ref<MyStatsResult | null>(null);

const displayName = computed(() => userStore.userInfo?.display_name || "未设置昵称");
const phoneText = computed(() => maskPhone(userStore.userInfo?.phone));

/** 头像文字：优先取昵称首字，昵称为空时退化为手机号后两位 */
const avatarText = computed(() => {
	const name = userStore.userInfo?.display_name?.trim();
	if (name) return name.slice(0, 1);
	const phone = userStore.userInfo?.phone ?? "";
	return phone ? phone.slice(-2) : "学";
});

/** 角色取自当前生效租户的成员关系，渲染为中文，不暴露英文枚举 */
const roleText = computed(() => {
	const matched = userStore.joinedTenants.find((tenant) => tenant.tenant_id === userStore.tenantId);
	return formatRole(matched?.role);
});

const statCells = computed(() => [
	{ label: "参加场次", value: String(stats.value?.total_exams_taken ?? 0) },
	{ label: "通过场次", value: String(stats.value?.passed_count ?? 0) },
	{ label: "通过率", value: `${stats.value?.pass_rate ?? 0}%` },
	{ label: "收藏题目", value: String(stats.value?.favorite_count ?? 0) },
]);

const favoriteText = computed(() => (stats.value ? `${stats.value.favorite_count} 题` : ""));

async function loadStats(silent = false): Promise<void> {
	if (!silent) statsStatus.value = "loading";
	try {
		stats.value = await fetchMyStats();
		statsStatus.value = "ready";
	} catch {
		// 失败信息已由请求层统一轻提示，这里只负责切换到错误态
		statsStatus.value = "error";
	}
}

function handleFavorites(): void {
	toast.info("重点题目收藏将在后续阶段开放");
}

function handleAbout(): void {
	const systemInfo = uni.getSystemInfoSync();
	uni.showModal({
		title: "关于智题库",
		content: `企业测评与考试一体化平台\n运行环境：${systemInfo.platform || "未知"}`,
		showCancel: false,
		confirmColor: "#1D63FF",
	});
}

function handleLogout(): void {
	uni.showModal({
		title: "退出登录",
		content: "退出后需要重新输入账号密码，确定退出吗？",
		confirmColor: "#1D63FF",
		success: (res) => {
			if (!res.confirm) return;
			// 清空登录态会同步写回本地存储，随后回到登录页，避免残留凭证
			userStore.clearAuth();
			uni.reLaunch({ url: "/pages/login/index" });
		},
	});
}

onShow(() => {
	loadStats(statsStatus.value === "ready");
});
</script>

<style lang="scss" scoped>
.profile {
	min-height: 100vh;
	background-color: #f6f8fc;
}

.profile__hero {
	padding-bottom: 96rpx;
	background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
	border-bottom-left-radius: 40rpx;
	border-bottom-right-radius: 40rpx;
}

.profile__identity {
	display: flex;
	align-items: center;
	padding: 40rpx 32rpx 0;
}

.profile__avatar {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	background-color: rgba(255, 255, 255, 0.22);
	border: 2rpx solid rgba(255, 255, 255, 0.36);
}

.profile__avatar-text {
	font-size: 44rpx;
	font-weight: 600;
	color: #ffffff;
}

.profile__info {
	flex: 1;
	display: flex;
	flex-direction: column;
	margin-left: 28rpx;
	overflow: hidden;
}

.profile__name {
	font-size: 38rpx;
	font-weight: 600;
	color: #ffffff;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.profile__phone {
	margin-top: 10rpx;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.76);
}

.profile__role {
	padding: 8rpx 20rpx;
	border-radius: 999rpx;
	background-color: rgba(255, 255, 255, 0.2);
}

.profile__role-text {
	font-size: 22rpx;
	color: #ffffff;
}

.profile__body {
	position: relative;
	margin-top: -64rpx;
	padding: 0 32rpx;
}

.stats-card {
	display: flex;
	flex-wrap: wrap;
	padding: 12rpx 0;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
}

.stats-card__item {
	width: 50%;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 26rpx 0;
}

.stats-card__value {
	font-size: 40rpx;
	font-weight: 600;
	color: #1d63ff;
}

.stats-card__label {
	margin-top: 8rpx;
	font-size: 22rpx;
	color: #748094;
}

.menu-card {
	margin-top: 24rpx;
	padding: 0 28rpx;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
}

.menu-item {
	display: flex;
	align-items: center;
	justify-content: space-between;
	height: 108rpx;
	border-bottom: 1rpx solid #f0f3f9;
	transition: opacity 0.2s ease;
}

.menu-item--last {
	border-bottom: none;
}

.menu-item--active {
	opacity: 0.6;
}

.menu-item__label {
	font-size: 28rpx;
	color: #1c2331;
}

.menu-item__tail {
	display: flex;
	align-items: center;
	color: #a8b2c4;
}

.menu-item__value {
	margin-right: 8rpx;
	font-size: 24rpx;
	color: #748094;
}

.menu-item__arrow {
	width: 30rpx;
	height: 30rpx;
}

.profile__logout {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 96rpx;
	margin-top: 40rpx;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.profile__logout--active {
	transform: scale(0.98);
	opacity: 0.9;
}

.profile__logout-text {
	font-size: 30rpx;
	font-weight: 600;
	color: #fa4350;
}

.profile__bottom-space {
	height: calc(48rpx + constant(safe-area-inset-bottom));
	height: calc(48rpx + env(safe-area-inset-bottom));
}
</style>
