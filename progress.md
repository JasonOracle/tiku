# 智题库 (TiKu) v1.4 架构规范与进度归档 (progress.md)

> **最新更新时间**：`2026-09-09`
> **架构定义**：v1.4 标志着本项目从“教育/考试单体应用”正式转型为“通用 B2B SaaS 平台（类钉钉/飞书）”。
> **最高铁律**：所有后端表、前端 UI 必须遵循本文件的【多租户隔离约束】与【通用化名词映射】，严禁出现“老师/学生/考试”等旧时代的业务词汇。

---

## 🏗️ 核心基石 1：多租户底座 (Tenant - Relation - User)

系统摒弃全局共享模式，采用标准的企业级 SaaS 多租户隔离机制。

1. **核心权限与身份层 (IAM)**：
   - `sys_tenant` (租户表)：企业/组织的载体。
   - `sys_user` (用户表)：仅保留登录凭证 (`username/phone`, `password`) 和全局 `is_super_admin` 标识，**绝不带有任何租户业务字段**。
   - `sys_tenant_user` (枢纽关联表)：记录用户在特定租户下的身份 (`role: owner/admin/member`)。
2. **上帝视角安全陷阱防御**：
   - 超级管理员 (`is_super_admin = true`) 不属于任何具体租户。
   - 上帝登录进入专用的 `/super-admin/tenants` 路由大盘。如果上帝需要视察某企业，必须显式在界面点击“进入”，系统将主动在 Header 挂载该企业的 `X-Tenant-ID` 以复用正常业务逻辑。
   - **绝对禁止**在业务接口中写出 `if is_super_admin: return all_data` 破坏底层隔离的代码。

## 🔐 核心基石 2：极简入驻流 (B端建号 -> 自动绑组织)

彻底废除 C 端的开放注册 (`/register`)，消灭“无组织悬空账户”。

1. **录入模式**：B端企业管理员在后台输入手机号添加成员。
2. **静默建号**：系统执行 UPSERT。若手机号不存在，则静默创建 `sys_user` 并初始化默认密码 (`123456`)。
3. **强制绑定**：无论账号是新建还是已存在，最终强绑定至当前 `tenant_id`。成员直接用手机号+密码登录，直达企业空间。

## 🧠 核心基石 3：AI 公私知识库与溯源 (Public/Private KB)

告别 AI 黑盒，建立企业级知识信任。

1. **公私分权**：
   - **公共知识库 (Public)**：仅限租户 Admin 上传，作为整个组织生成任务/条目的基准事实（如企业产品手册、合规制度）。
   - **私有知识库 (Private)**：成员个人上传，数据强隔离，仅供个人构建专属 Agent 助手或私人任务库。
2. **切片级溯源 (RAG Traceability)**：
   - 所有的 AI 动作（出题、组卷、对话）在落库时，必须将检索命中（Retrieved）的原文切片摘要及来源以 JSON 格式保存在 `ai_rag_sources` 字段中。

## 🔄 核心基石 4：《通用版名词映射表》 (UI/UX 规范)

从 v1.4 起，全站代码（除极个别无法迁移的历史库表外）、接口出入参、UI 展示、Console 日志，必须强制使用以下通用词汇：

| 原教育业务词汇 (废弃) | 通用 B2B 词汇 (v1.4 规范) | 对应的英文变量参考 |
| :--- | :--- | :--- |
| 老师 (Teacher) | **管理员 (Admin)** | `Admin` |
| 学生 (Student) | **成员 (Member)** | `Member / User` |
| 试卷 / 考场 (Exam) | **任务 / 测评 / 表单 (Task / Assessment)** | `Task / Assessment` |
| 题目 (Question) | **条目 / 资源 / 题项 (Item / Resource)** | `Item / Resource` |
| 题库 (Question Bank) | **资源库 / 项目库 (Resource Library)** | `Library` |
| 阅卷 (Grading) | **数据审批 / 结果核验 (Verification)** | `Verification` |
| 考情看板 (Dashboard) | **数据看板 (Data Dashboard)** | `Dashboard` |

---

## 🛠️ 当前进度与行动项 (Action Items)

- [x] **旧资产封存**：v1.3 以前的详细历史已归档至 `history/progress_v1.3_legacy.md`。
- [x] **演进说明书**：根目录 `version_history.md` 已生成。
- [x] **底层数据库爆破与重建**：已执行。新增 `backend/app/models/saas.py`（`sys_tenant/sys_user/sys_tenant_user/resources/tasks/task_records/kb_documents/kb_chunks`），`tiku_init.sql` 已重写为多租户 clean schema+种子企业101。
- [x] **API 鉴权与中间件重构**：已执行。`security.py` 支持 tenant/super 声明；`api/deps.py` 新增 `get_current_tenant/require_admin/require_member/require_super_admin`；统一登录 `POST /api/v1/auth/login` 返回租户列表；`POST /register` 默认410（`?legacy=1` 仅回归测试）；新路由 `admin/members/resources/tasks/verifications/kb/super-admin` 全打通，旧路由挂 `/legacy-members` 兼容。
- [x] **全域 UI 词汇替换（基础链路）**：已执行。tob/toc 请求层自动带 `X-Tenant-ID`；tob 新增租户大盘 `/super-admin/tenants`+视察模式；tob/toc 登录改手机号+租户持久化；路由标题资源库/任务管理/核验大厅/数据看板/我的任务已映射。

## ✅ 交接清单（2026-09-09 全自动重构冻结）

- 后端验证：`pytest tests/ -q` **78 passed**；SQLite 内存建表 27 张（含新9张）通过；端到端10步（登录→录入成员→建资源→下任务→成员待办→提交→防重交→KB上传→溯源聊天）全通；跨租户写 403、上帝无头400、带头视察200 符合隔离红线。
- 前端验证：`tob pnpm build` 通过（13s），`toc pnpm build` 通过；旧 exams/questions/grading 等重型页面逻辑未动，仅改请求头/登录/标题/新增租户页，深层词汇与 E2E 待后续迭代。
- 已知缺口：旧 `exams/questions` 表仍保留兼容未删；`POST /api/v1/admin/ai/chat` 仍由旧 AI 通道占用，新溯源桩在 `/api/v1/admin/kb/chat`；`GET /api/v1/member/tasks` 返回含分页的超集结构；生产 MySQL 需执行新 `tiku_init.sql`（或 `Base.metadata.create_all` 自动建新表）。
- 下一步：深层 UI 文案批量替换、旧表数据迁移脚本、TiDB Vector 列切换、AI 生成链路强制写 `ai_rag_sources`。

## 🔥 第二阶段：彻底清洗（0 用户零兼容，2026-09-09 全自动执行）

- [x] **旧模型物理删除**：`models/` 仅剩 `saas.py`（10 表），删除 `user/exam/question/record/category/banner/audit/notification/ai_usage/ai_chat/rag` 共 11 个旧模型；`schemas/` 仅剩 `common+saas`；`services/` 仅剩 `ai_service`（纯 LLM 网关）。
- [x] **旧路由物理删除**：`api/admin/*` 14 文件与 `api/v1/*` 6 文件全删，仅保留统一登录 + `api/saas/*`（members/tasks/kb/ai/categories/super_admin）；`main.py` 移除旧表补列与全部旧挂载，接口从 86 收敛至 55 个纯 SaaS 路径。
- [x] **AI 通道对接新表**：`saas/ai.py` 出题/组卷/核验/对话全部读写 `resources/tasks/task_records` 并强制 `ai_rag_sources`，附兼容旧表单的 `/questions/generate`、`/exams/generate`（返回旧字段形状）；`tasks.py` 补齐资源/任务全量 CRUD（复制/批量/Excel导入/详情/统计/状态/核验详情）。
- [x] **测试基线重置**：15 个旧测试文件全删，仅 `tests/test_saas_pure.py` 7 用例（注册关闭/登录租户/隔离403/缺头400/成员全闭环/KB分权+AI溯源/上帝视图）。
- [x] **前端大洗牌**：tob `questions→resources`、`exams→tasks`、`grading→verification`、`rag→kb`（文件+组件+路由+菜单+API 前缀），删除 `types.ts` 生成旧客户端与 `UsersView`（路由重定向 members）；重写 Members/Verification/Kb/Copilot/资料弹窗/登录页；toc `quiz→task`、`mytests→my-tasks`，重写我的任务页。
- [x] **验证**：`pytest 7 passed`；冒烟 21/21；`tob build` 与 `toc build`（含 vue-tsc）全绿。
- **遗留运行时缺口（下阶段）**：AiAssistant 会话流、Dashboard/看板统计、Banners/消息/审计页、toc 答题/报告/收藏/首页列表仍调用已删除的旧接口（构建通过，运行时报错）；`scripts/e2e_selftest.py` 与根 `test_tools.py` 仍为旧契约，需重写或删除。

## 🩸 第三阶段：血管接通与运行时修复（2026-09-09 全自动执行）

- [x] **toc 核心闭环**：新增成员端 `saas/member.py`（作答入口/我的提交/成绩/收藏）+ `ResourceFavorite` 表；成员任务详情对 member 角色剥离答案防泄漏；重写 TaskView 数据层（入口/提交/收藏）、ReportView（核验中/得分/评语/本人作答）、IndexView（任务+分类+横幅）、MyTasks/History/Favorite 全对接；终端模拟成员链路 10/10（含泄漏断言与越权隔离）。
- [x] **B 端重型模块**：新增 `saas/ops.py`（看板聚合/banner CRUD+配置/上传/通知/审计）+ 4 张运营表；提交/核验/录入/上传/AI生成全链路写审计，提交/核验触发通知；Dashboard 通用化文案；`tob build` 全绿。
- [x] **AI 会话持久化**：新增 `AiSession/AiMessage` 表，对话落库用户+助手双消息及 `rag_sources`；会话列表/新建/改名/删除/游标消息全接口；重写 AiAssistantView（会话侧栏+溯源徽章+原文弹窗）；修复网关元组解包 bug（`chat_completion` 返回 `(content, tool_calls)`，5 处调用点经 `_ask` 归一）；Copilot 抽屉展示溯源。
- [x] **测试桩更新**：`scripts/e2e_selftest.py` 重写 31 项新契约（含空库一次性引导 `POST /super-admin/bootstrap`，自锁）；`test_tools.py` 改网关契约校验；实机 e2e（SQLite 服务+真实大模型）**31/31**；`pytest 9 passed`；双端 build 全绿。

## 🏁 第四阶段：生产就绪与终极收官（2026-09-09 全自动执行）

- [x] **ai-config 重写**：新增 `AiTenantConfig` 表 + 网关 provider 覆盖（租户优先、失败回退环境）；`GET /ai/config`（脱敏）、`PUT`（空密钥沿用旧值/clear 回退）、`POST /config/test`（真实连通探针）；重写模型配置页（总开关+连通测试+回退）。
- [x] **C 端计时防作弊**：入口落 `in_progress` 行锁定服务端开考时刻（重复进入不刷新）；提交时服务端结算用时（忽略客户端上报，限时截断）、校验发布态与截止；TaskView 倒计时锚定 `started_at/server_now`，删除超限清零后门。
- [x] **TiDB Vector 适配（严守本地模式）**：新增 `vector_store.py`（本地余弦+LIKE，`TIDB_VECTOR=1` 才走原生 `VEC_COSINE_DISTANCE`，异常回退，默认永不连云）；上传切片尽力向量化；`tiku_init.sql` 全量 18 表零演示数据 + Vector 备用段（注释）；新增 `DEPLOY.md`（本地/Docker/云端/向量启用/验证清单）；compose 与 render.yaml 对齐。
- [x] **验证**：`pytest 12 passed`；实机 e2e **33/33**（含真实 AI 与网关连通）；tob/toc 双 build 全绿。

## 🩹 线上排障实录（2026-09-09 रात，上帝无租户 400 事件）

- 现象：上帝登录后进首页，`dashboard/stats` 与 `notifications/unread-count` 同报 400 缺少 X-Tenant-ID。
- 根因：上帝无归属企业、无默认租户，前端发不出租户头，后端按铁律拦截。另发现线上 MySQL 卷为旧库，四张运营表为 v1.x 旧结构（`create_all` 不改已存在表）。
- 修复（方案 A+C，拒方案 B 保铁律）：后端无头上帝改 403 明示「请先选择视察企业」（+非法租户头 400）；路由守卫强制上帝落租户大盘；顶栏常驻视察企业切换器；登录清残留租户；缺头错误不再全局弹红；DROP 重建四张旧运营表。
- 验证（线上栈实测）：无头 403 指引 → 大盘选企业进入视察 → stats/unread/me 三接口 200；`pytest 12 passed`；tob 重打 `/admin/` 基线后 build 全绿。

## �հ�ҳ�ع��޸���2026-09-10��

- ����/admin/ �հף�����ȫͨ��������֤��������Ĭ�� base���� /admin/ �� dist ���ǳ� /assets/* ����·����
- �޸���tob ���� .env.production��VITE_BASE_URL=/admin/��+ vite.config ���� loadEnv����ͨ pnpm build ������ȷ���ߣ�����֤���� 200��


## UI�ذ������ղ��루2026-09-10��

- ��ҵ������A���š����Ž�����B��˾���ʯ���ţ�UPDATE sys_tenant����
- ���Ͽձ������򣺺�˽������� auth.py �޸ģ��� /me ���� profile �ֶΣ����������ã��Ժ�ĺ�˼ǵ� restart��
- ���ࣺ���⻧���� 12 ��Դ+8 ������࣬24 ��Ŀ�� 4 ����ȫ���������
- B��չʾ��ذڽ����ʻ㣺�Ծ�����/��Ŀ����/�ľ�����/AI֪ʶ��/�ҵ��Ŷӣ����İ���·����ӿڱ���ͨ��������progress �����ؼǣ���
- AI����/AI�����������Ĳο�˽���Ŀ�����Ų��߼�ѡ���۵��ڣ��ύ�߼���Ķ���


## ��ʾ���޸���2026-09-10��

- �Ŷ����������docker exec �� UPDATE �� GBK/TTY ˫�ر�����Ⱦ��HEX ȡ֤ CHAR_LENGTH=12������ pymysql utf8mb4 ��д�����ֽ�������
- �����˺ſհ׸���ͳһ��¼�� username �ֶΣ�store ȡ����Լ�ֶεÿգ���Ϊ phone���� + �������ˡ�
- ������� AI ģ��������ڣ�super+admin�����ҵ��Ŷӱ�ͷ��ҵ���ơ��Ŷ����ơ�


## �����İ�ͳһ��ȥ���棨2026-09-10��

- AI���ŵ�����AI�����Ծ����Ծ�����/�Ծ�����/����ʱ��/�Ծ��������������Ĭ����Ϊ��ʾ�����߼�ѡ�����Ŀ������Ĭ��10����������Ҫ��ʱǰ������������ͣ���� specs ԭ��֧�֣���Ķ�����
- �ֶ�����������½�/�༭�Ծ������������������������ɾ����������ҳչʾ���ύ���ء�CSS��tob+toc �б��� Hero ����ͬ���µ���CoverArt ����ļ���������
- AI����������AI������Ŀ��Ĭ������10�⣨����Ĭ��+�ط� count������Ŀ�Ѷ�/��������Ŀ�Ѷ�/��������ť������Ŀ�����棻���������ֶ������½���Ŀ���½���Ŀ��

