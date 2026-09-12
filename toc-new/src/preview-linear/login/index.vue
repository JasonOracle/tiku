<!--
  风格 A · Linear 极客冷灰风 · 登录页（静态预览）
  极简高冷登录面板：浮雕微阴影输入框、假性校验反馈与租户机构选择，纯静态不接后端
-->
<template>
	<view class="lg-page">
		<!-- 顶部品牌区：细网格线与电光蓝光斑 -->
		<view class="lg-hero">
			<view class="lg-hero__grid"></view>
			<view class="lg-hero__logo">
				<view class="lg-logo-mark">
					<view class="lg-logo-mark__bar"></view>
					<view class="lg-logo-mark__bar lg-logo-mark__bar--short"></view>
				</view>
			</view>
			<view class="lg-hero__title">智题库</view>
			<view class="lg-hero__sub">考试与测评 · 企业级数字化平台</view>
		</view>

		<!-- 登录面板 -->
		<view class="lg-panel">
			<view class="lg-field" :class="{ 'lg-field--error': phoneErr }">
				<view class="lg-field__label">手机号</view>
				<input class="lg-field__input" type="number" maxlength="11" v-model="phone" placeholder="请输入 11 位手机号" placeholder-class="lg-ph" />
			</view>
			<view class="lg-field__err" v-if="phoneErr">手机号格式不正确</view>

			<view class="lg-field" :class="{ 'lg-field--error': pwdErr }">
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
			<view class="lg-field__err" v-if="pwdErr">密码长度至少 6 位</view>

			<view class="lg-tenant">
				<view class="lg-tenant__label">选择机构</view>
				<view class="lg-tenant__opts">
					<view
						class="lg-tenant__item"
						:class="{ 'lg-tenant__item--on': tenantId === t.id }"
						v-for="t in tenants"
						:key="t.id"
						@click="tenantId = t.id"
					>
						{{ t.name }}
					</view>
				</view>
			</view>

			<button class="lg-submit" :class="{ 'lg-submit--loading': submitted }" @click="onSubmit">
				{{ submitted ? "登录中" : "登录" }}
			</button>
			<view class="lg-foot">尚未注册？<text class="lg-foot__link">联系企业管理员开通</text></view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { ref } from "vue";

const phone = ref("");
const password = ref("");
const pwdVisible = ref(false);
const phoneErr = ref(false);
const pwdErr = ref(false);
const submitted = ref(false);
const tenantId = ref(2);

/** 静态租户机构演示数据 */
const tenants = [
	{ id: 1, name: "星雅教育" },
	{ id: 2, name: "教务中心" },
	{ id: 3, name: "华东分部" },
];

/** 假性登录：仅做本地格式校验与 800ms 模拟提交动效 */
function onSubmit(): void {
	phoneErr.value = !/^1\d{10}$/.test(phone.value);
	pwdErr.value = password.value.length < 6;
	if (phoneErr.value || pwdErr.value) return;
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
	min-height: 100vh;
	background: $bg;
	padding: 96rpx 48rpx 80rpx;
	box-sizing: border-box;
}

.lg-hero {
	position: relative;
	padding: 40rpx 0 64rpx;
}

.lg-hero__grid {
	position: absolute;
	inset: -96rpx -48rpx auto;
	height: 360rpx;
	background-image: linear-gradient($line 1px, transparent 1px), linear-gradient(90deg, $line 1px, transparent 1px);
	background-size: 48rpx 48rpx;
	mask-image: linear-gradient(#000, transparent);
	-webkit-mask-image: linear-gradient(#000, transparent);
}

.lg-hero__logo {
	position: relative;
}

.lg-logo-mark {
	width: 96rpx;
	height: 96rpx;
	border-radius: 24rpx;
	background: $accent;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 10rpx;
	box-shadow: 0 12rpx 32rpx rgba(29, 99, 255, 0.35);
}

.lg-logo-mark__bar {
	width: 40rpx;
	height: 8rpx;
	border-radius: 4rpx;
	background: #ffffff;
}

.lg-logo-mark__bar--short {
	width: 24rpx;
}

.lg-hero__title {
	position: relative;
	margin-top: 32rpx;
	font-size: 56rpx;
	font-weight: 800;
	letter-spacing: 0.04em;
	color: $ink;
}

.lg-hero__sub {
	position: relative;
	margin-top: 12rpx;
	font-size: 24rpx;
	color: $muted;
	font-family: $mono;
}

.lg-panel {
	background: $surface;
	border: 1px solid $line;
	border-radius: $radius-card;
	padding: 40rpx 36rpx 48rpx;
	box-shadow: $shadow-card;
}

.lg-field {
	margin-bottom: 12rpx;
}

.lg-field--error .lg-field__input {
	border-color: $danger;
}

.lg-field__label {
	font-size: 22rpx;
	font-weight: 600;
	color: $muted;
	margin-bottom: 12rpx;
}

.lg-field__input {
	width: 100%;
	height: 88rpx;
	box-sizing: border-box;
	background: $surface-sunken;
	border: 1px solid $line;
	border-radius: $radius-inner;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: $ink;
	transition: border-color 0.2s, box-shadow 0.2s;
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

.lg-field__err {
	font-size: 22rpx;
	color: $danger;
	margin: 4rpx 4rpx 16rpx;
}

.lg-tenant {
	margin: 24rpx 0 40rpx;
}

.lg-tenant__label {
	font-size: 22rpx;
	font-weight: 600;
	color: $muted;
	margin-bottom: 12rpx;
}

.lg-tenant__opts {
	display: flex;
	gap: 16rpx;
}

.lg-tenant__item {
	flex: 1;
	text-align: center;
	font-size: 24rpx;
	color: $ink-2;
	padding: 18rpx 0;
	border-radius: $radius-inner;
	border: 1px solid $line;
	background: $surface-sunken;
	transition: all 0.2s;
}

.lg-tenant__item--on {
	border-color: $accent-line;
	background: $accent-soft;
	color: $accent;
	font-weight: 600;
}

.lg-submit {
	width: 100%;
	height: 96rpx;
	line-height: 96rpx;
	border-radius: $radius-inner;
	background: $accent;
	color: #ffffff;
	font-size: 30rpx;
	font-weight: 700;
	border: none;
	box-shadow: 0 8rpx 24rpx rgba(29, 99, 255, 0.3);
	transition: transform 0.2s, opacity 0.2s;
}

.lg-submit:active {
	transform: scale(0.98);
}

.lg-submit--loading {
	opacity: 0.72;
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
