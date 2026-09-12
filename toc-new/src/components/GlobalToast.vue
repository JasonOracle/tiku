<template>
	<!-- selector 必须与下方 useToast() 的入参严格一致，否则注入的不是同一份配置对象 -->
	<wd-toast selector="global-toast" />
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from "vue";
import { useToast } from "wot-design-uni";
import { useToastStore } from "@/stores/toast";

const toastStore = useToastStore();

// useToast 内部使用 provide/inject，必须在 setup 上下文中调用，
// 且挂载点 wd-toast 必须是当前组件的子节点，两者才能建立联系。
const toast = useToast("global-toast");

// 登记挂载状态：未挂载时 useGlobalToast 会降级为 uni.showToast，避免错误静默丢失
onMounted(() => {
	toastStore.markMounted();
});
onUnmounted(() => {
	toastStore.markUnmounted();
});

watch(
	() => toastStore.current,
	(payload) => {
		if (!payload) return;
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
