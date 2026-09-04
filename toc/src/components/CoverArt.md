# CoverArt 试卷封面组件

## 💡 核心思想

负责统一渲染试卷封面图，支持两种模式：

1. **预设 SVG 模式**（`cover` 以 `preset:` 前缀开头）：通过 `presetSrc()` 函数映射到内置 5 套透明背景矢量插画（盾牌/灯笼/书卷/奖杯/窗格），以 `object-fit: contain` 按比例居中显示。
2. **自定义图片模式**（`cover` 为 `/uploads/...` 真实 URL）：直接作为 `<img src>` 渲染。

### 防坑要点
- `cover` 为 `null` 或空时默认回退 `preset:1`（盾牌）。
- SVG 文件均为**透明背景**，不含实心矩形色块，确保在白色卡片上自然融入。
- `object-fit: contain`（非 `cover`），防止 SVG 被裁切变形。

## 💻 使用示例

```vue
<template>
  <!-- 预设封面 -->
  <CoverArt cover="preset:3" width="86px" height="104px" />

  <!-- 自定义图片 -->
  <CoverArt cover="/uploads/exam_cover_123.jpg" width="120px" height="150px" />

  <!-- 空值回退盾牌 -->
  <CoverArt :cover="null" width="86px" height="104px" />
</template>

<script setup lang="ts">
import CoverArt from '@/components/CoverArt.vue';
</script>
```
