<template>
	<view class="favorites-apple">
		<CustomHeader title="我的收藏" show-back />

		<PageState
			v-if="pageStatus !== 'ready'"
			:status="pageStatus === 'loading' ? 'loading' : 'error'"
			:skeleton-count="3"
			action-text="重新加载"
			@action="loadFavorites"
		/>

		<PageState
			v-else-if="items.length === 0"
			status="empty"
			title="暂无收藏的题目"
			description="在测试报告复盘时点击「收藏」，重点与错题便会沉淀在此处"
		/>

		<scroll-view v-else class="fv-scroll" scroll-y>
			<view v-for="item in items" :key="item.id" class="fv-card">
				<view class="fv-card__head">
					<view class="fv-card__type">
						<text class="fv-card__type-text">{{ typeLabel(item.type) }}</text>
					</view>

					<view
						class="fv-card__star"
						:class="{ 'fv-card__star--disabled': pendingId === item.id }"
						hover-class="fv-card__star--pressed"
						@click="handleRemove(item)"
					>
						<svg class="fv-card__star-icon" viewBox="0 0 24 24" fill="#1852E0" stroke="#1852E0" stroke-width="1.8" stroke-linejoin="round">
							<path d="m12 3.6 2.6 5.3 5.8.85-4.2 4.1 1 5.75L12 16.9l-5.2 2.7 1-5.75-4.2-4.1 5.8-.85L12 3.6Z" />
						</svg>
						<text class="fv-card__star-text">{{ pendingId === item.id ? "处理中" : "取消收藏" }}</text>
					</view>
				</view>

				<text class="fv-card__content">{{ item.content }}</text>

				<view v-if="item.options && item.options.length" class="fv-card__options">
					<view v-for="(option, index) in item.options" :key="index" class="fv-card__option-item">
						<text class="fv-card__option-text">{{ optionText(option) }}</text>
					</view>
				</view>
			</view>

			<view class="fv-bottom-space" />
		</scroll-view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 全面升级我的收藏页面为 Apple 钛金微光风，采用立体圆角题卡与拟物收藏徽标; 2. 真实对接后端 GET /api/v1/member/favorites 与 DELETE /api/v1/member/favorites/{id}]
 */
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchFavorites, removeFavorite, type FavoriteItem, type QuestionOption } from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";

type PageStatus = "loading" | "ready" | "error";

const toast = useGlobalToast();

const pageStatus = ref<PageStatus>("loading");
const items = ref<FavoriteItem[]>([]);
const pendingId = ref(0);

const TYPE_MAP: Record<string, string> = {
	single: "单选题",
	single_choice: "单选题",
	multiple: "多选题",
	multiple_choice: "多选题",
	judge: "判断题",
	true_false: "判断题",
	fill: "填空题",
	fill_in: "填空题",
	short: "简答题",
	short_answer: "简答题",
};

function typeLabel(type: string): string {
	return TYPE_MAP[type] || "测评试题";
}

function optionText(option: QuestionOption): string {
	if (typeof option === "object" && option !== null) {
		const key = option.key ? `${option.key}. ` : "";
		return `${key}${option.text ?? ""}`;
	}
	return String(option);
}

async function loadFavorites(): Promise<void> {
	pageStatus.value = "loading";
	try {
		const res = await fetchFavorites();
		items.value = res.items || [];
		pageStatus.value = "ready";
	} catch {
		pageStatus.value = "error";
	}
}

async function handleRemove(item: FavoriteItem): Promise<void> {
	if (pendingId.value === item.id) return;
	pendingId.value = item.id;

	try {
		await removeFavorite(item.resource_id);
		items.value = items.value.filter((target) => target.id !== item.id);
		toast.success("已取消收藏");
	} catch {
		toast.error("操作失败，请稍后重试");
	} finally {
		pendingId.value = 0;
	}
}

onShow(() => {
	loadFavorites();
});
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.favorites-apple {
	position: relative;
	min-height: 100vh;
	background: $bg;
}

.fv-scroll {
	height: calc(100vh - 88rpx);
	padding: 24rpx 32rpx 40rpx;
	box-sizing: border-box;
}

.fv-card {
	background: #ffffff;
	border-radius: $radius-card;
	padding: 32rpx;
	box-shadow: $shadow-card;
	border: 1px solid $line;
	margin-bottom: 24rpx;

	&__head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 20rpx;
	}

	&__type {
		background: $accent-soft;
		border-radius: 8rpx;
		padding: 4rpx 14rpx;
	}

	&__type-text {
		font-size: 22rpx;
		font-weight: 700;
		color: $accent;
	}

	&__star {
		display: flex;
		align-items: center;
		gap: 6rpx;
		padding: 6rpx 12rpx;

		&--disabled {
			opacity: 0.5;
			pointer-events: none;
		}

		&--pressed {
			opacity: 0.7;
		}
	}

	&__star-icon {
		width: 32rpx;
		height: 32rpx;
	}

	&__star-text {
		font-size: 22rpx;
		color: $muted;
	}

	&__content {
		display: block;
		font-size: 30rpx;
		font-weight: 700;
		color: $ink;
		line-height: 1.5;
		margin-bottom: 24rpx;
	}

	&__options {
		display: flex;
		flex-direction: column;
		gap: 12rpx;
		padding-top: 20rpx;
		border-top: 1px solid $line;
	}

	&__option-item {
		background: $surface-sunken;
		padding: 18rpx 22rpx;
		border-radius: 14rpx;
	}

	&__option-text {
		font-size: 24rpx;
		color: $ink-2;
		line-height: 1.4;
	}
}

.fv-bottom-space {
	height: calc(48rpx + env(safe-area-inset-bottom));
}
</style>
