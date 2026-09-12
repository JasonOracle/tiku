<template>
	<view class="report-apple">
		<!-- 沉浸式微质感导航栏 -->
		<CustomHeader title="成绩报告" show-back variant="gradient" />

		<view v-if="!record" class="rp-state">
			<PageState
				:status="pageStatus === 'error' ? 'error' : 'loading'"
				:skeleton-count="2"
				action-text="重新加载"
				@action="loadRecord"
			/>
		</view>

		<scroll-view v-else class="rp-scroll" scroll-y>
			<!-- 态 A：深空蓝出分夜空看板（微光漫反射） -->
			<view v-if="!isAuditing" class="rp-board">
				<view class="rp-board__glow rp-board__glow--1" />
				<view class="rp-board__glow rp-board__glow--2" />
				<view class="rp-board__main">
					<view class="rp-board__score">
						<text class="rp-board__num">{{ displayScore }}</text>
						<text class="rp-board__unit">/ {{ paperTotal }}</text>
					</view>
					<view class="rp-board__right">
						<view class="rp-grade-chip" :class="{ 'rp-grade-chip--fail': !record.passed }">
							{{ record.passed ? "及格 · 已核验" : "未及格 · 待努力" }}
						</view>
						<view class="rp-board__beat">{{ record.passed ? "恭喜顺利通过测评" : "继续加油，多看错题" }}</view>
					</view>
				</view>

				<view class="rp-metrics">
					<view class="rp-metric">
						<text class="rp-metric__num">{{ timeSpentText }}</text>
						<text class="rp-metric__label">用时</text>
					</view>
					<view class="rp-metric">
						<text class="rp-metric__num">{{ correctCount }}/{{ record.items.length }}</text>
						<text class="rp-metric__label">正确题数</text>
					</view>
					<view class="rp-metric">
						<text class="rp-metric__num">{{ accuracyPercent }}%</text>
						<text class="rp-metric__label">正确率</text>
					</view>
				</view>
			</view>

			<!-- 态 B：保密审核态（Apple 琉璃盾牌防泄题插画） -->
			<view v-else class="rp-secret">
				<view class="rp-secret__shield">
					<view class="rp-secret__lock" />
				</view>
				<view class="rp-secret__title">试卷已成功提交</view>
				<view class="rp-secret__sub">主客观题正在复核核验中，核验期间不公开标准答案与题目解析，防止考后私下对题</view>
				<view class="rp-secret__eta">状态：批阅核验中</view>
			</view>

			<!-- 试卷信息卡片 -->
			<view class="rp-paper">
				<text class="rp-paper-title">{{ record.task_title }}</text>
				<text class="rp-paper-time">提交于 {{ formatDateTime(record.submit_time) }}</text>
				<text v-if="record.comments" class="rp-paper-comment">教师评语：{{ record.comments }}</text>
				<text v-if="record.ai_comments" class="rp-paper-comment">AI 评语：{{ record.ai_comments }}</text>
			</view>

			<!-- 逐题复盘（100% 还原 Apple 钛金微光风卡片，含折叠、绿勾/红叉、考点解析） -->
			<view v-if="record.items.length" class="rp-review">
				<view class="rp-section">
					<text class="rp-section-title">逐题复盘</text>
					<text class="rp-section-count">共 {{ record.items.length }} 题</text>
				</view>

				<view
					v-for="(item, idx) in formattedItems"
					:key="item.resource_id ?? idx"
					class="rp-item"
				>
					<view class="rp-item__head" @click="toggleExpand(idx)">
						<view class="rp-item__left">
							<view class="rp-item__mark" :class="'rp-item__mark--' + item.status">
								{{ item.status === "ok" ? "✓" : "✕" }}
							</view>
							<view class="rp-item__info">
								<view class="rp-item__no">第 {{ idx + 1 }} 题 · {{ item.typeLabel }} · {{ item.eq_score }}分</view>
								<view class="rp-item__title">{{ item.title }}</view>
							</view>
						</view>
						<view class="rp-item__arrow" :class="{ 'rp-item__arrow--open': expandedIndices.has(idx) }">
							›
						</view>
					</view>

					<view v-if="expandedIndices.has(idx)" class="rp-item__body">
						<!-- 选择题选项渲染（绿勾 / 红叉 / 标准答案） -->
						<view v-if="item.renderedOptions.length" class="rp-options">
							<view
								v-for="o in item.renderedOptions"
								:key="o.key"
								class="rp-row"
								:class="'rp-row--' + o.state"
							>
								<view class="rp-row__key">{{ o.key }}</view>
								<view class="rp-row__text">{{ o.text }}</view>
								<view v-if="o.state === 'user-correct'" class="rp-row__tag">你的作答 ✓</view>
								<view v-else-if="o.state === 'user-wrong'" class="rp-row__tag">你的作答 ✕</view>
								<view v-else-if="o.state === 'correct'" class="rp-row__tag">标准答案</view>
							</view>
						</view>

						<!-- 填空题/主观题答案对比 -->
						<view v-else class="rp-text-answers">
							<view class="rp-answer-chip rp-answer-chip--user">
								<text class="rp-answer-chip__label">我的作答</text>
								<text class="rp-answer-chip__val">{{ answerText(item.user_answer) }}</text>
							</view>
							<view v-if="!isAuditing" class="rp-answer-chip rp-answer-chip--std">
								<text class="rp-answer-chip__label">标准答案</text>
								<text class="rp-answer-chip__val">{{ answerText(item.correct_answer) }}</text>
							</view>
						</view>

						<!-- 防泄题红线：态 B 审核态下隐藏解析，态 A 展示考点解析 -->
						<view v-if="!isAuditing && item.explanation" class="rp-point">
							<view class="rp-point__head">
								<view class="rp-point__label">考点解析</view>
								<view class="rp-point__tag">{{ item.typeLabel }}复盘</view>
							</view>
							<view class="rp-point__text">{{ item.explanation }}</view>
						</view>

						<view v-else-if="isAuditing" class="rp-locked-tip">
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" class="rp-locked-tip__icon">
								<rect x="4.5" y="10.5" width="15" height="9.5" rx="2.2" stroke="currentColor" stroke-width="1.8" />
								<path d="M8 10.5V7.8a4 4 0 0 1 8 0v2.7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
							</svg>
							<text>核验完成后公布正确答案与考点解析</text>
						</view>

						<!-- 底部操作条：收藏题目 -->
						<view class="rp-item__foot">
							<view
								class="rp-item__fav"
								:class="{ 'rp-item__fav--active': isFavorited(item) }"
								@click="toggleFavorite(item)"
							>
								<svg class="rp-item__star" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
									<path
										d="m12 3.6 2.6 5.3 5.8.85-4.2 4.1 1 5.75L12 16.9l-5.2 2.7 1-5.75-4.2-4.1 5.8-.85L12 3.6Z"
										:fill="isFavorited(item) ? '#1852E0' : 'none'"
									/>
								</svg>
								<text class="rp-item__fav-text">{{ isFavorited(item) ? "已加入错题/收藏本" : "收藏本题" }}</text>
							</view>
						</view>
					</view>
				</view>
			</view>

			<view class="rp-bottom-space" />
		</scroll-view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 完全采用与 preview-apple 一致的原生 Apple 钛金微光风设计语言：深空夜蓝看板 rp-board、双重漫反射光晕、折叠式逐题复盘卡片 rp-item、绿勾红叉状态徽标 rp-item__mark、选项行 rp-row、考点解析卡片 rp-point; 2. 移除外层 QuestionCard 冗余嵌套，消除旧版白底灰边普通样式; 3. 真实对接 GET /api/v1/member/task-records/{id}，严格保持安全防泄题逻辑]
 */
import { computed, reactive, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import {
	addFavorite,
	fetchExamRecord,
	fetchFavorites,
	removeFavorite,
	type ExamRecordDetail,
	type ExamRecordItem,
} from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";
import { formatDateTime } from "@/utils/format";

type PageStatus = "loading" | "ready" | "error";

const toast = useGlobalToast();

const pageStatus = ref<PageStatus>("loading");
const record = ref<ExamRecordDetail | null>(null);
const recordId = ref(0);
const favoriteIds = ref<number[]>([]);
const favoritePending = ref(false);

/** 默认展开第 1 题 */
const expandedIndices = reactive(new Set<number>([0]));

function toggleExpand(idx: number): void {
	if (expandedIndices.has(idx)) {
		expandedIndices.delete(idx);
	} else {
		expandedIndices.add(idx);
	}
}

const isAuditing = computed(() => Boolean(record.value?.pending));

const displayScore = computed(() => {
	if (!record.value || record.value.score === null) return 0;
	return Math.round(record.value.score);
});

const paperTotal = computed(() => {
	if (!record.value || !record.value.items.length) return 100;
	const total = record.value.items.reduce((sum, it) => sum + (it.eq_score || 0), 0);
	return total > 0 ? total : 100;
});

const timeSpentText = computed(() => {
	const minutes = record.value?.time_spent;
	if (typeof minutes !== "number" || minutes <= 0) return "不足 1 分";
	return `${minutes} 分钟`;
});

function answerText(ans: unknown): string {
	if (ans === undefined || ans === null || ans === "") return "未作答";
	if (Array.isArray(ans)) return ans.length ? ans.join("、") : "未作答";
	return String(ans);
}

function normalizeAnswers(ans: unknown): string[] {
	if (ans === undefined || ans === null || ans === "") return [];
	if (Array.isArray(ans)) return ans.map(String);
	return [String(ans)];
}

const typeLabelMap: Record<string, string> = {
	single: "单选题",
	single_choice: "单选题",
	multiple: "多选题",
	multiple_choice: "多选题",
	judge: "判断题",
	fill: "填空题",
	fill_in: "填空题",
	short: "简答题",
	short_answer: "简答题",
};

type OptionState = "user-correct" | "user-wrong" | "correct" | "plain";

const OPTION_PREFIX_PATTERN = /^([A-Z])[\.、\s\-\:：]+(.*)$/i;

function indexToLetter(idx: number): string {
	return String.fromCharCode(65 + (idx % 26));
}

function normalizeOptions(raw: unknown[] | undefined): { key: string; text: string }[] {
	if (!raw || !Array.isArray(raw)) return [];
	return raw.map((option, index) => {
		if (typeof option === "object" && option !== null) {
			const optObj = option as Record<string, unknown>;
			const key = String(optObj.key ?? "").trim().toUpperCase();
			return { key: key || indexToLetter(index), text: String(optObj.text ?? "").trim() };
		}
		const text = String(option ?? "").trim();
		const matched = text.match(OPTION_PREFIX_PATTERN);
		if (matched) return { key: matched[1].toUpperCase(), text: matched[2].trim() };
		return { key: indexToLetter(index), text };
	});
}

const formattedItems = computed(() => {
	if (!record.value) return [];
	return record.value.items.map((it) => {
		const userAnsList = normalizeAnswers(it.user_answer);
		const stdAnsList = normalizeAnswers(it.correct_answer);

		// 判断正误状态
		let isOk = false;
		if (userAnsList.length && stdAnsList.length) {
			const sortedUser = [...userAnsList].sort().join(",");
			const sortedStd = [...stdAnsList].sort().join(",");
			isOk = sortedUser === sortedStd;
		}

		// 处理选项列表状态
		const normalizedOpts = normalizeOptions(it.options);
		const renderedOptions = normalizedOpts.map((opt) => {
			const isUserPick = userAnsList.includes(opt.key);
			const isStd = !isAuditing.value && stdAnsList.includes(opt.key);

			let state: OptionState = "plain";
			if (isUserPick && isStd) {
				state = "user-correct";
			} else if (isUserPick && !isStd) {
				state = "user-wrong";
			} else if (!isUserPick && isStd) {
				state = "correct";
			}

			return {
				key: opt.key,
				text: opt.text,
				state,
			};
		});

		const rawType = String(it.type || "single").toLowerCase();
		const typeLabel = typeLabelMap[rawType] || "题目";

		return {
			...it,
			title: it.content,
			typeLabel,
			status: (isOk ? "ok" : "wrong") as "ok" | "wrong",
			renderedOptions,
		};
	});
});

const correctCount = computed(() => {
	return formattedItems.value.filter((it) => it.status === "ok").length;
});

const accuracyPercent = computed(() => {
	if (!formattedItems.value.length) return 0;
	return Math.round((correctCount.value / formattedItems.value.length) * 100);
});

function isFavorited(item: ExamRecordItem): boolean {
	return item.resource_id !== null && favoriteIds.value.includes(item.resource_id);
}

async function toggleFavorite(item: ExamRecordItem): Promise<void> {
	if (favoritePending.value || !item.resource_id) return;
	favoritePending.value = true;
	const id = item.resource_id;
	const currentlyFavorited = isFavorited(item);

	try {
		if (currentlyFavorited) {
			await removeFavorite(id);
			favoriteIds.value = favoriteIds.value.filter((favId) => favId !== id);
			toast.success("已取消收藏");
		} else {
			await addFavorite(id);
			favoriteIds.value = [...favoriteIds.value, id];
			toast.success("已加入我的收藏");
		}
	} catch {
		toast.error("操作失败，请重试");
	} finally {
		favoritePending.value = false;
	}
}

async function loadRecord(): Promise<void> {
	if (recordId.value <= 0) {
		pageStatus.value = "error";
		return;
	}

	pageStatus.value = "loading";
	try {
		const [recData, favData] = await Promise.allSettled([
			fetchExamRecord(recordId.value),
			fetchFavorites(),
		]);

		if (recData.status === "fulfilled") {
			record.value = recData.value;
			pageStatus.value = "ready";
		} else {
			pageStatus.value = "error";
		}

		if (favData.status === "fulfilled") {
			favoriteIds.value = (favData.value.items || []).map((f) => f.resource_id);
		}
	} catch {
		pageStatus.value = "error";
	}
}

onLoad((query) => {
	if (query?.record_id) {
		recordId.value = Number(query.record_id);
		loadRecord();
	} else {
		pageStatus.value = "error";
	}
});
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.report-apple {
	position: relative;
	min-height: 100vh;
	background: $bg;
	padding-bottom: 60rpx;
	box-sizing: border-box;
}

.rp-scroll {
	height: calc(100vh - 88rpx);
}

/* 深空蓝夜空微光看板（100% 还原 Apple 风格） */
.rp-board {
	position: relative;
	margin: 24rpx 32rpx 0;
	background: linear-gradient(150deg, #14306e 0%, #0a3299 48%, #1852e0 100%);
	border-radius: 32rpx;
	padding: 44rpx 40rpx;
	box-shadow: 0 24rpx 72rpx rgba(10, 50, 153, 0.35);
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
	font-size: 110rpx;
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

	&--fail {
		color: #b91c1c;
		background: linear-gradient(150deg, #ffffff, #fee2e2);
	}
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
	color: rgba(255, 255, 255, 0.65);
}

/* 态 B 保密审核态 */
.rp-secret {
	margin: 28rpx 32rpx 0;
	background: linear-gradient(160deg, rgba(255, 255, 255, 0.9), rgba(238, 242, 253, 0.7));
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: 32rpx;
	padding: 64rpx 44rpx;
	text-align: center;
	box-shadow: $shadow-card;
}

.rp-secret__shield {
	position: relative;
	width: 136rpx;
	height: 158rpx;
	margin: 0 auto 36rpx;
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
	margin: 16rpx auto 0;
	font-size: 24rpx;
	color: $muted;
	line-height: 1.7;
	max-width: 520rpx;
}

.rp-secret__eta {
	display: inline-block;
	margin-top: 26rpx;
	font-size: 22rpx;
	color: #b26a00;
	background: $warn-soft;
	border-radius: $radius-pill;
	padding: 10rpx 28rpx;
	box-shadow: 0 4rpx 16rpx rgba(245, 166, 35, 0.2);
}

/* 试卷信息条 */
.rp-paper {
	margin: 24rpx 32rpx 0;
	padding: 32rpx;
	background: #ffffff;
	border-radius: $radius-card;
	box-shadow: $shadow-card;
	border: 1px solid $line;

	&-title {
		display: block;
		font-size: 32rpx;
		font-weight: 700;
		color: $ink;
	}

	&-time {
		display: block;
		margin-top: 10rpx;
		font-size: 22rpx;
		color: $muted;
	}

	&-comment {
		display: block;
		margin-top: 14rpx;
		font-size: 24rpx;
		line-height: 1.6;
		color: $ink-2;
	}
}

/* 逐题复盘区域 */
.rp-section {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 44rpx 32rpx 20rpx;

	&-title {
		font-size: 34rpx;
		font-weight: 800;
		color: $ink;
	}

	&-count {
		font-size: 24rpx;
		color: $muted;
	}
}

.rp-review {
	padding: 0;
}

.rp-item {
	background: $surface;
	border-radius: $radius-card;
	margin: 0 32rpx 24rpx;
	box-shadow: $shadow-card;
	border: 1px solid $line;
	overflow: hidden;
}

.rp-item__head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 30rpx 32rpx;
	cursor: pointer;
}

.rp-item__left {
	display: flex;
	align-items: center;
	gap: 22rpx;
	flex: 1;
	min-width: 0;
}

.rp-item__info {
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

	&--ok {
		color: #1e8e3e;
		background: $ok-soft;
		box-shadow: 0 6rpx 18rpx rgba(52, 199, 89, 0.25);
	}

	&--wrong {
		color: #d70015;
		background: $danger-soft;
		box-shadow: 0 6rpx 18rpx rgba(255, 59, 48, 0.22);
	}
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
	padding: 28rpx 32rpx 32rpx;
}

/* 选项行（Apple 钛金微光质感） */
.rp-options {
	margin-top: 8rpx;
}

.rp-row {
	display: flex;
	align-items: center;
	gap: 20rpx;
	border: 1px solid rgba(20, 30, 60, 0.06);
	background: rgba(20, 30, 60, 0.02);
	border-radius: 20rpx;
	padding: 20rpx 24rpx;
	margin-bottom: 16rpx;
	transition: all 0.25s;

	&--user-correct {
		border-color: rgba(52, 199, 89, 0.4);
		background: $ok-soft;
	}

	&--user-wrong {
		border-color: rgba(255, 59, 48, 0.4);
		background: $danger-soft;
	}

	&--correct {
		border-color: rgba(24, 82, 224, 0.35);
		background: $accent-soft;
	}
}

.rp-row__key {
	width: 46rpx;
	height: 46rpx;
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

/* 主观题文本对照 */
.rp-text-answers {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
	margin-top: 8rpx;
}

.rp-answer-chip {
	padding: 20rpx 24rpx;
	border-radius: 16rpx;
	border: 1px solid $line;

	&__label {
		display: block;
		font-size: 20rpx;
		color: $muted;
	}

	&__val {
		display: block;
		margin-top: 8rpx;
		font-size: 26rpx;
		font-weight: 600;
		color: $ink;
	}

	&--user {
		background: $surface-sunken;
	}

	&--std {
		background: $accent-soft;
		border-color: $accent-line;
		.rp-answer-chip__label { color: $accent; }
		.rp-answer-chip__val { color: $accent; }
	}
}

/* 考点解析卡片 */
.rp-point {
	margin-top: 24rpx;
	background: linear-gradient(160deg, #f2f5fd, #eef2fd);
	border-radius: 22rpx;
	padding: 26rpx 28rpx;

	&__head {
		display: flex;
		align-items: center;
		gap: 14rpx;
		margin-bottom: 14rpx;
	}

	&__label {
		font-size: 20rpx;
		color: $muted;
	}

	&__tag {
		font-size: 20rpx;
		font-weight: 700;
		color: $accent;
		background: rgba(24, 82, 224, 0.1);
		border-radius: $radius-pill;
		padding: 6rpx 18rpx;
	}

	&__text {
		font-size: 25rpx;
		color: $ink-2;
		line-height: 1.75;
	}
}

.rp-locked-tip {
	display: flex;
	align-items: center;
	gap: 10rpx;
	margin-top: 20rpx;
	padding: 20rpx 24rpx;
	border-radius: 16rpx;
	background: $surface-sunken;
	font-size: 22rpx;
	color: $faint;

	&__icon {
		flex-shrink: 0;
	}
}

/* 底部操作 */
.rp-item__foot {
	display: flex;
	align-items: center;
	justify-content: flex-end;
	margin-top: 24rpx;
	padding-top: 20rpx;
	border-top: 1px solid $line;
}

.rp-item__fav {
	display: flex;
	align-items: center;
	color: $muted;
	font-size: 22rpx;
	cursor: pointer;

	&--active {
		color: $accent;
	}
}

.rp-item__star {
	width: 32rpx;
	height: 32rpx;
	margin-right: 8rpx;
}

.rp-bottom-space {
	height: calc(56rpx + env(safe-area-inset-bottom));
}
</style>
