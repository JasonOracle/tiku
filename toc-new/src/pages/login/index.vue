<template>
	<view class="login">
		<!-- 极客蓝通顶渐变区：自屏幕顶端铺满，状态栏高度自适应 -->
		<view class="login__hero">
			<view v-if="statusBarHeight > 0" :style="{ height: `${statusBarHeight}px` }" />

			<view class="login__hero-body">
				<image class="login__logo" src="/static/icons/brand-logo.svg" mode="widthFix" />
				<text class="login__brand">智题库</text>
				<text class="login__slogan">企业测评与考试一体化平台</text>
			</view>
		</view>

		<!-- 登录卡片：负边距上浮，压住渐变区下沿 -->
		<view class="login__card">
			<text class="login__card-title">账号登录</text>

			<wd-form ref="formRef" :model="form" :rules="rules">
				<wd-form-item prop="phone" :label-width="'0px'">
					<wd-input
						v-model="form.phone"
						type="number"
						:maxlength="11"
						placeholder="请输入手机号"
						prefix-icon="phone"
						clearable
						no-border
					/>
				</wd-form-item>

				<wd-form-item prop="password" :label-width="'0px'">
					<wd-input
						v-model="form.password"
						placeholder="请输入密码"
						prefix-icon="lock-on"
						show-password
						no-border
					/>
				</wd-form-item>
			</wd-form>

			<view
				class="login__submit"
				:class="{ 'login__submit--busy': submitting }"
				hover-class="login__submit--active"
				@click="handleSubmit"
			>
				<wd-loading v-if="submitting" type="ring" color="#FFFFFF" size="34" />
				<text class="login__submit-text">{{ submitting ? "登录中" : "登 录" }}</text>
			</view>

			<text class="login__hint">企业成员由管理员统一录入手机号，无需注册</text>
		</view>

		<text class="login__footer">智题库 · 让每一次测评都有据可依</text>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Deepseek-V4.1-Flash 底层
 * 修改内容：[1. 由占位页重塑为真实登录页：极客蓝通顶渐变、品牌标识、表单校验、提交态与租户边界拦截; 2. 登录成功后写入 Pinia 持久化并 switchTab 进入首页]
 */
import { onMounted, reactive, ref } from "vue";
import type { FormInstance, FormRules } from "wot-design-uni/components/wd-form/types";
import GlobalToast from "@/components/GlobalToast.vue";
import { login } from "@/api/auth";
import { useGlobalToast } from "@/stores/toast";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const toast = useGlobalToast();

const form = reactive({
	phone: "",
	password: "",
});

/** FormItemRule 的 required 与 message 为必填字段，非必填规则也要显式声明 required: false */
const rules: FormRules = {
	phone: [
		{ required: true, message: "请输入手机号" },
		{ required: false, pattern: /^1[3-9]\d{9}$/, message: "手机号格式不正确" },
	],
	password: [
		{ required: true, message: "请输入密码" },
		{ required: false, pattern: /^.{6,20}$/, message: "密码长度为 6 到 20 位" },
	],
};

const formRef = ref<FormInstance>();
const submitting = ref(false);
const statusBarHeight = ref(0);

onMounted(() => {
	// H5 端无原生状态栏，该值为 0；App / 小程序端返回真实高度
	const systemInfo = uni.getSystemInfoSync();
	statusBarHeight.value = systemInfo.statusBarHeight ?? 0;
});

async function handleSubmit(): Promise<void> {
	// 提交中直接拦截，避免重复点击产生多次登录请求
	if (submitting.value) return;

	const result = await formRef.value?.validate();
	if (!result?.valid) return;

	submitting.value = true;
	try {
		const data = await login({ phone: form.phone.trim(), password: form.password });

		// 边界拦截：账号未归属任何企业空间时，请求会缺失 X-Tenant-Id 而全链路失败，
		// 因此必须在进入首页之前就挡住，不能把问题留到后续页面逐个报错
		if (!data.joined_tenants || data.joined_tenants.length === 0) {
			toast.error("当前账号未加入任何企业空间，请联系管理员录入");
			return;
		}

		userStore.setLogin({
			token: data.token,
			user: data.user,
			default_tenant_id: data.default_tenant_id,
			joined_tenants: data.joined_tenants,
		});

		toast.success("登录成功");
		// 首页是 tabBar 页面，必须使用 switchTab，它会同时关闭登录页等非 tab 页面
		uni.switchTab({ url: "/pages/index/index" });
	} catch (error) {
		// 登录接口关闭了自动提示，此处显式呈现后端返回的真实失败原因
		const message = error instanceof Error && error.message ? error.message : "登录失败，请稍后重试";
		toast.error(message);
	} finally {
		submitting.value = false;
	}
}
</script>

<style lang="scss" scoped>
.login {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	background-color: #f6f8fc;
}

.login__hero {
	background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
}

.login__hero-body {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 72rpx 48rpx 220rpx;
}

.login__logo {
	width: 132rpx;
	height: 132rpx;
}

.login__brand {
	margin-top: 28rpx;
	font-size: 52rpx;
	font-weight: 600;
	letter-spacing: 4rpx;
	color: #ffffff;
}

.login__slogan {
	margin-top: 14rpx;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.76);
}

.login__card {
	margin: -160rpx 32rpx 0;
	padding: 44rpx 36rpx 36rpx;
	background-color: #ffffff;
	border-radius: 32rpx;
	box-shadow: 0 12rpx 40rpx rgba(29, 99, 255, 0.12);
}

.login__card-title {
	display: block;
	margin-bottom: 12rpx;
	font-size: 34rpx;
	font-weight: 600;
	color: #1c2331;
}

/* 去掉表单项默认下边框，输入区交由卡片与输入框自身留白承担 */
.login__card :deep(.wd-form-item) {
	padding: 0;
	margin-bottom: 8rpx;
}

.login__card :deep(.wd-form-item__body) {
	padding: 0;
}

.login__submit {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 92rpx;
	margin-top: 40rpx;
	border-radius: 999rpx;
	background-image: linear-gradient(135deg, #1d63ff 0%, #0045d8 100%);
	box-shadow: 0 12rpx 28rpx rgba(29, 99, 255, 0.24);
	transition: transform 0.2s ease, opacity 0.2s ease;
}

.login__submit--active {
	transform: scale(0.97);
	opacity: 0.92;
}

.login__submit--busy {
	opacity: 0.72;
}

.login__submit-text {
	margin-left: 12rpx;
	font-size: 32rpx;
	font-weight: 600;
	letter-spacing: 4rpx;
	color: #ffffff;
}

.login__hint {
	display: block;
	margin-top: 28rpx;
	font-size: 22rpx;
	line-height: 1.6;
	text-align: center;
	color: #a8b2c4;
}

.login__footer {
	margin-top: auto;
	padding: 48rpx 0 56rpx;
	font-size: 22rpx;
	text-align: center;
	color: #a8b2c4;
}
</style>
