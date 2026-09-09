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
- [ ] **底层数据库爆破与重建**：待执行（正在确认最终实体命名）。
- [ ] **API 鉴权与中间件重构**。
- [ ] **全域 UI 词汇替换**。
