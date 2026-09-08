# 智题库 (TiKu) 全栈项目超详细交接与进度的归档文档 (progress.md)

> **最新更新时间**：`2026-09-09 02:10:00`
> **文档目的**：本交接文档为接手的 AI 模型/开发人员提供 100% 细节落地指南，包含代码实现原理、文件目录树、命令清单、数据契约、测试操作步骤及具体避坑 SOP，确保无缝接续开发。

---

## 🌐 运行环境与部署守则 (Dual-Mode Strategy)
本项目严格执行 **“双擎驱动 (Dual-Mode)”** 的环境隔离架构，依赖环境变量（如 `.env.development` 与 `.env.production`）进行无缝切换：

1. **Development 模式 (本地开发流 - 默认)**
   - **核心定义**：日常写代码、修 Bug、调试 100% 在 Windows 本地进行。
   - **基础设施**：连接本地 MySQL 8.0；使用 Mem0 默认的本地 SQLite 存储；后端与前端均跑在本地 (`localhost`)。
   - **绝对红线**：开发期间禁止将测试脏数据写向上云端，确保线上业务数据的绝对纯净。

2. **Production 模式 (线上生产流)**
   - **核心定义**：仅当用户明确下达“部署到云端”指令，且本地测试通过后，才允许向线上环境推送与合并。
   - **基础设施**：后端部署于 Vercel (`tiku-api.vercel.app`)；数据库连接 TiDB Cloud Serverless；前端托管于 Cloudflare Pages (`tiku-tob/toc.pages.dev`)；Mem0 切换为云端 API/托管向量库以规避 Serverless 无状态限制。
- **当前已绑定的云端节点 (备查)**：
  - 数据库：TiDB Cloud Serverless (MySQL 8.0 兼容)
  - 后端：Vercel Serverless (`https://tiku-api.vercel.app`)
  - B 端：`https://tiku-tob.pages.dev`
  - C 端：`https://tiku-toc.pages.dev`

---

## 🕒 变更与同步历史 (Change Logs)

| 更新时间 (YYYY-MM-DD HH:mm:ss) | 记录模型 / Agent | 本周期主要落地事项 | 当前整体进度 |
| :--- | :--- | :--- | :--- |
| `2026-09-09 02:10:00` | Gemini 系列 Agent | **AI 文库 RAG 自动感知命题闭环与菜单规范重构**：1. **意图分流与批量出题**：新增 `batch_create_questions_draft` 工具及 Handler，严格隔离批量出题确认卡与整卷組卷；2. **RAG 自动感知与切片高亮**：出题自动检索私有文库切片，单题标注 `📚 依据切片#X`，点击拉起 `TraceDrawer` 原文高亮；3. **卡片视觉与操作收口**：引入 `wide-card` 宽幅排版消除垂直挤压竖排，移除内层套娃按钮，由外层统一业务区处理入库与分类联动；4. **弹窗私有文库多选集成**：AI 出题弹窗将「参考私有文库」移至出题材料正下方，AI 组卷弹窗新增选填多选下拉框，且均带 `v-if="ragDocs.length"` 无记录时完全隐藏；5. **方案 A 智能脱钩保障**：`retrieve_chunks` 注入 `min_score=0.45` 过滤，选中文档不相关时自动脱钩，以纯通识出题，绝不产生张冠李戴伪溯源；6. **全站菜单层级重构**：菜单顺序调整为「分类配置 → 题目管理 → 试卷管理」，原「题海管理」统一更名为「题目管理」，原「试卷与组卷」统一更名为「试卷管理」；全量构建打包通过。 | **100% (v1.3.1 闭环交付)** |
| `2026-09-08 02:46:00` | OpenCode / Gemini 底层 Agent | **云端全栈免卡部署与 AI 全面激活收口**：1. 后端成功部署至 Vercel Serverless (`tiku-api.vercel.app`)，连接 TiDB Cloud MySQL 8.0 兼容云数据库；2. 前端 B 端 (`tiku-tob.pages.dev`) 与 C 端 (`tiku-toc.pages.dev`) 成功部署至 Cloudflare Pages；3. 前端网络层实现 `pages.dev` 域名智能自适应直连 Vercel 后端，彻底解决静态反向代理下的 POST 405 Method Not Allowed 问题；4. 内置 Dots.ai API Key (`ak_9PZWVd3J...`) 兜底，本地与线上 AI 助手即开即用；5. agent.md 确立强制提交推送云端原则；代码全量推送到 GitHub 与 Gitee。 | **100% (v1.2.5 线上全通)** |
| `2026-09-03 21:10:49` | Gemini 底层 Agent | 完成阶段一后端(FastAPI+Pytest)、阶段二B端(Vue3+ElementPlus)、阶段三C端(Vue3+H5)，全自动化验证通过 | **85%** |
| `2026-09-03 21:13:15` | Gemini 底层 Agent | 补充全量交接细节：包含代码实现原理、运行命令、排错指南与阶段四 Docker/Nginx 精确落地方案 | **85%** |
| `2026-09-03 23:40:00` | Gemini 底层 Agent | 落地方案 A 题目默认分值(score)、试卷分类绑定、el-slider 及格百分比向上取整与双层隔离组卷，后端 Pytest 100% 通过 | **95%** |
| `2026-09-04 00:12:00` | Gemini 底层 Agent | 题目/试卷双分类 Tabs 隔离、试卷上/下架(确认框+已上架锁定+考情看板)、C端 ProfileView(SVG头像/仪表盘/Cell跳转/HistoryView)全链路闭环，后端测试 100% 通过 | **98%** |
| `2026-09-04 00:43:00` | Gemini 底层 Agent | **模型切换交接备忘录**：已归档物理表结构修补、路由顺序Bug、题库组卷分页与C端防误交卷逻辑细节 | **99%** |
| `2026-09-04 02:10:00` | OpenCode Agent | 数据治理全落地：分类快照category_name+删除引用拦截、题目删除拦截(仅拦上架/归档)+草稿联动重算、试卷删除三态守卫+归档终态、空卷拦截前后端、导入行级分类+short/fill跳过计数、新建默认第一项、B端baseURL同源化；看板is_passed→passed修复；pytest 18通过，MySQL实库回归通过，容器重建 | **100%** |
| `2026-09-04 14:35:00` | OpenCode Agent | UI改版+Banner全落地：5套封面preset双端+B端单选、Banner模块(上限3/秒数可调/链接三态/C端轮播)、C端首页/答题/解析按效果图还原+公共TabBar、个人中心还原+补TabBar、report加total_score/pass_score、Profile统计加载bug修复；pytest 22通过，MySQL实库9项通过 | **100%** |
| `2026-09-04 16:50:00` | Gemini 底层 Agent | 升级通用 NavBar 组件：支持 `immersive` 沉浸式透明背景及滚动动态渐变白底/毛玻璃效果，同步更新 `NavBar.md` 文档与 ReportView，打包验证通过 | **100%** |
| `2026-09-04 17:18:00` | Gemini 系列 Agent | 修复点击“开始做题”触发二次离开弹窗 Bug：首页 `startExam` 原直接带 `exam_id` 跳转，导致 `QuizView` 首次 `get` 失败触发 `router.push('/')` 被路由守卫二次拦截；现统一改为在首页调用 `POST /records/start` 获取 `record_id` 后平滑进入答题页，打包构建通过 | **100%** |
| `2026-09-04 17:26:00` | Gemini 系列 Agent | 1. 修复点击开始做题无响应Bug：`startExam` 增加 `res?.record_id || res?.id` 防御取值；2. 对齐 `zbzn` 项目 TabBar 毛玻璃晶体规范：引入 65% 折射渐变背景、`blur(8px)`、`inset 1px 1px 0 #fff` 内高光与胶囊大圆角，新建 `TabBar.md` 文档，构建重载通过 | **100%** |
| `2026-09-04 20:38:00` | Gemini 系列 Agent | **全量落地用户反哺高标准优化**：1. C端 `CoverArt.vue` 彻底移除背景色与渐变，纯净渲染原始 SVG 矢量图；2. Backend `/me/stats` 支持 `submitted` 与 `timeout` 答卷结算统计，修复个人中心记录为 0 的 Bug；3. B端试卷详情只读弹窗添加展开行 `type="expand"` 完整展现答案与解析；4. 答题页隐藏已收藏题目的图标；5. 新建毛玻璃 `AppModal.vue` 弹窗替代原生提示。 | **100%** |
| `2026-09-04 21:35:00` | Gemini 3.1 Pro | **文档查漏补缺与 B 端/C 端需求同步**：1. 同步 B 端菜单层级调整（分类配置前置于题海管理）；2. 同步新建/导入题目时的“无分类阻断拦截”及必填校验；3. 同步题海列表与试卷选题的 `checkbox-group` 多选批量删除机制；4. 同步试卷题目的拖拽排序与 C 端答题 `is_random` 随机乱序机制；5. 备选题库改为模态弹窗形式。全面更新 PRD、技术规范及进度文档。 | **100% (v1.1)** |
| `2026-09-04 22:55:00` | Antigravity Agent | **交接与状态冻结**：1. 彻底修复前序由于 PowerShell 双引号转义导致的 B/C 端 SVG 图片裂开/格式错误（全量改写 10 个 SVG 矢量图，杜绝任何背景色干扰）；2. `tob/src/views/exams/ExamsView.vue` 增加挂载时的 SVG 日志输出以便追踪资源；3. 实库重置默认 admin 账号密码为 `123456`；4. 开发工作流由静态 Docker Nginx 构建切换回本地 Vite 实时开发服务器（5173/5174端口），打通 HMR。 | **100% (v1.1)** |
| `2026-09-06 16:00:00` | Antigravity Agent | **v1.2 架构规划与技术说明书定稿**：完成 v1.2 MVP 的全量产品需求与底层技术拆解。涉及：AI 平权架构、角色分离、填空/主观题引擎、AI 全权阅卷(BackgroundTasks)、前端状态注入 Copilot、防刷/防逃逸懒计算机制等。同步产出定稿的 `product.md`、`tech-spec.md` (新增实现指北)、`api-contract.md`。 | **v1.2 规划完成 100% / 开发进度 0%** |
| `2026-09-07 12:15:00` | Antigravity Agent | **v1.2 深度业务与交互终态对齐**：1. 精确收敛 B 端三级 RBAC（超管/管理员/出题人，权限向下兼容，管理员可给下级出题人划拨额度）；2. 确立 AI 助管现代气泡与人机协同红色 Action Card 待确认机制；3. 确立简答题阅卷模式为试卷维度（`manual`/`ai_pre`/`ai_auto`）；4. 普通组卷与 AI 组卷题目列表统一透亮渲染选项与绿色高亮正确答案（剔除快速编辑）；5. AI 一键组卷收敛为“两项直出（需求+时间）+ 高级折叠”，题目为大模型实时全量原创生成；6. 全站隐去具体模型厂商名称。 | **v1.2 规格完备 100% / 即将进入开发** |
| `2026-09-06 18:30:00` | ZCode (GLM) | **v1.2 全栈开发 100% 落地并实库验证通过**：①数据层：admins(role/status/额度三列)/questions(is_deleted软删/source/grading_points)/exams(start_time/end_time/is_ai_auto_grade/creator_id)/exam_records(pending_grading/ai_grading_result/short_scores)+audit_logs/notifications/ai_usage_logs 三新表，auto_patch 幂等补列+tiku_init.sql 重生成(13表)；②引擎：填空题二维数组强匹配(切空格+统一大写)/多选漏选半对错选0分/简答题 pending_grading→finalize_record 终算/时间窗 ensure_exam_started+validate_exam_window(time_limit≤区间)/close_expired_window_records 惰性收卷/题目锁定防篡改(get_locked_exam_titles)+复制新题；③AI链路：SenseNova 客户端(**实测可用配置: token.sensenova.cn/v1 + sensenova-6.8-flash-lite，宿主机用户环境变量 SENSENOVA_API_KEY**)、原子Prompt单次批阅、全托管/预批改双模式、失败降级人工、AI出题(预览+batch二次确认入库)、AI组卷(强制Draft)、Copilot前端状态注入、额度资产化(主动扣个人/被动记系统/跨天惰性重置)；④RBAC：试卷按 creator_id 隔离(超管全览)、成员管理仅超管、审计双域留痕；⑤B端：阅卷大厅/消息中心(未读红点轮询)/成员与AI额度/审计日志四新页+组卷时间锁/双维状态badge/待批阅红点/AI组卷对话框/Copilot抽屉；⑥C端：TabBar新增我的测试/MyTestsView三态聚合(进行中/未开始/已考试+最新作答聚合+解析锁)/答题页填空输入框+简答文本域+end_time倒计时压缩(server_now校正)/报告页批阅中Hero+降级查看+部分得分+AI评语；⑦pytest 39项全绿(22旧口径适配+17项v1.2新用例test_v12.py)，tob/toc build通过，实库端到端真AI阅卷冒烟通过(简答按踩分点给20/40+自动发布80分及格)；⑧部署：D:\docker\docker-compose.yml backend 注入 SENSENOVA_API_KEY 透传，容器已重建，nginx 已 reload，sample_questions.xlsx 模板新增填空/简答示例与说明 | **100% (v1.2)** |
| `2026-09-06 19:30:00` | ZCode (GLM) | **v1.2.1 C端注册资料 + 全套自测落地**：①数据层：users 新增 nickname/gender/position/phone(唯一索引uix_users_phone)/email 五列(auto_patch幂等)+tiku_init.sql 重生成；②接口：注册扩展全字段且校验全走 400 中文(缺昵称/缺性别/手机号格式/手机号重复/用户名重复)，UserResponse 带全量资料，新增 GET /api/v1/users/me，B端答题明细/阅卷大厅/考情看板响应统一加 nickname(展示口径:昵称优先回退用户名)；③C端：注册表单扩展(昵称/性别单选/手机号/职务/邮箱，毛玻璃风格)+注册成功预填用户名，store 持久化 nickname，ProfileView 昵称主展示+@用户名+性别/职务标签(数据源 /users/me)；④B端：UsersView 用户tab加昵称/性别/手机号列并补齐分页、明细tab昵称口径，GradingView 考生列与批阅弹窗昵称，ExamsView 考情看板昵称；⑤修复两处 AI 组卷bug：recalc_exam_totals 补 flush(修复 AI 卷 total_score=0)、AI 漏项时按题型构成从题库确定性补齐+answer 结构规范化(字符串answer致500)；⑥pytest 47项全绿(新增 test_registration_profile.py 8项)，新增 scripts/e2e_selftest.py 可复跑全链路自测(35项断言对线上服务+真AI全部通过：分类/题目/AI出题/AI组卷/批量注册6账号/负路径/客观即时出分/半对/主观批阅/AI全托管/昵称展示/我的测试聚合/再考一次/消息/审计)；自测演示账号 e2e0906192200_1~6 (密码 E2ePass123) 保留在实库 | **100% (v1.2.1)** |
| `2026-09-06 20:50:00` | ZCode (GLM) | **v1.2.2 用户反馈 6 问题修复 + UI 实测**：①AI出题弹窗重构(默认仅材料输入框; 高级选项折叠且提示在标题右侧; 题型复选框组单选/多选/判断/填空/简答默认不选; 数量默认空/难度默认空; 任一填写三项必须完整否则400"高级选项需完整填写"; 与材料文字冲突以高级选项为准——prompt 硬性指令"恰好N道"+后端截断+题型越界丢弃)；②AI请求前端 timeout(出题120s/组卷180s/聊天120s, 原全局10s会超时报"网络开小差")+后端 ai_service 429/5xx 指数退避重试2次(免费档限流)；③多选连写答案["ABC"]自动拆分(前端answerStr正则提取字母+后端_validate_question_payload原地拆分, 不足两个仍400)；④AI组卷红错真因: AI生成 new_question 的 options 为字符串数组→落库后 QuestionResponse 校验500(连带拖垮题目列表接口=问题5)，修复: normalize_options("A. 文本"→{key,text}自动编号)贯穿 AI出题/AI组卷/batch/手工create/update 全入口 + QuestionResponse.options 读取放宽List[Any]容错历史数据 + 存量脏题(id54-58)经PUT API修复；⑤C端交卷"还有N题未作答"统计修复: 原只计客观选项漏填空/简答，现三类作答合计；⑥验证: pytest 52项全绿(新增test_v14_fixes.py 5项)+e2e自测38项全过(新增高级选项部分填写400/数量优先级/options规范化回归)+浏览器UI实测(登录→AI出题弹窗交互→勾选题型→数量6→难度→真AI 30s返回恰好6道单选→全选入库成功)。已知边界: IAB自动化合成点击对部分Element Plus控件不稳定(真实浏览器无此问题), UI验收建议人工过一遍 | **100% (v1.2.2)** |
| `2026-09-06 23:35:00` | Gemini 系列 Agent | **AI 出题 1 题逻辑优化与填空题入库对齐修复**：1. 高级选项数量指定为 `N` 且勾选多题型时，若 `N < len(types)`，优先以数量 `N` 为准截取前 `N` 个题型作为硬性要求进行 AI 提示词与约束对齐；2. 在 `admin_ai._normalize_generated_question` 与 `exam_service.validate_fill_question` 中增强填空题 `___` 占位符数量与答案二阶数组空数的容错对齐逻辑（缺失占位符时自动追加，空数不一致时自动切片或补充占位答案），彻底修复 AI 出题批量入库 `POST /api/v1/admin/questions/batch` 触发的 `400` 报错。 | **100% (v1.2.3+)** |
| `2026-09-06 23:06:00` | Gemini 系列 Agent | **AI 服务 4 级 Failover 轮询熔断机制落地**：新增 `SENSENOVA_API_KEY2`、`AGNES_API_KEY` (Agnes 2.5 Flash 模型 `https://apihub.agnes-ai.com/v1/chat/completions`) 与 `AGNES_API_KEY2` 环境变量解析与故障自动转移链路。当前序 Key/Provider 遭遇限流 429 或服务异常时，系统按优先级自动无缝切下一个 Key/模型，彻底杜绝单点失效。同步更新 `docker-compose.yml` 环境变量透传。 | **100% (v1.2.3+)** |
| `2026-09-07 02:30:00` | Antigravity Agent | **B端前端体验重构与 AI RBAC 架构定调**：① 全局重构 `LayoutView` 与 `AiAssistantView`，彻底铲除 emoji 表情符号，采用标准的 `@element-plus/icons-vue` (如 MagicStick/DocumentCopy/Refresh) 配合手写 SVG 矢量点赞/踩图标，实现专业级清爽 UI；② 修复消息中心(`MessagesView`)体验：全行点击乐观更新红点并直接跳转，消除网络延迟感；③ 修复 AI 聊天流高风险操作确认卡片 Bug：分离 Markdown 解析框与功能 Action 卡片（实现类似 Doubao 的独立区块布局），修复因 Vue Proxy 导致 `isThinking` 状态无限残留的坑；④ 确定求职级“企业 AI 网关”架构方案：计划后续通过『动态 Role-Based Prompt 注入 + 核心高光 Agentic Tool + Human-in-the-loop 确认卡片 + API 权限双层校验』来向面试官展示高级工程能力。 | **v1.2.4 体验优化 100% / RBAC 规划中** |
| `2026-09-07 22:00:00` | Antigravity Agent | **v1.2.5 任务规划（待 Opencode 执行）**：1. **静态 1:1 还原 Dashboard**：严格对照 `首页设计图.png` 进行 1:1 像素级还原。不要自行发散，**必须自己从全网搜索合适的无版权背景图、Icon 素材**。2. **UI 裁剪**：完全移除设计图顶部的“搜索”和“设置”按钮；侧边栏使用本文档定义的菜单结构。3. **RBAC 重构**：收敛“用户管理”（去学员列表，拆 B端/C端），超管可见全部，普管仅可见自建出题人，出题人不可见用户管理与审计；审计/Banner仅超管可见；消息中心拦截越权路由直接 Toast；AI助理移至最末。4. **新增模块**：试卷管理行级“阅卷大厅”全屏弹窗；点击头像的“个人信息”弹窗；预留管理员“AI模型配置”界面。 | **执行中** |

---

## 🎯 待执行开发任务 (Opencode Task Queue)

> **Opencode 执行约束：**
> 1. **1:1 还原首页设计图**：参照项目根目录的 `首页设计图.png`，必须严格 1:1 还原其风格（如高级质感、暗色或毛玻璃等）。
> 2. **资源获取自由**：对于设计图中的插画、背景图或图标，你必须自己从全网寻找无版权素材，不允许使用无样式的 Placeholder。
> 3. **不需要的模块**：首页顶部不要搜索框，右上角不要设置按钮。左侧菜单严格按照下方的要求来。目前先做静态假数据展示。
> 4. 所有组件和页面的变更，必须编写或同步更新对应的 `.md` 组件说明文档；在代码头部标注 `[变更日志]`。

**需求核心清单：**
1. **SaaS 首页 Dashboard**：大背景图 + 若干数据可视化组件(ECharts)。
2. **菜单结构重构**：Dashboard 放首位，AI 助理放最末，移除左上角 TiKu 文字。
3. **用户管理解耦与权限**：内部分 B端 / C端 Tab；出题人不可见，普管只能看自建出题人。
4. **弹窗新增**：试卷列表新增行级“阅卷大厅”全屏弹窗；点击头像新增“个人信息”设置弹窗。
5. **AI 模型配置**：预留管理员的模型 API Key 配置静态页。
6. **消息越权拦截**：在全局路由守卫与点击事件中，拦截越权跳转并弹 Toast。



## 1. 架构总览与全量文件目录树 (Directory Architecture)

```
d:\project\tiku\tiku\
├── backend/                       # Python 3.12 + FastAPI 后端 (Port 8000)
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py            # FastAPI 依赖项 (get_db, get_current_user, get_current_admin)
│   │   │   ├── v1/                # C端 API 路由前缀 (/api/v1/*)
│   │   │   │   ├── auth.py        # C端注册与登录 (/register, /login)
│   │   │   │   ├── categories.py  # C端试卷分类查询 (/categories)
│   │   │   │   ├── exams.py       # C端试卷列表与详情 (/exams, /exams/{id})
│   │   │   │   ├── favorites.py   # C端题目收藏/取消收藏 (/favorites)
│   │   │   │   └── records.py     # C端答题流 (/start, /submit, /report, /history)
│   │   │   └── admin/             # B端管理 API 前缀 (/api/v1/admin/*)
│   │   │       ├── admin_auth.py  # B端管理员登录与初始化 (/init, /login)
│   │   │       ├── admin_categories.py # B端分类 CRUD (/admin/categories)
│   │   │       ├── admin_exams.py # B端试卷 CRUD 与组卷 (/admin/exams)
│   │   │       ├── questions.py   # B端题海 CRUD 与 Excel 导入 (/admin/questions)
│   │   │       ├── upload.py      # B端文件上传 (/admin/upload)
│   │   │       └── users.py       # B端用户与全站答题明细 (/admin/users)
│   │   ├── core/
│   │   │   ├── config.py          # 系统配置与环境变量 (DATABASE_URL, SECRET_KEY)
│   │   │   ├── database.py        # SQLAlchemy 引擎与 SessionLocal 工厂
│   │   │   └── security.py        # 原生 bcrypt 密码 Hash & JWT 签发与 5 分钟宽限期解析
│   │   ├── models/                # SQLAlchemy ORM 数据库模型
│   │   │   ├── __init__.py
│   │   │   ├── category.py        # ExamCategory 分类模型
│   │   │   ├── exam.py            # Exam 试卷模型 & ExamQuestion 组卷明细模型
│   │   │   ├── question.py        # Question 题海模型 (支持 JSON 选项与答案)
│   │   │   ├── record.py          # ExamRecord 答题记录模型 & UserFavorite 收藏模型
│   │   │   └── user.py            # User C端用户模型 & Admin B端管理员模型
│   │   ├── schemas/               # Pydantic v2 数据验证模型
│   │   │   ├── auth.py, category.py, common.py, exam.py, question.py, record.py
│   │   ├── services/
│   │   │   └── exam_service.py    # 核心评分算法、悲观锁抢提交、幽灵记录被动超时结算引擎
│   │   ├── uploads/               # 静态图片与文件上传存储目录
│   │   └── main.py                # FastAPI 业务总入口 (CORS, 路由挂载, OpenAPI 配置)
│   ├── tests/                     # Pytest 自动化测试套件
│   │   ├── conftest.py            # SQLite 内存数据库与 TestClient 依赖注入 Override
│   │   ├── test_auth.py           # C/B端认证集成测试
│   │   └── test_quiz_engine.py    # 全流程答题流、评分、悲观锁、防重复提交测试
│   └── requirements.txt           # Python 依赖清单
├── tob/                           # B端 SaaS 管理后台 (Vue 3 + Element Plus, Port 5173)
│   ├── src/
│   │   ├── api/
│   │   │   └── types.ts           # 自动从 FastAPI /openapi.json 导出的 TypeScript 类型
│   │   ├── router/
│   │   │   └── index.ts           # Vue Router (导航守卫校验 tiku_tob_token)
│   │   ├── store/
│   │   │   └── user.ts            # Pinia 管理员状态 (token, username)
│   │   ├── utils/
│   │   │   └── request.ts         # Axios 拦截器 (携带 Bearer token, 统一解包 Response)
│   │   ├── views/
│   │   │   ├── categories/        # CategoriesView.vue & CategoriesView.md
│   │   │   ├── exams/             # ExamsView.vue & ExamsView.md (在线可视化组卷)
│   │   │   ├── layout/            # LayoutView.vue & LayoutView.md (Aero Glass 框架)
│   │   │   ├── login/             # LoginView.vue & LoginView.md (登录/初始化)
│   │   │   ├── questions/         # QuestionsView.vue & QuestionsView.md (CRUD + Excel导入)
│   │   │   └── users/             # UsersView.vue & UsersView.md (用户与答题明细)
│   │   ├── App.vue, main.ts
│   ├── tsconfig.app.json, package.json, vite.config.ts
├── toc/                           # C端移动端轻测评 (Vue 3 + H5, Port 5174)
│   ├── src/
│   │   ├── router/index.ts        # H5 路由 (首页, 答题页, 报告页, 收藏页, 登录页)
│   │   ├── store/user.ts          # Pinia C端用户状态 (tiku_toc_token)
│   │   ├── utils/http.ts          # Axios 拦截器 (独立 token 隔离)
│   │   ├── views/
│   │   │   ├── favorite/          # FavoriteView.vue & FavoriteView.md
│   │   │   ├── index/             # IndexView.vue & IndexView.md (Hero 推荐 + Pill 滚动)
│   │   │   ├── login/             # LoginView.vue & LoginView.md
│   │   │   ├── quiz/              # QuizView.vue & QuizView.md (倒计时 + 答题引擎)
│   │   │   └── report/            # ReportView.vue & ReportView.md (SVG 环形得分圈)
│   │   ├── App.vue, main.ts
│   ├── tsconfig.app.json, package.json, vite.config.ts
├── product.md                     # PRD 需求文档
├── tech-spec.md                  # 技术架构规范
├── api-contract.md                # 接口契约说明
├── agent.md                       # AI 操作与日志保存硬性规则
└── progress.md                    # 本项目进度与避坑经验归档
```

---

## 2. 核心技术原理与实现细节 (Technical Deep-Dive)

### 2.1 数据库悲观锁抢提交防护 (First-Submit-Wins)
- **实现文件**：`backend/app/services/exam_service.py` 中的 `submit_exam_record_with_lock` 函数。
- **机制原理**：
  ```python
  record = db.query(ExamRecord).filter(
      ExamRecord.id == record_id,
      ExamRecord.user_id == user_id
  ).with_for_update().first() # 关键：数据库行级悲观锁
  ```
  在提交答卷时，通过 `.with_for_update()` 锁定 `exam_records` 表的对应行。若 `record.status != 'in_progress'`，直接抛出 `HTTP 400 Bad Request` 拦截重复提交。

### 2.2 幽灵记录被动超时结算机制
- **实现文件**：`backend/app/services/exam_service.py` 中的 `cleanup_expired_records` 函数。
- **机制原理**：
  在用户触发 `POST /api/v1/records/start` 或 `GET /api/v1/exams/{id}` 时，后端会自动检索该用户所有为 `in_progress` 且已超期 (`now > start_time + time_limit + 2分钟网络缓冲`) 的记录，强制更新其 `status = 'timeout'` 并结算，无需消耗服务器后台定时巡检线程。

### 2.3 JWT 5 分钟交卷宽限期验证
- **实现文件**：`backend/app/core/security.py` 中的 `decode_token` 函数。
- **机制原理**：
  在 `submit_exam` 接口中调用 `decode_token(token, allow_grace_period=True)`。当 Token 触发 `jwt.ExpiredSignatureError` 时，若开启宽限期，系统解码出 `exp` 依赖项，只要当前时间未超出 `exp + 5分钟`，仍判定有效，防止考试中途 Token 过期丢失答案。

### 2.4 端到端 TypeScript 类型自动导出
- **导出指令**：
  ```bash
  # 在 backend 服务启动 (http://127.0.0.1:8000) 状态下运行
  cd tob
  npx openapi-typescript http://127.0.0.1:8000/openapi.json -o src/api/types.ts
  ```
  导出的 `types.ts` 包含了后端所有 `Pydantic BaseModel` 转换的精准类型。

---

## 3. 本地开发与自动化测试运行命令 (Runbook & Commands)

### 3.1 本地数据库环境 (MySQL 8.0)
- **Docker Compose 配置**：位于 `D:\docker\docker-compose.yml`
- **连接字符串**：`mysql+pymysql://root:rootpassword@127.0.0.1:3306/tiku_db`

### 3.2 后端服务与 Pytest 自动化测试
```bash
# 进入后端目录
cd d:\project\tiku\tiku\backend

# 1. 运行全量 pytest 集成与单元自动化测试
python -m pytest tests/ -v

# 2. 本地启动 FastAPI 开发服务器 (Port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
*验证成功标准：全量 39 项集成测试全部 PASSED（v1.1 存量 22 项已适配 v1.2 口径 + `test_v12.py` v1.2 新增 17 项）。*

### 3.3 B 端 SaaS 管理后台 (`tob`)
```bash
# 进入 B 端目录
cd d:\project\tiku\tiku\tob

# 1. 启动 Vite 开发服务器 (Port 5173)
pnpm dev --port 5173

# 2. 执行全量 TypeScript 类型校验与打包构建
pnpm build
```
*验证成功标准：`pnpm build` 顺利输出 `built in XXXms` 且无错误。*

### 3.4 C 端移动端轻测评 (`toc`)
```bash
# 进入 C 端目录
cd d:\project\tiku\tiku\toc

# 1. 启动 Vite H5 开发服务器 (Port 5174)
pnpm dev --port 5174

# 2. 执行 TypeScript 类型校验与打包
pnpm build
```

---

## 4. 故障排查与踩坑指南 (Troubleshooting SOP)

1. **Python 3.12 密码 Hash 触发 `ValueError: password cannot be longer than 72 bytes`**：
   - **绝不能引入 `passlib`**。必须在 `backend/app/core/security.py` 中直接调用 Python 原生 `bcrypt` 模块，并执行 `password.encode('utf-8')[:72]` 截断。

2. **pnpm + Vite 8 (Rolldown) 依赖解析找不到模块 (如 `pinia`, `vue-router`)**：
   - **解析**：Vite 8 底层引入 Rolldown 引擎，对于 pnpm 符号链接路径较敏感。
   - **解决**：在 `tob/tsconfig.app.json` 和 `toc/tsconfig.app.json` 中，确保包含以下配置：
     ```json
     {
       "compilerOptions": {
         "moduleResolution": "bundler",
         "verbatimModuleSyntax": false,
         "preserveSymlinks": true,
         "skipLibCheck": true
       }
     }
     ```
   - 并在 `package.json` 中配置 `"build": "vue-tsc --noEmit && vite build"`。

3. **Vue 组件中的定长格式与显式类型标注**：
   - Vue 3 `<script setup lang="ts">` 内避免对 `validate((valid) => ...)` 中的 `valid` 忽略类型声明，统一写为 `(valid: boolean)`，防止 `vue-tsc` 报隐式 `any` 错误。

4. **Vue `@click="fn"` 会把 MouseEvent 当首参传入**：
   - `QuizView` 曾因 `@click="submitExam"` 把事件对象当 `isAuto=true`，跳过未答确认。教训：无参调用一律写 `@click="fn()"`，且函数内部用 `isAuto === true` 防御。
   - 同类：`confirmExit` 与 `onBeforeRouteLeave` 双重提交，靠 `isFinished/submitting` 互斥 + 失败 `next(false)` 解决。

5. **前端 `baseURL` 禁止写死 `http://127.0.0.1:8000`**：
   - 生产经 Nginx 同源代理（`/api/v1/` → `backend:8000`），浏览器直连 8000 会因容器端口未映射宿主机而 `Provisional headers` 失败。`tob/utils/request.ts` 与 `toc/utils/http.ts` 统一 `baseURL: ''`，开发环境靠 `vite.config.ts` 的 `server.proxy` 转发 `/api` 与 `/uploads`。
   - B端 401 跳转必须带子路径前缀：`window.location.href = '/admin/login'`（路由 base 为 `/admin/`）。

6. **Nginx 启动时缓存 backend 容器 IP**：
   - `docker compose up -d backend` 重建后必须 `docker exec tiku_nginx nginx -s reload`，否则 `/api` 代理超时。同时确认 `docker ps` 中 backend 有 `0.0.0.0:8000->8000` 映射。

7. **发版后浏览器 304 缓存旧 bundle**：
   - Nginx 日志若仍是旧 hash（如 `request-DfgTj4kJ.js`），让用户 **Ctrl+Shift+R 硬刷**。`tob` base 为 `/admin/`，资源路径 `/admin/assets/*`，不要与 toc 根路径混淆。

8. **SQLAlchemy 模型字段名 vs 接口字段名**：
   - `ExamRecord` 字段是 `passed`，考情看板曾误用 `r.is_passed` 导致有成绩就 500。对外响应保持 `is_passed` 键（前端已依赖），内部一律用 `r.passed`。教训：新增聚合接口必须配 pytest（已补 `test_exam_stats_board_no_500`）。

9. **MySQL 外键是真实强制的**：
   - `exam_questions.question_id` 为 `ON DELETE CASCADE`，删题会级联吃掉上架卷的关联行；`exams.category_id` 为 `ON DELETE SET NULL`。凡删分类/题目/试卷必须先做引用检查（见 6.4 治理矩阵）。

10. **Excel 被占用时 openpyxl 报 PermissionError**：
    - 改模板前确认用户关闭 Excel；后端导入改用 `workbook[workbook.sheetnames[0]]` 而非 `active`，防止新增“导入说明”工作表后读错表。

---

## 5. 待完成阶段四：Docker 容器化与 Nginx 反向代理配置方案 (Next Steps)

接手的模型/开发人员接下来需完成 **阶段四 (Stage 4)** 的容器化构建与 Nginx 反向代理分发。

### 5.1 待创建 `backend/Dockerfile` 代码方案
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统基础依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 待更新 `D:\docker\docker-compose.yml` 拓扑方案
```yaml
version: '3.8'

services:
  mysql8:
    image: mysql:8.0
    container_name: tiku_mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: tiku_db
      TZ: Asia/Shanghai
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  backend:
    build:
      context: ../tiku/backend
      dockerfile: Dockerfile
    container_name: tiku_backend
    restart: always
    environment:
      DATABASE_URL: "mysql+pymysql://root:rootpassword@tiku_mysql:3306/tiku_db?charset=utf8mb4"
    ports:
      - "8000:8000"
    depends_on:
      - mysql8

volumes:
  mysql_data:
```

### 5.3 Nginx 反向代理分发规则 (`nginx.conf`) 规划
- `/api/v1/admin/` ➔ 代理至 `http://backend:8000/api/v1/admin/`
- `/api/v1/` ➔ 代理至 `http://backend:8000/api/v1/`
- `/uploads/` ➔ 代理至 `backend/app/uploads/`
- `/admin/` ➔ 部署 `tob/dist` 静态构建产物
- `/` ➔ 部署 `toc/dist` 静态构建产物

---

## 6. 🚨 模型无缝无死角接手指南 (Incoming Agent Protocol & Immediate Action Items)

> **给新模型的提示 (v1.2 已全量交付)**：
> v1.2 已于 **2026-09-06 18:30 由 ZCode (GLM) 全栈开发完成并通过实库真 AI 验证**（39 项 pytest 全绿 + 实库端到端 AI 阅卷冒烟通过 + Docker 容器已重建上线）。
> 接手后请阅读本节与 §7 治理规范，v1.2 新增业务规则见 §7.6。后续迭代请基于现状增量开发，**勿回退 v1.1 治理口径**。

### 6.0 v1.2 交付清单 (2026-09-06)
- **后端新增/改动**：
  - 模型：`Admin`(role/status/ai_quota_limit/daily_ai_quota/quota_reset_date)、`Question`(is_deleted/source/grading_points，answer 兼容二维数组)、`Exam`(start_time/end_time/is_ai_auto_grade/creator_id)、`ExamRecord`(pending_grading 状态/ai_grading_result/short_scores)、新表 `AuditLog`/`Notification`/`AiUsageLog`。
  - 服务：`ai_service.py`(SenseNova 客户端+JSON鲁棒提取)、`ai_grading.py`(原子Prompt批阅调度)、`quota_service.py`(额度惰性重置/扣减/系统账单)、`audit_service.py`(审计+站内信)、`exam_service.py` 重构(evaluate_submission 统一评分/最终分 finalize_record/时间窗/惰性收卷/题目锁定/填空校验)。
  - 路由：`admin_grading.py`(阅卷大厅)、`admin_ai.py`(出题/组卷/聊天/状态)、`admin_members.py`(成员与额度，仅超管)、`admin_notifications.py`(消息中心)、`admin_audit.py`(审计，仅超管)、`admin_auth.py` 新增 GET /me、records 重构(my-tests 三桶聚合/报告降级/解析锁/续答)、admin_exams(RBAC隔离/时间锁/红点)、questions(锁定/软删/复制/batch/import支持fill与short)。
- **B端新增页面**：`grading/GradingView.vue`(阅卷大厅)、`messages/MessagesView.vue`、`members/MembersView.vue`、`audit/AuditView.vue`、`components/AiCopilot.vue`(前端状态注入抽屉)；`ExamsView`/`QuestionsView`/`LayoutView` 大改。
- **C端**：`mytests/MyTestsView.vue` 新页 + TabBar 三项化 + QuizView 填空/简答/倒计时压缩 + ReportView 批阅中态。
- **v1.3 C端注册资料（2026-09-06）**：注册必填 昵称/性别(male|female)/手机号(唯一, ^1[3-9]\d{9}$)，选填 职务/邮箱；校验全走 400 中文（C端不解析 422，勿改回 Pydantic 422）；展示口径"昵称优先，无则回退 username"（B端 users 列表/答题明细/阅卷大厅/考情看板 已接）；GET /api/v1/users/me 返回全量资料；全链路自测脚本 `scripts/e2e_selftest.py [BASE_URL]` 可重复执行。
- **大模型实测定案**：`SENSENOVA_API_KEY` 放宿主机用户环境变量；网关 `https://token.sensenova.cn/v1/chat/completions`；**模型用 `sensenova-6.8-flash-lite`**（6.7-flash-lite 无路由、deepseek-v4-flash/glm-5.2 该账号配额不足、deepseek-v4-pro 思考型不返回 content 勿用）；可用模型清单 GET /v1/models。`D:\docker\docker-compose.yml` 已透传 SENSENOVA_* 环境变量，容器重建后自动生效。

### 6.1 已修复与完成的底层改动 (Empirical Groundwork Done)

1. **数据库物理列自动修复机制**：
   - 包含文件：`backend/app/main.py`
   - 已实装 `auto_patch_db_columns()`：启动时自动给 `exam_categories` 增加 `target_type` 列、给 `exams` 增加 `status`/`pass_percent` 列、给 `questions` 增加 `score` 列，并移除了 `exam_categories.name` 的唯一索引，支持题目分类和试卷分类重名。
2. **Schema 缺省覆盖隐患修复**：
   - 包含文件：`backend/app/schemas/category.py`
   - `CategoryResponse` 字段类型已改为 `Optional[str]`，防止 ORM 序列化时强行把数据库 `question` 改写为默认值 `exam`。
3. **CategoriesView.vue 分类隔离**：
   - `tob/src/views/categories/CategoriesView.vue` 已支持 `activeTab` 传递 `target_type` (`question` / `exam`) 进行查询、创建和更新。

---

### 6.2 v1.2 启动任务完成状态 (已于 2026-09-06 全部落地)

#### ✅ 任务 1: v1.2 数据库 Schema 拓展
- Admin 增加 `role/status/ai_quota_limit/daily_ai_quota/quota_reset_date`；Question 增加 `is_deleted/source/grading_points`；Exam 增加 `start_time/end_time/is_ai_auto_grade/creator_id`；ExamRecord 增加 `pending_grading/ai_grading_result/short_scores`；新增 `AuditLog/Notification/AiUsageLog`。`tiku_init.sql` 已重生成（13 表）。

#### ✅ 任务 2: 后端核心业务引擎改造
- 填空题校验 `validate_fill_question`（___ 数量 == answer 二维数组长度，不合法 400）；多选半对（真子集得 `int(score/2)`）；僵尸考卷惰性收卷 `close_expired_window_records`（无 Celery/Redis，0 运维基建）。

#### ✅ 任务 3: AI 阅卷入口与大模型联调
- `ai_grading.run_ai_grading` 经 FastAPI `BackgroundTasks` 后台执行；单卷简答题合并单个 JSON Prompt 原子批阅；格式错乱/超时回滚置 `pending_grading` 交人工大厅（`ai_grading_result.error` 落库 + 站内信告警）。
- **大模型接入定案（重要）**：开发期使用商汤日日新 (SenseNova)。API Key 在宿主机**用户系统环境变量** `SENSENOVA_API_KEY`，代码 `os.getenv()` 读取；`D:\docker\docker-compose.yml` 已透传至容器。实测网关与模型：`https://token.sensenova.cn/v1` + `sensenova-6.8-flash-lite`（老网关 api.sensenova.cn 返回 Forbidden 勿用）。文档：`https://platform.sensenova.cn/docs`。

---

### 6.3 验证标准与快速测试命令
接手后完成修改，执行以下命令验证：
```bash
# 1. 运行后端自动化测试套件（18 项：auth 3 + quiz_engine 1 + status_isolation 3 + governance 10 + 健康检查）
cd d:\project\tiku\tiku\backend
python -m pytest tests/ -v

# 2. B 端与 C 端前端类型校验与构建
cd d:\project\tiku\tiku\tob && pnpm build
cd d:\project\tiku\tiku\toc && pnpm build

# 3. MySQL 实库回归（8001 临时服 + 正式模板导入实测）
cd d:\project\tiku\tiku\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
# 按本章 7.x 治理矩阵逐项打点；模板用仓库根 `sample_questions.xlsx` 真测导入
```

---

## 7. 数据治理规范（2026-09-04 02:10 落地，用户逐项确认）

### 7.1 试卷三态生命周期（归档为彻底终态）
- `draft`（草稿）→ `published`（已上架）→ `archived`（已归档冻结）。
- 下架 = 进 `archived`（B端开关关闭即归档，`ExamsView.vue handleStatusChange`），不可再编辑/删除/变更状态（含重上架）。
- 上架校验（`ensure_publishable`）：必须绑定有效试卷分类，否则 400；同时写入 `exams.category_name` 快照。
- 分类被删/改名后：draft 悬空置空强制重选；published/archived 显示快照纯文字。

### 7.2 删除守卫矩阵
| 对象 | 条件 | 结果 |
| :--- | :--- | :--- |
| 分类 | 被题目/试卷引用 | 400（报数量） |
| 题目 | 被 published/archived 卷引用 | 400（报卷名） |
| 题目 | 仅被 draft 卷引用 | 允许，联动移除 + 重算总分及格线（`recalc_exam_totals`） |
| 试卷 | 有 submitted/timeout 作答 | 400（报人次，仅可下架归档） |
| 试卷 | published（无论有无作答） | 400（先下架） |
| 试卷 | archived | 400（终态冻结） |
| 试卷 | draft 零作答 | 允许，顺带清理 in_progress 幽灵记录 |

### 7.3 空卷拦截（根治 0 分幽灵记录）
- 后端 `submit_exam_record_with_lock`：零作答直接 400（`exam_service.py`）。
- C端 `QuizView`：0 作答离开只提示不提交；超时 0 作答直接返回不交卷。
- 历史脏数据：`exam_records id=13`（root/0分/3秒）仍在库中，待用户确认后手工清理。

### 7.4 导入与分类默认值
- 新建单题 / 导入无分类：默认 `(sort_order,id)` 第一条题目分类，前后端一致（分类列表接口已加 `id` 二级排序）。
- 导入弹窗去掉统一“归入分类”下拉；Excel 按表头“分类”列逐题归入，不存在自动新建，`short/fill` 预留题型跳过计数（`imported_count/skipped_count`）。
- 模板 `sample_questions.xlsx`（仓库根目录）：数据表保持第一顺位 + 新增“导入说明”工作表（含 short/fill 预留声明）。

### 7.5 用户确认过的取舍（勿擅自推翻）
- 归档可否重上架：**不可**（彻底终态）。
- 零作答归档卷可否删：**不可**。
- ~~已上架卷引用的题目内容（题干/答案/分值）：**不锁定编辑**~~ → **v1.2 已升级为锁定**（见 7.6）。
- 题目删除口径：**B方案**（仅拦上架/归档引用）→ **v1.2 已升级为软删除**（见 7.6）。

### 7.6 v1.2 数据治理新增规范（2026-09-06 落地，pytest 覆盖）
1. **题目锁定防篡改**：题目被 `published/archived` 试卷引用 → 全局只读（PUT 400"只读"），唯一修改路径是 `POST /admin/questions/{id}/copy` 复制新题。**取代 v1.1 的"不锁定编辑"取舍。**
2. **防牵连软删除**：删除题目一律 `is_deleted=1`（绝不物理删除），B端题库默认隐藏，已引用试卷仍正常拉取原题。**取代 v1.1 的"仅 draft 引用联动移除"逻辑。**
3. **试卷创建者隔离 (RBAC)**：`exams.creator_id` 记录创建老师；普通老师只能查/改/批自己创建的试卷（403 拦截他人试卷），超管全览；`creator_id=NULL` 的历史试卷仅超管可管。题库仍全局共享。
4. **考试时间窗**：组卷可选填 `start_time/end_time`；后端强校验 `time_limit ≤ (end-start)` 分钟；C端开考前置拦截"未开始/已结束"；倒计时 = min(限时-已耗时, 距end_time)；end_time 已过的 in_progress 记录由查询路径惰性强制收卷（无简答→submitted 计分，含简答→pending_grading）。
5. **主观题状态机**：`in_progress → pending_grading → submitted`（含简答题交卷）；`submit` 即返回 200 不阻塞，AI 批阅走 BackgroundTasks；`is_ai_auto_grade=true` AI 批完直接 `finalize_record` 发布成绩，否则仅写 `ai_grading_result.suggestions` 供阅卷大厅"一键采信"；AI 失败写 `error` 并站内信告警，可在阅卷大厅"重新触发AI"或人工定分 `confirm` 发布。
6. **解析锁（防泄题）**：报告接口在 `pending_grading` 或 `now ≤ end_time` 时置 `analysis_locked=true`，抹除标准答案/解析/评语；C端"查看解析"按钮同步置灰。
7. **AI 额度资产化**：老师主动调用（出题/组卷/聊天）扣 `daily_ai_quota`（跨天首次使用惰性回满为 `ai_quota_limit`，超管可即时 refill）；学生交卷触发的被动阅卷记系统账单不扣个人额度；余额不足 400 拦截。
8. **双域审计**：题目/试卷/成员/批阅等写操作全量落 `audit_logs`（前后快照），AI 操作 `operator_type='ai'`；审计查询仅超管。
9. **Excel 导入 v1.2 口径**：fill 答案 `北京,北京市|京`（逗号=一空多答，竖线=分空）；short 答案列=标准答案全文，可选"踩分点"列分号分隔；无法解析行跳过计数不中断。

---

## 8. 接手检查清单（新模型第一时间执行）
1. 读本文件 §7 治理矩阵 + §4 踩坑（尤其 4/5/6/7/8 条）。
2. `python -m pytest tests/ -v` 确认 39 通过；`tob/toc pnpm build` 确认通过。
3. 线上问题先查 Nginx 日志（旧 bundle hash 即缓存问题）与 `exam_records` 实库（幽灵记录先看 `status/score/time_spent`）。
4. 待办 backlog：清理 root 0分历史记录（待确认）；题目内容快照（已接受风险，暂不做）；阶段四 Docker/Nginx 已上线（`D:\docker\docker-compose.yml`），后续只做重建与 reload；后续开发请直接使用本地 Vite `npm run dev` 获取实时 HMR，避免被容器静态文件缓存迷惑。
5. 测试账号：B端管理员账号为 `admin` / `123456`（已重置）。
6. UI 改版（2026-09-04 16:30 最新落地）：
   - C端 Header：居中标题「题库」，无冗余导航。
   - 5套透明矢量 SVG 封面（盾牌/灯笼/书卷/奖杯/窗格）全量替换（严格遵守无背景色/无渐变的设计规范）。
   - 试卷卡片指标区：重构为上下两行结构（图标+标签在上行，数值在下行），适配设计图。
   - Banner 模块：`BannerCarousel.vue` 支持 backend 动态数组（图片 URL、跳转类型、跳转路径），0张时降级显示 Hero 卡片。
   - 全局 NavBar 组件 (`components/NavBar.vue`)：抽象标准化 22x22 SVG 返回箭头与居中标题，支持 `router.back()`。
   - 个人中心 (`ProfileView.vue`)：退出登录按钮从右上角移入 `cell-group` 底部 Cell。
   - 路由返回修复：`FavoriteView`、`HistoryView`、`ReportView` 返回跳转错误问题全部修复，统一调用 `NavBar` 回退上一页。
7. 已知小坑：`script setup` 内禁 `export`（封面常量抽 `assets/covers/index.ts`）；Profile 曾因 `if (res.data)` 取错解包层导致统计恒 0，已改为 `if (res)`。

---

## 🎯 9. v1.3 开发路线图 (Opencode 接手首要任务)
当前项目处于 v1.2 稳定态，**接手后请立即围绕以下 v1.3 核心目标展开开发**（详细架构与执行细节已全量同步至 `product.md` 与 `tech-spec.md`）：
- [x] **任务 1：动态模型中心 (前端先行)** (`2026-09-08` 落地：`ModelCenterView.vue` 渐变色卡片 + `store/modelCenter.ts` Pinia 多通道/BaseURL/Key/激活模型 + `/v1/models` 一键拉取 + 菜单路由)
- [x] **任务 2：Mem0 长期记忆接入 (后端)** (`2026-09-08` 落地本地 Qdrant；`2026-09-09 02:34:00` 升级云端/本地双轨支持：检测到 `MEM0_API_KEY` 自动切官方 `MemoryClient` 直连云端，本地未配自动回退 `fastembed+qdrant`，Vercel 生产环境变量已注入)
- [x] **任务 3：RAG 智能私有库与溯源抽屉 (全栈)** (`2026-09-08` 落地：`rag.py` 双表 + `admin_rag.py` 上传切片/进度/检索/删除 + `embedding_service.py` 本地 cosine；`Question.source_ref` 透传；`RagView.vue` + `TraceDrawer.vue` 高亮溯源；AI 出题 `doc_ids` 参数)
- [x] **任务 4：Dashboard 真实数据大屏** (`2026-09-08` 落地：`GET /api/v1/admin/dashboard/stats` 聚合 + 前端 ECharts 对接，出题人作用域隔离)
- [ ] **规范提醒**：多模态图片资源强制遵循 `agent.md` 的全网搜索与 MCP 生成协议；开发全程严格遵守本地 Develop 双轨协议。

---

### 10. 2026-09-09 02:34:00 云端 AI 模型通道与 Mem0 双轨闭环交付记录
1. **云端大模型通道切换确认**：
   - 用户在 Vercel 环境变量中注入了生产级大模型变量 (`DOTS_API_KEY`、`DOTS_API_URL`、`DOTS_MODEL`)，完成重新部署。
   - 系统所有 AI 出题、智能组卷、右侧助管问答与主观题批阅均走云端指定模型通道。
2. **Mem0 双轨长期记忆落地**：
   - 改造 `backend/app/services/memory_service.py`：优先读取 `MEM0_API_KEY` 启动官方 `mem0.MemoryClient` 直连云端服务（适配 Vercel Serverless 无状态环境）；本地环境保持 `fastembed + qdrant` 离线运行零开销。
   - 新增 `tests/test_memory_service.py` 自动化单测覆盖双轨分支，全量通过。
   - 用户的官方 Mem0 API Key 已成功注入 Vercel 生产环境变量。


