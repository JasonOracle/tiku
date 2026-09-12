<!--
  风格 A · Linear 极客冷灰风 · 个人中心（静态预览）
  数据矩阵 + 认证徽章 + 快捷入口，全部为静态演示数据
-->
<template>
	<view class="pf-page">
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
					<view class="pf-card__org">星雅教育 · 教务中心</view>
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
		<view class="pf-group">
			<view class="pf-group__title">常用功能</view>
			<view class="pf-row" v-for="r in entries" :key="r.title" @click="noop">
				<view class="pf-row__icon" :style="{ background: r.tint, color: r.color }">
					<view class="pf-glyph" :class="'pf-glyph--' + r.glyph"></view>
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">{{ r.title }}</text>
					<text class="pf-row__sub" v-if="r.sub">{{ r.sub }}</text>
				</view>
				<view class="pf-row__extra" v-if="r.extra">{{ r.extra }}</view>
				<view class="pf-row__toggle" :class="{ 'pf-row__toggle--on': toggles[r.key] }" v-if="r.key" @click.stop="toggles[r.key] = !toggles[r.key]">
					<view class="pf-row__knob"></view>
				</view>
				<text class="pf-row__arrow" v-else>›</text>
			</view>
		</view>

		<view class="pf-group">
			<view class="pf-group__title">账户与数据</view>
			<view class="pf-row" v-for="r in accountRows" :key="r.title" @click="noop">
				<view class="pf-row__icon" :style="{ background: r.tint, color: r.color }">
					<view class="pf-glyph" :class="'pf-glyph--' + r.glyph"></view>
				</view>
				<view class="pf-row__main">
					<text class="pf-row__title">{{ r.title }}</text>
					<text class="pf-row__sub" v-if="r.sub">{{ r.sub }}</text>
				</view>
				<view class="pf-row__extra" v-if="r.extra">{{ r.extra }}</view>
				<text class="pf-row__arrow">›</text>
			</view>
		</view>

		<!-- 退出登录 -->
		<view class="pf-logout" @click="noop">退出登录</view>
		<view class="pf-version">智题库 C 端 · 静态设计预览</view>

		<PreviewFloat current="preview-linear/profile/index" />
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

interface EntryRow {
	title: string;
	sub?: string;
	extra?: string;
	glyph: string;
	tint: string;
	color: string;
	key?: "dark" | "notice";
}
const entries: EntryRow[] = [
	{ title: "我的收藏", sub: "7 道错题与重点题", glyph: "star", tint: "#fef3c7", color: "#b45309" },
	{ title: "切换机构", sub: "当前：星雅教育 · 教务中心", glyph: "org", tint: "#eaf1ff", color: "#1d63ff" },
	{ title: "深色模式", glyph: "moon", tint: "#e2e8f0", color: "#334155", key: "dark" },
	{ title: "消息通知", glyph: "bell", tint: "#ffeceb", color: "#dc2626", key: "notice" },
];

const accountRows: EntryRow[] = [
	{ title: "清除缓存", extra: "32.6 MB", glyph: "clean", tint: "#ecfdf5", color: "#047857" },
	{ title: "关于智题库", sub: "版本与合规信息", glyph: "info", tint: "#f1f5f9", color: "#64748b" },
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
	min-height: 100vh;
	background: $bg;
	padding: 32rpx 40rpx 64rpx;
	box-sizing: border-box;
}

/* 个人名片 */
.pf-card {
	background: $ink;
	border-radius: $radius-card;
	padding: 40rpx 36rpx;
	box-shadow: $shadow-float;
}

.pf-card__top {
	display: flex;
	align-items: center;
	gap: 28rpx;
}

.pf-avatar {
	position: relative;
	width: 120rpx;
	height: 120rpx;
	border-radius: 28rpx;
	background: linear-gradient(150deg, #2b3a55, #101a2e);
	display: flex;
	align-items: center;
	justify-content: center;
	color: #ffffff;
	font-size: 44rpx;
	font-weight: 700;
	flex-shrink: 0;
}

.pf-avatar__badge {
	position: absolute;
	right: -8rpx;
	bottom: -8rpx;
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: $ok;
	color: #ffffff;
	font-size: 22rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border: 4rpx solid $ink;
}

.pf-card__name-row {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.pf-card__name {
	font-size: 36rpx;
	font-weight: 800;
	color: #ffffff;
}

.pf-cert {
	font-size: 18rpx;
	color: #93b4ff;
	border: 1px solid rgba(147, 180, 255, 0.45);
	border-radius: 6rpx;
	padding: 4rpx 12rpx;
}

.pf-card__phone {
	margin-top: 12rpx;
	font-size: 24rpx;
	color: #94a3b8;
	font-family: $mono;
}

.pf-card__org {
	margin-top: 8rpx;
	font-size: 22rpx;
	color: #64748b;
}

/* 数据看板 */
.pf-stats {
	display: flex;
	margin-top: 24rpx;
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 32rpx 0;
	box-shadow: $shadow-card;
}

.pf-stat {
	flex: 1;
	text-align: center;
}

.pf-stat__num {
	display: block;
	font-size: 44rpx;
	font-weight: 800;
	color: $ink;
	font-family: $mono;
}

.pf-stat__label {
	display: block;
	margin-top: 8rpx;
	font-size: 22rpx;
	color: $muted;
}

/* 分组列表 */
.pf-group {
	margin-top: 40rpx;
}

.pf-group__title {
	font-size: 24rpx;
	color: $muted;
	margin-bottom: 16rpx;
	padding-left: 8rpx;
}

.pf-row {
	display: flex;
	align-items: center;
	gap: 24rpx;
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 26rpx 28rpx;
	margin-bottom: 16rpx;
	box-shadow: $shadow-card;
	transition: transform 0.18s;
}

.pf-row:active {
	transform: scale(0.985);
}

.pf-row__icon {
	width: 64rpx;
	height: 64rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
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
	font-size: 28rpx;
	font-weight: 600;
	color: $ink;
}

.pf-row__sub {
	display: block;
	margin-top: 6rpx;
	font-size: 22rpx;
	color: $muted;
}

.pf-row__extra {
	font-size: 22rpx;
	color: $faint;
	font-family: $mono;
}

.pf-row__arrow {
	font-size: 34rpx;
	color: $faint;
}

/* 开关 */
.pf-row__toggle {
	width: 84rpx;
	height: 46rpx;
	border-radius: $radius-pill;
	background: $line-strong;
	padding: 4rpx;
	box-sizing: border-box;
	transition: background 0.25s;
}

.pf-row__toggle--on {
	background: $accent;
}

.pf-row__knob {
	width: 38rpx;
	height: 38rpx;
	border-radius: 50%;
	background: #ffffff;
	transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.pf-row__toggle--on .pf-row__knob {
	transform: translateX(38rpx);
}

/* 退出登录 */
.pf-logout {
	margin-top: 48rpx;
	text-align: center;
	background: $surface;
	border: 1px solid rgba(220, 38, 38, 0.35);
	border-radius: $radius-card;
	color: $danger;
	font-size: 28rpx;
	font-weight: 600;
	padding: 28rpx 0;
}

.pf-version {
	margin-top: 32rpx;
	text-align: center;
	font-size: 20rpx;
	color: $faint;
	font-family: $mono;
}
</style>
