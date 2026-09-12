# 在线考场页 (Exam)

## 💡 核心思想

本页面为考生在线作答的核反应堆，**100% 像素级对齐风格 B（Apple 钛金微光风）原生考场体验**，彻底杜绝抽象组件包裹带来的空白/渲染失败：

1. **五大题型原生直接展开**：
   - **单选 / 多选**：大圆角呼吸选项条（`ex-option`），选中即亮起深空蓝微光（`$accent-soft`）与渐变圆形微标。
   - **判断题**：醒目的双大胶囊按钮（`对 · 正确` / `错 · 错误`），绿色/红色微光高亮。
   - **填空题**：高清晰纯白底色（`#ffffff`）搭配清晰边框（`2rpx solid #cbd5e1`）与深灰易读占位符（`#64748b`），聚焦触发深空蓝微光光晕。
   - **简答题**：加宽加高大尺寸文本域（380rpx），高辨识度实体清晰边框与深色字体（`#0f172a`），彻底解决浅灰底色在移动端辨识不清的问题，字数超限实时标红预警。
2. **Apple 60vh 玻璃答题卡抽屉 (`ex-drawer`)**：
   - 顶部提供灵动把手（`ex-drawer__grabber`）与四态色标图例（当前题/已作答/已标记/未作答）。
   - 5 列响应式宫格矩阵，点击任意题号直接定位并收起抽屉。
3. **真实考场安全与闭环**：
   - 真实对接 `GET /api/v1/member/tasks/{id}/entry` 题目数据（自动归一化兼容 `content` 与 `title`）。
   - 服务端权威时间基准递减倒计时，最后 5 分钟激活动态心跳呼吸红标。
   - 累计 3 次切屏防作弊弹窗告警与强制收卷（`ex-modal`）。
   - 交卷提交 `POST /api/v1/member/task-records/submit` 并平滑重定向至成绩报告页。

---

## 💻 使用示例

```vue
<!-- 从首页或我的测试点击直接进入考场 -->
<script setup lang="ts">
function startExam(taskId: number, title: string) {
  uni.navigateTo({
    url: `/pages/exam/index?task_id=${taskId}&title=${encodeURIComponent(title)}`
  });
}
</script>
```
