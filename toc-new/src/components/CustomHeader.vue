<template>
	<view class="custom-header" :class="`custom-header--${variant}`">
		<!-- 状态栏占位：仅在设备真实存在状态栏高度时撑开（App / 小程序），H5 端为 0 不产生多余空白 -->
		<view v-if="statusBarHeight > 0" class="custom-header__status" :style="{ height: `${statusBarHeight}px` }" />

		<view class="custom-header__bar">
			<view class="custom-header__slot custom-header__slot--left">
				<slot name="left">
					<view
						v-if="showBack"
						class="custom-header__back"
						:style="{ color: iconColor }"
						hover-class="custom-header__back--active"
						@click="handleBack"
					>
						<!-- 返回箭头：纯矢量线条，stroke 取 currentColor，颜色由外层 style 统一控制 -->
						<svg class="custom-header__back-icon" viewBox="0 0 24 24" fill="none">
							<path
								d="M15 4.5 7.5 12 15 19.5"
								stroke="currentColor"
								stroke-width="2.2"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
					</view>
				</slot>
			</view>

			<view class="custom-header__center">
				<text class="custom-header__title" :style="{ color: titleColor }">{{ title }}</text>
				<text v-if="subtitle" class="custom-header__subtitle" :style="{ color: subtitleColor }">{{ subtitle }}</text>
			</view>

			<view class="custom-header__slot custom-header__slot--right">
				<slot name="right" />
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { computed, getCurrentInstance, onMounted, ref } from "vue";

type HeaderVariant = "solid" | "gradient" | "transparent";

const props = withDefaults(
	defineProps<{
		/** 标题文案 */
		title: string;
		/** 可选副标题，展示在标题正下方 */
		subtitle?: string;
		/** 是否展示返回键 */
		showBack?: boolean;
		/** 底色形态：白底 / 极客蓝渐变 / 透明（由页面自身背景决定） */
		variant?: HeaderVariant;
	}>(),
	{
		subtitle: "",
		showBack: false,
		variant: "solid",
	}
);

const emit = defineEmits<{
	/** 点击返回键时触发；父组件未监听时组件内部自动执行 uni.navigateBack */
	back: [];
}>();

/** 状态栏高度：H5 端返回 0，App / 小程序端返回真实像素值 */
const statusBarHeight = ref(0);

onMounted(() => {
	const systemInfo = uni.getSystemInfoSync();
	statusBarHeight.value = systemInfo.statusBarHeight ?? 0;
});

const instance = getCurrentInstance();
/** 父组件是否监听了 back 事件，用于决定是否执行默认返回行为 */
const hasBackHandler = computed(() => Boolean(instance?.vnode.props?.onBack));

const isLightText = computed(() => props.variant !== "solid");
const titleColor = computed(() => (isLightText.value ? "#FFFFFF" : "#1C2331"));
const subtitleColor = computed(() => (isLightText.value ? "rgba(255, 255, 255, 0.78)" : "#748094"));
const iconColor = computed(() => (isLightText.value ? "#FFFFFF" : "#1C2331"));

function handleBack(): void {
	emit("back");
	// 父组件没有自定义返回逻辑时，走最通用的返回上一页，避免点击无响应
	if (!hasBackHandler.value) {
		uni.navigateBack({ delta: 1 });
	}
}
</script>

<style lang="scss" scoped>
.custom-header {
	position: relative;
	width: 100%;

	&--solid {
		background-color: #ffffff;
		box-shadow: 0 2rpx 12rpx rgba(28, 35, 49, 0.04);
	}

	&--gradient {
		background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
	}

	&--transparent {
		background-color: transparent;
	}
}

.custom-header__bar {
	display: flex;
	align-items: center;
	height: 88rpx;
	padding: 0 24rpx;
}

.custom-header__slot {
	display: flex;
	align-items: center;
	min-width: 96rpx;

	&--right {
		justify-content: flex-end;
	}
}

.custom-header__back {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 60rpx;
	height: 60rpx;
	margin-left: -12rpx;
	border-radius: 50%;
	transition: background-color 0.2s ease;
}

.custom-header__back--active {
	background-color: rgba(255, 255, 255, 0.16);
}

.custom-header__back-icon {
	width: 42rpx;
	height: 42rpx;
}

.custom-header__center {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	overflow: hidden;
}

.custom-header__title {
	font-size: 34rpx;
	font-weight: 600;
	line-height: 1.2;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	max-width: 100%;
}

.custom-header__subtitle {
	margin-top: 4rpx;
	font-size: 22rpx;
	line-height: 1.2;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
	max-width: 100%;
}
</style>
