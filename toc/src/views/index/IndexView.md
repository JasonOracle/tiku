# IndexView 首页组件

## 💡 核心思想

C 端移动端首页核心入口视图，贯彻扁平化与真实业务数据驱动：

1. **Header**：居中显示程序名「题库」，统一视觉基准。
2. **Banner / Hero 智能切换**：
   - 后端配置轮播图时优先渲染 `<BannerCarousel>`；
   - 无轮播图时回退为第一套可作答试卷的立体质感 Feature 卡片；
   - **无可作答试卷时 Hero 整体隐藏**，避免残留点击无响应的「立即开始」死按钮（此时由下方空状态卡片承担引导）。
3. **只呈现「还能作答」的试卷（首页可见性收敛）**：
   - 首页**只展示未作答 / 进行中**的已上架试卷；`submitted`（已交卷）、`pending_verification`（审核中）、`verified`（已核验）的试卷一律从首页移除，成绩统一去「我的测试」查看。
   - 过滤发生在前端 `loadData` 的入口处（`DONE_STATUSES` 常量），后端接口保持返回全量便于「我的测试」复用。
4. **真实分类动态提取与切换**：
   - 彻底废弃脱离实际的虚拟死分类；
   - 分类集合基于**过滤后的可见试卷**重算（如「专业问答」、「入职培训」、「模拟考试」），从根源杜绝「点了分类却列表空白」；并提供「全部精选」一键聚合。
5. **试卷卡片真实业务呈现**：
   - 标签区精准展示真实分类胶囊与限时考试（如“30分钟限时”），不再出现无中生有的“练习模式”与“已参加”；
   - 真实统计指标：接口直读题目数（`N题`）、总分（`M分`）与动态折算及格线（`K分`）；
   - 右侧主行动按钮恒为「开始」（首页出现的卷子必然可作答）。
6. **空状态引导**：当企业内所有试卷均已完成（`exams.length === 0`），展示插画 + 文案 + 「去我的测试查看」按钮，而不是空白页。
7. **底部安全区防遮挡**：配置 `padding-bottom: 140px`，配合毛玻璃浮动 `<TabBar>`，滑动体验丝滑无死角。

### 数据流

```
onMounted → 并行请求 loadBanners / loadData (获取 member-tasks)
           ↓
过滤 DONE_STATUSES（submitted / verified / pending_verification）→ 仅保留可作答试卷
           ↓
提取可见试卷的真实分类 (catMap) 并响应式更新 categories
           ↓
selectCategory(catId) → 响应式 exams 过滤
           ↓
startExam(examId) → 登录校验 → router.push('/task?task_id=...')
           ↓
exams 为空 → 空状态卡片 → router.push('/my-tasks')
```

### 防坑逻辑

- **不要在首页做「查看成绩」入口**：已交卷试卷既已从首页过滤，若再保留查看按钮分支，会出现「列表里没有该卷却仍要跳报告页」的死逻辑。
- **分类必须以过滤后列表为数据源**：否则会出现某分类下所有试卷都已完成 → 首页可见列表为空但分类胶囊仍在 → 点击即空白的体验缺陷。

## 💻 使用示例

```vue
<!-- 在 router/index.ts 中作为 C 端默认首页路由 -->
import IndexView from '../views/index/IndexView.vue';

const routes = [
  { path: '/', component: IndexView, meta: { title: '题库首页' } },
];
```
