# 成绩报告页 (Report)

## 💡 核心思想

本页面作为考生答题结束后的主交付触点，严格贯彻 **Apple 钛金微光设计系统**与**考务安全防泄题合规红线**：

1. **视觉分层与双模态看板**：
   - **出分态（态 A）**：顶部采用与 `preview-apple` 100% 对齐的深空夜蓝渐变微光看板（`#14306e` 至 `#1852e0`），融合双层漫反射呼吸光晕与居右微章（优秀/及格/未及格），并提供用时、正确题数、正确率三大指标网格。
   - **保密审核态（态 B）**：主客观题由 AI/人工核验中时（`pending = true`），自动切换为 Apple 琉璃盾牌安全插画，在 DOM 层面物理阻断标准答案与考点解析的渲染，防止考生私下对题。
2. **Apple 逐题复盘卡片（折叠微动效）**：
   - 不使用通用白底平庸组件，卡片直接采用圆角钛金微边框（`border-radius: 32rpx`）与柔和投影。
   - 题头配备绿勾（`#1e8e3e`）与红叉（`#d70015`）圆形呼吸徽标，右侧配备折叠旋转指示箭头。
   - 展开后，选项行自动根据考生作答与标准答案渲染为「你的作答 ✓」、「你的作答 ✕」、「标准答案」，下方内嵌淡蓝渐变考点解析卡片（`rp-point`）。
3. **真实后端接口闭环**：
   - 页面入参为 URL 查询参数 `record_id`，请求 `GET /api/v1/member/task-records/{record_id}` 获取考试详情。
   - 支持本题收藏状态同步：调用 `POST /api/v1/member/favorites` 与 `DELETE /api/v1/member/favorites/{id}`。

---

## 💻 使用示例

```vue
<!-- 考生在考试结束交卷后跳转成绩报告页 -->
<script setup lang="ts">
function goToReport(recordId: number) {
  uni.redirectTo({
    url: `/pages/report/index?record_id=${recordId}`
  });
}
</script>
```
