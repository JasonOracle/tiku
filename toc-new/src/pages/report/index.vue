<template>
	<view class="report-apple">
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
			<!-- 态 A：即时出分态（深空夜蓝微光渐变看板） -->
			<view v-if="!isAuditing" class="rp-score">
				<view class="rp-score-glow" />
				<view class="rp-ring">
					<wd-circle
						:model-value="scorePercent"
						:size="190"
						:stroke-width="12"
						color="#FFFFFF"
						layer-color="rgba(255, 255, 255, 0.22)"
						:speed="60"
					/>
					<view class="rp-ring-center">
						<text class="rp-score-value">{{ displayScore }}</text>
						<text class="rp-score-total">满分 {{ paperTotal }} 分</text>
					</view>
				</view>

				<view class="rp-pills">
					<view class="rp-pill" :class="record.passed ? 'rp-pill--pass' : 'rp-pill--fail'">
						<svg v-if="record.passed" width="12" height="12" viewBox="0 0 24 24" fill="none">
							<polyline points="20 6 9 17 4 12" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
						<text class="rp-pill-text">{{ record.passed ? "及格" : "未及格" }}</text>
					</view>
					<text class="rp-meta">答题用时 {{ timeSpentText }}</text>
				</view>
			</view>

			<!-- 态 B：安全审核态（防泄题插画） -->
			<view v-else class="rp-audit">
				<svg class="rp-audit-art" viewBox="0 0 160 160" fill="none">
					<rect x="34" y="26" width="72" height="94" rx="14" stroke="#CBD5E1" stroke-width="2.5" />
					<path d="M50 54h40M50 70h40M50 86h24" stroke="#E2E8F0" stroke-width="2.5" stroke-linecap="round" />
					<circle cx="112" cy="104" r="22" fill="#EFF6FF" stroke="#1852E0" stroke-width="2.5" />
					<path d="M112 94v10.5l7 4" stroke="#1852E0" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
				</svg>
				<text class="rp-audit-title">试卷已成功提交</text>
				<text class="rp-audit-desc">正在等待人工 / AI 批阅核验后公布成绩</text>
				<text class="rp-audit-tip">为防止考后私下对答案，核验期间不展示标准答案与解析</text>
			</view>

			<!-- 试卷信息条 -->
			<view class="rp-paper">
				<text class="rp-paper-title">{{ record.task_title }}</text>
				<text class="rp-paper-time">提交于 {{ formatDateTime(record.submit_time) }}</text>
				<text v-if="record.comments" class="rp-paper-comment">教师评语：{{ record.comments }}</text>
				<text v-if="record.ai_comments" class="rp-paper-comment">AI 评语：{{ record.ai_comments }}</text>
			</view>

			<!-- 逐题复盘 -->
			<block v-if="record.items.length">
				<view class="rp-section">
					<text class="rp-section-title">逐题复盘</text>
					<text class="rp-section-count">共 {{ record.items.length }} 题</text>
				</view>

				<view v-for="(item, index) in record.items" :key="item.resource_id ?? index" class="review-card-apple">
					<QuestionCard
						:question="toQuestion(item)"
						:model-value="answerToValue(item.user_answer)"
						:index="index"
						:total="record.items.length"
						:review-mode="!isAuditing"
						:correct-answer="!isAuditing ? item.correct_answer : null"
						readonly
					/>

					<!-- 防泄题红线：态 B 下「正确答案」与「解析」在 DOM 中物理不渲染（v-if） -->
					<view v-if="!isAuditing" class="review-card-apple__compare">
						<view class="review-answer-bar">
							<view class="review-badge" :class="`review-badge--${answerThemeClass(item)}`">
								<text class="review-badge__label">我的作答</text>
								<text class="review-badge__content">{{ answerText(item.user_answer) }}</text>
							</view>
							<view class="review-badge review-badge--standard">
								<text class="review-badge__label">标准答案</text>
								<text class="review-badge__content">{{ answerText(item.correct_answer) }}</text>
							</view>
						</view>

						<view v-if="item.explanation" class="review-card-apple__explain">
							<view class="review-card-apple__explain-header">
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
									<circle cx="12" cy="12" r="10" stroke="#1852E0" stroke-width="2"/>
									<path d="M12 16v-4M12 8h.01" stroke="#1852E0" stroke-width="2" stroke-linecap="round"/>
								</svg>
								<text class="review-card-apple__explain-title">答案解析</text>
							</view>
							<text class="review-card-apple__explain-text">{{ item.explanation }}</text>
						</view>
					</view>
					<view v-else class="review-card-apple__locked">
						<svg class="review-card-apple__locked-icon" viewBox="0 0 24 24" fill="none">
							<rect x="4.5" y="10.5" width="15" height="9.5" rx="2.2" stroke="currentColor" stroke-width="1.8" />
							<path d="M8 10.5V7.8a4 4 0 0 1 8 0v2.7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
						</svg>
						<text class="review-card-apple__locked-text">核验完成后公布正确答案与解析</text>
					</view>

					<view class="review-card-apple__foot">
						<text class="review-card-apple__score">本题 {{ item.eq_score }} 分</text>
						<view class="review-card-apple__fav" hover-class="review-card-apple__fav--pressed" @click="toggleFavorite(item)">
							<svg class="review-card-apple__star" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round">
								<path
									d="m12 3.6 2.6 5.3 5.8.85-4.2 4.1 1 5.75L12 16.9l-5.2 2.7 1-5.75-4.2-4.1 5.8-.85L12 3.6Z"
									:fill="isFavorited(item) ? '#1852E0' : 'none'"
								/>
							</svg>
							<text class="review-card-apple__fav-text">{{ isFavorited(item) ? "已收藏" : "收藏" }}</text>
						</view>
					</view>
				</view>
			</block>

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
 * 修改内容：[1. 全面升级成绩报告为 Apple 钛金微光风，采用深空微漫反射夜蓝看板与选项正误精准高亮; 2. 真实对接后端 GET /api/v1/member/task-records/{id}，严格保持态 A 出分与态 B 安全防泄题隔离]
 */
import { computed, ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import QuestionCard from "@/components/QuestionCard.vue";
import {
	addFavorite,
	fetchExamRecord,
	fetchFavorites,
	removeFavorite,
	type ExamQuestion,
	type ExamRecordDetail,
	type ExamRecordItem,
} from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";
import { formatDateTime } from "@/utils/format";

type PageStatus = "loading" | "ready" | "error";
type AnswerTheme = "right" | "wrong" | "neutral";

const toast = useGlobalToast();

const pageStatus = ref<PageStatus>("loading");
const record = ref<ExamRecordDetail | null>(null);
const recordId = ref(0);
const favoriteIds = ref<number[]>([]);
const favoritePending = ref(false);

const isAuditing = computed(() => Boolean(record.value?.pending));

const displayScore = computed(() => {
	if (!record.value || record.value.score === null) return 0;
	return Math.round(record.value.score);
});

const paperTotal = computed(() => {
	if (!record.value) return 100;
	return 100;
});

const scorePercent = computed(() => {
	if (paperTotal.value <= 0) return 0;
	return Math.min(100, Math.max(0, Math.round((displayScore.value / paperTotal.value) * 100)));
});

const timeSpentText = computed(() => {
	const minutes = record.value?.time_spent;
	if (typeof minutes !== "number" || minutes <= 0) return "不足 1 分钟";
	return `${minutes} 分钟`;
});

function toQuestion(item: ExamRecordItem): ExamQuestion {
	return {
		id: item.resource_id || 0,
		type: item.type || "single",
		title: item.content || "",
		content: item.content || "",
		options: item.options || [],
		score: item.eq_score || 0,
		category_id: null,
	};
}

function answerToValue(ans: unknown): string | string[] {
	if (Array.isArray(ans)) return ans.map(String);
	if (typeof ans === "string") return ans;
	if (typeof ans === "number" || typeof ans === "boolean") return String(ans);
	return "";
}

function answerText(ans: unknown): string {
	if (ans === undefined || ans === null || ans === "") return "未作答";
	if (Array.isArray(ans)) return ans.length ? ans.join("、") : "未作答";
	return String(ans);
}

function answerThemeClass(item: ExamRecordItem): AnswerTheme {
	const userAns = answerText(item.user_answer);
	const correctAns = answerText(item.correct_answer);
	if (!userAns || userAns === "未作答") return "neutral";
	return userAns === correctAns ? "right" : "wrong";
}

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
}

.rp-scroll {
	height: calc(100vh - 88rpx);
}

/* 深空微光看板 */
.rp-score {
	position: relative;
	margin: 20rpx 28rpx 0;
	padding: 40rpx 0 36rpx;
	border-radius: 28rpx;
	background: linear-gradient(145deg, #1852E0 0%, #0A3299 100%);
	box-shadow: 0 16rpx 40rpx rgba(10, 50, 153, 0.28);
	overflow: hidden;
}

.rp-score-glow {
	position: absolute;
	top: -60rpx;
	right: -40rpx;
	width: 220rpx;
	height: 220rpx;
	background: radial-gradient(circle, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0) 70%);
	border-radius: 50%;
	pointer-events: none;
}

.rp-ring {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	height: 190px;
}

.rp-ring-center {
	position: absolute;
	inset: 0;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.rp-score-value {
	font-size: 96rpx;
	font-weight: 800;
	line-height: 1;
	color: #ffffff;
	font-feature-settings: "tnum";
	letter-spacing: -1px;
}

.rp-score-total {
	margin-top: 10rpx;
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.75);
	font-weight: 500;
}

.rp-pills {
	display: flex;
	align-items: center;
	justify-content: center;
	margin-top: 28rpx;
}

.rp-pill {
	display: flex;
	align-items: center;
	gap: 6rpx;
	padding: 8rpx 24rpx;
	border-radius: 999rpx;

	&--pass {
		background: rgba(255, 255, 255, 0.2);
		backdrop-filter: blur(8px);
		border: 1px solid rgba(255, 255, 255, 0.3);
	}

	&--fail {
		background-color: $danger;
	}

	&-text {
		font-size: 24rpx;
		font-weight: 700;
		color: #ffffff;
	}
}

.rp-meta {
	margin-left: 20rpx;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.85);
}

/* 态 B 审核中 */
.rp-audit {
	display: flex;
	flex-direction: column;
	align-items: center;
	margin: 24rpx 28rpx 0;
	padding: 48rpx 40rpx;
	background: #ffffff;
	border-radius: $radius-card;
	box-shadow: $shadow-card;
	border: 1px solid $glass-border;

	&-art {
		width: 240rpx;
		height: 240rpx;
	}

	&-title {
		margin-top: 24rpx;
		font-size: 34rpx;
		font-weight: 800;
		color: $ink;
	}

	&-desc {
		margin-top: 12rpx;
		font-size: 26rpx;
		color: $muted;
	}

	&-tip {
		margin-top: 14rpx;
		font-size: 22rpx;
		color: $faint;
		text-align: center;
	}
}

.rp-paper {
	margin: 24rpx 28rpx 0;
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

.rp-section {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 36rpx 32rpx 16rpx;

	&-title {
		font-size: 32rpx;
		font-weight: 800;
		color: $ink;
	}

	&-count {
		font-size: 24rpx;
		color: $muted;
	}
}

.review-card-apple {
	margin: 0 28rpx 24rpx;
	background: #ffffff;
	border-radius: $radius-card;
	box-shadow: $shadow-card;
	border: 1px solid $line;
	overflow: hidden;

	&__compare {
		padding: 24rpx 30rpx;
		border-top: 1rpx solid $line;
	}

	&__explain {
		margin-top: 20rpx;
		padding: 20rpx 24rpx;
		border-radius: 14rpx;
		background-color: $surface-sunken;
		border: 1px dashed $line-strong;

		&-header {
			display: flex;
			align-items: center;
			gap: 8rpx;
		}

		&-title {
			font-size: 22rpx;
			font-weight: 600;
			color: $accent;
		}

		&-text {
			display: block;
			margin-top: 10rpx;
			font-size: 24rpx;
			line-height: 1.65;
			color: $ink-2;
		}
	}

	&__locked {
		display: flex;
		align-items: center;
		padding: 24rpx 32rpx;
		border-top: 1rpx solid $line;
		color: $faint;

		&-icon {
			width: 32rpx;
			height: 32rpx;
			margin-right: 12rpx;
		}

		&-text {
			font-size: 24rpx;
		}
	}

	&__foot {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 20rpx 32rpx;
		border-top: 1rpx solid $line;
	}

	&__score {
		font-size: 24rpx;
		color: $muted;
		font-weight: 500;
	}

	&__fav {
		display: flex;
		align-items: center;
		color: $muted;

		&--pressed {
			opacity: 0.7;
		}

		&-text {
			margin-left: 8rpx;
			font-size: 24rpx;
		}
	}

	&__star {
		width: 34rpx;
		height: 34rpx;
	}
}

.review-answer-bar {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.review-badge {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 16rpx 22rpx;
	border-radius: 14rpx;
	background: $surface-sunken;
	border: 1px solid $line;

	&__label {
		font-size: 22rpx;
		font-weight: 500;
		color: $muted;
	}

	&__content {
		font-size: 28rpx;
		font-weight: 800;
		color: $ink;
	}

	&--right {
		background: $ok-soft;
		border-color: rgba(52, 199, 89, 0.4);
		.review-badge__label { color: $ok; }
		.review-badge__content { color: $ok; }
	}

	&--wrong {
		background: $danger-soft;
		border-color: rgba(255, 59, 48, 0.4);
		.review-badge__label { color: $danger; }
		.review-badge__content { color: $danger; }
	}

	&--standard {
		background: $accent-soft;
		border-color: $accent-line;
		.review-badge__label { color: $accent; }
		.review-badge__content { color: $accent; }
	}
}

.rp-bottom-space {
	height: calc(48rpx + env(safe-area-inset-bottom));
}
</style>
