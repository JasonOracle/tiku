<!--
  preview-nav：双风格 UI 选型索引导航台
  汇集 Linear 与 Apple 两套风格的全部 7 个静态预览页面入口，供浏览器一键直达对比
-->
<template>
	<view class="nav-page">
		<view class="nav-header">
			<view class="nav-header__tag">UI SELECTION</view>
			<view class="nav-header__title">双风格选型导航台</view>
			<view class="nav-header__sub">智题库 C 端审美升维 · 7 大页面 × 2 套风格 · 纯静态交互演示</view>
		</view>

		<view class="nav-list">
			<view
				class="nav-card"
				v-for="group in groups"
				:key="group.key"
				:style="{ background: group.cardBg, color: group.ink }"
			>
				<view class="nav-card__head">
					<view class="nav-card__badge" :style="{ background: group.accent }">{{ group.badge }}</view>
					<view>
						<view class="nav-card__name">{{ group.name }}</view>
						<view class="nav-card__meta">{{ group.meta }}</view>
					</view>
				</view>
				<view class="nav-card__grid">
					<view
						class="nav-link"
						:style="{ color: group.ink }"
						v-for="item in group.pages"
						:key="item.path"
						@click="go(item.path)"
					>
						<text>{{ item.name }}</text>
						<text class="nav-link__arrow" :style="{ color: group.accent }">→</text>
					</view>
				</view>
			</view>
		</view>

		<view class="nav-foot">预览体系不接入真实后端，全部为内置静态演示数据</view>
	</view>
</template>

<script setup lang="ts">
interface PreviewPageItem {
	name: string;
	path: string;
}
interface PreviewGroup {
	key: string;
	badge: string;
	name: string;
	meta: string;
	cardBg: string;
	ink: string;
	accent: string;
	pages: PreviewPageItem[];
}

const groups: PreviewGroup[] = [
	{
		key: "linear",
		badge: "A",
		name: "Linear 极客冷灰风",
		meta: "硬核 · 工程 · 高信息承载 · 秩序严谨",
		cardBg: "linear-gradient(160deg, #0f172a 0%, #1e293b 100%)",
		ink: "#e2e8f0",
		accent: "#1d63ff",
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
		badge: "B",
		name: "Apple 钛金微光风",
		meta: "温润 · 轻奢 · 呼吸感 · 触控质感",
		cardBg: "linear-gradient(160deg, #ffffff 0%, #eef2fb 100%)",
		ink: "#1d1d1f",
		accent: "#1852e0",
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

/** 跳转指定预览页 */
function go(path: string): void {
	uni.navigateTo({ url: "/" + path });
}
</script>

<style lang="scss" scoped>
.nav-page {
	min-height: 100vh;
	background: #070b14;
	padding: 120rpx 40rpx 80rpx;
	box-sizing: border-box;
}

.nav-header__tag {
	display: inline-block;
	font-size: 20rpx;
	letter-spacing: 0.3em;
	color: #1d63ff;
	border: 1px solid rgba(29, 99, 255, 0.45);
	border-radius: 999rpx;
	padding: 8rpx 20rpx;
	margin-bottom: 24rpx;
}

.nav-header__title {
	font-size: 52rpx;
	font-weight: 800;
	color: #f1f5f9;
}

.nav-header__sub {
	margin-top: 14rpx;
	font-size: 24rpx;
	color: #64748b;
}

.nav-list {
	margin-top: 56rpx;
	display: flex;
	flex-direction: column;
	gap: 32rpx;
}

.nav-card {
	border-radius: 28rpx;
	padding: 40rpx 36rpx;
	box-shadow: 0 24rpx 80rpx rgba(0, 0, 0, 0.35);
}

.nav-card__head {
	display: flex;
	align-items: center;
	gap: 24rpx;
	margin-bottom: 32rpx;
}

.nav-card__badge {
	width: 72rpx;
	height: 72rpx;
	border-radius: 20rpx;
	color: #ffffff;
	font-size: 34rpx;
	font-weight: 800;
	display: flex;
	align-items: center;
	justify-content: center;
}

.nav-card__name {
	font-size: 32rpx;
	font-weight: 700;
}

.nav-card__meta {
	margin-top: 6rpx;
	font-size: 22rpx;
	opacity: 0.6;
}

.nav-card__grid {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.nav-link {
	width: calc(50% - 8rpx);
	box-sizing: border-box;
	display: flex;
	align-items: center;
	justify-content: space-between;
	font-size: 26rpx;
	padding: 22rpx 24rpx;
	border-radius: 16rpx;
	background: rgba(255, 255, 255, 0.06);
	transition: transform 0.2s;
}

.nav-link:active {
	transform: scale(0.97);
}

.nav-link__arrow {
	font-weight: 700;
}

.nav-foot {
	margin-top: 56rpx;
	text-align: center;
	font-size: 22rpx;
	color: #475569;
}
</style>
