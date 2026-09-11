# IndexView 首页组件

## 💡 核心思想

C 端移动端首页核心入口视图，贯彻扁平化与真实业务数据驱动：

1. **Header**：居中显示程序名「题库」，统一视觉基准。
2. **Banner / Hero 智能切换**：
   - 后端配置轮播图时优先渲染 `<BannerCarousel>`；
   - 无轮播图时自动回退为第一套试卷的立体质感 Feature 卡片。
3. **真实分类动态提取与切换**：
   - 彻底废弃脱离实际的虚拟死分类；
   - 动态解析当前企业已发布试卷所归属的真实分类集合（如「专业问答」、「入职培训」、「模拟考试」），并提供「全部精选」一键聚合。
4. **试卷卡片真实业务呈现**：
   - **去除无中生有的“练习模式”**：标签区域精准展示该试卷所属的真实分类胶囊，以及限时考试（如“30分钟限时”）；
   - **真实统计指标**：从接口直读真实题目数（`N题`）、试卷总分（`M分`）及动态折算的及格线（`K分`）；
   - **主行动按钮明确为「开始」**：右侧操作按钮由模糊的“做题”升级为“开始”；若用户已参加则呈现“查看”与绿色“已参加”状态胶囊。
5. **底部安全区防遮挡**：配置 `padding-bottom: 140px`，配合毛玻璃浮动 `<TabBar>`，滑动体验丝滑无死角。

### 数据流

```
onMounted → 并行请求 loadBanners / loadData (获取 member-tasks)
           ↓
提取当前任务真实分类 (catMap) 并响应式更新 categories
           ↓
selectCategory(catId) → 响应式 exams 过滤
           ↓
startExam(examId) → 登录校验 → router.push('/task?task_id=...')
```

## 💻 使用示例

```vue
<!-- 在 router/index.ts 中作为 C 端默认首页路由 -->
import IndexView from '../views/index/IndexView.vue';

const routes = [
  { path: '/', component: IndexView, meta: { title: '题库首页' } },
];
```
