<!--
  风格 B · Apple 钛金微光风 · 首页（静态预览）
  暮光微渐变 Banner 轮播 + 多形态试卷卡片 + 右上角三态演示切换器（列表 / 清空成就 / 骨架屏）
-->
<template>
	<view class="hm-page">
		<!-- 通顶 Header -->
		<view class="hm-header">
			<view class="hm-header__inner">
				<view>
					<view class="hm-header__hello">下午好</view>
					<view class="hm-header__org">星雅教育 · 教务中心</view>
				</view>
				<view class="hm-avatar">陈</view>
			</view>
		</view>

		<!-- 演示状态切换器 -->
		<view class="hm-switch-wrap">
			<view class="hm-switch">
				<view
					class="hm-switch__item"
					:class="{ 'hm-switch__item--on': mode === m.key }"
					v-for="m in modes"
					:key="m.key"
					@click="mode = m.key"
				>
					{{ m.label }}
				</view>
			</view>
		</view>

		<!-- Banner 轮播 -->
		<swiper class="hm-banner" circular autoplay :interval="4200" :duration="560" @change="onSwiperChange">
			<swiper-item v-for="b in banners" :key="b.id">
				<view class="hm-banner__item">
					<image class="hm-banner__img" :src="b.image" mode="aspectFill" />
					<view class="hm-banner__mask"></view>
					<view class="hm-banner__text">
						<view class="hm-banner__tag">{{ b.tag }}</view>
						<view class="hm-banner__title">{{ b.title }}</view>
						<view class="hm-banner__sub">{{ b.sub }}</view>
					</view>
				</view>
			</swiper-item>
		</swiper>
		<view class="hm-dots">
			<view class="hm-dot" :class="{ 'hm-dot--on': i - 1 === bannerIndex }" v-for="i in banners.length" :key="i"></view>
		</view>

		<view class="hm-section">
			<view class="hm-section__title">为你推荐</view>
			<view class="hm-section__count">{{ cards.length }} 项进行中</view>
		</view>

		<!-- 骨架屏态 -->
		<view v-if="mode === 'skeleton'">
			<view class="hm-skel" v-for="n in 3" :key="n">
				<view class="hm-skel__bar hm-skel__bar--wide"></view>
				<view class="hm-skel__bar"></view>
				<view class="hm-skel__row">
					<view class="hm-skel__chip"></view>
					<view class="hm-skel__chip"></view>
					<view class="hm-skel__btn"></view>
				</view>
			</view>
		</view>

		<!-- 清空成就态：琉璃勋章 -->
		<view class="hm-empty" v-else-if="mode === 'empty'">
			<view class="hm-medal">
				<view class="hm-medal__halo"></view>
				<view class="hm-medal__ribbon"></view>
				<view class="hm-medal__disc">
					<view class="hm-medal__star"></view>
				</view>
			</view>
			<view class="hm-empty__title">本季测评圆满收官</view>
			<view class="hm-empty__sub">16 项测评全部完成，下一批发布后将第一时间提醒你</view>
		</view>

		<!-- 丰满列表态 -->
		<view class="hm-cards" v-else>
			<view class="hm-card" v-for="c in cards" :key="c.id" :class="{ 'hm-card--urgent': c.urgent }">
				<view class="hm-card__glow" :class="'hm-card__glow--' + c.kindKey"></view>
				<view class="hm-card__top">
					<view class="hm-card__kind" :class="'hm-card__kind--' + c.kindKey">{{ c.kind }}</view>
					<view class="hm-card__alert" v-if="c.urgent">
						<view class="hm-card__pulse"></view>
						剩余 2 小时截止
					</view>
				</view>
				<view class="hm-card__title">{{ c.title }}</view>
				<view class="hm-card__meta">
					<view class="hm-meta">
						<text class="hm-meta__num">{{ c.count }}</text>
						<text class="hm-meta__label">题量</text>
					</view>
					<view class="hm-meta">
						<text class="hm-meta__num">{{ c.limit }}</text>
						<text class="hm-meta__label">限时</text>
					</view>
					<view class="hm-meta">
						<text class="hm-meta__num">{{ c.score }}</text>
						<text class="hm-meta__label">总分</text>
					</view>
				</view>
				<view class="hm-card__foot">
					<view class="hm-deadline" :class="{ 'hm-deadline--hot': c.urgent }">截止 {{ c.deadline }}</view>
					<view class="hm-card__btn">{{ c.urgent ? "立即开考" : "去参加" }}</view>
				</view>
			</view>
		</view>

		<PreviewFloat current="preview-apple/index/index" />
	</view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import PreviewFloat from "@/components/PreviewFloat.vue";

type HomeMode = "list" | "empty" | "skeleton";
const mode = ref<HomeMode>("list");
const modes: { key: HomeMode; label: string }[] = [
	{ key: "list", label: "列表" },
	{ key: "empty", label: "清空" },
	{ key: "skeleton", label: "骨架" },
];

const bannerIndex = ref(0);
function onSwiperChange(e: { detail: { current: number } }): void {
	bannerIndex.value = e.detail.current;
}

interface HomeBanner {
	id: number;
	image: string;
	tag: string;
	title: string;
	sub: string;
}
const banners: HomeBanner[] = [
	{ id: 1, image: "/static/preview/banner-apple.png", tag: "季度合规", title: "2026 安全生产合规季", sub: "全员必修 · 倒计时 2 小时" },
	{ id: 2, image: "/static/preview/banner-apple.png", tag: "能力认证", title: "教学质量标准化认证", sub: "100 题综合金标测评" },
	{ id: 3, image: "/static/preview/banner-apple.png", tag: "AI 实操", title: "大模型教学实操评估", sub: "5 题实操 · AI 智能推荐" },
];

interface HomeCard {
	id: number;
	kindKey: "timed" | "mixed" | "special";
	kind: string;
	title: string;
	count: string;
	limit: string;
	score: string;
	deadline: string;
	urgent: boolean;
}
const cards: HomeCard[] = [
	{
		id: 1,
		kindKey: "timed",
		kind: "严苛限时",
		title: "星雅教育 2026 年全员安全生产与合规考试",
		count: "50",
		limit: "30 分钟",
		score: "100",
		deadline: "今日 18:00",
		urgent: true,
	},
	{
		id: 2,
		kindKey: "mixed",
		kind: "综合测评",
		title: "教务教学质量标准化综合测试",
		count: "100",
		limit: "不限时",
		score: "100",
		deadline: "本周日 23:59",
		urgent: false,
	},
	{
		id: 3,
		kindKey: "special",
		kind: "专项技能",
		title: "AI 教学辅助与出题大模型实操评估",
		count: "5",
		limit: "20 分钟",
		score: "50",
		deadline: "9 月 20 日",
		urgent: false,
	},
];
</script>

<style lang="scss" scoped>
@import "../tokens.scss";

.hm-page {
	min-height: 100vh;
	background: $bg;
	padding-bottom: 80rpx;
}

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
	font-size: 30rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 12rpx 32rpx rgba(10, 50, 153, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

/* 演示切换器：毛玻璃小胶囊 */
.hm-switch-wrap {
	display: flex;
	justify-content: flex-end;
	padding: 8rpx 44rpx 0;
}

.hm-switch {
	display: flex;
	gap: 6rpx;
	background: rgba(255, 255, 255, 0.7);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: $radius-pill;
	padding: 6rpx;
	box-shadow: $shadow-card;
}

.hm-switch__item {
	font-size: 22rpx;
	color: $muted;
	border-radius: $radius-pill;
	padding: 10rpx 26rpx;
	transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.hm-switch__item--on {
	background: $gradient;
	color: #ffffff;
	box-shadow: 0 6rpx 20rpx rgba(24, 82, 224, 0.35);
}

/* Banner */
.hm-banner {
	height: 300rpx;
	margin: 24rpx 44rpx 0;
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
	transition: all 0.3s;
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

/* 试卷卡片：大圆角 + 柔光 */
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
	animation: skel-shimmer 1.5s ease infinite;
}

@keyframes skel-shimmer {
	0% {
		background-position: 100% 0;
	}
	100% {
		background-position: -100% 0;
	}
}

/* 清空成就态 */
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
</style>
