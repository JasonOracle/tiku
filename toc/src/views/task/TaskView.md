# TaskView 答题执行组件文档

## 💡 核心思想

C 端学员核心答题考场视图，负责考试答题交互、服务端防作弊计时、多种题型渲染与交卷结算：

1. **题型兼容与选项智能规范化（Normalized Options Flow）**：
   - 兼容后端 `single_choice`、`multiple_choice`、`judge`、`fill_in`、`short_answer` 等全部题型枚举；
   - 引入 `normalizedCurrentOptions`，智能兼容 AI 组卷与 Excel 导入产出的不同格式数据（无论数据库选项字段存储的是对象列表 `[{key, text}]`、字符串列表 `["A. 选项", "B. 选项"]` 还是普通文本），均能准确提取前缀键（`A, B, C...`）与选项内容，彻底杜绝选项内容区域空白的问题；
   - 判断题若未配置选项，自动智能补充「A. 正确 / B. 错误」交互选项。
2. **填空题防崩与连续下划线正则兼容（Zero-Crash Fill-In Inputs）**：
   - 使用正则 `/_{2,}/` 兼容切分 2 个及以上连续下划线（如 `__`, `___`, `____`）作为填空槽位；
   - 提供 `getFillAnswers(qId)` 防御性访问函数，即使题目未预先初始化也动态生成空值数组，彻底根除 `TypeError: Cannot read properties of undefined (reading '0')` 崩溃导致白屏与交卷中断的问题。
3. **服务端权威计时（Anti-Cheat Timer）**：
   - 作答倒计时强力锚定服务端开考时刻 `started_at` 与当前服务器时间 `server_now`，客户端仅做时钟平移微调；
   - 到期强制触发自动收卷结算。
4. **主客观混合精准提交与路由直达（Direct-Record Submission & Route）**：
   - 提交作答直接读取后端返回的精确 `record_id`，直达成绩报告页 `/report?record_id=...`，确保任务完成态落库后即时流转至“已参加”列表。
5. **弹窗脱节防白屏架构（Root-Level Modal）**：
   - 将 `<AppModal>` 提升至顶层根节点，无论任务是否处于已提交拦截状态均能稳定弹出对话框，杜绝因 `v-if="record"` 未就绪造成的白屏或页面假死。

---

## 💻 使用示例

```vue
<!-- 在 router/index.ts 中作为二级路由挂载 -->
import TaskView from '../views/task/TaskView.vue';

const routes = [
  { path: '/task', component: TaskView, meta: { title: '在线答题' } },
];
```
