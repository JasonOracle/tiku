# 智题库 (TiKu) 核心研发进展与版本里程碑 (Progress Log)

---
## 📌 「继续测试」入口收窄 + 语义改为保留作答续答（2026-09-12 02:05:00）

> 背景：用户反馈「我的测试 → 已参加」卡片同时出现「30分 + 继续测试 + 查看成绩」三者并存，属错误形态。经查为同日实现的 `can_retake` 判定过宽所致，本次做收窄修正。

- [x] **缺陷根因**：
  - `can_retake` 原判定只看 `status ∈ (submitted, pending_verification)` + 未过 `deadline`，**缺「是否含简答题 / 是否 manual / 成绩是否已出」三个必要条件**，且 `deadline IS NULL` 被当成长期开放直接放行。
  - 真实库证据（`docker exec tiku_mysql mysql -e SELECT`）：卷 30（manual / deadline NULL / 不含简答 / submitted / 30分）、卷 29（manual / deadline NULL / 不含简答 / submitted / 10分）双双命中 → 卡片上错误出现继续测试入口。
  - 前端 `can_retake` 为真时同时渲染 分数 + 继续测试 + 查看成绩，语义自相矛盾。
- [x] **新判定规则（后端唯一判定，四条件缺一不可）**：
  ```
  can_continue = verification_mode == 'manual'          // 人工审核模式
              && 记录状态 == 'pending_verification'      // 未出成绩（客观分只是部分分）
              && 卷内含简答题(short/short_answer)         // 有简答题
              && (deadline IS NULL || now < deadline)   // 考试时间没到期（NULL 视为长期开放）
  ```
  AI 全托管卷、纯客观卷、`submitted` 已定稿、`verified` 已核验、已过截止 —— 一律 `false`。
- [x] **后端（`backend/app/api/saas/tasks.py` / `member.py`）**：
  - `member_tasks`：`can_retake` → **`can_continue`**；题目分值映射升级为 `TaskResource JOIN ResourceItem` 一次批量查询，同时取 `type` 用于含简答判定（`subj_map`），不引入 N+1。
  - `task_entry`：响应新增 **`my_answers`**（`rec.answers or []`）供考场回填续答。
  - `POST /tasks/{task_id}/retake` 改造为 **`POST /tasks/{task_id}/continue`**：**保留 `answers`**，把记录从 `pending_verification` 原地退回 `pending`，清空未终审的 `score`/`ai_result`/`ai_rag_sources`/`comments`/`submit_time`/`time_spent`，`created_at` 重置为服务端当前时间（**重新给满考试时限**）；校验链在接口层二次兜底（manual + 含简答 + 记录为 pending_verification + 未过截止），杜绝绕过前端直调；审计动作 `continue`。
- [x] **前端（`toc`）**：
  - `MyTasksView.vue`：已参加卡片改为**互斥二分** —— `can_continue` 为真时**只显示「继续测试」**（不显示分数、不显示查看成绩）；为假时显示分数 + 「查看」。确认弹窗文案改为「带着上次作答回考场、可修改后重新交卷、成绩仍待人工核验」，接口改调 `/continue`；清理废弃的 `retake`/`link-btn` 样式与状态变量。
  - `TaskView.vue`：`onMounted` 读取 `entry.my_answers` 回填三类作答态（客观题选项数组 / 填空逐空数组，长度取 `max(题干空数, 上次作答长度)` 防截断 / 简答文本），回填顺序严格放在空态初始化之后。
  - `IndexView.vue` 无需改动（首页已过滤 `pending_verification`，逻辑自洽）。
- [x] **文档同源**：`api-contract.md` 第 8 章重写为 `can_continue` + 「继续测试（保留作答续答）」+ `my_answers` 契约；`tech-spec.md` §6 同步四条件与续答语义；`MyTasksView.md`、`TaskView.md` 重写。
- [x] **测试**：`test_subjective_manual_retake_and_member_stats` 升级为九段断言，覆盖 `can_continue` 四条件真值矩阵（manual+含简答+审核中+未到期为真；纯客观定稿、AI 全托管、已核验、已截止均为假）、`/continue` 保留作答且入口透传 `my_answers`、续答重新交卷再回 `pending_verification`。
- [x] **对截图两张卡片的预期效果**：卷 29 / 卷 30 收窄后 `can_continue = false` → 只剩「已交卷」标签 + 分数 + 绿色「查看」，两个错误入口消失。

---
## 📌 C 端首页可见性收敛 / 截止前重考 / 交卷状态规则裂缝修复 / 个人中心四项真实统计（2026-09-12 01:31:34）

- [x] **首页只呈现「还能作答」的试卷（`toc/src/views/index/IndexView.vue`）**：
  - `loadData` 入口按 `DONE_STATUSES = ['submitted','verified','pending_verification']` 过滤，已交卷/审核中/已核验的试卷一律从首页移除（成绩统一去「我的测试」看）。
  - 分类胶囊 `catMap` 改为基于**过滤后**的可见试卷重算，杜绝「某分类下试卷全部做完 → 点分类空白」。
  - 新增空状态卡片（插画 + 文案 + 「去我的测试查看」按钮），避免全部完成时出现空白页。
  - 清理已参加徽章（`done-tag`）、查看按钮分支与 `is_done`/`record_id` 无用映射字段及相关样式。
- [x] **交卷状态规则裂缝修复（`backend/app/api/saas/tasks.py`）**：
  - `answer_map` 构建前移至状态决策之前，据此预先判定 `has_subjective`；`need_verify = (verification_mode == "ai_auto") or has_subjective`。
  - 修复「manual 人工审核卷含简答题交卷后被错误定稿为 `submitted`，永远进不了核验池」的历史缺陷；现只要含简答题即转 `pending_verification` 并触发管理员待核验通知。
  - `member_tasks` 新增下发 `can_retake`（后端统一判定：`submitted`/`pending_verification` 且未过 `deadline`，`verified` 恒 false）与 `verification_mode`。
- [x] **截止前重考（`backend/app/api/saas/member.py` + `toc/src/views/my-tasks/MyTasksView.vue`）**：
  - 新增 `POST /api/v1/member/tasks/{task_id}/retake`：**原地重置**本人该卷 `TaskRecord` 为 `pending`（清空 score/answers/ai_result/comments/submit_time，`created_at` 重置为重开计时锚点），**不新增记录行**；已核验定分、已过截止、非 published 一律拒绝；写 `retake` 审计留痕。
  - 「我的测试」已参加卡片：状态文案 `pending_verification` 由「待核验」改为「**审核中**」；`can_retake = true` 时渲染「继续测试」主按钮 + 「查看成绩 ›」次级入口，点击先弹 `AppModal` 二次确认（明示清空上次成绩）再重置并直达考场。
- [x] **个人中心统计从「恒为 0」修复为真实数据**：
  - 根因：前端一直调用 `GET /api/v1/users/me/stats`，**后端不存在该路由**，404 被 `catch` 静默吞掉 → 四项数字恒为 0。
  - 新增 `GET /api/v1/member/me/stats`（常规口径）：场次/历史答卷 = 已交卷+审核中+已核验记录数；通过率分母为已出分记录，及格线 = `sum(TaskResource.score) × (pass_percent or 60)%`（与列表 `pass_score`、报告页 `passed` 同源）；收藏数取收藏表计数。全程 `tenant_id` + `user_id` 双过滤，仅 3 条 SQL。
  - `ProfileView.vue` 请求地址更正，失败不再完全静默（`console.warn`）。
- [x] **测试基线（`backend/tests/test_saas_pure.py`）**：
  - 新增 `test_subjective_manual_retake_and_member_stats`：覆盖 manual 含简答 → `pending_verification`、`can_retake` 下发、重考原地重置（record_id 不变）、统计口径与 100% 通过率、已核验/已截止拒绝重考、manual 纯客观卷仍为 `submitted` 对照。
  - 顺带对齐陈旧断言：`test_server_authoritative_timing_anti_cheat` 原断言「重复进入不得刷新开考时刻」与已提交代码（pending 重进重置开考时刻以修复用时累加）相互矛盾，已改为断言 `started_at` 不早于首次且 `my_record_id` 复用同一行。
  - 验证结果：`python -m pytest tests/test_saas_pure.py -k "not ai_session"` → **12 passed**；`toc` 侧 `pnpm build`（含 vue-tsc 类型检查）全绿。
- [x] **遗留说明**：`test_ai_session_persistence_and_traceability` 仍失败，原因为本机环境 RAG 召回切片为空（`ai_rag_sources == []`），属环境依赖的既有失败，与本次改动无关。
- [x] **真实环境联调（2026-09-12 01:3x）**：
  - 环境状态修正：`tiku_backend` 容器此前**没有挂载 `./backend/app`**（仅挂载 uploads，代码烧死在镜像里），已 `docker rm -f tiku_backend` + `docker compose up -d --no-build backend` 重建，现源码目录已挂载（Docker Hub 拉取不通，禁止 `--build`）。`toc/dist` 为 nginx 挂载目录，`pnpm build` 后即生效。
  - 实测（皓石集团·陈伟 13900000006）：`GET /api/v1/member/me/stats` → `{total_exams_taken: 5, history_count: 5, passed_count: 3, pass_rate: 60.0, favorite_count: 0}`（修复前页面恒为 0）。
  - 实测 `GET /api/v1/member/member-tasks`：卷 30(30分)/29(10分) 状态 `submitted` 且 `can_retake=true`；卷 28/27/26 状态 `verified` 且 `can_retake=false`（截止 2026-10-11 未过），与「已核验不可重考」规则一致。
  - 历史数据不做回溯迁移：修复规则前已定稿为 `submitted` 的人工卷不会自动转「审核中」，仅新提交按新规则流转。
- [x] **踩坑记录**：同一文件的多处改动**不可并行下发**（并发写导致后写覆盖先写，`ProfileView.vue` 的接口地址改动曾被静默丢弃），必须串行逐处修改并用构建产物二次校验。
- [x] **文档同源**：`api-contract.md` 新增第 8 章「C 端试卷可见性、重考与个人统计契约」并在 6.1 补状态流转契约；`tech-spec.md` §6 补「含主观题即进核验池」「首页可见性收敛与截止前重考」「个人中心统计口径」；三个组件同名 `.md`（IndexView / MyTasksView / ProfileView）同步更新。

---
## 📌 答案解析全链路（resources.explanation 字段 + 前端五处回显 + 文档同源）2026-09-11 23:43:31

- [x] **数据库层**：
esources 表新增 explanation（TEXT，选填）列；现网库已 ALTER，	iku_init.sql 全量 Schema 同步；新增 ackend/app/services/db_migrate.py 幂等补列助手，挂进 main.py lifespan 启动钩子，存量库零停机自动对齐。
- [x] **后端全链路读写**：
  - 	asks.py：_res_out 改读持久化 
.explanation（替代硬编码空串）；create / batch / update / copy / verify_detail 全链路读写该字段。
  - member.py：C 端成绩明细 GET /member/task-records/{id} 的 items 补 correct_answer + explanation（提交后复盘场景，核验中/已提交/已核验三态均可见）。
  - i.py：两条 AI 出题/组卷接口 + 聊天工具链（create_exam_draft / create_question_draft）的 Prompt schema、TOOL_DEFINITIONS、落库、响应透传全部加回 explanation（50-150 字解析/采分要点）。
- [x] **前端五处回显**：
  - B 端 ResourcesView.vue：普通新建/编辑表单新增「答案解析」多行输入框（全题型通用，选填），编辑回填 + 保存带 payload。
  - B 端 ResourcePreview.vue：题目预览组件恢复琥珀色「答案解析」卡片（AI 出题/AI 组卷审阅清单共用），explanation 为空不渲染。
  - B 端 AI 聊天 ToolCallCard.vue：组卷/出题确认卡每题折叠项加「解析」行。
  - B 端阅卷大厅 VerificationView.vue：批阅抽屉每题在「标准参考答案」下方加「答案解析」块，辅助定分。
  - C 端 ReportView.vue：成绩报告每题加「标准答案（绿）+ 答案解析（琥珀）」对照区块 + 「暂无解析」占位。
- [x] **文档同源**：	ech-spec.md 数据模型补字段说明并修正 4.3 工具描述自相矛盾（"剔除解析"→"含解析"）；pi-contract.md 新增第 7 章「答案解析全链路」契约；product.md 补 C 端能力描述。
- [x] **验证**：	oc + 	ob 双端 pnpm run build（含 ue-tsc --noEmit 类型检查）全绿；现有测试不断言该字段，无回归风险。

## 📌 C 端答题卡抽屉（移动端题目回溯半屏弹窗）2026-09-11 落地

- [x] **TaskView.vue 答题卡抽屉全链路（纯前端，零后端改动）**：
  - **双入口触发**：顶部进度条区（statis-con 整条含 "10/10" 与进度条）点击可开；底部操作区在「上一题/下一题」之间常驻「答题卡」胶囊按钮（白底+轻描边+4 方格图标），任意题序均可触发。
  - **半屏底部抽屉**：max-height: 60vh，圆角顶部+顶部把手，从底部滑入（280ms ease-out 纯 CSS Transition），点击遮罩或跳转后自动收起；适配 iPhone 底部安全区 env(safe-area-inset-bottom)。
  - **方块网格**：5 列自适应，每格显示题号；状态判定与交卷逻辑同源（抽成 isQuestionAnswered：客观看选项、填空看逐空、简答看文本）——白色底+轻阴影=未答，浅蓝实心=已答，当前题蓝色描边+浅蓝底+蓝色数字；点击任意格 currentIndex 直跳目标题并**自动关闭抽屉**（按用户定案交互）。
  - **图例+统计**：抽屉顶部三枚色块图例（已答/未答/当前），底部一行「已答 X / 未答 Y」+「共 N 题」计数。
  - **交卷入口不变**：按用户定案，抽屉内不放交卷按钮，交卷结算仍只走答题卡片底部，避免弹窗内多按钮干扰。
  - **验证**：pnpm run build（ue-tsc --noEmit && vite build）全绿，TaskView chunk 正常产出。

- [x] **代码变更日志规范执行**：	oc/src/views/task/TaskView.vue 文件头新增 2026-09-11 条目，客观描述动作，无版本号前缀。

2026-09-11 20:15:16

---
## 🏆 阶段五：企业全景AI感知、Mem0本地记忆闭环、明亮科技风知识库与租户数据收敛（2026-09-10 ~ 2026-09-11 最终落地）

- [x] **业务词汇彻底确立与回摆**：
  - 废除早期过度泛化的抽象词汇（"条目/核验/我的团队"）。
  - B 端菜单与页面全面正式定型为：**「试卷管理」、「题目管理」、「阅卷管理」、「AI知识库」**；超管端确立为**「企业管理」**。
- [x] **AI 知识库明亮科技风全面重构 (合并与收敛)**：
  - **页面多合一**：重构 `tob/src/views/kb/KbView.vue`（彻底删除旧版 `views/rag/`），顶部整合 4 块动态度量卡片（文档总量、切片分块、就绪状态、存储渐变条）；卡片原地 Switch 切换「公共知识库」与「私有知识库」（`scope: 'public'|'private'`）。
  - **功能解耦（消除对话污染）**：彻底剔除旧版"知识库检索混入 Copilot 会话历史"的设计；落地右侧抽屉式「RAG 检索调试器」，调用专属独立接口 `POST /api/v1/admin/kb/query` 与 `GET /api/v1/admin/kb/metrics`，零写入会话库，即测即看。
  - **多格式切片解析**：支持 DOCX/PDF/XLSX/TXT，切片列表实时外显解析进度与彩色格式徽章。
- [x] **AI 助手工具链规范化（写操作卡片 vs 只读聚合感知）**：
  - **只读聚合工具（自动结构化返回）**：落地 `_get_tenant_organization_snapshot`（在职员工花名册/职业/性别/年龄/简介）与 `_get_tenant_tasks_snapshot`（企业试卷总数/各老师出卷统计/近期试卷明细清单）。执行器在推理初始化时自动静默聚合注入上下文，彻底杜绝企业业务问答幻觉。
  - **写操作工具（前端卡片确认）**：规范化 `create_exam_draft`、`create_question_draft`、`delete_exam`、`delete_question`。前端渲染 Ant Design X 风格卡片预览，用户确认后调用 `POST /chat/execute_tool` 正式事务落库。
- [x] **本地 Mem0 长期记忆闭环 (零云端外部依赖)**：
  - 在 `backend/app/services/memory_service.py` 落地本地嵌入式 Qdrant + `fastembed` (`BAAI/bge-small-zh-v1.5` 512维向量) + 本地持久化目录，实现完全离线运行零开销。
  - 严格多租户记忆隔离（`tenant:{tid}:user:{uid}`）；AI 对话流完成时后台异步提炼偏好；成员物理注销时级联清除 Qdrant 向量数据。
- [x] **成员画像闭环与 C 端做题流转**：
  - 成员模型打通 `gender, age, occupation, bio` 的回显、编辑与表格列外显。
  - C 端（`toc`）通过手机号登录后，自动拉取当前企业已上架（`published`）试卷，服务端锁定 `started_at` 计时开考并支持防篡改交卷。
- [x] **基准租户数据清洗收敛**：
  - 安全删除所有历史测试脏租户，全库收敛锁定为两家标准基线企业：**「星雅教育」（Tenant ID: 1）** 与 **「皓石集团」（Tenant ID: 2）**，各自包含完整教师名册与 2 套已上架试卷。
- [x] **v1.4 试卷/全员考查数据造数与阅卷大厅抽屉重构**：
  - **造数打样落库**：为星雅教育（Tenant 1）与皓石集团（Tenant 2）各成功生成 3 份试卷（共 6 份）、30 道试题，并生成两家企业全部 10 位员工的 30 条真实作答记录（含至少 1 份不及格）。
  - **阅卷大厅重构 (`VerificationView.vue`)**：列表展现"考核试卷全名 + 考生姓名账号 + AI预判得分评语"，支持 700px 抽屉可视化批改，**默认精简只呈现待批改简答题**（标准答案 vs 考生答卷高亮对比），一键采纳 AI 建议分数或手动定分。
  - **AI 阅卷 Prompt 优化**：重构 `ai_verify_record` 提示词，格式化题目与答卷为人类可读格式，彻底抹平 `resource_id` 抽象技术编号。
  - **个人资料与顶栏优化**：顶栏头像侧优先高亮展示**用户真实姓名 (`display_name`)**，并将个人资料编辑中的【姓名】字段设置为强校验必填项。
- [x] **代码归档与状态**：
  - 最新提交 Hash：`0068467`
  - 生产镜像与容器服务（`tiku_nginx`, `tiku_backend`, `tiku_mysql`）均健康平稳运行。

---

## 🏁 阶段四：生产就绪与终极收官（2026-09-09 全自动执行）

- [x] **ai-config 重写**：新增 `AiTenantConfig` 表 + 网关 provider 覆盖（租户优先、失败回退环境）；`GET /ai/config`（脱敏）、`PUT`（空密钥沿用旧值、clear 回退）、`POST /config/test`（真实连通探针）；重写模型配置页（总开关、连通测试、回退）。
- [x] **C 端计时防作弊**：入口落 `in_progress` 行锁定服务端开考时刻（重复进入不刷新）；提交时服务端结算用时（忽略客户端上报，限时截断）、校验发布态与截止；TaskView 倒计时锚定 `started_at/server_now`，删除超限清零后门。
- [x] **TiDB Vector 适配（严守本地模式）**：新增 `vector_store.py`（本地余弦 / LIKE，`TIDB_VECTOR=1` 才走原生 `VEC_COSINE_DISTANCE`，异常回退，默认永不连云）；上传切片尽力向量化；`tiku_init.sql` 全量 18 表零演示数据 + Vector 备用段（注释）；新增 `DEPLOY.md`；compose 与 render.yaml 对齐。
- [x] **双端构建验证**：tob/toc 构建与类型检查（`vue-tsc`）全绿。

---

## 🩸 阶段三：血管接通与运行时修复（2026-09-09）

- [x] **toc 核心闭环**：新增成员端 `saas/member.py`（作答入口/我的提交/成绩/收藏）；成员任务详情对 member 角色剥离答案防泄漏；重写 TaskView 数据层、ReportView、IndexView、MyTasks/History/Favorite。
- [x] **B 端重型模块**：新增 `saas/ops.py`（看板聚合/banner CRUD/配置/上传/通知/审计）；提交/核验/录入/上传/AI生成全链路写审计，提交/核验触发通知；Dashboard 通用化文案。
- [x] **AI 会话持久化**：新增 `AiSession/AiMessage` 表，对话落库用户+助手双消息及 `rag_sources`；会话列表/新建/改名/删除/游标消息全接口；重写 AiAssistantView；修复网关元组解包 bug。
- [x] **测试桩更新**：`test_tools.py` 改网关契约校验；`scripts/e2e_selftest.py` 重写 31 项新契约；双端 build 全绿。

---

## 🔥 阶段二：彻底清洗（0 用户零兼容，2026-09-09）

- [x] **旧模型物理删除**：`models/` 仅剩 `saas.py`（20 表），删除全部旧模型；`schemas/` 仅剩 `common+saas`；`services/` 仅剩 `ai_service`。
- [x] **旧路由物理删除**：删除 `api/admin/*` 14 文件与 `api/v1/*` 6 文件，仅保留统一登录 + `api/saas/*`；`main.py` 移除旧表挂载，接口收敛为纯 SaaS 路径。
- [x] **测试基线重置**：旧测试文件清理，仅保留 `tests/test_saas_pure.py`（登录租户/隔离403/缺头400/成员全闭环/KB分权+AI溯源/上帝视图）。
- [x] **前端重构迁移**：tob 结构重组与旧文件彻底淘汰，重写 Members/Verification/Kb/Copilot；toc 路由对齐。

