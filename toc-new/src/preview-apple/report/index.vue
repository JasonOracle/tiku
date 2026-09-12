<!--
  风格 B · Apple 钛金微光风 · 成绩报告页（静态预览）
  深空蓝微渐变夜空看板（微漫反射光晕）+ 绿勾/红叉逐题复盘 + 考点展开卡片 + 防泄题保密态一键切换
-->
<template>
	<view class="rp-page">
		<!-- 保密态切换 -->
		<view class="rp-modebar">
			<view class="rp-modebar__inner">
				<text class="rp-modebar__label">{{ secretMode ? "保密审核态" : "成绩查看态" }}</text>
				<view class="rp-switch" :class="{ 'rp-switch--on': secretMode }" @click="secretMode = !secretMode">
					<view class="rp-switch__knob"></view>
				</view>
			</view>
			<view class="rp-modebar__sub">{{ secretMode ? "主观题核验完成前，答案与解析已锁定" : "客观题已批阅，可查看逐题复盘" }}</view>
		</view>

		<!-- 深空蓝出分夜空看板 -->
		<view class="rp-board">
			<view class="rp-board__glow rp-board__glow--1"></view>
			<view class="rp-board__glow rp-board__glow--2"></view>
			<view class="rp-board__main">
				<view class="rp-board__score">
					<text class="rp-board__num">92</text>
					<text class="rp-board__unit">/ 100</text>
				</view>
				<view class="rp-board__right">
					<view class="rp-grade-chip">优秀 · 已核验</view>
					<view class="rp-board__beat">击败 98% 考生</view>
				</view>
			</view>
			<view class="rp-metrics">
				<view class="rp-metric" v-for="m in metrics" :key="m.label">
					<text class="rp-metric__num">{{ m.value }}</text>
					<text class="rp-metric__label">{{ m.label }}</text>
				</view>
			</view>
		</view>

		<!-- 保密态琉璃插画 -->
		<view class="rp-secret" v-if="secretMode">
			<view class="rp-secret__shield">
				<view class="rp-secret__lock"></view>
			</view>
			<view class="rp-secret__title">解析保密中</view>
			<view class="rp-secret__sub">全部 4 道主观题正在 AI 与人工双通道复核，核验完成后将自动解锁答案与考点解析</view>
			<view class="rp-secret__eta">预计解锁：明日 18:00 前</view>
		</view>

		<!-- 逐题复盘 -->
		<view class="rp-review" v-else>
			<view class="rp-section">逐题复盘</view>
			<view class="rp-item" v-for="(it, idx) in reviewItems" :key="it.id">
				<view class="rp-item__head" @click="toggleExpand(it.id)">
					<view class="rp-item__left">
						<view class="rp-item__mark" :class="'rp-item__mark--' + it.status">{{ it.status === "ok" ? "✓" : "✕" }}</view>
						<view>
							<view class="rp-item__no">第 {{ idx + 1 }} 题 · {{ it.type }}</view>
							<view class="rp-item__title">{{ it.title }}</view>
						</view>
					</view>
					<view class="rp-item__arrow" :class="{ 'rp-item__arrow--open': expanded.has(it.id) }">›</view>
				</view>
				<view class="rp-item__body" v-if="expanded.has(it.id)">
					<view class="rp-row" :class="'rp-row--' + o.state" v-for="o in it.options" :key="o.key">
						<view class="rp-row__key">{{ o.key }}</view>
						<view class="rp-row__text">{{ o.text }}</view>
						<view class="rp-row__tag" v-if="o.state === 'user-correct'">你的答案 ✓</view>
						<view class="rp-row__tag" v-else-if="o.state === 'user-wrong'">你的答案 ✕</view>
						<view class="rp-row__tag" v-else-if="o.state === 'correct'">标准答案</view>
					</view>
					<view class="rp-point">
						<view class="rp-point__head">
							<view class="rp-point__label">考点</view>
							<view class="rp-point__tag">{{ it.point }}</view>
						</view>
						<view class="rp-point__text">{{ it.analysis }}</view>
					</view>
				</view>
			</view>
		</view>

		<PreviewFloat current="preview-apple/report/index" />
	</view>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import PreviewFloat from "@/components/PreviewFloat.vue";

const secretMode = ref(false);
const expanded = reactive(new Set<number>([1]));

function toggleExpand(id: number): void {
	if (expanded.has(id)) expanded.delete(id);
	else expanded.add(id);
}

const metrics = [
	{ value: "18", label: "用时(分)" },
	{ value: "46/50", label: "正确题数" },
	{ value: "60", label: "及格线" },
];

type RowState = "user-correct" | "user-wrong" | "correct" | "plain";
interface ReviewRow {
	key: string;
	text: string;
	state: RowState;
}
interface ReviewItem {
	id: number;
	type: string;
	title: string;
	status: "ok" | "wrong";
	options: ReviewRow[];
	point: string;
	analysis: string;
}

const reviewItems: ReviewItem[] = [
	{
		id: 1,
		type: "单选题",
		title: "企业安全生产标准化的核心运行模式是？",
		status: "ok",
		options: [
			{ key: "A", text: "策划、实施、检查、改进的 PDCA 动态循环", state: "user-correct" },
			{ key: "B", text: "一把手负责、全员签字确认的静态达标", state: "plain" },
			{ key: "C", text: "以年度检查代替日常隐患排查治理", state: "plain" },
		],
		point: "安全生产标准化 · PDCA 循环",
		analysis:
			"GB/T 33000-2016 明确标准化系统采用 PDCA 动态循环运行模式。策划（P）建立目标与制度，实施（D）落实资源与培训，检查（C）开展隐患排查与绩效监测，改进（A）持续修正体系有效性。",
	},
	{
		id: 2,
		type: "多选题",
		title: "下列属于危险作业审批范围的有（多选）？",
		status: "wrong",
		options: [
			{ key: "A", text: "动火作业", state: "user-correct" },
			{ key: "B", text: "有限空间作业", state: "user-wrong" },
			{ key: "C", text: "临时用电作业", state: "correct" },
			{ key: "D", text: "办公室内纸质文件传阅", state: "plain" },
		],
		point: "危险作业审批 · 八大危险作业",
		analysis:
			"动火、有限空间、临时用电、高处、吊装、动土、断路、盲板抽堵均属危险作业，实施前必须办理作业审批票证。B 项漏选是高频失分点：有限空间作业因中毒窒息风险高，审批要求最为严格。",
	},
	{
		id: 3,
		type: "判断题",
		title: "新员工入职后，可先上岗操作再补做三级安全教育。",
		status: "wrong",
		options: [
			{ key: "对", text: "该说法错误，三级安全教育必须在入职后上岗前完成", state: "correct" },
		],
		point: "三级安全教育 · 先培训后上岗",
		analysis:
			"安全生产法要求从业人员必须经安全生产教育和培训合格后方可上岗作业。厂级、车间级、班组级三级安全教育总学时不得少于 24 学时，未完成培训擅自上岗属重大违规行为。",
	},
];
</script>

<style lang="scss" scoped>
@import "../tokens.scss";

.rp-page {
	min-height: 100vh;
	background: $bg;
	padding-bottom: 80rpx;
}

/* 保密态切换条 */
.rp-modebar {
	background: linear-gradient(180deg, rgba(24, 82, 224, 0.07), transparent);
	padding: 28rpx 44rpx;
}

.rp-modebar__inner {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.rp-modebar__label {
	font-size: 28rpx;
	font-weight: 700;
	color: $ink;
}

.rp-modebar__sub {
	margin-top: 10rpx;
	font-size: 22rpx;
	color: $muted;
}

.rp-switch {
	width: 92rpx;
	height: 52rpx;
	border-radius: $radius-pill;
	background: rgba(20, 30, 60, 0.14);
	padding: 4rpx;
	box-sizing: border-box;
	transition: background 0.25s;
}

.rp-switch--on {
	background: $gradient;
	box-shadow: 0 6rpx 20rpx rgba(24, 82, 224, 0.3);
}

.rp-switch__knob {
	width: 44rpx;
	height: 44rpx;
	border-radius: 50%;
	background: #ffffff;
	box-shadow: 0 2rpx 8rpx rgba(20, 30, 60, 0.25);
	transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.rp-switch--on .rp-switch__knob {
	transform: translateX(40rpx);
}

/* 深空蓝夜空看板 */
.rp-board {
	position: relative;
	margin: 20rpx 44rpx 0;
	background: linear-gradient(150deg, #14306e 0%, #0a3299 48%, #1852e0 100%);
	border-radius: 32rpx;
	padding: 44rpx 40rpx;
	box-shadow: 0 24rpx 72rpx rgba(10, 50, 153, 0.4);
	overflow: hidden;
}

.rp-board__glow {
	position: absolute;
	border-radius: 50%;
	filter: blur(70rpx);
	pointer-events: none;
}

.rp-board__glow--1 {
	width: 320rpx;
	height: 320rpx;
	background: rgba(126, 158, 255, 0.4);
	right: -80rpx;
	top: -100rpx;
	animation: glow-breathe 5s ease-in-out infinite;
}

.rp-board__glow--2 {
	width: 260rpx;
	height: 260rpx;
	background: rgba(255, 255, 255, 0.16);
	left: -60rpx;
	bottom: -120rpx;
	animation: glow-breathe 6.5s ease-in-out infinite reverse;
}

@keyframes glow-breathe {
	0%,
	100% {
		opacity: 0.6;
		transform: scale(1);
	}
	50% {
		opacity: 1;
		transform: scale(1.12);
	}
}

.rp-board__main {
	position: relative;
	display: flex;
	align-items: flex-end;
	justify-content: space-between;
}

.rp-board__num {
	font-size: 120rpx;
	font-weight: 800;
	color: #ffffff;
	letter-spacing: -0.03em;
	line-height: 1;
	text-shadow: 0 12rpx 40rpx rgba(0, 0, 0, 0.25);
}

.rp-board__unit {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.65);
	margin-left: 14rpx;
}

.rp-board__right {
	text-align: right;
}

.rp-grade-chip {
	display: inline-block;
	font-size: 22rpx;
	font-weight: 600;
	color: #0a3299;
	background: linear-gradient(150deg, #ffffff, #d9f4e3);
	border-radius: $radius-pill;
	padding: 12rpx 26rpx;
	box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.18);
}

.rp-board__beat {
	margin-top: 14rpx;
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.75);
}

.rp-metrics {
	position: relative;
	display: flex;
	margin-top: 40rpx;
	border-top: 1px solid rgba(255, 255, 255, 0.18);
	padding-top: 30rpx;
}

.rp-metric {
	flex: 1;
	text-align: center;
}

.rp-metric__num {
	display: block;
	font-size: 34rpx;
	font-weight: 800;
	color: #ffffff;
}

.rp-metric__label {
	display: block;
	margin-top: 10rpx;
	font-size: 20rpx;
	color: rgba(255, 255, 255, 0.6);
}

/* 保密态琉璃插画 */
.rp-secret {
	margin: 48rpx 44rpx 0;
	background: linear-gradient(160deg, rgba(255, 255, 255, 0.9), rgba(238, 242, 253, 0.7));
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: 32rpx;
	padding: 76rpx 52rpx;
	text-align: center;
	box-shadow: $shadow-card;
}

.rp-secret__shield {
	position: relative;
	width: 136rpx;
	height: 158rpx;
	margin: 0 auto 40rpx;
	background: $gradient;
	clip-path: polygon(50% 0, 100% 18%, 100% 62%, 50% 100%, 0 62%, 0 18%);
	box-shadow: 0 20rpx 48rpx rgba(10, 50, 153, 0.35);
}

.rp-secret__lock {
	position: absolute;
	left: 50%;
	top: 62rpx;
	transform: translateX(-50%);
	width: 42rpx;
	height: 32rpx;
	border-radius: 10rpx;
	background: #ffd76a;
}

.rp-secret__lock::before {
	content: "";
	position: absolute;
	top: -20rpx;
	left: 50%;
	transform: translateX(-50%);
	width: 22rpx;
	height: 22rpx;
	border: 4rpx solid #ffd76a;
	border-bottom: none;
	border-radius: 11rpx 11rpx 0 0;
}

.rp-secret__title {
	font-size: 34rpx;
	font-weight: 800;
	color: $ink;
}

.rp-secret__sub {
	margin: 18rpx auto 0;
	font-size: 24rpx;
	color: $muted;
	line-height: 1.75;
	max-width: 480rpx;
}

.rp-secret__eta {
	display: inline-block;
	margin-top: 30rpx;
	font-size: 22rpx;
	color: #b26a00;
	background: $warn-soft;
	border-radius: $radius-pill;
	padding: 12rpx 28rpx;
	box-shadow: 0 4rpx 16rpx rgba(245, 166, 35, 0.2);
}

/* 逐题复盘 */
.rp-section {
	font-size: 34rpx;
	font-weight: 800;
	color: $ink;
	padding: 48rpx 44rpx 24rpx;
}

.rp-review {
	padding: 0 44rpx;
}

.rp-item {
	background: $surface;
	border-radius: $radius-card;
	margin-bottom: 28rpx;
	box-shadow: $shadow-card;
	overflow: hidden;
}

.rp-item__head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 32rpx 36rpx;
}

.rp-item__left {
	display: flex;
	align-items: center;
	gap: 22rpx;
	flex: 1;
	min-width: 0;
}

.rp-item__mark {
	width: 56rpx;
	height: 56rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 30rpx;
	font-weight: 800;
	flex-shrink: 0;
}

.rp-item__mark--ok {
	color: #1e8e3e;
	background: $ok-soft;
	box-shadow: 0 6rpx 18rpx rgba(52, 199, 89, 0.25);
}

.rp-item__mark--wrong {
	color: #d70015;
	background: $danger-soft;
	box-shadow: 0 6rpx 18rpx rgba(255, 59, 48, 0.22);
}

.rp-item__no {
	font-size: 20rpx;
	color: $muted;
}

.rp-item__title {
	margin-top: 8rpx;
	font-size: 28rpx;
	font-weight: 600;
	color: $ink;
	line-height: 1.5;
}

.rp-item__arrow {
	font-size: 38rpx;
	color: $faint;
	transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}

.rp-item__arrow--open {
	transform: rotate(90deg);
}

.rp-item__body {
	border-top: 1px solid $line;
	padding: 30rpx 36rpx 36rpx;
}

/* 选项行：绿勾 / 红叉 / 标准答案 */
.rp-row {
	display: flex;
	align-items: center;
	gap: 20rpx;
	border: 1px solid rgba(20, 30, 60, 0.05);
	background: rgba(20, 30, 60, 0.03);
	border-radius: 20rpx;
	padding: 22rpx 26rpx;
	margin-bottom: 16rpx;
	transition: all 0.25s;
}

.rp-row--user-correct {
	border-color: rgba(52, 199, 89, 0.4);
	background: $ok-soft;
}

.rp-row--user-wrong {
	border-color: rgba(255, 59, 48, 0.4);
	background: $danger-soft;
}

.rp-row--correct {
	border-color: rgba(24, 82, 224, 0.35);
	background: $accent-soft;
}

.rp-row__key {
	width: 48rpx;
	height: 48rpx;
	border-radius: 50%;
	background: #ffffff;
	box-shadow: 0 2rpx 8rpx rgba(20, 30, 60, 0.08);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	font-weight: 700;
	color: $ink-2;
	flex-shrink: 0;
}

.rp-row__text {
	flex: 1;
	font-size: 26rpx;
	color: $ink-2;
	line-height: 1.55;
}

.rp-row__tag {
	flex-shrink: 0;
	font-size: 20rpx;
	font-weight: 700;
	padding: 8rpx 18rpx;
	border-radius: $radius-pill;
}

.rp-row--user-correct .rp-row__tag {
	color: #1e8e3e;
	background: rgba(52, 199, 89, 0.16);
}

.rp-row--user-wrong .rp-row__tag {
	color: #d70015;
	background: rgba(255, 59, 48, 0.12);
}

.rp-row--correct .rp-row__tag {
	color: $accent;
	background: rgba(24, 82, 224, 0.12);
}

/* 考点解析 */
.rp-point {
	margin-top: 26rpx;
	background: linear-gradient(160deg, #f2f5fd, #eef2fd);
	border-radius: 22rpx;
	padding: 28rpx;
}

.rp-point__head {
	display: flex;
	align-items: center;
	gap: 16rpx;
	margin-bottom: 16rpx;
}

.rp-point__label {
	font-size: 20rpx;
	color: $muted;
}

.rp-point__tag {
	font-size: 20rpx;
	font-weight: 700;
	color: $accent;
	background: rgba(24, 82, 224, 0.1);
	border-radius: $radius-pill;
	padding: 8rpx 20rpx;
}

.rp-point__text {
	font-size: 25rpx;
	color: $ink-2;
	line-height: 1.8;
}
</style>
