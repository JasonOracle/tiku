<!--
  PreviewFloat：双风格 UI 选型预览专用全局悬浮球
  仅服务于 preview-linear / preview-apple / preview-nav 预览体系，不参与任何正式业务页面
-->
<template>
	<view class="pf-root">
		<!-- 悬浮球本体：纯 CSS 九点网格图标（uni 模板对原生 svg 标签编译不可靠，故不使用 svg 标签） -->
		<view class="pf-ball" :class="{ 'pf-ball--active': panelOpen }" @click="panelOpen = !panelOpen">
			<view class="pf-ball__grid" :class="{ 'pf-ball__grid--open': panelOpen }">
				<view class="pf-dot" v-for="n in 9" :key="n"></view>
			</view>
		</view>

		<!-- 展开面板：双风格全部页面一键直达 -->
		<view class="pf-mask" v-if="panelOpen" @click="panelOpen = false"></view>
		<view class="pf-panel" v-if="panelOpen">
			<view class="pf-panel__head">
				<text class="pf-panel__title">UI 选型导航台</text>
				<text class="pf-panel__sub" @click="go('preview-nav/index')">返回索引总览</text>
			</view>
			<view class="pf-cols">
				<view class="pf-col" v-for="group in groups" :key="group.key">
					<view class="pf-col__head" :style="{ color: group.accent }">{{ group.label }}</view>
					<view
						class="pf-item"
						:class="{ 'pf-item--current': current === item.path }"
						v-for="item in group.pages"
						:key="item.path"
						@click="go(item.path)"
					>
						<text class="pf-item__name">{{ item.name }}</text>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup lang="ts">
import { ref } from "vue";

/** 当前预览页路由路径，用于在面板中高亮定位 */
defineProps<{ current: string }>();

const panelOpen = ref(false);

interface PreviewPageItem {
	name: string;
	path: string;
}
interface PreviewGroup {
	key: string;
	label: string;
	accent: string;
	pages: PreviewPageItem[];
}

const groups: PreviewGroup[] = [
	{
		key: "linear",
		label: "A · Linear 极客冷灰",
		accent: "#1D63FF",
		pages: [
			{ name: "首页", path: "preview-linear/index/index" },
			{ name: "我的测试", path: "preview-linear/records/index" },
			{ name: "在线考场", path: "preview-linear/exam/index" },
			{ name: "成绩报告", path: "preview-linear/report/index" },
			{ name: "个人中心", path: "preview-linear/profile/index" },
			{ name: "我的收藏", path: "preview-linear/favorites/index" },
			{ name: "登录页", path: "preview-linear/login/index" },
		],
	},
	{
		key: "apple",
		label: "B · Apple 钛金微光",
		accent: "#1852E0",
		pages: [
			{ name: "首页", path: "preview-apple/index/index" },
			{ name: "我的测试", path: "preview-apple/records/index" },
			{ name: "在线考场", path: "preview-apple/exam/index" },
			{ name: "成绩报告", path: "preview-apple/report/index" },
			{ name: "个人中心", path: "preview-apple/profile/index" },
			{ name: "我的收藏", path: "preview-apple/favorites/index" },
			{ name: "登录页", path: "preview-apple/login/index" },
		],
	},
];

/** 跳转到指定预览页，预览页均非 tabBar 页面，navigateTo 即可 */
function go(path: string): void {
	panelOpen.value = false;
	if (path === "preview-nav/index") {
		uni.redirectTo({ url: "/" + path });
		return;
	}
	uni.navigateTo({ url: "/" + path });
}
</script>

<style lang="scss" scoped>
.pf-root {
	position: relative;
	z-index: 990;
}

.pf-ball {
	position: fixed;
	right: 28rpx;
	bottom: 140rpx;
	width: 96rpx;
	height: 96rpx;
	border-radius: 50%;
	background: #0f172a;
	color: #ffffff;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 12rpx 40rpx rgba(15, 23, 42, 0.35);
	transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.pf-ball:active {
	transform: scale(0.92);
}

.pf-ball--active {
	background: #1d63ff;
}

.pf-ball__grid {
	width: 40rpx;
	height: 40rpx;
	display: flex;
	flex-wrap: wrap;
	gap: 8rpx;
	transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.pf-ball__grid--open {
	transform: rotate(45deg);
}

.pf-dot {
	width: 8rpx;
	height: 8rpx;
	border-radius: 50%;
	background: currentColor;
}

.pf-mask {
	position: fixed;
	left: 0;
	top: 0;
	right: 0;
	bottom: 0;
	background: rgba(15, 23, 42, 0.45);
	z-index: 990;
}

.pf-panel {
	position: fixed;
	right: 28rpx;
	bottom: 252rpx;
	width: 560rpx;
	background: #ffffff;
	border-radius: 24rpx;
	padding: 32rpx;
	box-shadow: 0 24rpx 80rpx rgba(15, 23, 42, 0.22);
	z-index: 991;
}

.pf-panel__head {
	display: flex;
	align-items: baseline;
	justify-content: space-between;
	margin-bottom: 24rpx;
}

.pf-panel__title {
	font-size: 30rpx;
	font-weight: 700;
	color: #0f172a;
}

.pf-panel__sub {
	font-size: 22rpx;
	color: #1d63ff;
}

.pf-cols {
	display: flex;
	gap: 24rpx;
}

.pf-col {
	flex: 1;
	min-width: 0;
}

.pf-col__head {
	font-size: 22rpx;
	font-weight: 700;
	padding-bottom: 12rpx;
	border-bottom: 1px solid rgba(15, 23, 42, 0.08);
	margin-bottom: 8rpx;
}

.pf-item {
	padding: 14rpx 16rpx;
	border-radius: 12rpx;
	margin: 4rpx 0;
	background: #f8fafc;
	transition: background 0.2s;
}

.pf-item--current {
	background: #eaf1ff;
}

.pf-item__name {
	font-size: 24rpx;
	color: #334155;
}

.pf-item--current .pf-item__name {
	color: #1d63ff;
	font-weight: 600;
}
</style>
