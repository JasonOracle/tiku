<template>
	<!-- selector 必须与下方 useToast() 的入参严格一致，否则注入的不是同一份配置对象 -->
	<wd-toast selector="global-toast" />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from "vue";
import { useToast } from "wot-design-uni";
import { useToastStore } from "@/stores/toast";

const toastStore = useToastStore();

// useToast 内部使用 provide/inject，必须在 setup 上下文中调用，
// 且挂载点 wd-toast 必须是当前组件的子节点，两者才能建立联系。
const toast = useToast("global-toast");

/**
 * 本挂载点归属的页面路由。
 * 页面栈里可能同时存在多个挂载了 GlobalToast 的页面（首页 navigateTo 到考场后首页仍在栈中），
 * 它们共用同一个 store，若不区分归属，后台页面的实例会抢先消费掉提示，
 * 导致用户在当前页面完全看不到反馈。因此只有归属页与自身路由一致的挂载点才派发。
 */
const ownerRoute = ref("");

function resolveCurrentRoute(): string {
	const pages = getCurrentPages();
	const page = pages[pages.length - 1] as unknown as { route?: string } | undefined;
	return page?.route ?? "";
}

// 登记挂载状态：未挂载时 useGlobalToast 会降级为 uni.showToast，避免错误静默丢失
onMounted(() => {
	ownerRoute.value = resolveCurrentRoute();
	toastStore.markMounted();
});
onUnmounted(() => {
	toastStore.markUnmounted();
});

watch(
	() => toastStore.current,
	(payload) => {
		if (!payload) return;
		// 非本页触发的提示不消费，留给归属页面的挂载点派发（空归属视为全局提示，人人可派发）
		if (payload.page && payload.page !== ownerRoute.value) return;
		toast[payload.type]({
			msg: payload.msg,
			duration: payload.duration,
			position: payload.position,
		});
		// 派发完成后立即复位，防止页面重建时重复弹出同一条提示
		toastStore.consume();
	}
);
</script>
