# ProfileView 个人中心视图组件文档

## 💡 核心思想

C 端移动端个人中心组件。包含标准 Aero 渐变 SVG 默认头像、作答统计仪表盘（累计作答场次、综合通过率）以及双导航 Cell 选项：

1. **我的题目收藏夹** Cell ➔ 显示题数，跳转 `/favorite`。
2. **历史答题记录** Cell ➔ 显示试卷份数，跳转 `/history`。

### 统计数据源与口径（常规口径）

数据源：`GET /api/v1/member/me/stats`（后端 `backend/app/api/saas/member.py` 的 `my_stats`）。

| 字段 | 口径 |
| :--- | :--- |
| `total_exams_taken`（累计作答场次） | 本人已交卷 + 审核中 + 已核验的提交记录数 |
| `history_count`（历史答题记录） | 同上（提交记录数） |
| `passed_count` / `pass_rate`（综合通过率） | 已出分记录中「得分 ≥ 该卷动态及格线（总分 × pass_percent%，默认 60%）」的占比，保留 1 位小数 |
| `favorite_count`（收藏题数） | 本人收藏表真实计数 |

后端全程强制 `tenant_id` + `user_id` 双过滤，且只用 3 条 SQL（记录 / 试卷 / 题目分值映射批量查询），不做逐记录查库。

### 防坑逻辑

- **接口地址必须是 `/api/v1/member/me/stats`**：早期前端误调 `/api/v1/users/me/stats`（后端根本不存在该路由），404 被 `catch` 静默吞掉，导致页面上四个数字恒为 0。
- 现在请求失败会 `console.warn` 暴露异常，便于排查，但 UI 仍以 0 兜底，避免白屏。
- 及格线必须与 C 端报告页、B 端统计接口口径一致（`sum(TaskResource.score) × pass_percent%`），否则同一份答卷会出现「报告说及格、个人中心说不通过」的互斥结论。

## 💻 使用示例

```vue
<template>
  <ProfileView />
</template>

<script setup lang="ts">
import ProfileView from './ProfileView.vue';
</script>
```
