# ProfileDialog 头像个人信息与编辑弹窗

## 💡 核心思想

v1.3 点击右上角头像下拉菜单的“个人资料”唤出此弹窗。该弹窗不仅展示用户账号、角色类型与今日 AI 额度，还支持 B 端教研管理员补充与编辑基础档案（姓名、性别、手机号、常用邮箱、职位头衔、个人介绍）。数据流向为：打开弹窗时从 `/api/v1/admin/auth/me` 同步最新资料，编辑后调用 `PUT /api/v1/admin/auth/profile` 白名单保存，规避前端误改角色或额度权限。

## 💻 使用示例

```vue
<script setup lang="ts">
import { ref } from 'vue';
import ProfileDialog from './components/ProfileDialog.vue';

const profileVisible = ref(false);
</script>

<template>
  <el-dropdown trigger="hover" @command="(cmd) => { if (cmd === 'profile') profileVisible = true }">
    <div class="user-info">
      <span>Admin</span>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="profile">个人资料</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

  <ProfileDialog v-model="profileVisible" />
</template>
```
