<template>
	<view class="exam">
		<CustomHeader title="考场" show-back />

		<view class="exam__body">
			<!-- 手写矢量插画：作答纸与笔，呼应考场语义 -->
			<svg class="exam__art" viewBox="0 0 160 160" fill="none">
				<rect x="34" y="24" width="76" height="96" rx="14" stroke="#C9D4E8" stroke-width="3" />
				<path d="M50 52h44M50 68h44M50 84h26" stroke="#DCE4F2" stroke-width="3" stroke-linecap="round" />
				<path d="M112 96.5 138 70.5a6.4 6.4 0 0 1 9 9l-26 26-12.5 3.5L112 96.5Z" stroke="#1D63FF" stroke-width="3" stroke-linejoin="round" />
				<path d="M131 77.5 140 86.5" stroke="#1D63FF" stroke-width="3" stroke-linecap="round" />
			</svg>

			<text class="exam__title">考场将在下一阶段开放</text>
			<text class="exam__desc">作答流、倒计时与交卷能力正在开发中，当前已成功承接测评跳转</text>

			<view class="exam__panel">
				<view class="exam__row">
					<text class="exam__row-label">测评编号</text>
					<text class="exam__row-value">{{ taskId || "未携带" }}</text>
				</view>
				<view class="exam__row exam__row--last">
					<text class="exam__row-label">测评名称</text>
					<text class="exam__row-value">{{ taskTitle || "未携带" }}</text>
				</view>
			</view>

			<view class="exam__back" hover-class="exam__back--active" @click="handleBack">
				<text class="exam__back-text">返回测评列表</text>
			</view>

			<view class="exam__bottom-space" />
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import CustomHeader from "@/components/CustomHeader.vue";
import GlobalToast from "@/components/GlobalToast.vue";

const taskId = ref("");
const taskTitle = ref("");

/**
 * 承接首页卡片的跳转参数。
 * uni-app 在解析 navigateTo 的 URL 时已对查询串做过解码，此处直接取用即可，重复解码会破坏含 % 的文案。
 */
onLoad((query) => {
	const rawId = query?.task_id;
	if (typeof rawId === "string" || typeof rawId === "number") {
		taskId.value = String(rawId);
	}
	const rawTitle = query?.title;
	if (typeof rawTitle === "string") {
		taskTitle.value = rawTitle;
	}
});

function handleBack(): void {
	uni.navigateBack({ delta: 1 });
}
</script>

<style lang="scss" scoped>
.exam {
	min-height: 100vh;
	background-color: #f6f8fc;
}

.exam__body {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 0 32rpx;
}

.exam__art {
	display: block;
	width: 300rpx;
	height: 300rpx;
	margin-top: 90rpx;
}

.exam__title {
	margin-top: 28rpx;
	font-size: 34rpx;
	font-weight: 600;
	color: #1c2331;
}

.exam__desc {
	margin-top: 16rpx;
	padding: 0 40rpx;
	font-size: 24rpx;
	line-height: 1.7;
	text-align: center;
	color: #748094;
}

.exam__panel {
	width: 100%;
	margin-top: 48rpx;
	padding: 0 28rpx;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
}

.exam__row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	height: 96rpx;
	border-bottom: 1rpx solid #f0f3f9;
}

.exam__row--last {
	border-bottom: none;
}

.exam__row-label {
	font-size: 26rpx;
	color: #748094;
}

.exam__row-value {
	flex: 1;
	margin-left: 24rpx;
	font-size: 26rpx;
	font-weight: 600;
	text-align: right;
	color: #1c2331;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

.exam__back {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 100%;
	height: 92rpx;
	margin-top: 48rpx;
	border-radius: 999rpx;
	background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
	box-shadow: 0 12rpx 28rpx rgba(29, 99, 255, 0.24);
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.exam__back--active {
	transform: scale(0.97);
	opacity: 0.92;
}

.exam__back-text {
	font-size: 30rpx;
	font-weight: 600;
	color: #ffffff;
}

.exam__bottom-space {
	height: calc(56rpx + constant(safe-area-inset-bottom));
	height: calc(56rpx + env(safe-area-inset-bottom));
}
</style>
