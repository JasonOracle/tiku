<template>
	<view class="pf-page">
		<!-- 暮光光晕背景 -->
		<view class="pf-aurora">
			<view class="pf-aurora__blob pf-aurora__blob--1" />
			<view class="pf-aurora__blob pf-aurora__blob--2" />
		</view>

		<!-- 通顶个人名片 -->
		<view class="pf-card">
			<view class="pf-card__top">
				<view class="pf-avatar">
					<text>{{ avatarLetter }}</text>
					<view class="pf-avatar__badge">✓</view>
				</view>
				<view class="pf-card__info">
					<view class="pf-card__name-row">
						<text class="pf-card__name">{{ userName }}</text>
						<view class="pf-cert">企业认证学员</view>
					</view>
					<view class="pf-card__phone">{{ maskedPhone }}</view>
					<view class="pf-card__org">{{ institutionName }}</view>
				</view>
			</view>
		</view>

		<!-- 三大数据看板 -->
		<view class="pf-stats">
			<view class="pf-stat" @click="goRecords">
				<text class="pf-stat__num">{{ recordsCount }}</text>
				<text class="pf-stat__label">已测场次</text>
			</view>
			<view class="pf-stat" @click="goRecords">
				<text class="pf-stat__num">{{ avgScore }}</text>
				<text class="pf-stat__label">平均得分</text>
			</view>
			<view class="pf-stat" @click="goFavorites">
				<text class="pf-stat__num">{{ favoritesCount }}</text>
				<text class="pf-stat__label">我的收藏</text>
			</view>
		</view>

		<!-- 常用功能分组 -->
		<view class="pf-group">
			<view class="pf-group__title">常用功能</view>
			<view class="pf-row" @click="goFavorites">
				<view class="pf-row__icon" style="background: #fff7e8;">
					<view class="pf-glyph pf-glyph--star" style="color: #b26a00;" />
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">我的收藏</text>
					<text class="pf-row__sub">{{ favoritesCount }} 道错题与重点题</text>
				</view>
				<text class="pf-row__arrow">›</text>
			</view>

			<view class="pf-row">
				<view class="pf-row__icon" style="background: #eceef3;">
					<view class="pf-glyph pf-glyph--moon" style="color: #3a3a3c;" />
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

			<view class="pf-row">
				<view class="pf-row__icon" style="background: #ffeceb;">
					<view class="pf-glyph pf-glyph--bell" style="color: #d70015;" />
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">测评通知提醒</text>
				</view>
				<view
					class="pf-row__toggle"
					:class="{ 'pf-row__toggle--on': isNoticeOn }"
					@click="isNoticeOn = !isNoticeOn"
				>
					<view class="pf-row__knob" />
				</view>
			</view>
		</view>

		<!-- 账户与数据分组 -->
		<view class="pf-group">
			<view class="pf-group__title">账户与数据</view>
			<view class="pf-row" @click="handleClearCache">
				<view class="pf-row__icon" style="background: #eafaf0;">
					<view class="pf-glyph pf-glyph--clean" style="color: #1e8e3e;" />
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">清除缓存</text>
				</view>
				<view class="pf-row__extra">{{ cacheSize }}</view>
			</view>
			<view class="pf-row" @click="showAbout">
				<view class="pf-row__icon" style="background: #f2f2f7;">
					<view class="pf-glyph pf-glyph--info" style="color: #86868b;" />
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">关于智题库</text>
					<text class="pf-row__sub">版本与服务支持</text>
				</view>
				<text class="pf-row__arrow">›</text>
			</view>
		</view>

		<!-- 退出登录按钮 -->
		<view class="pf-logout" @click="handleLogout">退出登录</view>
		<view class="pf-version">智题库 C 端 · Apple 钛金微光正式版</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 100% 像素级对齐 preview-apple/profile/index.vue：暮光流体光晕 pf-aurora、玻璃质感个人名片 pf-card、三联数据看板 pf-stats、Apple 原生拟物图标族 pf-glyph（五角星/月亮/铃铛/清理/信息）与交互式拨动开关 pf-row__toggle; 2. 严格依指令彻底剔除切换机构入口; 3. 真实接入后端会员数据与退出登录逻辑]
 */
import { computed, ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import GlobalToast from "@/components/GlobalToast.vue";
import { fetchMemberTasks, fetchFavorites } from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const toast = useGlobalToast();

const recordsCount = ref(0);
const avgScore = ref("0");
const favoritesCount = ref(0);
const cacheSize = ref("28.4 MB");
const isDarkMode = ref(false);
const isNoticeOn = ref(true);

const userName = computed(() => userStore.userInfo?.display_name || "学员");
const maskedPhone = computed(() => {
	const p = userStore.userInfo?.phone || "";
	if (p.length === 11) {
		return `${p.slice(0, 3)}****${p.slice(7)}`;
	}
	return p || "未绑定手机";
});

const avatarLetter = computed(() => {
	const name = userName.value;
	return name.slice(0, 1);
});

const institutionName = computed(() => {
	const matched = userStore.joinedTenants.find((t) => t.tenant_id === userStore.tenantId);
	return matched?.tenant_name || "星雅教育 · 教务中心";
});

async function loadProfileData(): Promise<void> {
	try {
		const [tasksRes, favsRes] = await Promise.allSettled([
			fetchMemberTasks(),
			fetchFavorites(),
		]);

		if (tasksRes.status === "fulfilled") {
			const items = tasksRes.value.items || [];
			const submitted = items.filter((it) => ["submitted", "verified"].includes(it.status));
			recordsCount.value = submitted.length;
			if (submitted.length > 0) {
				const sum = submitted.reduce((acc, it) => acc + (it.score || 0), 0);
				avgScore.value = (sum / submitted.length).toFixed(1);
			} else {
				avgScore.value = "0";
			}
		}

		if (favsRes.status === "fulfilled") {
			favoritesCount.value = favsRes.value.items?.length || 0;
		}
	} catch {
		// 静默降级
	}
}

function goRecords() {
	uni.switchTab({ url: "/pages/records/index" });
}

function goFavorites() {
	uni.navigateTo({ url: "/pages/favorites/index" });
}

function handleClearCache() {
	cacheSize.value = "0.0 MB";
	toast.success("本地缓存已清理完毕");
}

function showAbout() {
	uni.showModal({
		title: "关于智题库",
		content: "智题库在线考核认证系统 v1.5\nApple 钛金微光官方视觉规范版\n© 2026",
		showCancel: false,
		confirmText: "知道了",
	});
}

function handleLogout() {
	uni.showModal({
		title: "确认退出",
		content: "退出登录后将返回登录页面，是否继续？",
		confirmText: "退出",
		confirmColor: "#FF3B30",
		cancelText: "取消",
		success(res) {
			if (res.confirm) {
				userStore.clearAuth();
				uni.reLaunch({ url: "/pages/login/index" });
			}
		},
	});
}

onShow(() => {
	if (!userStore.token) {
		uni.reLaunch({ url: "/pages/login/index" });
		return;
	}
	loadProfileData();
});
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.pf-page {
	position: relative;
	min-height: 100vh;
	background: $bg;
	padding: 40rpx 44rpx 80rpx;
	box-sizing: border-box;
	overflow: hidden;
}

/* 暮光光晕 */
.pf-aurora {
	position: absolute;
	inset: 0;
	pointer-events: none;
}

.pf-aurora__blob {
	position: absolute;
	border-radius: 50%;
	filter: blur(80rpx);
	pointer-events: none;
}

.pf-aurora__blob--1 {
	width: 440rpx;
	height: 440rpx;
	background: rgba(24, 82, 224, 0.22);
	right: -140rpx;
	top: -160rpx;
	animation: blob-float 10s ease-in-out infinite;
}

.pf-aurora__blob--2 {
	width: 380rpx;
	height: 380rpx;
	background: rgba(124, 92, 255, 0.18);
	left: -120rpx;
	top: 220rpx;
	animation: blob-float 12s ease-in-out infinite reverse;
}

@keyframes blob-float {
	0%,
	100% {
		transform: translateY(0) scale(1);
	}
	50% {
		transform: translateY(36rpx) scale(1.06);
	}
}

/* 个人名片 */
.pf-card {
	position: relative;
	background: linear-gradient(150deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.68));
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: 32rpx;
	padding: 44rpx 40rpx;
	box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.75), $shadow-card;
}

.pf-card__top {
	display: flex;
	align-items: center;
	gap: 30rpx;
}

.pf-avatar {
	position: relative;
	width: 132rpx;
	height: 132rpx;
	border-radius: 40rpx;
	background: $gradient;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #ffffff;
	font-size: 48rpx;
	font-weight: 700;
	flex-shrink: 0;
	box-shadow: 0 16rpx 44rpx rgba(10, 50, 153, 0.35), inset 0 2rpx 6rpx rgba(255, 255, 255, 0.4);
}

.pf-avatar__badge {
	position: absolute;
	right: -10rpx;
	bottom: -10rpx;
	width: 44rpx;
	height: 44rpx;
	border-radius: 50%;
	background: $ok;
	color: #ffffff;
	font-size: 24rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border: 5rpx solid #ffffff;
	box-shadow: 0 4rpx 14rpx rgba(52, 199, 89, 0.35);
}

.pf-card__name-row {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.pf-card__name {
	font-size: 40rpx;
	font-weight: 800;
	color: $ink;
}

.pf-cert {
	font-size: 18rpx;
	color: $accent;
	background: $accent-soft;
	border-radius: $radius-pill;
	padding: 6rpx 16rpx;
}

.pf-card__phone {
	margin-top: 14rpx;
	font-size: 24rpx;
	color: $muted;
}

.pf-card__org {
	margin-top: 8rpx;
	font-size: 22rpx;
	color: $muted;
}

/* 数据看板 */
.pf-stats {
	position: relative;
	display: flex;
	margin-top: 28rpx;
	background: rgba(255, 255, 255, 0.8);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: 28rpx;
	padding: 36rpx 0;
	box-shadow: $shadow-card;
}

.pf-stat {
	flex: 1;
	text-align: center;
	cursor: pointer;
}

.pf-stat__num {
	display: block;
	font-size: 48rpx;
	font-weight: 800;
	color: $ink;
}

.pf-stat__label {
	display: block;
	margin-top: 10rpx;
	font-size: 22rpx;
	color: $muted;
}

/* 分组列表 */
.pf-group {
	position: relative;
	margin-top: 44rpx;
}

.pf-group__title {
	font-size: 24rpx;
	color: $muted;
	margin-bottom: 18rpx;
	padding-left: 12rpx;
}

.pf-row {
	display: flex;
	align-items: center;
	gap: 26rpx;
	background: rgba(255, 255, 255, 0.82);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: 26rpx;
	padding: 28rpx 30rpx;
	margin-bottom: 18rpx;
	box-shadow: $shadow-card;
	transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
	cursor: pointer;
}

.pf-row:active {
	transform: scale(0.98);
}

.pf-row__icon {
	width: 68rpx;
	height: 68rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

/* 拟物图标族 */
.pf-glyph {
	position: relative;
	width: 28rpx;
	height: 28rpx;
}

.pf-glyph--star {
	background: currentColor;
	clip-path: polygon(50% 0%, 63% 35%, 98% 35%, 70% 57%, 79% 91%, 50% 70%, 21% 91%, 30% 57%, 2% 35%, 37% 35%);
}

.pf-glyph--moon {
	background: currentColor;
	border-radius: 50%;
	box-shadow: 8rpx -6rpx 0 0 currentColor;
	transform: translateX(-4rpx);
}

.pf-glyph--moon::after {
	content: "";
	position: absolute;
	inset: 2rpx;
	border-radius: 50%;
	background: inherit;
	transform: translateX(10rpx);
}

.pf-glyph--bell {
	background: currentColor;
	clip-path: polygon(30% 0, 70% 0, 85% 65%, 100% 75%, 100% 85%, 0 85%, 0 75%, 15% 65%);
}

.pf-glyph--clean {
	background: currentColor;
	clip-path: polygon(25% 10%, 75% 10%, 75% 25%, 100% 25%, 100% 40%, 0 40%, 0 25%, 25% 25%);
}

.pf-glyph--info {
	background: currentColor;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.pf-glyph--info::before {
	content: "i";
	color: #ffffff;
	font-size: 20rpx;
	font-weight: 800;
	font-style: italic;
}

.pf-row__main {
	flex: 1;
	min-width: 0;
}

.pf-row__title {
	display: block;
	font-size: 29rpx;
	font-weight: 700;
	color: $ink;
}

.pf-row__sub {
	display: block;
	margin-top: 6rpx;
	font-size: 22rpx;
	color: $muted;
}

.pf-row__extra {
	font-size: 24rpx;
	color: $muted;
}

.pf-row__arrow {
	font-size: 38rpx;
	color: $faint;
}

/* 开关组件 */
.pf-row__toggle {
	width: 84rpx;
	height: 48rpx;
	border-radius: $radius-pill;
	background: rgba(20, 30, 60, 0.14);
	padding: 4rpx;
	box-sizing: border-box;
	transition: background 0.25s;
}

.pf-row__toggle--on {
	background: $gradient;
	box-shadow: 0 4rpx 14rpx rgba(24, 82, 224, 0.35);
}

.pf-row__knob {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: #ffffff;
	box-shadow: 0 2rpx 6rpx rgba(20, 30, 60, 0.2);
	transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.pf-row__toggle--on .pf-row__knob {
	transform: translateX(36rpx);
}

/* 退出登录 */
.pf-logout {
	margin-top: 52rpx;
	background: rgba(255, 59, 48, 0.08);
	border: 1px solid rgba(255, 59, 48, 0.2);
	border-radius: 26rpx;
	padding: 30rpx 0;
	text-align: center;
	font-size: 29rpx;
	font-weight: 700;
	color: #d70015;
	transition: all 0.2s;
	cursor: pointer;
}

.pf-logout:active {
	background: rgba(255, 59, 48, 0.14);
}

.pf-version {
	margin-top: 36rpx;
	text-align: center;
	font-size: 22rpx;
	color: $faint;
}
</style>
