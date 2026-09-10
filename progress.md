# 智题库 (TiKu) 核心研发进展与版本里程碑 (Progress Log)

---

## 🏆 阶段五：企业全景AI感知、Mem0本地记忆闭环、明亮科技风知识库与租户数据收敛（2026-09-10 ~ 2026-09-11 最终落地）

- [x] **业务词汇彻底确立与回摆**：
  - 废除早期过度泛化的抽象词汇（“条目/核验/我的团队”）。
  - B 端菜单与页面全面正式定型为：**「试卷管理」、「题目管理」、「阅卷管理」、「AI知识库」**；超管端确立为**「企业管理」**。
- [x] **AI 知识库明亮科技风全面重构 (合并与收敛)**：
  - **页面多合一**：重构 `tob/src/views/kb/KbView.vue`（彻底删除旧版 `views/rag/`），顶部整合 4 块动态度量卡片（文档总量、切片分块、就绪状态、存储渐变条）；卡片原地 Switch 切换「公共知识库」与「私有知识库」（`scope: 'public'|'private'`）。
  - **功能解耦（消除对话污染）**：彻底剔除旧版“知识库检索混入 Copilot 会话历史”的设计；落地右侧抽屉式「RAG 检索调试器」，调用专属独立接口 `POST /api/v1/admin/kb/query` 与 `GET /api/v1/admin/kb/metrics`，零写入会话库，即测即看。
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
  - **阅卷大厅重构 (`VerificationView.vue`)**：列表展现“考核试卷全名 + 考生姓名账号 + AI预判得分评语”，支持 700px 抽屉可视化批改，**默认精简只呈现待批改简答题**（标准答案 vs 考生答卷高亮对比），一键采纳 AI 建议分数或手动定分。
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
