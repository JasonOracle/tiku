<template>
	<wd-popup
		:model-value="modelValue"
		position="bottom"
		:safe-area-inset-bottom="true"
		custom-style="height: 60vh; background-color: #ffffff; border-top-left-radius: 32rpx; border-top-right-radius: 32rpx; overflow: hidden;"
		@update:model-value="handleVisibleChange"
	>
		<view class="answer-sheet">
			<view class="answer-sheet__handle" />

			<view class="answer-sheet__head">
				<text class="answer-sheet__title">答题卡</text>
				<text class="answer-sheet__summary">已答 {{ answeredIds.length }} / 共 {{ questions.length }}</text>
			</view>

			<view class="answer-sheet__legend">
				<view class="legend-item">
					<view class="legend-dot legend-dot--todo" />
					<text class="legend-text">未作答</text>
				</view>
				<view class="legend-item">
					<view class="legend-dot legend-dot--done" />
					<text class="legend-text">已作答</text>
				</view>
				<view class="legend-item">
					<view class="legend-dot legend-dot--current" />
					<text class="legend-text">当前题</text>
				</view>
			</view>

			<scroll-view class="answer-sheet__grid-wrap" scroll-y>
				<view class="answer-sheet__grid">
					<view
						v-for="(question, index) in questions"
						:key="question.id"
						class="sheet-cell"
						:class="resolveCellClass(question.id, index)"
						hover-class="sheet-cell--pressed"
						@click="handleSelect(index)"
					>
						<text class="sheet-cell__text">{{ index + 1 }}</text>
					</view>
				</view>
			</scroll-view>
		</view>
	</wd-popup>
</template>

<script setup lang="ts">
import type { ExamQuestion } from "@/api/exam";

const props = defineProps<{
	/** 抽屉显隐，配合 v-model 使用 */
	modelValue: boolean;
	/** 全部题目，仅用于渲染题号网格 */
	questions: ExamQuestion[];
	/** 已作答题目 ID 集合，判定规则由父级单点维护，本组件只负责渲染 */
	answeredIds: number[];
	/** 当前题序，用于渲染「当前题」描边态 */
	currentIndex: number;
}>();

const emit = defineEmits<{
	"update:modelValue": [visible: boolean];
	/** 点击题号，父级据此关闭抽屉并定位到该题 */
	select: [index: number];
}>();

function resolveCellClass(questionId: number, index: number): Record<string, boolean> {
	return {
		"sheet-cell--done": props.answeredIds.includes(questionId),
		"sheet-cell--current": index === props.currentIndex,
	};
}

function handleSelect(index: number): void {
	emit("select", index);
}

function handleVisibleChange(visible: boolean): void {
	emit("update:modelValue", visible);
}
</script>

<style lang="scss" scoped>
.answer-sheet {
	display: flex;
	flex-direction: column;
	height: 100%;
	padding: 0 32rpx;
}

.answer-sheet__handle {
	width: 72rpx;
	height: 8rpx;
	margin: 18rpx auto 0;
	border-radius: 4rpx;
	background-color: #e3e9f5;
}

.answer-sheet__head {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 26rpx 0 20rpx;
}

.answer-sheet__title {
	font-size: 34rpx;
	font-weight: 600;
	color: #1c2331;
}

.answer-sheet__summary {
	font-size: 24rpx;
	color: #748094;
}

.answer-sheet__legend {
	display: flex;
	align-items: center;
	padding-bottom: 22rpx;
	border-bottom: 1rpx solid #f0f3f9;
}

.legend-item {
	display: flex;
	align-items: center;
	margin-right: 32rpx;
}

.legend-dot {
	width: 22rpx;
	height: 22rpx;
	margin-right: 10rpx;
	border-radius: 8rpx;
}

.legend-dot--todo {
	background-color: #eef2f9;
}

.legend-dot--done {
	background-color: #1d63ff;
}

.legend-dot--current {
	border: 3rpx solid #1d63ff;
	background-color: #ffffff;
}

.legend-text {
	font-size: 22rpx;
	color: #748094;
}

.answer-sheet__grid-wrap {
	flex: 1;
	min-height: 0;
}

.answer-sheet__grid {
	display: flex;
	flex-wrap: wrap;
	padding: 28rpx 0 40rpx;
}

.sheet-cell {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 88rpx;
	height: 88rpx;
	margin: 0 20rpx 20rpx 0;
	border-radius: 16rpx;
	border: 3rpx solid transparent;
	background-color: #eef2f9;
	transition: transform 0.2s ease, background-color 0.2s ease;
}

.sheet-cell--pressed {
	transform: scale(0.94);
	opacity: 0.9;
}

.sheet-cell--done {
	background-color: #1d63ff;
}

.sheet-cell--current {
	border-color: #1d63ff;
	background-color: #ffffff;
}

.sheet-cell--done.sheet-cell--current {
	background-color: #1d63ff;
	border-color: #0045d8;
}

.sheet-cell__text {
	font-size: 28rpx;
	font-weight: 500;
	color: #748094;
}

.sheet-cell--done .sheet-cell__text {
	color: #ffffff;
}

.sheet-cell--current .sheet-cell__text {
	font-weight: 700;
	color: #1d63ff;
}

.sheet-cell--done.sheet-cell--current .sheet-cell__text {
	color: #ffffff;
}
</style>
