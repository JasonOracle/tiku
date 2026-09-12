<template>
	<view class="page-state">
		<!-- 加载态：流光骨架卡，数量可配，默认三张 -->
		<block v-if="status === 'loading'">
			<view v-for="index in skeletonCount" :key="index" class="page-state__skeleton">
				<view class="page-state__skeleton-line page-state__skeleton-line--title" />
				<view class="page-state__skeleton-line page-state__skeleton-line--meta" />
				<view class="page-state__skeleton-line page-state__skeleton-line--short" />
			</view>
		</block>

		<!-- 空态 / 错误态 / 成功清空态：手绘矢量插画 + 文案 + 可选操作 -->
		<block v-else>
			<view class="page-state__art-wrap">
				<!-- 错误态 -->
				<svg v-if="status === 'error'" class="page-state__art" viewBox="0 0 120 120" fill="none">
					<circle cx="60" cy="56" r="30" stroke="#CBD5E1" stroke-width="2.5" />
					<path d="M60 42v18" stroke="#EF4444" stroke-width="3" stroke-linecap="round" />
					<circle cx="60" cy="68" r="2.5" fill="#EF4444" />
					<path d="M36 96h48" stroke="#E2E8F0" stroke-width="2.5" stroke-linecap="round" />
				</svg>

				<!-- 正向空态（如已完成所有测评任务） -->
				<svg v-else-if="variant === 'celebrate'" class="page-state__art" viewBox="0 0 120 120" fill="none">
					<circle cx="60" cy="58" r="34" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="2" />
					<path d="M46 58l10 10 18-18" stroke="#1D63FF" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" />
					<circle cx="32" cy="38" r="4" fill="#60A5FA" opacity="0.6" />
					<circle cx="88" cy="36" r="3" fill="#93C5FD" opacity="0.8" />
					<circle cx="92" cy="74" r="5" fill="#3B82F6" opacity="0.4" />
					<path d="M26 68l6 2M84 92l8-3" stroke="#CBD5E1" stroke-width="2" stroke-linecap="round" />
					<path d="M40 100h40" stroke="#E2E8F0" stroke-width="2" stroke-linecap="round" />
				</svg>

				<!-- 常规数据空态 -->
				<svg v-else class="page-state__art" viewBox="0 0 120 120" fill="none">
					<rect x="28" y="28" width="64" height="60" rx="14" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="2" />
					<path d="M42 46h36M42 58h22" stroke="#E2E8F0" stroke-width="2.5" stroke-linecap="round" />
					<circle cx="86" cy="82" r="14" fill="#EFF6FF" stroke="#1D63FF" stroke-width="2" />
					<path d="M82 82h8M86 78v8" stroke="#1D63FF" stroke-width="2" stroke-linecap="round" />
				</svg>
			</view>

			<text class="page-state__title">{{ resolvedTitle }}</text>
			<text class="page-state__desc">{{ resolvedDescription }}</text>

			<view v-if="actionText" class="page-state__action" :class="{ 'page-state__action--ghost': actionVariant === 'ghost' }" hover-class="page-state__action--active" @click="emit('action')">
				<text class="page-state__action-text">{{ actionText }}</text>
			</view>
		</block>
	</view>
</template>

<script setup lang="ts">
import { computed } from "vue";

type PageStateStatus = "loading" | "empty" | "error";
type PageStateVariant = "default" | "celebrate";
type ActionVariant = "primary" | "ghost";

const props = withDefaults(
	defineProps<{
		/** 当前状态：加载中 / 空数据 / 加载失败 */
		status: PageStateStatus;
		/** 插画视觉模式：default 普通空态 / celebrate 通关或完成庆祝态 */
		variant?: PageStateVariant;
		/** 按钮样式：primary 极客蓝实色 / ghost 幽灵按钮 */
		actionVariant?: ActionVariant;
		/** 空态与错误态的标题，缺省按状态取默认文案 */
		title?: string;
		/** 空态与错误态的补充说明 */
		description?: string;
		/** 操作按钮文案，留空则不渲染按钮 */
		actionText?: string;
		/** 加载态的骨架卡数量 */
		skeletonCount?: number;
	}>(),
	{
		variant: "default",
		actionVariant: "primary",
		title: "",
		description: "",
		actionText: "",
		skeletonCount: 3,
	}
);

const emit = defineEmits<{
	/** 点击操作按钮时触发，通常用于「重新加载」 */
	action: [];
}>();

const resolvedTitle = computed(() => {
	if (props.title) return props.title;
	return props.status === "error" ? "加载失败" : "暂无内容";
});

const resolvedDescription = computed(() => {
	if (props.description) return props.description;
	return props.status === "error" ? "网络异常或服务暂时不可用，请稍后重试" : "这里暂时还没有可展示的内容";
});
</script>

<style lang="scss" scoped>
.page-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 100%;
}

.page-state__skeleton {
	width: 100%;
	margin-bottom: 24rpx;
	padding: 36rpx 32rpx;
	background-color: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 20rpx rgba(29, 99, 255, 0.06);
}

.page-state__skeleton-line {
	border-radius: 12rpx;
	background-image: linear-gradient(90deg, #eef2f9 25%, #f8fafd 37%, #eef2f9 63%);
	background-size: 400% 100%;
	animation: page-state-shimmer 1.4s ease infinite;
}

.page-state__skeleton-line + .page-state__skeleton-line {
	margin-top: 20rpx;
}

.page-state__skeleton-line--title {
	width: 62%;
	height: 30rpx;
}

.page-state__skeleton-line--meta {
	width: 88%;
	height: 22rpx;
}

.page-state__skeleton-line--short {
	width: 40%;
	height: 22rpx;
}

@keyframes page-state-shimmer {
	0% {
		background-position: 200% 0;
	}
	100% {
		background-position: -200% 0;
	}
}

.page-state__art-wrap {
	margin-top: 80rpx;
}

.page-state__art {
	display: block;
	width: 240rpx;
	height: 240rpx;
}

.page-state__title {
	margin-top: 24rpx;
	font-size: 30rpx;
	font-weight: 600;
	color: #1c2331;
}

.page-state__desc {
	margin-top: 14rpx;
	padding: 0 60rpx;
	font-size: 24rpx;
	line-height: 1.6;
	text-align: center;
	color: #748094;
}

.page-state__action {
	margin-top: 40rpx;
	padding: 0 52rpx;
	height: 76rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	border-radius: 999rpx;
	background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
	box-shadow: 0 8rpx 24rpx rgba(29, 99, 255, 0.22);
	transition: transform 0.2s ease, opacity 0.2s ease;

	&--ghost {
		background-image: none;
		background-color: #FFFFFF;
		border: 1px solid #CBD5E1;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);

		.page-state__action-text {
			color: #475569;
			font-weight: 500;
		}
	}
}

.page-state__action--active {
	transform: scale(0.97);
	opacity: 0.92;
}

.page-state__action-text {
	font-size: 28rpx;
	font-weight: 600;
	color: #ffffff;
}
</style>
