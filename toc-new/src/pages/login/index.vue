<template>
	<view class="login-page">
		<view class="login-blank">
			<text class="login-title">智题库</text>
			<text class="login-tip">登录界面将在下一阶段实现，当前仅保证路由可达</text>
		</view>

		<!-- 全局轻提示挂载点：401 拦截与业务错误提示都依赖它，每个页面都必须放置 -->
		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
import GlobalToast from "@/components/GlobalToast.vue";
</script>

<style scoped>
.login-page {
	min-height: 100vh;
	background-color: #f6f8fc;
	display: flex;
	align-items: center;
	justify-content: center;
}

.login-blank {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.login-title {
	font-size: 48rpx;
	font-weight: 600;
	color: #1d63ff;
}

.login-tip {
	margin-top: 24rpx;
	font-size: 26rpx;
	color: #748094;
}
</style>
