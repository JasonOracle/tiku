# TenantMembersDrawer 组件自说明文档

## 💡 核心思想

TenantMembersDrawer 是超级管理员专用的**「企业成员视察抽屉」**组件，贯彻 Karpathy 务实设计原则与 SaaS 数据安全隔离逻辑：
1. **零上下文污染的轻量视察**：超级管理员无需经历“全局切换视察租户 -> 页面强制重刷 -> 路由跳转成员管理”的繁重链路，直接在「企业管理」列表点击「成员」即可原地右侧滑出抽屉。后端通过精准路径传参 `/api/v1/super-admin/tenants/{tenant_id}/members` 隔离查询，杜绝任何对全局 `localStorage` 或 Pinia 租户状态的意外覆写。
2. **所有者卡片置顶与快捷切换**：抽屉顶部采用橙色风格高亮置顶「企业所有者 (Owner)」卡片，展示负责人姓名、手机号与加入时间，方便超管第一时间联系企业负责人。同时右侧配备「进入该企业视察」快捷入口，随时按需下钻进入沉浸式全局操作。

## 💻 使用示例

```vue
<template>
  <TenantMembersDrawer
    :visible="drawerVisible"
    :tenant-id="selectedTenantId"
    :tenant-name="selectedTenantName"
    @update:visible="drawerVisible = $event"
    @enter-tenant="handleEnterTenant"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import TenantMembersDrawer from './components/TenantMembersDrawer.vue';

const drawerVisible = ref(false);
const selectedTenantId = ref<number | null>(1);
const selectedTenantName = ref('星辰教育科技');

const handleEnterTenant = (tenantId: number) => {
  console.log('超管切换进入该企业视察：', tenantId);
};
</script>
```
