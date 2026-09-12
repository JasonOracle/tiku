<!--
  风格 A · Linear 极客冷灰风 · 我的收藏（静态预览）
  错题卡片流：学科分类、当时错误答案与标准解析、一键移除交互
-->
<template>
	<view class="fv-page">
		<view class="fv-header">
			<view class="fv-header__inner">
				<view class="fv-header__title">我的收藏</view>
				<view class="fv-header__count">{{ items.length }} 道</view>
			</view>
		</view>

		<!-- 筛选胶囊 -->
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

		<PreviewFloat current="preview-linear/favorites/index" />
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
	padding-bottom: 64rpx;
}

.fv-header {
	background: $surface;
	border-bottom: 1px solid $line;
}

.fv-header__inner {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 36rpx 40rpx 28rpx;
}

.fv-header__title {
	font-size: 40rpx;
	font-weight: 800;
	color: $ink;
}

.fv-header__count {
	font-size: 22rpx;
	color: $muted;
	font-family: $mono;
}

/* 筛选胶囊 */
.fv-filters {
	display: flex;
	gap: 14rpx;
	padding: 24rpx 40rpx 8rpx;
	position: sticky;
	top: 0;
	z-index: 20;
	background: rgba(248, 250, 252, 0.92);
	backdrop-filter: blur(12px);
}

.fv-filter {
	font-size: 23rpx;
	color: $muted;
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-pill;
	padding: 12rpx 28rpx;
	transition: all 0.2s;
}

.fv-filter--on {
	background: $ink;
	border-color: $ink;
	color: #ffffff;
}

/* 卡片流 */
.fv-list {
	padding: 24rpx 40rpx 0;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.fv-card {
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 32rpx;
	box-shadow: $shadow-card;
	opacity: 1;
	transition: opacity 0.45s, transform 0.45s;
}

.fv-card--removing {
	opacity: 0;
	transform: translateX(40rpx);
}

.fv-card__top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 18rpx;
}

.fv-card__subject {
	font-size: 20rpx;
	font-weight: 600;
	padding: 6rpx 16rpx;
	border-radius: 6rpx;
}

.fv-card__subject--blue {
	color: $accent;
	background: $accent-soft;
}

.fv-card__subject--amber {
	color: #b45309;
	background: $warn-soft;
}

.fv-card__subject--green {
	color: #047857;
	background: $ok-soft;
}

.fv-card__remove {
	font-size: 22rpx;
	color: $muted;
	border: 1px solid $line;
	border-radius: $radius-pill;
	padding: 8rpx 24rpx;
	transition: all 0.2s;
}

.fv-card__remove:active {
	color: $danger;
	border-color: rgba(220, 38, 38, 0.4);
}

.fv-card__title {
	font-size: 29rpx;
	font-weight: 700;
	color: $ink;
	line-height: 1.5;
}

/* 答案对比 */
.fv-compare {
	margin-top: 24rpx;
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.fv-compare__row {
	display: flex;
	align-items: center;
	gap: 14rpx;
	border-radius: $radius-inner;
	padding: 16rpx 20rpx;
	font-size: 24rpx;
}

.fv-compare__row--wrong {
	background: $danger-soft;
	color: #b91c1c;
}

.fv-compare__row--ok {
	background: $ok-soft;
	color: #047857;
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
	margin-top: 20rpx;
	background: $surface-sunken;
	border-radius: $radius-inner;
	padding: 22rpx;
	font-size: 24rpx;
	color: $ink-2;
	line-height: 1.7;
}

/* 空态 */
.fv-empty {
	padding: 96rpx 0 48rpx;
	text-align: center;
}

.fv-empty__mark {
	font-size: 72rpx;
	color: $faint;
}

.fv-empty__title {
	margin-top: 16rpx;
	font-size: 30rpx;
	font-weight: 700;
	color: $ink;
}

.fv-empty__sub {
	margin-top: 12rpx;
	font-size: 24rpx;
	color: $muted;
}
</style>
