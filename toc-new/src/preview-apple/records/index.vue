<!--
  风格 B · Apple 钛金微光风 · 我的测试页（静态预览）
  毛玻璃吸顶分段切换（进行中 / 未开始 / 已参加），已参加覆盖 100 分、核验中、48 分三种边界
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

		<!-- 毛玻璃吸顶分段控制器 -->
		<view class="rc-tabs">
			<view class="rc-seg">
				<view class="rc-seg__thumb" :class="'rc-seg__thumb--' + tab"></view>
				<view
					class="rc-seg__item"
					:class="{ 'rc-seg__item--on': tab === t.key }"
					v-for="t in tabs"
					:key="t.key"
					@click="tab = t.key"
				>
					{{ t.label }}
				</view>
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
					<view class="rc-card__time">
						<view class="rc-card__dot rc-card__dot--live"></view>
						剩余 {{ c.remain }}
					</view>
					<view class="rc-btn">继续答题</view>
				</view>
			</view>
		</view>

		<!-- 未开始 -->
		<view class="rc-list" v-else-if="tab === 'todo'">
			<view class="rc-card rc-card--muted" v-for="c in todoList" :key="c.id">
				<view class="rc-card__top">
					<view class="rc-card__title rc-card__title--soft">{{ c.title }}</view>
					<view class="rc-lock">
						<view class="rc-lock__hole"></view>
					</view>
				</view>
				<view class="rc-plan">预约开考：{{ c.plan }}</view>
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

		<PreviewFloat current="preview-apple/records/index" />
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
	padding-bottom: 80rpx;
}

.rc-header {
	background: linear-gradient(180deg, rgba(24, 82, 224, 0.07), transparent);
}

.rc-header__inner {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 44rpx 44rpx 24rpx;
}

.rc-header__title {
	font-size: 44rpx;
	font-weight: 800;
	color: $ink;
}

.rc-header__count {
	font-size: 22rpx;
	color: $muted;
}

/* 毛玻璃吸顶分段控制器 */
.rc-tabs {
	position: sticky;
	top: 0;
	z-index: 20;
	padding: 16rpx 44rpx 20rpx;
	background: rgba(251, 251, 253, 0.78);
	backdrop-filter: $glass-blur;
	border-bottom: 1px solid $line;
}

.rc-seg {
	position: relative;
	display: flex;
	background: rgba(20, 30, 60, 0.05);
	border-radius: 22rpx;
	padding: 6rpx;
}

.rc-seg__thumb {
	position: absolute;
	top: 6rpx;
	bottom: 6rpx;
	width: calc((100% - 12rpx) / 3);
	background: #ffffff;
	border-radius: 18rpx;
	box-shadow: 0 4rpx 16rpx rgba(20, 30, 60, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.8);
	transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
}

.rc-seg__thumb--doing {
	transform: translateX(0);
}

.rc-seg__thumb--todo {
	transform: translateX(100%);
}

.rc-seg__thumb--done {
	transform: translateX(200%);
}

.rc-seg__item {
	position: relative;
	flex: 1;
	text-align: center;
	font-size: 27rpx;
	color: $muted;
	padding: 20rpx 0;
	transition: color 0.25s, font-weight 0.25s;
}

.rc-seg__item--on {
	color: $ink;
	font-weight: 700;
}

/* 卡片列表 */
.rc-list {
	padding: 36rpx 44rpx 0;
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.rc-card {
	background: $surface;
	border-radius: $radius-card;
	padding: 38rpx 36rpx;
	box-shadow: $shadow-card;
	transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.rc-card:active {
	transform: scale(0.982);
}

.rc-card--muted {
	background: linear-gradient(170deg, #f7f7fa, #eef0f5);
	box-shadow: none;
}

.rc-card__top {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
}

.rc-card__title {
	font-size: 30rpx;
	font-weight: 700;
	color: $ink;
	line-height: 1.5;
}

.rc-card__title--soft {
	color: $ink-2;
	flex: 1;
	margin-right: 20rpx;
}

.rc-card__title--tight {
	margin-top: 26rpx;
}

/* 灰色小锁（CSS 绘制） */
.rc-lock {
	position: relative;
	width: 40rpx;
	height: 32rpx;
	background: #c7c7cc;
	border-radius: 9rpx;
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
	border: 4rpx solid #c7c7cc;
	border-bottom: none;
	border-radius: 12rpx 12rpx 0 0;
}

.rc-lock__hole {
	display: none;
}

/* 进度条 */
.rc-progress {
	display: flex;
	align-items: center;
	gap: 20rpx;
	margin: 28rpx 0;
}

.rc-progress__track {
	flex: 1;
	height: 10rpx;
	border-radius: 5rpx;
	background: rgba(20, 30, 60, 0.06);
	overflow: hidden;
}

.rc-progress__fill {
	height: 100%;
	border-radius: 5rpx;
	background: $gradient;
	transition: width 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

.rc-progress__text {
	font-size: 22rpx;
	color: $muted;
}

/* 预约计划 */
.rc-plan {
	font-size: 24rpx;
	color: $ink-2;
	margin: 22rpx 0;
}

/* 分数区 */
.rc-score-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 10rpx;
}

.rc-score__num {
	font-size: 64rpx;
	font-weight: 800;
	letter-spacing: -0.02em;
	line-height: 1;
}

.rc-score--ok .rc-score__num {
	color: $ok;
	text-shadow: 0 8rpx 24rpx rgba(52, 199, 89, 0.3);
}

.rc-score--warn .rc-score__num {
	font-size: 36rpx;
	color: $warn;
}

.rc-score--danger .rc-score__num {
	color: $danger;
	text-shadow: 0 8rpx 24rpx rgba(255, 59, 48, 0.25);
}

.rc-score__unit {
	font-size: 22rpx;
	margin-left: 8rpx;
	color: $muted;
}

.rc-badge {
	font-size: 20rpx;
	font-weight: 600;
	padding: 10rpx 22rpx;
	border-radius: $radius-pill;
}

.rc-badge--ok {
	color: #1e8e3e;
	background: $ok-soft;
}

.rc-badge--warn {
	color: #b26a00;
	background: $warn-soft;
	box-shadow: 0 4rpx 16rpx rgba(245, 166, 35, 0.2);
}

.rc-badge--danger {
	color: #d70015;
	background: $danger-soft;
}

/* 底部操作 */
.rc-card__foot {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: 30rpx;
	padding-top: 26rpx;
	border-top: 1px solid $line;
}

.rc-card__time {
	display: flex;
	align-items: center;
	gap: 10rpx;
	font-size: 22rpx;
	color: $muted;
}

.rc-card__dot--live {
	width: 12rpx;
	height: 12rpx;
	border-radius: 50%;
	background: $ok;
	animation: dot-live 1.6s ease-in-out infinite;
}

@keyframes dot-live {
	0%,
	100% {
		opacity: 1;
	}
	50% {
		opacity: 0.35;
	}
}

.rc-btn {
	font-size: 24rpx;
	font-weight: 700;
	color: #ffffff;
	background: $gradient;
	padding: 16rpx 38rpx;
	border-radius: $radius-pill;
	box-shadow: 0 8rpx 24rpx rgba(24, 82, 224, 0.3);
}

.rc-btn--ghost {
	color: $accent;
	background: $accent-soft;
	box-shadow: none;
}

.rc-btn--disabled {
	color: #aeaeb2;
	background: rgba(20, 30, 60, 0.06);
	box-shadow: none;
}
</style>
