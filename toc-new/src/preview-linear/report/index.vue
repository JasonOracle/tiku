<!--
  风格 A · Linear 极客冷灰风 · 成绩报告页（静态预览）
  仪表盘式数据矩阵看板 + 绿勾/红叉逐题复盘 + 考点展开卡片 + 防泄题保密态一键切换
-->
<template>
	<view class="rp-page">
		<!-- 顶部操作条：查看态 / 保密态 切换 -->
		<view class="rp-modebar">
			<view class="rp-modebar__inner">
				<text class="rp-modebar__label">{{ secretMode ? "保密审核态" : "成绩查看态" }}</text>
				<view class="rp-switch" :class="{ 'rp-switch--on': secretMode }" @click="secretMode = !secretMode">
					<view class="rp-switch__knob"></view>
				</view>
			</view>
			<view class="rp-modebar__sub">{{ secretMode ? "主观题核验完成前，答案与解析已锁定" : "客观题已批阅，可查看逐题复盘" }}</view>
		</view>

		<!-- 出分看板：数据矩阵 -->
		<view class="rp-board">
			<view class="rp-board__main">
				<view class="rp-board__score">
					<text class="rp-board__num">92</text>
					<text class="rp-board__unit">/ 100</text>
				</view>
				<view class="rp-board__grade">
					<view class="rp-grade-chip">优秀 · 已核验</view>
					<view class="rp-board__beat">击败 98% 考生</view>
				</view>
			</view>
			<view class="rp-metrics">
				<view class="rp-metric">
					<text class="rp-metric__num">18</text>
					<text class="rp-metric__label">用时(分)</text>
				</view>
				<view class="rp-metric">
					<text class="rp-metric__num">46/50</text>
					<text class="rp-metric__label">正确题数</text>
				</view>
				<view class="rp-metric">
					<text class="rp-metric__num">60</text>
					<text class="rp-metric__label">及格线</text>
				</view>
			</view>
		</view>

		<!-- 保密态插画 -->
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
					<!-- 考点解析 -->
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

		<PreviewFloat current="preview-linear/report/index" />
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
	padding-bottom: 64rpx;
}

/* 保密态切换条 */
.rp-modebar {
	background: $surface;
	border-bottom: 1px solid $line;
	padding: 24rpx 40rpx;
}

.rp-modebar__inner {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.rp-modebar__label {
	font-size: 27rpx;
	font-weight: 700;
	color: $ink;
}

.rp-modebar__sub {
	margin-top: 8rpx;
	font-size: 22rpx;
	color: $muted;
}

.rp-switch {
	width: 88rpx;
	height: 48rpx;
	border-radius: $radius-pill;
	background: $line-strong;
	padding: 4rpx;
	box-sizing: border-box;
	transition: background 0.25s;
}

.rp-switch--on {
	background: $accent;
}

.rp-switch__knob {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: #ffffff;
	box-shadow: 0 2rpx 8rpx rgba(15, 23, 42, 0.2);
	transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.rp-switch--on .rp-switch__knob {
	transform: translateX(40rpx);
}

/* 出分看板 */
.rp-board {
	margin: 24rpx 40rpx 0;
	background: $ink;
	border-radius: $radius-card;
	padding: 40rpx 36rpx;
	box-shadow: $shadow-float;
}

.rp-board__main {
	display: flex;
	align-items: flex-end;
	justify-content: space-between;
}

.rp-board__num {
	font-size: 108rpx;
	font-weight: 800;
	color: #ffffff;
	font-family: $mono;
	letter-spacing: -0.03em;
	line-height: 1;
}

.rp-board__unit {
	font-size: 26rpx;
	color: #64748b;
	margin-left: 12rpx;
}

.rp-grade-chip {
	display: inline-block;
	font-size: 22rpx;
	font-weight: 600;
	color: #047857;
	background: #d1fae5;
	border-radius: 8rpx;
	padding: 8rpx 18rpx;
}

.rp-board__beat {
	margin-top: 12rpx;
	font-size: 22rpx;
	color: #93b4ff;
	font-family: $mono;
}

.rp-metrics {
	display: flex;
	margin-top: 36rpx;
	border-top: 1px solid rgba(148, 163, 184, 0.18);
	padding-top: 28rpx;
}

.rp-metric {
	flex: 1;
	text-align: center;
}

.rp-metric__num {
	display: block;
	font-size: 32rpx;
	font-weight: 700;
	color: #e2e8f0;
	font-family: $mono;
}

.rp-metric__label {
	display: block;
	margin-top: 8rpx;
	font-size: 20rpx;
	color: #64748b;
}

/* 保密态插画 */
.rp-secret {
	margin: 48rpx 40rpx 0;
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 72rpx 48rpx;
	text-align: center;
	box-shadow: $shadow-card;
}

.rp-secret__shield {
	width: 128rpx;
	height: 150rpx;
	margin: 0 auto 36rpx;
	background: linear-gradient(165deg, #1e293b, #0f172a);
	clip-path: polygon(50% 0, 100% 18%, 100% 62%, 50% 100%, 0 62%, 0 18%);
	position: relative;
	box-shadow: 0 16rpx 40rpx rgba(15, 23, 42, 0.25);
}

.rp-secret__lock {
	position: absolute;
	left: 50%;
	top: 58rpx;
	transform: translateX(-50%);
	width: 40rpx;
	height: 30rpx;
	border-radius: 8rpx;
	background: #fbbf24;
}

.rp-secret__lock::before {
	content: "";
	position: absolute;
	top: -18rpx;
	left: 50%;
	transform: translateX(-50%);
	width: 20rpx;
	height: 20rpx;
	border: 4rpx solid #fbbf24;
	border-bottom: none;
	border-radius: 10rpx 10rpx 0 0;
}

.rp-secret__title {
	font-size: 32rpx;
	font-weight: 800;
	color: $ink;
}

.rp-secret__sub {
	margin: 16rpx auto 0;
	font-size: 24rpx;
	color: $muted;
	line-height: 1.7;
	max-width: 480rpx;
}

.rp-secret__eta {
	display: inline-block;
	margin-top: 28rpx;
	font-size: 22rpx;
	color: $warn;
	background: $warn-soft;
	border-radius: 8rpx;
	padding: 10rpx 22rpx;
	font-family: $mono;
}

/* 逐题复盘 */
.rp-section {
	font-size: 30rpx;
	font-weight: 700;
	color: $ink;
	padding: 44rpx 40rpx 20rpx;
}

.rp-review {
	padding: 0 40rpx;
}

.rp-item {
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	margin-bottom: 24rpx;
	box-shadow: $shadow-card;
	overflow: hidden;
}

.rp-item__head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 28rpx 32rpx;
}

.rp-item__left {
	display: flex;
	align-items: center;
	gap: 20rpx;
	flex: 1;
	min-width: 0;
}

.rp-item__mark {
	width: 52rpx;
	height: 52rpx;
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 28rpx;
	font-weight: 800;
	flex-shrink: 0;
}

.rp-item__mark--ok {
	color: #047857;
	background: $ok-soft;
}

.rp-item__mark--wrong {
	color: $danger;
	background: $danger-soft;
}

.rp-item__no {
	font-size: 20rpx;
	color: $muted;
	font-family: $mono;
}

.rp-item__title {
	margin-top: 6rpx;
	font-size: 27rpx;
	font-weight: 600;
	color: $ink;
	line-height: 1.45;
}

.rp-item__arrow {
	font-size: 36rpx;
	color: $faint;
	transition: transform 0.25s;
}

.rp-item__arrow--open {
	transform: rotate(90deg);
}

.rp-item__body {
	border-top: 1px solid $line;
	padding: 28rpx 32rpx 32rpx;
}

/* 选项行：绿勾 / 红叉 / 标准答案 */
.rp-row {
	display: flex;
	align-items: center;
	gap: 18rpx;
	border: 1px solid $line;
	border-radius: $radius-inner;
	padding: 20rpx 24rpx;
	margin-bottom: 14rpx;
}

.rp-row--user-correct {
	border-color: rgba(16, 185, 129, 0.45);
	background: $ok-soft;
}

.rp-row--user-wrong {
	border-color: rgba(220, 38, 38, 0.45);
	background: $danger-soft;
}

.rp-row--correct {
	border-color: $accent-line;
	background: $accent-soft;
}

.rp-row__key {
	width: 44rpx;
	height: 44rpx;
	border-radius: 8rpx;
	background: $surface;
	border: 1px solid $line-strong;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24rpx;
	font-weight: 700;
	color: $ink-2;
	font-family: $mono;
	flex-shrink: 0;
}

.rp-row__text {
	flex: 1;
	font-size: 25rpx;
	color: $ink-2;
	line-height: 1.5;
}

.rp-row__tag {
	flex-shrink: 0;
	font-size: 20rpx;
	font-weight: 600;
	padding: 6rpx 14rpx;
	border-radius: 6rpx;
}

.rp-row--user-correct .rp-row__tag {
	color: #047857;
	background: rgba(16, 185, 129, 0.14);
}

.rp-row--user-wrong .rp-row__tag {
	color: #b91c1c;
	background: rgba(220, 38, 38, 0.12);
}

.rp-row--correct .rp-row__tag {
	color: $accent;
	background: rgba(29, 99, 255, 0.12);
}

/* 考点解析 */
.rp-point {
	margin-top: 24rpx;
	background: $surface-sunken;
	border-radius: $radius-inner;
	padding: 24rpx;
}

.rp-point__head {
	display: flex;
	align-items: center;
	gap: 14rpx;
	margin-bottom: 14rpx;
}

.rp-point__label {
	font-size: 20rpx;
	color: $muted;
}

.rp-point__tag {
	font-size: 20rpx;
	font-weight: 600;
	color: $accent;
	background: $accent-soft;
	border-radius: 6rpx;
	padding: 6rpx 14rpx;
}

.rp-point__text {
	font-size: 24rpx;
	color: $ink-2;
	line-height: 1.75;
}
</style>
