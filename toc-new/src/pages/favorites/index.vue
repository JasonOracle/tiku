<template>
	<view class="favorites">
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
			title="还没有收藏的题目"
			description="在成绩报告页的复盘卡片上点击「收藏」，重点题目会集中到这里"
		/>

		<scroll-view v-else class="favorites__scroll" scroll-y>
			<view v-for="item in items" :key="item.id" class="fav-card">
				<view class="fav-card__head">
					<view class="fav-card__type">
						<text class="fav-card__type-text">{{ typeLabel(item.type) }}</text>
					</view>

					<view
						class="fav-card__star"
						:class="{ 'fav-card__star--disabled': pendingId === item.id }"
						hover-class="fav-card__star--pressed"
						@click="handleRemove(item)"
					>
						<svg class="fav-card__star-icon" viewBox="0 0 24 24" fill="#1D63FF" stroke="#1D63FF" stroke-width="1.8" stroke-linejoin="round">
							<path d="m12 3.6 2.6 5.3 5.8.85-4.2 4.1 1 5.75L12 16.9l-5.2 2.7 1-5.75-4.2-4.1 5.8-.85L12 3.6Z" />
						</svg>
						<text class="fav-card__star-text">{{ pendingId === item.id ? "处理中" : "取消收藏" }}</text>
					</view>
				</view>

				<text class="fav-card__content">{{ item.content }}</text>

				<view v-if="item.options.length" class="fav-card__options">
					<text v-for="(option, index) in item.options" :key="index" class="fav-card__option">{{ optionText(option) }}</text>
				</view>
			</view>

			<view class="favorites__bottom-space" />
		</scroll-view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";
import PageState from "@/components/PageState.vue";
import { fetchFavorites, removeFavorite, type FavoriteItem, type QuestionOption } from "@/api/exam";
import { useGlobalToast } from "@/stores/toast";

type PageStatus = "loading" | "ready" | "error";

/** 题型中文标签，需与后端枚举别名保持一致（此处仅用于展示，不参与判分） */
const TYPE_LABELS: Record<string, string> = {
	single_choice: "单选",
	single: "单选",
	multiple_choice: "多选",
	multiple: "多选",
	judge: "判断",
	true_false: "判断",
	fill_in: "填空",
	fill: "填空",
	short_answer: "简答",
	short: "简答",
};

const toast = useGlobalToast();

const pageStatus = ref<PageStatus>("loading");
const items = ref<FavoriteItem[]>([]);
/** 正在处理取消收藏的条目 ID，用于置灰按钮并拦截重复点击 */
const pendingId = ref(0);

onShow(() => {
	// 从报告页返回时可能新增过收藏，每次展示都重新拉取，保证与实际数据一致
	loadFavorites();
});

async function loadFavorites(): Promise<void> {
	pageStatus.value = "loading";
	try {
		items.value = (await fetchFavorites()).items;
		pageStatus.value = "ready";
	} catch {
		// 失败原因已由请求层统一轻提示，这里只负责切换到错误态
		pageStatus.value = "error";
	}
}

function typeLabel(type: string): string {
	return TYPE_LABELS[type] ?? "题目";
}

/** 选项可能是对象或字符串，统一取展示文案 */
function optionText(option: QuestionOption): string {
	if (typeof option === "object" && option !== null) return String(option.text ?? "");
	return String(option ?? "");
}

function handleRemove(item: FavoriteItem): void {
	if (pendingId.value) return;
	uni.showModal({
		title: "取消收藏",
		content: "确定要从我的收藏中移除这道题吗？",
		confirmColor: "#1D63FF",
		success: (res) => {
			if (res.confirm) {
				confirmRemove(item);
			}
		},
	});
}

async function confirmRemove(item: FavoriteItem): Promise<void> {
	pendingId.value = item.id;
	try {
		await removeFavorite(item.resource_id);
		items.value = items.value.filter((row) => row.id !== item.id);
		toast.success("已取消收藏");
	} catch (error) {
		const message = error instanceof Error && error.message ? error.message : "取消收藏失败，请稍后重试";
		toast.error(message);
	} finally {
		pendingId.value = 0;
	}
}
</script>

<style lang="scss" scoped>
.favorites {
	display: flex;
	flex-direction: column;
	height: 100vh;
	overflow: hidden;
	background-color: #f6f8fc;
}

.favorites__scroll {
	flex: 1;
	min-height: 0;
	padding: 24rpx 32rpx 0;
}

.fav-card {
	padding: 28rpx 28rpx 30rpx;
	margin-bottom: 24rpx;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
}

.fav-card__head {
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.fav-card__type {
	padding: 6rpx 18rpx;
	border-radius: 999rpx;
	background-color: #e8f0ff;
}

.fav-card__type-text {
	font-size: 22rpx;
	font-weight: 600;
	color: #1d63ff;
}

.fav-card__star {
	display: flex;
	align-items: center;
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.fav-card__star--pressed {
	transform: scale(0.94);
	opacity: 0.85;
}

.fav-card__star--disabled {
	opacity: 0.5;
}

.fav-card__star-icon {
	width: 34rpx;
	height: 34rpx;
}

.fav-card__star-text {
	margin-left: 8rpx;
	font-size: 24rpx;
	color: #748094;
}

.fav-card__content {
	display: block;
	margin-top: 22rpx;
	font-size: 29rpx;
	font-weight: 600;
	line-height: 1.6;
	color: #1c2331;
}

.fav-card__options {
	margin-top: 20rpx;
	padding-top: 20rpx;
	border-top: 1rpx solid #f0f3f9;
}

.fav-card__option {
	display: block;
	margin-bottom: 12rpx;
	font-size: 25rpx;
	line-height: 1.55;
	color: #748094;
}

.favorites__bottom-space {
	height: calc(48rpx + constant(safe-area-inset-bottom));
	height: calc(48rpx + env(safe-area-inset-bottom));
}
</style>
