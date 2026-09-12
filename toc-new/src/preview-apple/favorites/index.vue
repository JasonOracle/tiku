<!--
  风格 B · Apple 钛金微光风 · 我的收藏（静态预览）
  错题卡片流：柔和分类胶囊、当时错误答案与标准解析、一键移除交互
-->
<template>
	<view class="fv-page">
		<view class="fv-header">
			<view class="fv-header__inner">
				<view class="fv-header__title">我的收藏</view>
				<view class="fv-header__count">{{ items.length }} 道</view>
			</view>
		</view>

		<!-- 毛玻璃筛选胶囊 -->
		<view class="fv-filters">
			<view
				class="fv-filter"
				:class="{ 'fv-filter--on': filter === f.key }"
				v-for="f in filters"
				:key="f.key"
				@click="filter = f.key"
			>
				{{ f.label }}
			</view>
		</view>

		<view class="fv-list">
			<view class="fv-card" v-for="it in shownItems" :key="it.id" :class="{ 'fv-card--removing': removing.has(it.id) }">
				<view class="fv-card__top">
					<view class="fv-card__subject" :class="'fv-card__subject--' + it.tone">{{ it.subject }}</view>
					<view class="fv-card__remove" @click="removeItem(it.id)">
						{{ removing.has(it.id) ? "已移除" : "移除" }}
					</view>
				</view>
				<view class="fv-card__title">{{ it.title }}</view>
				<view class="fv-compare">
					<view class="fv-compare__row fv-compare__row--wrong">
						<text class="fv-compare__mark">✕</text>
						<text class="fv-compare__label">当时作答</text>
						<text class="fv-compare__value">{{ it.myAnswer }}</text>
					</view>
					<view class="fv-compare__row fv-compare__row--ok">
						<text class="fv-compare__mark">✓</text>
						<text class="fv-compare__label">标准答案</text>
						<text class="fv-compare__value">{{ it.correctAnswer }}</text>
					</view>
				</view>
				<view class="fv-card__analysis">{{ it.analysis }}</view>
			</view>

			<!-- 空态 -->
			<view class="fv-empty" v-if="shownItems.length === 0">
				<view class="fv-empty__mark">☆</view>
				<view class="fv-empty__title">该分类暂无收藏</view>
				<view class="fv-empty__sub">在成绩报告页长按题目即可加入收藏</view>
			</view>
		</view>

		<PreviewFloat current="preview-apple/favorites/index" />
	</view>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import PreviewFloat from "@/components/PreviewFloat.vue";

type FavFilter = "all" | "safety" | "teach" | "ai";
const filter = ref<FavFilter>("all");
const filters: { key: FavFilter; label: string }[] = [
	{ key: "all", label: "全部" },
	{ key: "safety", label: "安全生产" },
	{ key: "teach", label: "教学教务" },
	{ key: "ai", label: "AI 实操" },
];

interface FavItem {
	id: number;
	subject: string;
	tone: "blue" | "amber" | "green";
	title: string;
	myAnswer: string;
	correctAnswer: string;
	analysis: string;
	category: Exclude<FavFilter, "all">;
}
const items: FavItem[] = [
	{
		id: 1,
		subject: "安全生产",
		tone: "blue",
		title: "有限空间作业前必须落实的检测顺序是？",
		myAnswer: "先通风、后检测、再作业",
		correctAnswer: "先检测、后通风、再作业",
		analysis:
			"正确顺序为「先检测、后通风、再作业」：必须先检测氧气、可燃气体与有毒气体浓度并留存记录，检测合格后方可机械通风，再次检测达标后才能进入作业。",
		category: "safety",
	},
	{
		id: 2,
		subject: "教学教务",
		tone: "amber",
		title: "新课标背景下，学期教学计划的核心变更点是？",
		myAnswer: "压缩考试频次",
		correctAnswer: "素养导向的单元整体设计",
		analysis:
			"新课标强调从「课时教学」走向「单元整体教学」，以大概念统领单元目标，教学计划需体现素养导向、学科实践与跨学科主题学习，而非单纯压缩考试频次。",
		category: "teach",
	},
	{
		id: 3,
		subject: "AI 实操",
		tone: "green",
		title: "出题大模型生成题库后，保证题目质量的第一道关卡是？",
		myAnswer: "随机抽检",
		correctAnswer: "结构化 Prompt 约束 + 知识库溯源校验",
		analysis:
			"生成质量的第一道关卡是提示词结构化约束（题型、难度、考点分布显式声明），再以知识库溯源校验答案唯一性，随机抽检只能作为最后的人工兜底。",
		category: "ai",
	},
];

/** 移除交互：标记后卡片淡出并从列表消失 */
const removing = reactive(new Set<number>());
function removeItem(id: number): void {
	if (removing.has(id)) return;
	removing.add(id);
	setTimeout(() => {
		const idx = items.findIndex((i) => i.id === id);
		if (idx >= 0) items.splice(idx, 1);
		removing.delete(id);
	}, 480);
}

const shownItems = computed(() => items.filter((i) => filter.value === "all" || i.category === filter.value));
</script>

<style lang="scss" scoped>
@import "../tokens.scss";

.fv-page {
	min-height: 100vh;
	background: $bg;
	padding-bottom: 80rpx;
}

.fv-header {
	background: linear-gradient(180deg, rgba(24, 82, 224, 0.07), transparent);
}

.fv-header__inner {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 44rpx 44rpx 24rpx;
}

.fv-header__title {
	font-size: 44rpx;
	font-weight: 800;
	color: $ink;
}

.fv-header__count {
	font-size: 22rpx;
	color: $muted;
}

/* 毛玻璃筛选胶囊 */
.fv-filters {
	display: flex;
	gap: 14rpx;
	padding: 20rpx 44rpx 8rpx;
	position: sticky;
	top: 0;
	z-index: 20;
	background: rgba(251, 251, 253, 0.78);
	backdrop-filter: $glass-blur;
	border-bottom: 1px solid $line;
	padding-bottom: 20rpx;
}

.fv-filter {
	font-size: 24rpx;
	color: $muted;
	background: rgba(255, 255, 255, 0.8);
	border: 1px solid $line;
	border-radius: $radius-pill;
	padding: 14rpx 30rpx;
	transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.fv-filter--on {
	background: $gradient;
	border-color: transparent;
	color: #ffffff;
	box-shadow: 0 8rpx 24rpx rgba(24, 82, 224, 0.3);
}

/* 卡片流 */
.fv-list {
	padding: 28rpx 44rpx 0;
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.fv-card {
	background: $surface;
	border-radius: $radius-card;
	padding: 38rpx 36rpx;
	box-shadow: $shadow-card;
	opacity: 1;
	transition: opacity 0.45s, transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
}

.fv-card--removing {
	opacity: 0;
	transform: translateX(48rpx) scale(0.96);
}

.fv-card__top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.fv-card__subject {
	font-size: 21rpx;
	font-weight: 600;
	padding: 10rpx 22rpx;
	border-radius: $radius-pill;
}

.fv-card__subject--blue {
	color: $accent;
	background: $accent-soft;
}

.fv-card__subject--amber {
	color: #b26a00;
	background: $warn-soft;
}

.fv-card__subject--green {
	color: #1e8e3e;
	background: $ok-soft;
}

.fv-card__remove {
	font-size: 22rpx;
	color: $muted;
	background: rgba(20, 30, 60, 0.05);
	border-radius: $radius-pill;
	padding: 10rpx 26rpx;
	transition: all 0.22s;
}

.fv-card__remove:active {
	color: #d70015;
	background: $danger-soft;
}

.fv-card__title {
	font-size: 30rpx;
	font-weight: 700;
	color: $ink;
	line-height: 1.55;
}

/* 答案对比 */
.fv-compare {
	margin-top: 26rpx;
	display: flex;
	flex-direction: column;
	gap: 14rpx;
}

.fv-compare__row {
	display: flex;
	align-items: center;
	gap: 16rpx;
	border-radius: 20rpx;
	padding: 18rpx 24rpx;
	font-size: 25rpx;
}

.fv-compare__row--wrong {
	background: $danger-soft;
	color: #d70015;
}

.fv-compare__row--ok {
	background: $ok-soft;
	color: #1e8e3e;
}

.fv-compare__mark {
	font-weight: 800;
}

.fv-compare__label {
	font-size: 20rpx;
	opacity: 0.75;
	flex-shrink: 0;
}

.fv-compare__value {
	font-weight: 600;
}

.fv-card__analysis {
	margin-top: 24rpx;
	background: linear-gradient(160deg, #f6f7fb, #f0f3fa);
	border-radius: 22rpx;
	padding: 26rpx;
	font-size: 25rpx;
	color: $ink-2;
	line-height: 1.75;
}

/* 空态 */
.fv-empty {
	padding: 100rpx 0 48rpx;
	text-align: center;
}

.fv-empty__mark {
	font-size: 76rpx;
	color: #c7c7cc;
}

.fv-empty__title {
	margin-top: 20rpx;
	font-size: 32rpx;
	font-weight: 700;
	color: $ink;
}

.fv-empty__sub {
	margin-top: 14rpx;
	font-size: 24rpx;
	color: $muted;
}
</style>
