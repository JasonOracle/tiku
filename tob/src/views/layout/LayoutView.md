# LayoutView 后台框架组件文档 (v1.7)

## 💡 核心思想
后台 SaaS 系统全局响应式侧边栏与 Header 顶栏导航布局。集成 Aero Glass 边框折射特效与 Pinia 登录用户状态销毁。

## 🧭 v1.7 菜单结构
Dashboard（首页）首位 → 试卷与组卷 → 题海管理 → 阅卷大厅 → 分类配置 → 用户管理（超管/管理员）→
首页 Banner（超管）→ 审计日志（超管）→ AI 模型配置（超管/管理员）→ ✨ AI 助理（最末）。
左上角品牌去除 TiKu 文字，改为「智」+ 智题库；侧边栏底部含 AI 赋能教育推广卡。

## 👤 头像个人信息弹窗
点击右上角头像弹出 `components/ProfileDialog.vue`（账号/角色/额度 + 退出登录）。

## 💻 使用示例
```vue
<template>
  <LayoutView />
</template>

<script setup lang="ts">
import LayoutView from './views/layout/LayoutView.vue';
</script>
```
