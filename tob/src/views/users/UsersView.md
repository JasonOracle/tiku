# UsersView 用户管理组件文档 (v1.7)

## 💡 核心思想
用户管理收敛为 B端 / C端双 Tab：
1. **B端成员**：B 端账号（超管/管理员/出题人）一览。超管全览，普通管理员仅见自己创建的直属下级（后端接口已按 `created_by_id` 隔离）。
2. **C端学员**：C 端注册用户列表及账号状态。

## 🔒 权限
- 路由 `meta.roles: ['super_admin', 'admin']`，出题人无菜单入口，越权直访由全局守卫 Toast 拦截。
- 成员的新增/启停/充值等写操作仍在「成员管理」页（`/members`）。

## 💻 使用示例
```vue
<template>
  <UsersView />
</template>

<script setup lang="ts">
import UsersView from './views/users/UsersView.vue';
</script>
```
