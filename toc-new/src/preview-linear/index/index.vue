<!--
  风格 A · Linear 极客冷灰风 · 首页（静态预览）
  Banner 轮播 + 限时/综合/专项多形态试卷卡片 + 右上角三态演示切换器（列表 / 清空成就 / 骨架屏）
-->
<template>
	<view class="hm-page">
		<!-- 通顶 Header -->
		<view class="hm-header">
			<view class="hm-header__inner">
				<view>
					<view class="hm-header__hello">欢迎回来，陈伟</view>
					<view class="hm-header__org">星雅教育 · 教务中心</view>
				</view>
				<view class="hm-avatar">陈</view>
			</view>
		</view>

		<!-- 演示状态切换器 -->
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

		<!-- Banner 轮播 -->
		<swiper class="hm-banner" circular autoplay :interval="4200" :duration="520" @change="onSwiperChange">
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
			<view class="hm-dot" :class="{ 'hm-dot--on': i === bannerIndex }" v-for="i in banners.length" :key="i"></view>
		</view>

		<!-- 区块标题 -->
		<view class="hm-section">
			<view class="hm-section__title">进行中的测评</view>
			<view class="hm-section__count">{{ cards.length }} 项</view>
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

		<!-- 清空成就态：勋章插画 -->
		<view class="hm-empty" v-else-if="mode === 'empty'">
			<view class="hm-medal">
				<view class="hm-medal__ribbon"></view>
				<view class="hm-medal__disc">
					<view class="hm-medal__star"></view>
				</view>
			</view>
			<view class="hm-empty__title">阶段测评全部完成</view>
			<view class="hm-empty__sub">本季度 16 项测评均已参加，等待下一批发布</view>
		</view>

		<!-- 丰满列表态 -->
		<view class="hm-cards" v-else>
			<view class="hm-card" v-for="c in cards" :key="c.id" :class="{ 'hm-card--urgent': c.urgent }">
				<view class="hm-card__top">
					<view class="hm-card__kind" :class="'hm-card__kind--' + c.kindKey">{{ c.kind }}</view>
					<view class="hm-card__alert" v-if="c.urgent">剩余 2 小时截止</view>
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
					<view class="hm-card__btn" :class="{ 'hm-card__btn--ghost': !c.urgent }">{{ c.urgent ? "立即开考" : "去参加" }}</view>
				</view>
			</view>
		</view>

		<PreviewFloat current="preview-linear/index/index" />
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
	{ id: 1, image: "/static/preview/banner-linear.png", tag: "季度合规", title: "2026 安全生产合规季", sub: "全员必修 · 倒计时 2 小时" },
	{ id: 2, image: "/static/preview/banner-linear.png", tag: "能力认证", title: "教学质量标准化认证", sub: "100 题综合金标测评" },
	{ id: 3, image: "/static/preview/banner-linear.png", tag: "AI 实操", title: "大模型教学实操评估", sub: "5 题实操 · AI 智能推荐" },
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
	padding-bottom: 64rpx;
}

.hm-header {
	background: $surface;
	border-bottom: 1px solid $line;
}

.hm-header__inner {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 36rpx 40rpx 28rpx;
}

.hm-header__hello {
	font-size: 22rpx;
	color: $muted;
	font-family: $mono;
}

.hm-header__org {
	margin-top: 8rpx;
	font-size: 34rpx;
	font-weight: 800;
	color: $ink;
}

.hm-avatar {
	width: 72rpx;
	height: 72rpx;
	border-radius: 18rpx;
	background: $ink;
	color: #ffffff;
	font-size: 28rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

/* 演示切换器 */
.hm-switch {
	position: sticky;
	top: 0;
	z-index: 20;
	display: flex;
	justify-content: flex-end;
	gap: 8rpx;
	padding: 16rpx 40rpx 0;
}

.hm-switch__item {
	font-size: 22rpx;
	color: $muted;
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-pill;
	padding: 10rpx 24rpx;
	transition: all 0.2s;
}

.hm-switch__item--on {
	background: $ink;
	border-color: $ink;
	color: #ffffff;
}

/* Banner */
.hm-banner {
	height: 280rpx;
	margin: 20rpx 40rpx 0;
	border-radius: $radius-card;
	overflow: hidden;
}

.hm-banner__item {
	position: relative;
	height: 100%;
	border-radius: $radius-card;
	overflow: hidden;
}

.hm-banner__img {
	width: 100%;
	height: 100%;
}

.hm-banner__mask {
	position: absolute;
	inset: 0;
	background: linear-gradient(100deg, rgba(15, 23, 42, 0.82) 0%, rgba(15, 23, 42, 0.28) 62%, transparent 100%);
}

.hm-banner__text {
	position: absolute;
	left: 36rpx;
	bottom: 32rpx;
	right: 36rpx;
	color: #ffffff;
}

.hm-banner__tag {
	display: inline-block;
	font-size: 20rpx;
	font-family: $mono;
	letter-spacing: 0.12em;
	color: #93b4ff;
	border: 1px solid rgba(147, 180, 255, 0.5);
	border-radius: 6rpx;
	padding: 4rpx 12rpx;
	margin-bottom: 12rpx;
}

.hm-banner__title {
	font-size: 34rpx;
	font-weight: 800;
}

.hm-banner__sub {
	margin-top: 8rpx;
	font-size: 22rpx;
	opacity: 0.8;
}

.hm-dots {
	display: flex;
	justify-content: center;
	gap: 10rpx;
	margin-top: 18rpx;
}

.hm-dot {
	width: 10rpx;
	height: 10rpx;
	border-radius: 2rpx;
	background: $line-strong;
	transition: all 0.3s;
}

.hm-dot--on {
	width: 32rpx;
	background: $accent;
}

/* 区块标题 */
.hm-section {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 44rpx 40rpx 20rpx;
}

.hm-section__title {
	font-size: 30rpx;
	font-weight: 700;
	color: $ink;
}

.hm-section__count {
	font-size: 22rpx;
	color: $muted;
	font-family: $mono;
}

/* 试卷卡片 */
.hm-cards {
	padding: 0 40rpx;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.hm-card {
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 32rpx;
	box-shadow: $shadow-card;
	transition: transform 0.2s;
}

.hm-card:active {
	transform: scale(0.985);
}

.hm-card--urgent {
	border-color: rgba(220, 38, 38, 0.35);
}

.hm-card__top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 18rpx;
}

.hm-card__kind {
	font-size: 20rpx;
	font-weight: 600;
	padding: 6rpx 16rpx;
	border-radius: 6rpx;
}

.hm-card__kind--timed {
	color: $danger;
	background: $danger-soft;
}

.hm-card__kind--mixed {
	color: $accent;
	background: $accent-soft;
}

.hm-card__kind--special {
	color: $warn;
	background: $warn-soft;
}

.hm-card__alert {
	font-size: 20rpx;
	color: $danger;
	font-family: $mono;
}

.hm-card__title {
	font-size: 30rpx;
	font-weight: 700;
	color: $ink;
	line-height: 1.45;
}

.hm-card__meta {
	display: flex;
	gap: 40rpx;
	margin-top: 24rpx;
	padding: 20rpx 0;
	border-top: 1px solid $line;
	border-bottom: 1px solid $line;
}

.hm-meta__num {
	font-size: 30rpx;
	font-weight: 700;
	color: $ink;
	font-family: $mono;
}

.hm-meta__label {
	margin-left: 8rpx;
	font-size: 20rpx;
	color: $muted;
}

.hm-card__foot {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: 24rpx;
}

.hm-deadline {
	font-size: 22rpx;
	color: $muted;
}

.hm-deadline--hot {
	color: $danger;
	font-weight: 600;
}

.hm-card__btn {
	font-size: 24rpx;
	font-weight: 600;
	color: #ffffff;
	background: $accent;
	border-radius: $radius-inner;
	padding: 14rpx 32rpx;
}

.hm-card__btn--ghost {
	color: $accent;
	background: $accent-soft;
}

/* 骨架屏态 */
.hm-skel {
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 32rpx;
	margin: 0 40rpx 24rpx;
}

.hm-skel__bar {
	height: 24rpx;
	border-radius: 8rpx;
	background: linear-gradient(90deg, $surface-sunken 25%, #e6ecf4 50%, $surface-sunken 75%);
	background-size: 400% 100%;
	animation: skel-shimmer 1.4s ease infinite;
	margin-bottom: 18rpx;
	width: 60%;
}

.hm-skel__bar--wide {
	width: 90%;
	height: 32rpx;
}

.hm-skel__row {
	display: flex;
	gap: 16rpx;
	margin-top: 24rpx;
}

.hm-skel__chip {
	width: 120rpx;
	height: 40rpx;
	border-radius: 8rpx;
	background: $surface-sunken;
}

.hm-skel__btn {
	margin-left: auto;
	width: 160rpx;
	height: 52rpx;
	border-radius: $radius-inner;
	background: linear-gradient(90deg, $surface-sunken 25%, #e6ecf4 50%, $surface-sunken 75%);
	background-size: 400% 100%;
	animation: skel-shimmer 1.4s ease infinite;
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
	padding: 80rpx 40rpx 40rpx;
	text-align: center;
}

.hm-medal {
	position: relative;
	width: 160rpx;
	height: 200rpx;
	margin: 0 auto 40rpx;
}

.hm-medal__ribbon {
	position: absolute;
	left: 50%;
	top: 0;
	transform: translateX(-50%);
	width: 56rpx;
	height: 96rpx;
	background: linear-gradient(180deg, $accent 50%, $accent-deep 50%);
	clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 78%, 0 100%);
}

.hm-medal__disc {
	position: absolute;
	left: 50%;
	top: 72rpx;
	transform: translateX(-50%);
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	background: linear-gradient(150deg, #2b3a55, #101a2e);
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 16rpx 40rpx rgba(15, 23, 42, 0.3), inset 0 2rpx 6rpx rgba(255, 255, 255, 0.18);
}

.hm-medal__star {
	width: 52rpx;
	height: 52rpx;
	background: #fbbf24;
	clip-path: polygon(50% 0%, 63% 35%, 98% 35%, 70% 57%, 79% 91%, 50% 70%, 21% 91%, 30% 57%, 2% 35%, 37% 35%);
}

.hm-empty__title {
	font-size: 32rpx;
	font-weight: 700;
	color: $ink;
}

.hm-empty__sub {
	margin-top: 14rpx;
	font-size: 24rpx;
	color: $muted;
}
</style>
