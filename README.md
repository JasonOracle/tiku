# 智题库 TiKu — 企业级多租户智能题库与在线考核系统

轻量、现代化的 AI-Native 测评与考试平台。本项目不仅是一个全栈开源产品，更是一次**前端工程师通过 AI 赋能跨越边界，独立交付全套企业级 SaaS 系统**的深度工程化实践。

系统涵盖：**B 端 SaaS 管理大屏**（多租户隔离/智能组卷/AI智能出题助手）+ **C 端移动端沉浸式考场**（uni-app 跨端/防泄题报告/智能阅卷）+ **FastAPI 核心后端**。

- **GitHub 源码**: [https://github.com/JasonOracle/tiku](https://github.com/JasonOracle/tiku)
- **Gitee 镜像**: [https://gitee.com/jason-oracle/tiku](https://gitee.com/jason-oracle/tiku)
- **English Docs**: [README.en.md](./README.en.md)
- 🎨 **v1.5 C 端全景快照指南**: [docs/v1.5_c_showcase.md](./docs/v1.5_c_showcase.md)
- 🖥️ **v1.4 B 端全景快照指南**: [docs/v1.4_showcase.md](./docs/v1.4_showcase.md)
- 📖 **零成本云端部署教程**: [docs/deploy-free-cloud.md](./docs/deploy-free-cloud.md)

---

## 🌐 线上公网体验 (Live Demo)

本系统的 C端与 B端已全面部署至云端 (Cloudflare Pages + Vercel Serverless + TiDB Cloud)，**无需任何本地配置，点击即可体验**：

| 端 / 服务 | 访问入口 (公网直连) | 测试账号 / 密码 | 说明 |
| :--- | :--- | :--- | :--- |
| **📱 C 端移动端 (考生版)** | [https://tiku-toc-new.pages.dev](https://tiku-toc-new.pages.dev/#/) | `13900000001` / `123456` | Cloudflare 托管，uni-app 跨端原生重塑 |
| **💻 B 端管理台 (机构版)** | [https://tiku-tob.pages.dev/dashboard](https://tiku-tob.pages.dev/dashboard) | `13800000012` / `123456` | 皓石集团企业管理员 (SaaS 租户隔离) |
| **⚡ FastAPI 云端接口** | [https://tiku-tob.pages.dev/docs.html](https://tiku-tob.pages.dev/docs.html) | — | Cloudflare 托管静态 Swagger，国内公网直连秒开（备用直连：[Vercel Docs](https://tiku-api.vercel.app/docs)） |

---

## 💡 工程亮点与架构突破 (Architecture & Highlights)

```mermaid
graph TD
    subgraph 客户端 (Client Layer)
        C[C端移动端 <br> uni-app / Vue3]
        B[B端管理台 <br> Vue3 / Element Plus]
    end

    subgraph 统一网关层
        Nginx[Nginx 反向代理 <br> JWT 双域鉴权隔离]
    end

    subgraph 核心服务层 (Backend Layer)
        FastAPI[FastAPI 核心业务 <br> 考试状态机 / 多租户管理]
    end

    subgraph AI引擎与底座 (AI & Data)
        LLM[大模型 API <br> 对话式出题 / 自动阅卷]
        RAG[知识库 RAG <br> 私有文档切片溯源]
        TiDB[(TiDB Cloud 分布式库)]
    end

    C <--> Nginx
    B <--> Nginx
    Nginx <--> FastAPI
    FastAPI <--> LLM
    FastAPI <--> RAG
    FastAPI <--> TiDB
```

本项目重点突破了在线考核系统的三大工程痛点：

### 1. 🤖 AI-Native 的工程化落地与控制边界
作为项目的核心策划者，我清晰界定了 AI 的能力边界，没有盲目追求底层算法，而是将重点放在**“AI 与前端大屏的工程化结合”**：
- **AI 对话式智能命题与组卷**：突破传统表单录入，我设计并实现了基于 LLM 的对话交互界面。通过严谨的结构化 Prompt 契约，支持根据岗位、知识点自动批量生成单选、多选、填空甚至整套试卷，大幅降低教务人员制卷成本。
- **AI 风险操控卡片 (Action Cards)**：为了让大模型输出处于绝对可控的业务边界内，我构思了交互式的“操作卡片”机制。AI 并不直接越权写入题库，而是渲染一张包含题目详情的“拟态预审卡片”，由管理员最终审核（采纳/抛弃），实现了高确定性的系统级风险管控。
- **AI 长期记忆与状态持久化**：针对复杂的出题场景，我打通了 AI 会话状态与大屏工作流，将多轮对话记录与操作卡片数据（`action_card_data`）深度持久化到 TiDB，赋予了智能助手长期记忆与连贯上下文的能力，确保 AI 随时能够回溯之前的修改意图。

### 2. 🚀 前端跨端重塑与多租户 SaaS 隔离
- **C端原生级去抽象重构**：v1.5 版本放弃了厚重的多层嵌套黑盒抽象，基于 `uni-app` (Vue 3.5 + Vite) 进行了跨端原生重构。所有题型（单选、多选、双大胶囊判断、填空、简答）采用直白平铺的扁平化渲染方案，彻底杜绝了移动端白屏与计算错位。
- **SaaS 级多租户逻辑隔离**：在 Vue3/Pinia 与 FastAPI 配合下，实现了真正的多租户环境。无论是企业合规考核（如皓石集团）还是教育培训（如星雅教育），均能在同一个平台上实现完美的数据物理与逻辑隔离。
- **Apple 钛金微光风设计语言**：系统全面推行 `#fbfbfd` 冷钛白通透底盘与双色温漫反射呼吸微光，兼顾极客感与高级审美。

### 3. 🛡️ 极其苛刻的安全防御与防作弊机制
- **DOM 级物理防泄题**：针对在线考试的“抓包”和“审查元素”作弊痛点，我在前端及服务端实施了双端拦截。在试卷未核验状态（`pending_verification`）下，服务端直接剔除答案节点并阻断解析下发，前端 DOM 物理层面毫无痕迹。
- **强力时钟同步与状态机锁**：
  - 考试倒计时完全锚定服务端开考时间戳，无视客户端本地时钟篡改。
  - 试卷遵循 `draft → published → archived` 强状态机单向流转。试卷一旦锁定上架，即冻结所有题库修改动作，杜绝“考试中途篡改题目”。

---

## 📸 系统全景快照 (Showcase)

### 一、v1.5 C 端移动端全景展示 (Apple 钛金微光风)
> 完整高清指南 👉 **[v1.5 C端全景功能快照与视觉规范指南](./docs/v1.5_c_showcase.md)**

| 暮光微光登录 (Login) | 任务大厅首页 (Home) | 在线沉浸考场 (Exam) |
| :---: | :---: | :---: |
| ![C端登录](./docs/images/v1.5/01_toc_login.png) | ![C端首页](./docs/images/v1.5/02_toc_home.png) | ![C端考场](./docs/images/v1.5/03_toc_exam.png) |

| 我的测评进度 (Records) | 成绩复盘报告 (Report) | 个人中心与错题 (Profile) |
| :---: | :---: | :---: |
| ![我的测试](./docs/images/v1.5/04_toc_records.png) | ![成绩报告](./docs/images/v1.5/05_toc_report_done.png) | ![个人中心](./docs/images/v1.5/06_toc_profile.png) |

---

### 二、B 端管理后台全景展示 (v1.4 PC 桌面端)
> 完整高清指南 👉 **[v1.4 系统功能快照与架构指南](./docs/v1.4_showcase.md)**

| 数据看板 (Dashboard) | 题目资产管理 (Questions) |
| :---: | :---: |
| ![数据看板](./docs/images/v1.4/01_tob_dashboard.png) | ![题目管理](./docs/images/v1.4/02_tob_resources.png) |

| AI 智能助手与操控卡片 (AI Assistant) | 试卷考核中心 (Exams) |
| :---: | :---: |
| ![AI 智能助手](./docs/images/v1.4/04_tob_ai_assistant.png) | ![试卷管理](./docs/images/v1.4/03_tob_tasks.png) |

---

## 🏗️ 模块技术拓扑

```
tiku/
├── backend/                  # FastAPI 核心（状态机、多租户鉴权、AI引擎网关）
├── tob/                      # B端管理后台（Vue 3.5 + Element Plus + Pinia + Vite）
├── toc-new/                  # [v1.5 最新交付] C端跨端全新工程（uni-app + Vue 3.5 + TS）
├── docs/                     # 系统对外版本展示与部署指南中心
├── history/                  # 历史版本开发需求与方案归档
├── scripts/                  # 自动化测试与快照工程引擎 (Playwright)
├── nginx.conf                # 统一网关路由（反代后端、B端、C端）
└── docker-compose.yml        # Docker 一键编排容器栈
```

---

## 🚀 快速启动

### 方式一：Docker Compose 一键启动（本地全套）
```bash
# 启动 MySQL 8.0、FastAPI 后端与 Nginx 网关
docker compose up -d

# 若更新了前端静态资源或后端配置，重载 Nginx
docker exec tiku_nginx nginx -s reload
```

### 方式二：本地分端开发启动
```bash
# 1. 启动后端 (FastAPI)
cd backend && python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. 启动 B 端后台 (Vue 3 + Vite)
cd ../tob && pnpm install && pnpm dev

# 3. 启动 C 端考生端 (uni-app + Vite)
cd ../toc-new && pnpm install && pnpm dev:h5
```

---

## 📝 开发者自白 (Developer's Note)

作为一个具有前端开发背景的工程师，在当前充满挑战的行业周期中，本项目是我对 **AI-Driven Development (AI 驱动开发)** 的一次深度探索。

在整个研发周期中，我不仅独立负责了从 H5 到 uni-app 的前端跨端重构，深入攻克了移动端渲染性能与复杂的多租户状态管理（Pinia），**更担任了该项目的“架构师与 Orchestrator”**。我清晰地划定了业务需求与 AI 能力的工程边界，借助大模型跨越了后端与数据库的语言壁垒，从 0 到 1 成功搭建了 FastAPI 核心服务与 TiDB 分布式底座的全栈闭环。

这个项目使我坚信：现代开发者的核心护城河，已不再是拘泥于单一语言的语法细节，而是**对复杂系统的全局掌控力、清晰的业务边界感，以及将 AI 转化为实际工程生产力的落地执行能力**。这也是我一以贯之的开发哲学，并一直保持着对新技术的极度渴望与持续学习。

---

## 📈 版本演进之路 (Milestones & Evolution)

本项目采用规范严谨的**敏捷递进开发**范式，每一个版本均具备清晰的阶段定位、物理成果物与可追溯的死生快照：

```
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│  v1.0 MVP │──>│ v1.1 治理 │──>│v1.2 AI阅卷│──>│v1.3 RAG命题│──>│v1.4 SaaS化│──>│v1.5 钛金微光│
│基础客观题 │   │锁定/数据防│   │填空简答AI │   │私有文库溯源│   │多租户/卡片│   │Uni-app重塑│
└───────────┘   └───────────┘   └───────────┘   └───────────┘   └───────────┘   └───────────┘
  已归档(v1.0)    已归档(v1.1)    已归档(v1.2)    已归档(v1.3)    已归档(v1.4)    已交付(v1.5)
```

- **v1.0 (MVP 基础闭环)**：打通客观题录入、组卷、答题与秒级算分全链路。
- **v1.1 (数据治理与试卷锁定)**：引入“已上架锁定”防篡改机制及删除阻断保护。
- **v1.2 (AI-Native 能力跃升)**：引入大模型主观题预批改阅卷与租户限额审计。
- **v1.3 (RAG 命题与状态机)**：私有文档向量检索高亮溯源，确立 `draft → published → archived` 状态机。
- **v1.4 (SaaS 架构与智能 Agent)**：真正多租户逻辑隔离落地，引入 AI 批量出题操作卡片。
- **v1.5 (C 端跨端原生重塑)**：Apple 钛金微光风设计语言，基于 `uni-app` 去除黑盒嵌套，实现 DOM 级防泄题拦截。

---

## 📚 核心规范导航
- **[`agent.md`](./agent.md)** — **最高优先级！** 确立工程最高行为准则。
- **[`progress.md`](./progress.md)** — 项目实时事实来源、当前任务清单与踩坑指南。
- **[`product.md`](./product.md)** — 最新产品需求规格说明书 (PRD)。
- **[`tech-spec.md`](./tech-spec.md)** — 架构设计与技术规范白皮书。
- **[`api-contract.md`](./api-contract.md)** — 双端 API 契约与防泄题接口规范。
