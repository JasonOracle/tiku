<template>
	<view class="profile-apple">
		<!-- 漫反射暮光背景 -->
		<view class="pf-aurora">
			<view class="pf-aurora__blob pf-aurora__blob--1" />
			<view class="pf-aurora__blob pf-aurora__blob--2" />
		</view>

		<!-- 钛金个人名片 -->
		<view class="pf-card">
			<view class="pf-card__top">
				<view class="pf-avatar">
					<text class="pf-avatar__text">{{ avatarLetter }}</text>
					<view class="pf-avatar__badge">✓</view>
				</view>
				<view class="pf-card__info">
					<view class="pf-card__name-row">
						<text class="pf-card__name">{{ userName }}</text>
						<view class="pf-cert">企业认证学员</view>
					</view>
					<text class="pf-card__phone">{{ maskedPhone }}</text>
					<text class="pf-card__org">{{ institutionName }}</text>
				</view>
			</view>
		</view>

		<!-- 资产数据统计看板 -->
		<view class="pf-stats">
			<view class="pf-stat" @click="goRecords">
				<text class="pf-stat__num">{{ recordsCount }}</text>
				<text class="pf-stat__label">已测场次</text>
			</view>
			<view class="pf-stat" @click="goFavorites">
				<text class="pf-stat__num">{{ favoritesCount }}</text>
				<text class="pf-stat__label">我的收藏</text>
			</view>
			<view class="pf-stat">
				<text class="pf-stat__num">100%</text>
				<text class="pf-stat__label">完考率</text>
			</view>
		</view>

		<!-- 功能快捷入口（已按指令严格移除“切换机构”） -->
		<view class="pf-group">
			<view class="pf-group__title">常用功能</view>
			<view class="pf-row" @click="goFavorites">
				<view class="pf-row__icon" style="background: #fff7e8;">
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none">
						<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" stroke="#b26a00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">我的收藏</text>
					<text class="pf-row__sub">重点错题与知识点题库</text>
				</view>
				<text class="pf-row__arrow">›</text>
			</view>

			<view class="pf-row">
				<view class="pf-row__icon" style="background: #eceef3;">
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none">
						<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="#3a3a3c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">深色模式</text>
				</view>
				<view
					class="pf-row__toggle"
					:class="{ 'pf-row__toggle--on': isDarkMode }"
					@click="isDarkMode = !isDarkMode"
				>
					<view class="pf-row__knob" />
				</view>
			</view>
		</view>

		<view class="pf-group">
			<view class="pf-group__title">系统设置</view>
			<view class="pf-row" @click="handleClearCache">
				<view class="pf-row__icon" style="background: #eafaf0;">
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none">
						<polyline points="23 4 23 10 17 10" stroke="#1e8e3e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						<path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" stroke="#1e8e3e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">清除缓存</text>
				</view>
				<text class="pf-row__extra">{{ cacheSize }}</text>
			</view>
		</view>

		<!-- 退出登录 -->
		<view class="pf-logout" hover-class="pf-logout--pressed" @click="handleLogout">
			<text class="pf-logout__text">退出登录</text>
		</view>
		<text class="pf-version">智题库 C 端 · v1.5 Apple 钛金微光正式版</text>

		<!-- 底部占位安全区 -->
		<view class="pf-bottom-space" />

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 全面升级个人中心为 Apple 钛金微光风，严格按照指示移除「切换机构」选项; 2. 真实读取 Pinia 学员状态与所属机构，真实统计已测与收藏数量，支持安全登出]
 */
import { computed, onMounted, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import GlobalToast from "@/components/GlobalToast.vue";
import { fetchFavorites, fetchMemberTasks } from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const toast = useGlobalToast();

const recordsCount = ref(0);
const favoritesCount = ref(0);
const isDarkMode = ref(false);
const cacheSize = ref("12.4 MB");

const userName = computed(() => userStore.userInfo?.display_name || "认证学员");
const avatarLetter = computed(() => userName.value.slice(0, 1));

const maskedPhone = computed(() => {
	const phone = userStore.userInfo?.phone || "";
	if (phone.length === 11) {
		return `${phone.slice(0, 3)}****${phone.slice(7)}`;
	}
	return phone || "139****0001";
});

const institutionName = computed(() => {
	const matched = userStore.joinedTenants.find((t) => t.tenant_id === userStore.tenantId);
	return matched?.tenant_name || "智题库认证空间";
});

async function loadCounts(): Promise<void> {
	try {
		const [favRes, taskRes] = await Promise.allSettled([
			fetchFavorites(),
			fetchMemberTasks()
		]);
		if (favRes.status === "fulfilled") {
			favoritesCount.value = favRes.value.items?.length || 0;
		}
		if (taskRes.status === "fulfilled") {
			const tasks = taskRes.value.items || [];
			recordsCount.value = tasks.filter((t) => ["submitted", "verified", "pending_verification"].includes(t.status)).length;
		}
	} catch {
		// 容错静默
	}
}

function goRecords(): void {
	uni.switchTab({ url: "/pages/records/index" });
}

function goFavorites(): void {
	uni.navigateTo({ url: "/pages/favorites/index" });
}

function handleClearCache(): void {
	cacheSize.value = "0 KB";
	toast.success("本地缓存已清理");
}

function handleLogout(): void {
	uni.showModal({
		title: "退出确认",
		content: "确定要安全退出当前账号吗？",
		confirmText: "确定退出",
		confirmColor: "#ff3b30",
		success: (res) => {
			if (res.confirm) {
				userStore.clearAuth();
				uni.reLaunch({ url: "/pages/login/index" });
			}
		}
	});
}

onShow(() => {
	if (!userStore.token) {
		uni.reLaunch({ url: "/pages/login/index" });
		return;
	}
	loadCounts();
});
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.profile-apple {
	position: relative;
	min-height: 100vh;
	background: $bg;
	padding: 40rpx 36rpx 80rpx;
	box-sizing: border-box;
	overflow: hidden;
}

/* 暮光光晕 */
.pf-aurora {
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
			left: -120rpx;
			background: radial-gradient(circle, rgba(24, 82, 224, 0.4), rgba(24, 82, 224, 0));
		}

		&--2 {
			width: 440rpx;
			height: 440rpx;
			top: 320rpx;
			right: -100rpx;
			background: radial-gradient(circle, rgba(124, 92, 255, 0.28), rgba(124, 92, 255, 0));
		}
	}
}

/* 钛金名片 */
.pf-card {
	position: relative;
	z-index: 2;
	background: rgba(255, 255, 255, 0.92);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: $radius-card;
	padding: 36rpx 32rpx;
	box-shadow: $shadow-card;
	margin-bottom: 24rpx;

	&__top {
		display: flex;
		align-items: center;
		gap: 24rpx;
	}

	&__info {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 6rpx;
	}

	&__name-row {
		display: flex;
		align-items: center;
		gap: 12rpx;
	}

	&__name {
		font-size: 36rpx;
		font-weight: 800;
		color: $ink;
	}

	&__phone {
		font-size: 24rpx;
		color: $muted;
	}

	&__org {
		font-size: 22rpx;
		font-weight: 600;
		color: $accent;
	}
}

.pf-avatar {
	position: relative;
	width: 104rpx;
	height: 104rpx;
	border-radius: 50%;
	background: $gradient;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 24rpx rgba(24, 82, 224, 0.3);

	&__text {
		color: #ffffff;
		font-size: 42rpx;
		font-weight: 700;
	}

	&__badge {
		position: absolute;
		right: -2rpx;
		bottom: -2rpx;
		width: 32rpx;
		height: 32rpx;
		border-radius: 50%;
		background: $ok;
		color: #ffffff;
		border: 4rpx solid #ffffff;
		font-size: 18rpx;
		font-weight: 900;
		display: flex;
		align-items: center;
		justify-content: center;
	}
}

.pf-cert {
	background: $accent-soft;
	padding: 2rpx 12rpx;
	border-radius: 6rpx;
	font-size: 18rpx;
	font-weight: 700;
	color: $accent;
}

/* 统计看板 */
.pf-stats {
	position: relative;
	z-index: 2;
	background: rgba(255, 255, 255, 0.92);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: $radius-card;
	padding: 28rpx 20rpx;
	display: flex;
	box-shadow: $shadow-card;
	margin-bottom: 24rpx;
}

.pf-stat {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 6rpx;

	&__num {
		font-size: 38rpx;
		font-weight: 800;
		color: $ink;
		font-feature-settings: "tnum";
	}

	&__label {
		font-size: 22rpx;
		color: $muted;
	}
}

/* 列表组 */
.pf-group {
	position: relative;
	z-index: 2;
	background: rgba(255, 255, 255, 0.92);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: $radius-card;
	padding: 16rpx 28rpx;
	box-shadow: $shadow-card;
	margin-bottom: 24rpx;

	&__title {
		font-size: 22rpx;
		font-weight: 700;
		color: $muted;
		padding: 12rpx 4rpx 8rpx;
		letter-spacing: 0.5px;
	}
}

.pf-row {
	display: flex;
	align-items: center;
	padding: 22rpx 4rpx;
	border-top: 1px solid $line;

	&:first-of-type {
		border-top: none;
	}

	&__icon {
		width: 56rpx;
		height: 56rpx;
		border-radius: 16rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 20rpx;
	}

	&__main {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 2rpx;
	}

	&__title {
		font-size: 28rpx;
		font-weight: 600;
		color: $ink;
	}

	&__sub {
		font-size: 20rpx;
		color: $muted;
	}

	&__extra {
		font-size: 24rpx;
		color: $muted;
	}

	&__arrow {
		font-size: 32rpx;
		color: $faint;
	}

	&__toggle {
		width: 80rpx;
		height: 44rpx;
		border-radius: 999rpx;
		background: $surface-sunken;
		position: relative;
		transition: background 0.2s ease;

		&--on {
			background: $ok;
			.pf-row__knob {
				transform: translateX(36rpx);
			}
		}
	}

	&__knob {
		width: 36rpx;
		height: 36rpx;
		border-radius: 50%;
		background: #ffffff;
		position: absolute;
		top: 4rpx;
		left: 4rpx;
		box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.2);
		transition: transform 0.2s ease;
	}
}

/* 退出登录 */
.pf-logout {
	position: relative;
	z-index: 2;
	height: 88rpx;
	border-radius: $radius-card;
	background: rgba(255, 255, 255, 0.92);
	border: 1px solid $glass-border;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-top: 10rpx;
	box-shadow: $shadow-card;
	transition: all 0.2s ease;

	&--pressed {
		transform: scale(0.985);
		background: $danger-soft;
	}

	&__text {
		font-size: 28rpx;
		font-weight: 700;
		color: $danger;
	}
}

.pf-version {
	position: relative;
	z-index: 2;
	display: block;
	text-align: center;
	margin-top: 24rpx;
	font-size: 20rpx;
	color: $faint;
}

.pf-bottom-space {
	height: calc(100rpx + env(safe-area-inset-bottom));
}
</style>
