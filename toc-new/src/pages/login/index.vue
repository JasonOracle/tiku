<template>
	<view class="login-apple">
		<!-- 漫反射暮光背景 -->
		<view class="lg-aurora">
			<view class="lg-aurora__blob lg-aurora__blob--1" />
			<view class="lg-aurora__blob lg-aurora__blob--2" />
		</view>

		<!-- 品牌标识与标语 -->
		<view class="lg-hero">
			<view class="lg-logo">
				<view class="lg-logo__ring" />
				<view class="lg-logo__core" />
			</view>
			<text class="lg-hero__title">智题库</text>
			<text class="lg-hero__sub">让每一次测评都有温度与依据</text>
		</view>

		<!-- 钛金微光浮雕登录面板 -->
		<view class="lg-panel">
			<view class="lg-field">
				<text class="lg-field__label">手机号</text>
				<input
					class="lg-field__input"
					type="number"
					maxlength="11"
					v-model="form.phone"
					placeholder="请输入 11 位手机号"
					placeholder-class="lg-ph"
				/>
			</view>

			<view class="lg-field">
				<text class="lg-field__label">密码</text>
				<view class="lg-field__row">
					<input
						class="lg-field__input"
						:password="!pwdVisible"
						v-model="form.password"
						placeholder="请输入登录密码"
						placeholder-class="lg-ph"
					/>
					<view class="lg-field__eye" @click="pwdVisible = !pwdVisible">
						<text class="lg-field__eye-text">{{ pwdVisible ? "隐藏" : "显示" }}</text>
					</view>
				</view>
			</view>

			<view
				class="lg-submit"
				:class="{ 'lg-submit--loading': submitting }"
				hover-class="lg-submit--pressed"
				@click="handleSubmit"
			>
				<text class="lg-submit__text">{{ submitting ? "正在安全进入..." : "进入智题库" }}</text>
			</view>

			<view class="lg-foot">
				<text class="lg-foot__text">企业成员账号已由管理员配置，无需额外注册</text>
			</view>
		</view>

		<GlobalToast />
	</view>
</template>

<script setup lang="ts">
/**
 * [变更日志]
 * 修改时间：2026-09-12
 * AI模型：Gemini 系列
 * 修改内容：[1. 全面升级为 Apple 钛金微光风登录界面，去除多机构选择卡片，改为隐式无感知机构绑定; 2. 100% 接入真实后端 POST /api/v1/auth/login 鉴权闭环并注入 Pinia]
 */
import { reactive, ref } from "vue";
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

const pwdVisible = ref(false);
const submitting = ref(false);

async function handleSubmit(): Promise<void> {
	if (submitting.value) return;

	const phoneClean = form.phone.trim();
	if (!/^1[3-9]\d{9}$/.test(phoneClean)) {
		toast.error("请输入有效的 11 位手机号码");
		return;
	}
	if (form.password.length < 6) {
		toast.error("密码长度至少为 6 位");
		return;
	}

	submitting.value = true;
	try {
		const data = await login({ phone: phoneClean, password: form.password });

		// 边界拦截：账号未归属任何机构时阻断
		if (!data.joined_tenants || data.joined_tenants.length === 0) {
			toast.error("当前账号未加入任何机构空间，请联系管理员");
			return;
		}

		// 隐式绑定默认机构（优先取 default_tenant_id，无则取首个机构）
		userStore.setLogin({
			token: data.token,
			user: data.user,
			default_tenant_id: data.default_tenant_id || data.joined_tenants[0].tenant_id,
			joined_tenants: data.joined_tenants,
		});

		toast.success("登录成功");
		uni.switchTab({ url: "/pages/index/index" });
	} catch (error) {
		const message = error instanceof Error && error.message ? error.message : "登录失败，请核对账号密码";
		toast.error(message);
	} finally {
		submitting.value = false;
	}
}
</script>

<style lang="scss" scoped>
@import "@/styles/tokens-apple.scss";

.login-apple {
	position: relative;
	min-height: 100vh;
	background: $bg;
	padding: 120rpx 48rpx 80rpx;
	box-sizing: border-box;
	overflow: hidden;
}

/* 暮光微漫反射光晕 */
.lg-aurora {
	position: absolute;
	inset: 0;
	pointer-events: none;
	overflow: hidden;

	&__blob {
		position: absolute;
		border-radius: 50%;
		filter: blur(80px);
		opacity: 0.45;

		&--1 {
			width: 520rpx;
			height: 520rpx;
			top: -160rpx;
			left: -120rpx;
			background: radial-gradient(circle, rgba(24, 82, 224, 0.42), rgba(24, 82, 224, 0));
		}

		&--2 {
			width: 480rpx;
			height: 480rpx;
			top: 240rpx;
			right: -140rpx;
			background: radial-gradient(circle, rgba(124, 92, 255, 0.32), rgba(124, 92, 255, 0));
		}
	}
}

/* 品牌区 */
.lg-hero {
	position: relative;
	z-index: 2;
	display: flex;
	flex-direction: column;
	align-items: center;
	margin-bottom: 60rpx;

	&__title {
		font-size: 52rpx;
		font-weight: 800;
		color: $ink;
		letter-spacing: -0.5px;
	}

	&__sub {
		margin-top: 10rpx;
		font-size: 26rpx;
		color: $muted;
	}
}

.lg-logo {
	position: relative;
	width: 120rpx;
	height: 120rpx;
	margin-bottom: 24rpx;
	display: flex;
	align-items: center;
	justify-content: center;

	&__ring {
		position: absolute;
		inset: 0;
		border-radius: 36rpx;
		background: $gradient;
		box-shadow: 0 14rpx 40rpx rgba(24, 82, 224, 0.35);
	}

	&__core {
		position: relative;
		z-index: 1;
		width: 44rpx;
		height: 44rpx;
		border-radius: 12rpx;
		border: 4rpx solid #ffffff;
		background: rgba(255, 255, 255, 0.2);
	}
}

/* 登录面板卡片 */
.lg-panel {
	position: relative;
	z-index: 2;
	background: rgba(255, 255, 255, 0.88);
	backdrop-filter: $glass-blur;
	border: 1px solid $glass-border;
	border-radius: 36rpx;
	padding: 48rpx 40rpx;
	box-shadow: $shadow-card;
	display: flex;
	flex-direction: column;
	gap: 32rpx;
}

.lg-field {
	display: flex;
	flex-direction: column;
	gap: 12rpx;

	&__label {
		font-size: 24rpx;
		font-weight: 600;
		color: $ink-2;
	}

	&__input {
		height: 88rpx;
		background: $surface-sunken;
		border-radius: 20rpx;
		padding: 0 28rpx;
		font-size: 28rpx;
		color: $ink;
		border: 1px solid transparent;
		transition: all 0.2s ease;

		&:focus {
			background: #ffffff;
			border-color: $accent-line;
		}
	}

	&__row {
		display: flex;
		align-items: center;
		position: relative;

		.lg-field__input {
			flex: 1;
			padding-right: 90rpx;
		}
	}

	&__eye {
		position: absolute;
		right: 24rpx;
		padding: 10rpx;
		display: flex;
		align-items: center;
	}

	&__eye-text {
		font-size: 22rpx;
		color: $accent;
		font-weight: 600;
	}
}

.lg-ph {
	color: $faint;
	font-size: 26rpx;
}

/* 登录提交按钮 */
.lg-submit {
	margin-top: 16rpx;
	height: 96rpx;
	border-radius: 28rpx;
	background: $gradient;
	box-shadow: 0 12rpx 36rpx rgba(24, 82, 224, 0.32);
	display: flex;
	align-items: center;
	justify-content: center;
	transition: all 0.2s ease;

	&--pressed {
		transform: scale(0.985);
		opacity: 0.92;
	}

	&--loading {
		opacity: 0.75;
	}

	&__text {
		color: #ffffff;
		font-size: 30rpx;
		font-weight: 700;
		letter-spacing: 0.5px;
	}
}

.lg-foot {
	text-align: center;
	margin-top: 10rpx;

	&__text {
		font-size: 22rpx;
		color: $muted;
	}
}
</style>
