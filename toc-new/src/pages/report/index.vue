<template>
	<view class="report">
		<CustomHeader title="成绩报告" show-back variant="gradient" />

		<!--
			以「数据是否已取到」作为分支条件：v-else 分支里编译器可自动收窄 record 为非空，
			既避免到处判空，也无需使用类型断言。
		-->
		<view v-if="!record" class="report__state">
			<PageState
				:status="pageStatus === 'error' ? 'error' : 'loading'"
				:skeleton-count="2"
				action-text="重新加载"
				@action="loadRecord"
			/>
		</view>

		<scroll-view v-else class="report__scroll" scroll-y>
			<!-- 态 A：即时出分态（深邃极客微渐变 + 层次微光晕） -->
			<view v-if="!isAuditing" class="report__score">
				<view class="report__score-glow" />
				<view class="report__ring">
					<wd-circle
						:model-value="scorePercent"
						:size="200"
						:stroke-width="12"
						color="#FFFFFF"
						layer-color="rgba(255, 255, 255, 0.2)"
						:speed="60"
					/>
					<view class="report__ring-center">
						<text class="report__score-value">{{ displayScore }}</text>
						<text class="report__score-total">满分 {{ paperTotal }} 分</text>
					</view>
				</view>

				<view class="report__pills">
					<view class="report__pill" :class="record.passed ? 'report__pill--pass' : 'report__pill--fail'">
						<svg v-if="record.passed" width="12" height="12" viewBox="0 0 24 24" fill="none">
							<polyline points="20 6 9 17 4 12" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
						<text class="report__pill-text">{{ record.passed ? "及格" : "未及格" }}</text>
					</view>
					<text class="report__meta">答题用时 {{ timeSpentText }}</text>
				</view>
			</view>

			<!-- 态 B：安全审核态 -->
			<view v-else class="report__audit">
				<svg class="report__audit-art" viewBox="0 0 160 160" fill="none">
					<rect x="34" y="26" width="72" height="94" rx="14" stroke="#CBD5E1" stroke-width="2.5" />
					<path d="M50 54h40M50 70h40M50 86h24" stroke="#E2E8F0" stroke-width="2.5" stroke-linecap="round" />
					<circle cx="112" cy="104" r="22" fill="#EFF6FF" stroke="#1D63FF" stroke-width="2.5" />
					<path d="M112 94v10.5l7 4" stroke="#1D63FF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
				</svg>
				<text class="report__audit-title">试卷已成功提交</text>
				<text class="report__audit-desc">正在等待人工 / AI 批阅核验后公布成绩</text>
				<text class="report__audit-tip">为防止考后私下对答案，核验期间不展示标准答案与解析</text>
			</view>

			<!-- 试卷信息条 -->
			<view class="report__paper">
				<text class="report__paper-title">{{ record.task_title }}</text>
				<text class="report__paper-time">提交于 {{ formatDateTime(record.submit_time) }}</text>
				<text v-if="record.comments" class="report__paper-comment">评语：{{ record.comments }}</text>
				<text v-if="record.ai_comments" class="report__paper-comment">AI 评语：{{ record.ai_comments }}</text>
			</view>

			<!-- 逐题复盘 -->
			<block v-if="record.items.length">
				<view class="report__section">
					<text class="report__section-title">逐题复盘</text>
					<text class="report__section-count">共 {{ record.items.length }} 题</text>
				</view>

				<view v-for="(item, index) in record.items" :key="item.resource_id ?? index" class="review-card">
					<QuestionCard
						:question="toQuestion(item)"
						:model-value="answerToValue(item.user_answer)"
						:index="index"
						:total="record.items.length"
						:review-mode="!isAuditing"
						:correct-answer="!isAuditing ? item.correct_answer : null"
						readonly
					/>

					<!--
						防泄题红线：态 B 下「正确答案」与「解析」必须根本不渲染（v-if），
						绝不可用 CSS 隐藏——DOM 中残留即等于泄题。
					-->
					<view v-if="!isAuditing" class="review-card__compare">
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

						<view v-if="item.explanation" class="review-card__explain">
							<view class="review-card__explain-header">
								<svg width="12" height="12" viewBox="0 0 24 24" fill="none">
									<circle cx="12" cy="12" r="10" stroke="#1D63FF" stroke-width="2"/>
									<path d="M12 16v-4M12 8h.01" stroke="#1D63FF" stroke-width="2" stroke-linecap="round"/>
								</svg>
								<text class="review-card__explain-title">答案解析</text>
							</view>
							<text class="review-card__explain-text">{{ item.explanation }}</text>
						</view>
					</view>
					<view v-else class="review-card__locked">
						<svg class="review-card__locked-icon" viewBox="0 0 24 24" fill="none">
							<rect x="4.5" y="10.5" width="15" height="9.5" rx="2.2" stroke="currentColor" stroke-width="1.8" />
							<path d="M8 10.5V7.8a4 4 0 0 1 8 0v2.7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
						</svg>
						<text class="review-card__locked-text">核验完成后公布正确答案与解析</text>
					</view>

					<view class="review-card__foot">
						<text class="review-card__score">本题 {{ item.eq_score }} 分</text>
						<view class="review-card__fav" hover-class="review-card__fav--pressed" @click="toggleFavorite(item)">
							<svg class="review-card__star" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round">
								<path
									d="m12 3.6 2.6 5.3 5.8.85-4.2 4.1 1 5.75L12 16.9l-5.2 2.7 1-5.75-4.2-4.1 5.8-.85L12 3.6Z"
									:fill="isFavorited(item) ? '#1D63FF' : 'none'"
								/>
							</svg>
							<text class="review-card__fav-text">{{ isFavorited(item) ? "已收藏" : "收藏" }}</text>
						</view>
					</view>
				</view>
			</block>

			<view class="report__bottom-space" />
		</scroll-view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
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
/** 单题答案的展示语义：正确 / 错误 / 主观题不判定 */
type AnswerTheme = "right" | "wrong" | "neutral";

const toast = useGlobalToast();

const pageStatus = ref<PageStatus>("loading");
const record = ref<ExamRecordDetail | null>(null);
const recordId = ref(0);
const favoriteIds = ref<number[]>([]);
const favoritePending = ref(false);

/**
 * 双态判定：全工程唯一判定点，只认后端算好的 pending 字段
 * （pending = status == "pending_verification"），不自行推断试卷是否含简答题。
 */
const isAuditing = computed(() => record.value?.pending === true);

const displayScore = computed(() => record.value?.score ?? 0);

/** 试卷总分：接口不返回，由各题实际分值求和得出 */
const paperTotal = computed(() => (record.value?.items ?? []).reduce((sum, item) => sum + (item.eq_score || 0), 0));

const scorePercent = computed(() => {
  if (paperTotal.value <= 0) return 0;
  return Math.round((displayScore.value / paperTotal.value) * 100);
});

const timeSpentText = computed(() => {
  const seconds = record.value?.time_spent ?? 0;
  if (seconds <= 0) return "--";
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return rest > 0 ? `${minutes} 分 ${rest} 秒` : `${minutes} 分钟`;
});

onLoad((query) => {
  const rawId = query?.record_id;
  recordId.value = Number(rawId) || 0;
  loadRecord();
});

async function loadRecord(): Promise<void> {
  if (!recordId.value) {
    pageStatus.value = "error";
    return;
  }
  pageStatus.value = "loading";
  try {
    record.value = await fetchExamRecord(recordId.value);
    pageStatus.value = "ready";
    // 仅出分态需要展示复盘卡片，收藏态也只在此态下有意义，故按需拉取一次收藏集合
    if (!isAuditing.value) {
      loadFavorites();
    }
  } catch {
    // 失败原因已由请求层统一轻提示，这里只负责切换到错误态
    pageStatus.value = "error";
  }
}

async function loadFavorites(): Promise<void> {
  try {
    const data = await fetchFavorites();
    favoriteIds.value = data.items.map((item) => item.resource_id);
  } catch {
    // 收藏集合拉取失败不阻断成绩复盘，保持为空集即可，用户仍可继续尝试收藏
    favoriteIds.value = [];
  }
}

/** 把复命题条目映射为 QuestionCard 需要的题目结构，复用其选项归一化与题型兼容能力 */
function toQuestion(item: ExamRecordItem): ExamQuestion {
  return {
    id: item.resource_id ?? 0,
    type: item.type ?? "",
    title: item.content,
    content: item.content,
    options: item.options ?? [],
    score: item.eq_score || 0,
    category_id: null,
  };
}

/** 只读回显：把历史答案还原成 QuestionCard 可渲染的值 */
function answerToValue(value: string | string[] | null): string | string[] {
  if (Array.isArray(value)) return value.map((item) => String(item));
  return value ?? "";
}

function answerText(value: string | string[] | null): string {
  if (value === null || value === undefined) return "未作答";
  if (Array.isArray(value)) {
    return value.length ? value.map((item) => String(item)).join("、") : "未作答";
  }
  return String(value).trim() ? String(value) : "未作答";
}

/** 统一归一化后比对，避免大小写与数组/字符串差异造成误判 */
function normalizeAnswer(value: string | string[] | null): string[] {
  if (value === null || value === undefined) return [];
  const list = Array.isArray(value) ? value : [value];
  return list.map((item) => String(item).trim().toUpperCase()).filter((item) => item !== "");
}

/** 简答题与主观题不参与自动评分，不做对错判定，避免误导 */
function isObjective(item: ExamRecordItem): boolean {
  const type = item.type ?? "";
  return type !== "short_answer" && type !== "short";
}

function answerTheme(item: ExamRecordItem): AnswerTheme {
  if (!isObjective(item)) return "neutral";
  const user = normalizeAnswer(item.user_answer);
  const correct = normalizeAnswer(item.correct_answer);
  if (user.length === 0) return "wrong";
  if (user.length !== correct.length) return "wrong";
  return user.every((value) => correct.includes(value)) ? "right" : "wrong";
}

function answerThemeClass(item: ExamRecordItem): Record<string, boolean> {
  const theme = answerTheme(item);
  return {
    "review-row__value--right": theme === "right",
    "review-row__value--wrong": theme === "wrong",
    "review-row__value--neutral": theme === "neutral",
  };
}

function isFavorited(item: ExamRecordItem): boolean {
  if (item.resource_id === null || item.resource_id === undefined) return false;
  return favoriteIds.value.includes(item.resource_id);
}

async function toggleFavorite(item: ExamRecordItem): Promise<void> {
  const resourceId = item.resource_id;
  if (resourceId === null || resourceId === undefined) return;
  // 处理中直接拦截，避免连点产生重复请求
  if (favoritePending.value) return;

  favoritePending.value = true;
  try {
    if (isFavorited(item)) {
      await removeFavorite(resourceId);
      favoriteIds.value = favoriteIds.value.filter((id) => id !== resourceId);
      toast.success("已取消收藏");
    } else {
      await addFavorite(resourceId);
      favoriteIds.value = [...favoriteIds.value, resourceId];
      toast.success("已加入我的收藏");
    }
  } catch (error) {
    const message = error instanceof Error && error.message ? error.message : "操作失败，请稍后重试";
    toast.error(message);
  } finally {
    favoritePending.value = false;
  }
}
</script>

<style lang="scss" scoped>
.report {
	display: flex;
	flex-direction: column;
	height: 100vh;
	overflow: hidden;
	background-color: #f6f8fc;
}

.report__state {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0 32rpx;
}

.report__scroll {
	flex: 1;
	min-height: 0;
}

/* 态 A：环形得分区 */
.report__score {
	position: relative;
	margin: 20rpx 28rpx 0;
	padding: 40rpx 0 36rpx;
	border-radius: 28rpx;
	background: linear-gradient(145deg, #1852E0 0%, #0A3299 100%);
	box-shadow: 0 16rpx 40rpx rgba(10, 50, 153, 0.28);
	overflow: hidden;
}

.report__score-glow {
	position: absolute;
	top: -60rpx;
	right: -40rpx;
	width: 220rpx;
	height: 220rpx;
	background: radial-gradient(circle, rgba(255, 255, 255, 0.25) 0%, rgba(255, 255, 255, 0) 70%);
	border-radius: 50%;
	pointer-events: none;
}

.report__ring {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	height: 200px;
}

.report__ring-center {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.report__score-value {
	font-size: 96rpx;
	font-weight: 800;
	line-height: 1;
	color: #ffffff;
	font-feature-settings: "tnum";
	letter-spacing: -1px;
}

.report__score-total {
	margin-top: 10rpx;
	font-size: 22rpx;
	color: rgba(255, 255, 255, 0.75);
	font-weight: 500;
}

.report__pills {
	display: flex;
	align-items: center;
	justify-content: center;
	margin-top: 28rpx;
}

.report__pill {
	display: flex;
	align-items: center;
	gap: 6rpx;
	padding: 8rpx 24rpx;
	border-radius: 999rpx;
}

.report__pill--pass {
	background: rgba(255, 255, 255, 0.2);
	backdrop-filter: blur(8px);
	border: 1px solid rgba(255, 255, 255, 0.3);
}

.report__pill--fail {
	background-color: #EF4444;
}

.report__pill-text {
	font-size: 24rpx;
	font-weight: 700;
	color: #ffffff;
}

.report__meta {
	margin-left: 20rpx;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.85);
}

/* 态 B：安全审核区 */
.report__audit {
	display: flex;
	flex-direction: column;
	align-items: center;
	margin: 24rpx 32rpx 0;
	padding: 48rpx 40rpx 44rpx;
	background-color: #ffffff;
	border-radius: 28rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
}

.report__audit-art {
	display: block;
	width: 260rpx;
	height: 260rpx;
}

.report__audit-title {
	margin-top: 26rpx;
	font-size: 34rpx;
	font-weight: 600;
	color: #1c2331;
}

.report__audit-desc {
	margin-top: 14rpx;
	font-size: 26rpx;
	line-height: 1.6;
	text-align: center;
	color: #748094;
}

.report__audit-tip {
	margin-top: 14rpx;
	font-size: 22rpx;
	line-height: 1.5;
	text-align: center;
	color: #a8b2c4;
}

/* 试卷信息条 */
.report__paper {
	margin: 24rpx 28rpx 0;
	padding: 32rpx;
	background-color: #ffffff;
	border-radius: 20rpx;
	box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.04);
	border: 1px solid rgba(226, 232, 240, 0.6);
}

.report__paper-title {
	display: block;
	font-size: 32rpx;
	font-weight: 700;
	color: #0F172A;
}

.report__paper-time {
	display: block;
	margin-top: 12rpx;
	font-size: 24rpx;
	color: #94A3B8;
}

.report__paper-comment {
	display: block;
	margin-top: 16rpx;
	font-size: 24rpx;
	line-height: 1.6;
	color: #64748B;
}

.report__section {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	padding: 36rpx 32rpx 20rpx;
}

.report__section-title {
	font-size: 30rpx;
	font-weight: 700;
	color: #0F172A;
}

.report__section-count {
	font-size: 24rpx;
	color: #94A3B8;
}

/* 逐题复盘卡片 */
.review-card {
	margin: 0 28rpx 24rpx;
	background-color: #ffffff;
	border-radius: 20rpx;
	box-shadow: 0 4rpx 16rpx rgba(15, 23, 42, 0.04);
	border: 1px solid rgba(226, 232, 240, 0.6);
	overflow: hidden;
}

.review-card .question-card {
	box-shadow: none;
	border-radius: 0;
}

.review-card__compare {
	padding: 24rpx 30rpx;
	border-top: 1rpx solid #F1F5F9;
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
	background: #F8FAFC;
	border: 1px solid #E2E8F0;

	&__label {
		font-size: 22rpx;
		font-weight: 500;
		color: #64748B;
	}

	&__content {
		font-size: 28rpx;
		font-weight: 800;
		color: #0F172A;
	}

	&--right {
		background: #ECFDF5;
		border-color: #A7F3D0;
		.review-badge__label {
			color: #059669;
		}
		.review-badge__content {
			color: #047857;
		}
	}

	&--wrong {
		background: #FEF2F2;
		border-color: #FECACA;
		.review-badge__label {
			color: #DC2626;
		}
		.review-badge__content {
			color: #B91C1C;
		}
	}

	&--standard {
		background: #EFF6FF;
		border-color: #BFDBFE;
		.review-badge__label {
			color: #1D63FF;
		}
		.review-badge__content {
			color: #1D4ED8;
		}
	}
}

.review-card__explain {
	margin-top: 20rpx;
	padding: 20rpx 24rpx;
	border-radius: 14rpx;
	background-color: #F8FAFC;
	border: 1px dashed #E2E8F0;
}

.review-card__explain-header {
	display: flex;
	align-items: center;
	gap: 8rpx;
}

.review-card__explain-title {
	font-size: 22rpx;
	font-weight: 600;
	color: #1D63FF;
}

.review-card__explain-text {
	display: block;
	margin-top: 10rpx;
	font-size: 24rpx;
	line-height: 1.65;
	color: #748094;
}

.review-card__locked {
	display: flex;
	align-items: center;
	padding: 24rpx 32rpx;
	border-top: 1rpx solid #f0f3f9;
	color: #a8b2c4;
}

.review-card__locked-icon {
	width: 32rpx;
	height: 32rpx;
	margin-right: 12rpx;
}

.review-card__locked-text {
	font-size: 24rpx;
	color: #a8b2c4;
}

.review-card__foot {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 20rpx 32rpx;
	border-top: 1rpx solid #f0f3f9;
}

.review-card__score {
	font-size: 24rpx;
	color: #a8b2c4;
}

.review-card__fav {
	display: flex;
	align-items: center;
	color: #748094;
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.review-card__fav--pressed {
	transform: scale(0.94);
	opacity: 0.85;
}

.review-card__star {
	width: 36rpx;
	height: 36rpx;
}

.review-card__fav-text {
	margin-left: 8rpx;
	font-size: 24rpx;
	color: #748094;
}

.report__bottom-space {
	height: calc(48rpx + constant(safe-area-inset-bottom));
	height: calc(48rpx + env(safe-area-inset-bottom));
}
</style>
