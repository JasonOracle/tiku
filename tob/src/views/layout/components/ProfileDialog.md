# ProfileDialog 头像个人信息弹窗

## 设计初衷

v1.7 点击右上角头像弹出个人信息（账号/角色/额度），替代裸露的文字信息；内置退出登录，关闭弹窗即返回。

## 调用示例

```vue
<script setup lang="ts">
import ProfileDialog from './components/ProfileDialog.vue';

const profileVisible = ref(false);
</script>

<template>
  <div class="user-info" @click="profileVisible = true">
    ...
  </div>
  <ProfileDialog v-model="profileVisible" />
</template>
```
