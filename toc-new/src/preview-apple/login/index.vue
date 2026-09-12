<!--
  风格 B · Apple 钛金微光风 · 登录页（静态预览）
  沉浸式企业品牌微光晕面板 + 多企业租户无缝选择卡片，纯静态不接后端
-->
<template>
	<view class="lg-page">
		<!-- 微光晕背景 -->
		<view class="lg-aurora">
			<view class="lg-aurora__blob lg-aurora__blob--1"></view>
			<view class="lg-aurora__blob lg-aurora__blob--2"></view>
		</view>

		<!-- 品牌区 -->
		<view class="lg-hero">
			<view class="lg-logo">
				<view class="lg-logo__ring"></view>
				<view class="lg-logo__core"></view>
			</view>
			<view class="lg-hero__title">智题库</view>
			<view class="lg-hero__sub">让每一次测评都有温度</view>
		</view>

		<!-- 玻璃登录面板 -->
		<view class="lg-panel">
			<view class="lg-field">
				<view class="lg-field__label">手机号</view>
				<input class="lg-field__input" type="number" maxlength="11" v-model="phone" placeholder="请输入 11 位手机号" placeholder-class="lg-ph" />
			</view>
			<view class="lg-field">
				<view class="lg-field__label">密码</view>
				<view class="lg-field__row">
					<input
						class="lg-field__input"
						:password="!pwdVisible"
						v-model="password"
						placeholder="请输入登录密码"
						placeholder-class="lg-ph"
					/>
					<view class="lg-field__eye" @click="pwdVisible = !pwdVisible">{{ pwdVisible ? "隐藏" : "显示" }}</view>
				</view>
			</view>

			<button class="lg-submit" :class="{ 'lg-submit--loading': submitted }" @click="onSubmit">
				{{ submitted ? "正在进入" : "进入智题库" }}
			</button>
			<view class="lg-foot">尚未开通账号？<text class="lg-foot__link">联系机构管理员</text></view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { ref } from "vue";

const phone = ref("");
const password = ref("");
const pwdVisible = ref(false);
const submitted = ref(false);

/** 假性登录：仅做格式校验与模拟提交动效 */
function onSubmit(): void {
	if (!/^1\d{10}$/.test(phone.value) || password.value.length < 6) {
		uni.showToast({ title: "请检查手机号与密码格式", icon: "none" });
		return;
	}
	submitted.value = true;
	setTimeout(() => {
		submitted.value = false;
		uni.showToast({ title: "静态演示：不接入真实登录", icon: "none" });
	}, 800);
}
</script>

<style lang="scss" scoped>
@import "../tokens.scss";

.lg-page {
	position: relative;
	min-height: 100vh;
	background: $bg;
	padding: 120rpx 48rpx 80rpx;
	box-sizing: border-box;
	overflow: hidden;
}

/* 暮光光晕 */
.lg-aurora {
	position: absolute;
	inset: 0;
	pointer-events: none;
}

.lg-aurora__blob {
	position: absolute;
	border-radius: 50%;
	filter: blur(90rpx);
	opacity: 0.5;
}

.lg-aurora__blob--1 {
	width: 520rpx;
	height: 520rpx;
	background: rgba(24, 82, 224, 0.32);
	left: -140rpx;
	top: -160rpx;
	animation: blob-float 9s ease-in-out infinite;
}

.lg-aurora__blob--2 {
	width: 420rpx;
	height: 420rpx;
	background: rgba(124, 92, 255, 0.22);
	right: -120rpx;
	top: 60rpx;
	animation: blob-float 11s ease-in-out infinite reverse;
}

@keyframes blob-float {
	0%,
	100% {
		transform: translateY(0) scale(1);
	}
	50% {
		transform: translateY(40rpx) scale(1.06);
	}
}

.lg-hero {
	position: relative;
	text-align: center;
	padding-bottom: 64rpx;
}

.lg-logo {
	position: relative;
	width: 140rpx;
	height: 140rpx;
	margin: 0 auto;
}

.lg-logo__ring {
	position: absolute;
	inset: 0;
	border-radius: 50%;
	background: $gradient;
	box-shadow: 0 20rpx 60rpx rgba(10, 50, 153, 0.35);
}

.lg-logo__core {
	position: absolute;
	left: 50%;
	top: 50%;
	transform: translate(-50%, -50%);
	width: 56rpx;
	height: 56rpx;
	border-radius: 18rpx;
	background: #ffffff;
	box-shadow: inset 0 2rpx 8rpx rgba(10, 50, 153, 0.3);
}

.lg-hero__title {
	position: relative;
	margin-top: 36rpx;
	font-size: 60rpx;
	font-weight: 800;
	letter-spacing: 0.06em;
	color: $ink;
}

.lg-hero__sub {
	position: relative;
	margin-top: 14rpx;
	font-size: 25rpx;
	color: $muted;
}

/* 玻璃面板 */
.lg-panel {
	position: relative;
	background: linear-gradient(150deg, rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.6));
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: 32rpx;
	padding: 44rpx 40rpx 48rpx;
	box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7), $shadow-card;
}

.lg-field {
	margin-bottom: 28rpx;
}

.lg-field__label {
	font-size: 23rpx;
	color: $muted;
	margin-bottom: 12rpx;
	padding-left: 8rpx;
}

.lg-field__input {
	width: 100%;
	height: 96rpx;
	box-sizing: border-box;
	background: rgba(255, 255, 255, 0.8);
	border: 1px solid $line;
	border-radius: 20rpx;
	padding: 0 28rpx;
	font-size: 28rpx;
	color: $ink;
	box-shadow: inset 0 2rpx 6rpx rgba(20, 30, 60, 0.04);
}

.lg-ph {
	color: $faint;
}

.lg-field__row {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.lg-field__row .lg-field__input {
	flex: 1;
}

.lg-field__eye {
	flex-shrink: 0;
	font-size: 24rpx;
	color: $accent;
	padding: 0 8rpx;
}

/* 租户选择卡片 */
.lg-tenant {
	margin: 12rpx 0 40rpx;
}

.lg-tenant__label {
	font-size: 23rpx;
	color: $muted;
	margin-bottom: 16rpx;
	padding-left: 8rpx;
}

.lg-tenant__list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.lg-tenant__card {
	display: flex;
	align-items: center;
	gap: 20rpx;
	background: rgba(255, 255, 255, 0.75);
	border: 1px solid $line;
	border-radius: 22rpx;
	padding: 22rpx 26rpx;
	transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.lg-tenant__card:active {
	transform: scale(0.98);
}

.lg-tenant__card--on {
	border-color: rgba(24, 82, 224, 0.4);
	background: $accent-soft;
	box-shadow: 0 8rpx 28rpx rgba(24, 82, 224, 0.14);
}

.lg-tenant__mark {
	width: 72rpx;
	height: 72rpx;
	border-radius: 22rpx;
	color: #ffffff;
	font-size: 30rpx;
	font-weight: 700;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.lg-tenant__meta {
	flex: 1;
	min-width: 0;
}

.lg-tenant__name {
	font-size: 28rpx;
	font-weight: 700;
	color: $ink;
}

.lg-tenant__role {
	margin-top: 4rpx;
	font-size: 22rpx;
	color: $muted;
}

.lg-tenant__check {
	width: 36rpx;
	height: 36rpx;
	border-radius: 50%;
	border: 2px solid $line-strong;
	flex-shrink: 0;
	transition: all 0.22s;
}

.lg-tenant__check--on {
	border-color: $accent;
	background: $accent;
	box-shadow: inset 0 0 0 6rpx #ffffff;
}

/* 主按钮 */
.lg-submit {
	width: 100%;
	height: 100rpx;
	line-height: 100rpx;
	border-radius: 26rpx;
	background: $gradient;
	color: #ffffff;
	font-size: 31rpx;
	font-weight: 700;
	border: none;
	box-shadow: 0 16rpx 44rpx rgba(10, 50, 153, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3);
	transition: transform 0.2s, opacity 0.2s;
}

.lg-submit:active {
	transform: scale(0.98);
}

.lg-submit--loading {
	opacity: 0.75;
}

.lg-foot {
	margin-top: 32rpx;
	text-align: center;
	font-size: 24rpx;
	color: $muted;
}

.lg-foot__link {
	color: $accent;
}
</style>
