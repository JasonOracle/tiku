<!--
  风格 A · Linear 极客冷灰风 · 我的测试页（静态预览）
  三态切换（进行中 / 未开始 / 已参加），已参加覆盖 100 分优秀、核验中黄色胶囊、48 分不及格三种边界
-->
<template>
	<view class="rc-page">
		<!-- 通顶 Header -->
		<view class="rc-header">
			<view class="rc-header__inner">
				<view class="rc-header__title">我的测试</view>
				<view class="rc-header__count">{{ activeList.length }} 条记录</view>
			</view>
		</view>

		<!-- 吸顶 Tab -->
		<view class="rc-tabs">
			<view
				class="rc-tab"
				:class="{ 'rc-tab--on': tab === t.key }"
				v-for="t in tabs"
				:key="t.key"
				@click="tab = t.key"
			>
				{{ t.label }}
				<view class="rc-tab__line" v-if="tab === t.key"></view>
			</view>
		</view>

		<!-- 进行中 -->
		<view class="rc-list" v-if="tab === 'doing'">
			<view class="rc-card" v-for="c in doingList" :key="c.id">
				<view class="rc-card__title">{{ c.title }}</view>
				<view class="rc-progress">
					<view class="rc-progress__track">
						<view class="rc-progress__fill" :style="{ width: c.percent + '%' }"></view>
					</view>
					<view class="rc-progress__text">{{ c.done }}/{{ c.total }} 已作答</view>
				</view>
				<view class="rc-card__foot">
					<view class="rc-card__time">剩余 {{ c.remain }}</view>
					<view class="rc-btn rc-btn--primary">继续答题</view>
				</view>
			</view>
		</view>

		<!-- 未开始 -->
		<view class="rc-list" v-else-if="tab === 'todo'">
			<view class="rc-card" v-for="c in todoList" :key="c.id">
				<view class="rc-card__top">
					<view class="rc-card__title rc-card__title--lock">{{ c.title }}</view>
					<view class="rc-lock">
						<view class="rc-lock__body"></view>
						<view class="rc-lock__hole"></view>
					</view>
				</view>
				<view class="rc-plan">
					<view class="rc-plan__dot"></view>
					<text>预约开考：{{ c.plan }}</text>
				</view>
				<view class="rc-card__foot">
					<view class="rc-card__time">{{ c.window }}</view>
					<view class="rc-btn rc-btn--disabled">未到开考时间</view>
				</view>
			</view>
		</view>

		<!-- 已参加：全边界状态 -->
		<view class="rc-list" v-else>
			<view class="rc-card" v-for="r in doneList" :key="r.id">
				<view class="rc-score-row">
					<view class="rc-score" :class="'rc-score--' + r.tone">
						<text class="rc-score__num">{{ r.scoreDisplay }}</text>
						<text class="rc-score__unit" v-if="r.scoreUnit">{{ r.scoreUnit }}</text>
					</view>
					<view class="rc-badge" :class="'rc-badge--' + r.tone">{{ r.badge }}</view>
				</view>
				<view class="rc-card__title rc-card__title--tight">{{ r.title }}</view>
				<view class="rc-card__foot">
					<view class="rc-card__time">{{ r.meta }}</view>
					<view class="rc-btn rc-btn--ghost">查看报告</view>
				</view>
			</view>
		</view>

		<PreviewFloat current="preview-linear/records/index" />
	</view>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import PreviewFloat from "@/components/PreviewFloat.vue";

type RecordTab = "doing" | "todo" | "done";
const tab = ref<RecordTab>("done");
const tabs: { key: RecordTab; label: string }[] = [
	{ key: "doing", label: "进行中" },
	{ key: "todo", label: "未开始" },
	{ key: "done", label: "已参加" },
];

interface DoingItem {
	id: number;
	title: string;
	done: number;
	total: number;
	percent: number;
	remain: string;
}
const doingList: DoingItem[] = [
	{ id: 1, title: "AI 教学辅助与出题大模型实操评估", done: 3, total: 5, percent: 60, remain: "14 分 32 秒" },
	{ id: 2, title: "教学心理学阶段性小测", done: 12, total: 30, percent: 40, remain: "22 分 05 秒" },
];

interface TodoItem {
	id: number;
	title: string;
	plan: string;
	window: string;
}
const todoList: TodoItem[] = [
	{ id: 1, title: "2026 秋季学期教学素养统一测评", plan: "明日 09:00", window: "限时 60 分钟 · 满分 100" },
	{ id: 2, title: "新课标落地专项能力核验", plan: "9 月 18 日 14:00", window: "限时 45 分钟 · 满分 100" },
];

type ScoreTone = "ok" | "warn" | "danger";
interface DoneItem {
	id: number;
	title: string;
	tone: ScoreTone;
	scoreDisplay: string;
	scoreUnit?: string;
	badge: string;
	meta: string;
}
const doneList: DoneItem[] = [
	{
		id: 1,
		title: "星雅教育 2026 年全员安全生产与合规考试",
		tone: "ok",
		scoreDisplay: "100",
		scoreUnit: "分",
		badge: "优秀 · 已核验",
		meta: "答题用时 18 分钟 · 击败 98% 考生",
	},
	{
		id: 2,
		title: "教务教学质量标准化综合测试",
		tone: "warn",
		scoreDisplay: "核验中",
		badge: "AI/人工批阅核验中",
		meta: "客观题已批阅 · 主观题待复核",
	},
	{
		id: 3,
		title: "教学心理学阶段性小测",
		tone: "danger",
		scoreDisplay: "48",
		scoreUnit: "分",
		badge: "未及格 · 待补考",
		meta: "答题用时 25 分钟 · 及格线 60 分",
	},
];

const activeList = computed(() => (tab.value === "doing" ? doingList : tab.value === "todo" ? todoList : doneList));
</script>

<style lang="scss" scoped>
@import "../tokens.scss";

.rc-page {
	min-height: 100vh;
	background: $bg;
	padding-bottom: 64rpx;
}

.rc-header {
	background: $surface;
	border-bottom: 1px solid $line;
}

.rc-header__inner {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 36rpx 40rpx 28rpx;
}

.rc-header__title {
	font-size: 40rpx;
	font-weight: 800;
	color: $ink;
}

.rc-header__count {
	font-size: 22rpx;
	color: $muted;
	font-family: $mono;
}

/* 吸顶 Tab */
.rc-tabs {
	position: sticky;
	top: 0;
	z-index: 20;
	display: flex;
	background: rgba(248, 250, 252, 0.92);
	backdrop-filter: blur(12px);
	border-bottom: 1px solid $line;
	padding: 0 40rpx;
}

.rc-tab {
	position: relative;
	flex: 1;
	text-align: center;
	font-size: 28rpx;
	color: $muted;
	padding: 28rpx 0 24rpx;
	transition: color 0.2s;
}

.rc-tab--on {
	color: $ink;
	font-weight: 700;
}

.rc-tab__line {
	position: absolute;
	left: 50%;
	bottom: 0;
	transform: translateX(-50%);
	width: 48rpx;
	height: 4rpx;
	border-radius: 2rpx;
	background: $accent;
}

/* 卡片列表 */
.rc-list {
	padding: 32rpx 40rpx 0;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.rc-card {
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 32rpx;
	box-shadow: $shadow-card;
}

.rc-card__top {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
}

.rc-card__title {
	font-size: 29rpx;
	font-weight: 700;
	color: $ink;
	line-height: 1.45;
}

.rc-card__title--lock {
	color: $ink-2;
	flex: 1;
	margin-right: 20rpx;
}

.rc-card__title--tight {
	margin-top: 24rpx;
}

/* 灰色小锁（CSS 绘制） */
.rc-lock {
	position: relative;
	width: 40rpx;
	height: 32rpx;
	background: $faint;
	border-radius: 8rpx;
	margin-top: 6rpx;
	flex-shrink: 0;
}

.rc-lock::before {
	content: "";
	position: absolute;
	top: -18rpx;
	left: 50%;
	transform: translateX(-50%);
	width: 22rpx;
	height: 22rpx;
	border: 4rpx solid $faint;
	border-bottom: none;
	border-radius: 12rpx 12rpx 0 0;
}

.rc-lock__hole,
.rc-lock__body {
	display: none;
}

.rc-lock__hole {
	position: absolute;
	left: 50%;
	top: 12rpx;
	transform: translateX(-50%);
	width: 8rpx;
	height: 8rpx;
	border-radius: 50%;
	background: $surface;
}

/* 进度条 */
.rc-progress {
	display: flex;
	align-items: center;
	gap: 20rpx;
	margin: 24rpx 0;
}

.rc-progress__track {
	flex: 1;
	height: 8rpx;
	border-radius: 4rpx;
	background: $surface-sunken;
	overflow: hidden;
}

.rc-progress__fill {
	height: 100%;
	border-radius: 4rpx;
	background: $accent;
	transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.rc-progress__text {
	font-size: 22rpx;
	color: $muted;
	font-family: $mono;
}

/* 预约计划 */
.rc-plan {
	display: flex;
	align-items: center;
	gap: 12rpx;
	font-size: 24rpx;
	color: $ink-2;
	margin: 20rpx 0;
}

.rc-plan__dot {
	width: 12rpx;
	height: 12rpx;
	border-radius: 4rpx;
	background: $faint;
}

/* 分数区 */
.rc-score-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 8rpx;
}

.rc-score__num {
	font-size: 56rpx;
	font-weight: 800;
	font-family: $mono;
	letter-spacing: -0.02em;
}

.rc-score--ok .rc-score__num {
	color: $ok;
}

.rc-score--warn .rc-score__num {
	font-size: 34rpx;
	color: $warn;
}

.rc-score--danger .rc-score__num {
	color: $danger;
}

.rc-score__unit {
	font-size: 22rpx;
	margin-left: 6rpx;
	color: $muted;
}

.rc-badge {
	font-size: 20rpx;
	font-weight: 600;
	padding: 8rpx 18rpx;
	border-radius: 8rpx;
}

.rc-badge--ok {
	color: #047857;
	background: $ok-soft;
}

.rc-badge--warn {
	color: #b45309;
	background: $warn-soft;
}

.rc-badge--danger {
	color: #b91c1c;
	background: $danger-soft;
}

/* 底部操作 */
.rc-card__foot {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: 28rpx;
	padding-top: 24rpx;
	border-top: 1px solid $line;
}

.rc-card__time {
	font-size: 22rpx;
	color: $muted;
}

.rc-btn {
	font-size: 24rpx;
	font-weight: 600;
	padding: 14rpx 30rpx;
	border-radius: $radius-inner;
}

.rc-btn--primary {
	color: #ffffff;
	background: $accent;
}

.rc-btn--ghost {
	color: $accent;
	background: $accent-soft;
}

.rc-btn--disabled {
	color: $faint;
	background: $surface-sunken;
}
</style>
