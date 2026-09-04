# IndexView 首页组件

## 💡 核心思想

C 端移动端首页入口视图，负责以下核心业务流：

1. **Header**：居中显示程序名「题库」，无多余导航图标。
2. **Banner / Hero 二选一渲染**：
   - 后端 `/api/v1/banners` 返回 ≥1 条数据时 → 渲染 `<BannerCarousel>` 轮播组件（支持手滑、圆点、自动轮播）。
   - 返回 0 条时 → 降级为 Hero 推荐卷卡片（蓝紫渐变背景 + CoverArt + 立即挑战按钮）。
3. **分类横向滚动 Pill**：渲染试卷分类 Tab，选中态蓝紫渐变高亮，未选中白底灰字。点击切换触发试卷列表重新加载。
4. **试卷列表卡片**：左侧展示模式标签（限时/练习）、标题、三连指标（题目|总分|及格，`|` 分隔）；右侧展示透明背景 `CoverArt` SVG 插画 + 「开始做题 ›」渐变按钮。
5. **底部安全区**：`padding-bottom: 140px` 保证 `<TabBar>` 浮动导航不遮挡列表末尾。

### 数据流

```
onMounted → 并行请求 loadBanners / loadCategories / loadExams
           ↓
banners.length > 0 ? BannerCarousel : Hero(heroExam)
           ↓
selectCategory(catId) → loadExams(catId) → exams 列表重渲染
           ↓
startExam(examId) → 判断登录态 → router.push('/quiz?exam_id=...')
```

## 💻 使用示例

```vue
<!-- 在 router/index.ts 中挂载为首页 -->
import IndexView from '../views/index/IndexView.vue';

const routes = [
  { path: '/', component: IndexView },
];
```

该组件为页面级视图，不接收外部 Props，所有数据由内部 `onMounted` 自行拉取。
