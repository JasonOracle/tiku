# MyTasksView 我的测试组件文档

## 💡 核心思想

C 端学员「我的测试」中心视图，负责学员个人测试生命周期管理与进度追踪：

1. **统一顶部视效与命名**：顶部导航标题为「我的测试」，与底部 TabBar 及业务场景全面对齐。
2. **规范的三态切换与动态计数（三态流向闭环）**：
   - **进行中 (`ongoing`)**：任务已发布、未交卷，且未到未来开考时间。
   - **未开始 (`upcoming`)**：任务设置了未来的 `start_time`，当前时间尚未到达开考时间，学员不可作答（行动按钮置灰锁定）。
   - **已参加 (`completed`)**：学员已提交（`submitted` / `pending_verification` / `verified`）。
   - 每个 Tab 右侧均实时统计当前状态下的测试数量徽章。
3. **状态文案统一三态**：

   | 后端 `status` | 卡片文案 | 样式色 |
   | :--- | :--- | :--- |
   | `pending_verification` | **审核中** | 琥珀（待人工/AI 批改） |
   | `submitted` | **已交卷** | 蓝（客观题已自动判分定稿） |
   | `verified` | **已核验** | 绿（终审完成） |

4. **已参加卡片右侧渲染规则（互斥二分，不再三者并存）**：
   - `exam.can_continue === true` → **只显示「继续测试」主按钮**：不显示分数、不显示「查看成绩」（成绩未终审，展示分数自相矛盾）。
   - `exam.can_continue === false` → 显示最终得分 + 绿色「查看」按钮直达 `/report?record_id=...`。

   > `can_continue` **只信后端**，前端不做任何时间/模式推断。

5. **「继续测试」的四条件（后端判定，缺一不可）**：
   - 试卷 `verification_mode === 'manual'`（AI 全托管卷走 AI 核验，无需回考场）；
   - 记录状态 `pending_verification`（**没出成绩**，客观分只是部分分）；
   - 试卷**含简答题**（纯客观卷交卷即定稿）；
   - 考试时间**未到期**（`deadline` 为空视为长期开放）。

6. **继续测试 = 保留作答续答**：
   - 点击先弹 `AppModal` 说明「将带着上次的作答回到考场，可修改后重新交卷，成绩仍待人工核验」；
   - 确认后调用 `POST /api/v1/member/tasks/{task_id}/continue`：后端把本人该卷记录从 `pending_verification` 退回 `pending`，**保留 `answers`**，清空未终审的 score / ai_result / comments / submit_time，并把 `created_at` 重置为服务端当前时间（**重新给满考试时限**）；
   - 成功后跳 `/task?task_id=...`，考场按入口返回的 `my_answers` 回填上次作答；
   - 返回「我的测试」时该卷已回到「进行中」Tab（状态为 pending），符合续答语义。
   - 失败（已截止 / 已核验 / 已定稿 / AI 模式 / 纯客观卷）时以 danger 弹窗展示后端 `detail`。

### 数据流

```
onMounted → GET /api/v1/member/member-tasks
           ↓
按 status 三态分组（已参加 = submitted / verified / pending_verification）
           ↓
已参加卡片：exam.can_continue ? 「继续测试」 : (分数 + 「查看」)
           ↓
askContinue → AppModal 确认 → POST /tasks/{id}/continue → router.push('/task?task_id=')
```

### 防坑逻辑

- **卡片右侧两分支必须互斥**：曾出现「分数 + 继续测试 + 查看成绩」三者同时渲染的错误形态——因为 `can_continue` 判定过宽（只看状态与截止时间），已出成绩的卷子也被放行。收窄为四条件后，审核中卡片不再出现分数。
- **重考不新增记录行**：`TaskRecord` 全库按「每用户每卷唯一」建模（`{task_id: record}` 映射与 `.first()` 查询遍地都是），故继续测试走**原地状态回退**，新增行会让列表与统计全部错乱。

## 💻 使用示例

```vue
<!-- 在 router/index.ts 中作为二级路由挂载 -->
import MyTasksView from '../views/my-tasks/MyTasksView.vue';

const routes = [
  { path: '/my-tasks', component: MyTasksView, meta: { title: '我的测试' } },
];
```
