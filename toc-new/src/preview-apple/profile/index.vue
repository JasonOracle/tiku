<!--
  风格 B · Apple 钛金微光风 · 个人中心（静态预览）
  钛金名片 + 柔和数据看板 + 玻璃质感快捷入口，全部为静态演示数据
-->
<template>
	<view class="pf-page">
		<!-- 暮光光晕背景 -->
		<view class="pf-aurora">
			<view class="pf-aurora__blob pf-aurora__blob--1"></view>
			<view class="pf-aurora__blob pf-aurora__blob--2"></view>
		</view>

		<!-- 通顶个人名片 -->
		<view class="pf-card">
			<view class="pf-card__top">
				<view class="pf-avatar">
					<text>陈</text>
					<view class="pf-avatar__badge">✓</view>
				</view>
				<view class="pf-card__info">
					<view class="pf-card__name-row">
						<text class="pf-card__name">陈伟</text>
						<view class="pf-cert">企业员工认证</view>
					</view>
					<view class="pf-card__phone">139****0006</view>
					<view class="pf-card__org">星雅教育 · 教务中心 · 学员</view>
				</view>
			</view>
		</view>

		<!-- 三大数据看板 -->
		<view class="pf-stats">
			<view class="pf-stat" v-for="s in stats" :key="s.label">
				<text class="pf-stat__num">{{ s.value }}</text>
				<text class="pf-stat__label">{{ s.label }}</text>
			</view>
		</view>

		<!-- 快捷入口 -->
		<view class="pf-group" v-for="g in groups" :key="g.title">
			<view class="pf-group__title">{{ g.title }}</view>
			<view class="pf-row" v-for="r in g.rows" :key="r.title" @click="noop">
				<view class="pf-row__icon" :style="{ background: r.tint }">
					<view class="pf-glyph" :class="'pf-glyph--' + r.glyph" :style="{ color: r.color }"></view>
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">{{ r.title }}</text>
					<text class="pf-row__sub" v-if="r.sub">{{ r.sub }}</text>
				</view>
				<view class="pf-row__extra" v-if="r.extra">{{ r.extra }}</view>
				<view
					class="pf-row__toggle"
					:class="{ 'pf-row__toggle--on': toggles[r.key || ''] }"
					v-if="r.key"
					@click.stop="toggles[r.key] = !toggles[r.key]"
				>
					<view class="pf-row__knob"></view>
				</view>
				<text class="pf-row__arrow" v-else>›</text>
			</view>
		</view>

		<!-- 退出登录 -->
		<view class="pf-logout" @click="noop">退出登录</view>
		<view class="pf-version">智题库 C 端 · 静态设计预览</view>

		<PreviewFloat current="preview-apple/profile/index" />
	</view>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import PreviewFloat from "@/components/PreviewFloat.vue";

const stats = [
	{ value: "16", label: "已测测评" },
	{ value: "91.4", label: "平均得分" },
	{ value: "7", label: "错题收藏" },
];

interface Row {
	title: string;
	sub?: string;
	extra?: string;
	glyph: string;
	tint: string;
	color: string;
	key?: "dark" | "notice";
}
interface Group {
	title: string;
	rows: Row[];
}
const groups: Group[] = [
	{
		title: "常用功能",
		rows: [
			{ title: "我的收藏", sub: "7 道错题与重点题", glyph: "star", tint: "#fff7e8", color: "#b26a00" },
			{ title: "深色模式", glyph: "moon", tint: "#eceef3", color: "#3a3a3c", key: "dark" },
			{ title: "消息通知", glyph: "bell", tint: "#ffeceb", color: "#d70015", key: "notice" },
		],
	},
	{
		title: "账户与数据",
		rows: [
			{ title: "清除缓存", extra: "32.6 MB", glyph: "clean", tint: "#eafaf0", color: "#1e8e3e" },
			{ title: "关于智题库", sub: "版本与合规信息", glyph: "info", tint: "#f2f2f7", color: "#86868b" },
		],
	},
];

/** 视觉开关状态（深色模式 / 消息通知），仅作静态交互演示 */
const toggles = reactive<Record<string, boolean>>({ dark: false, notice: true });

function noop(): void {
	uni.showToast({ title: "静态演示入口", icon: "none" });
}
</script>

<style lang="scss" scoped>
@import "../tokens.scss";

.pf-page {
	position: relative;
	min-height: 100vh;
	background: $bg;
	padding: 40rpx 44rpx 80rpx;
	box-sizing: border-box;
	overflow: hidden;
}

/* 光晕 */
.pf-aurora {
	position: absolute;
	inset: 0;
	pointer-events: none;
}

.pf-aurora__blob {
	position: absolute;
	border-radius: 50%;
	filter: blur(90rpx);
	opacity: 0.45;
}

.pf-aurora__blob--1 {
	width: 480rpx;
	height: 480rpx;
	background: rgba(24, 82, 224, 0.28);
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

/* CSS 图标族：星形 / 机构 / 月亮 / 铃铛 / 清理 / 信息 */
.pf-glyph {
	position: relative;
	width: 28rpx;
	height: 28rpx;
}

.pf-glyph--star {
	background: currentColor;
	clip-path: polygon(50% 0%, 63% 35%, 98% 35%, 70% 57%, 79% 91%, 50% 70%, 21% 91%, 30% 57%, 2% 35%, 37% 35%);
}

.pf-glyph--org {
	background: currentColor;
	clip-path: polygon(0 100%, 0 20%, 40% 20%, 40% 0, 100% 0, 100% 100%);
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
	border-radius: 14rpx 14rpx 4rpx 4rpx;
}

.pf-glyph--bell::after {
	content: "";
	position: absolute;
	left: 50%;
	bottom: -8rpx;
	transform: translateX(-50%);
	width: 12rpx;
	height: 8rpx;
	border-radius: 0 0 8rpx 8rpx;
	background: currentColor;
}

.pf-glyph--clean {
	background: currentColor;
	clip-path: polygon(0 30%, 40% 30%, 50% 15%, 100% 15%, 100% 100%, 0 100%);
}

.pf-glyph--info {
	background: currentColor;
	border-radius: 50%;
}

.pf-glyph--info::after {
	content: "";
	position: absolute;
	left: 50%;
	top: 6rpx;
	transform: translateX(-50%);
	width: 4rpx;
	height: 12rpx;
	border-radius: 2rpx;
	background: #ffffff;
}

.pf-row__main {
	flex: 1;
	min-width: 0;
}

.pf-row__title {
	display: block;
	font-size: 29rpx;
	font-weight: 600;
	color: $ink;
}

.pf-row__sub {
	display: block;
	margin-top: 8rpx;
	font-size: 22rpx;
	color: $muted;
}

.pf-row__extra {
	font-size: 22rpx;
	color: $faint;
}

.pf-row__arrow {
	font-size: 36rpx;
	color: $faint;
}

/* 开关 */
.pf-row__toggle {
	width: 88rpx;
	height: 50rpx;
	border-radius: $radius-pill;
	background: rgba(20, 30, 60, 0.14);
	padding: 4rpx;
	box-sizing: border-box;
	transition: background 0.25s;
}

.pf-row__toggle--on {
	background: $ok;
	box-shadow: 0 6rpx 18rpx rgba(52, 199, 89, 0.3);
}

.pf-row__knob {
	width: 42rpx;
	height: 42rpx;
	border-radius: 50%;
	background: #ffffff;
	box-shadow: 0 2rpx 8rpx rgba(20, 30, 60, 0.25);
	transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.pf-row__toggle--on .pf-row__knob {
	transform: translateX(38rpx);
}

/* 退出登录 */
.pf-logout {
	position: relative;
	margin-top: 52rpx;
	text-align: center;
	background: rgba(255, 255, 255, 0.82);
	border: 1px solid rgba(255, 59, 48, 0.3);
	border-radius: 26rpx;
	color: #d70015;
	font-size: 29rpx;
	font-weight: 600;
	padding: 30rpx 0;
	box-shadow: $shadow-card;
}

.pf-version {
	position: relative;
	margin-top: 36rpx;
	text-align: center;
	font-size: 20rpx;
	color: $faint;
}
</style>
