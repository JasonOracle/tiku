# 智题库 TiKu — 企业级多租户智能题库与在线考核闭环系统

轻量、现代化的 AI-Native 测评与考试平台：**B 端 SaaS 管理大屏**（题库资产/智能组卷/阅卷大厅/AI智能出题助手/成员与机构多租户隔离）+ **C 端移动端轻测评**（支持刷题/考试/答题卡/防泄题报告/错题收藏）+ **FastAPI 核心后端**。

- **GitHub 源码**: [https://github.com/JasonOracle/tiku](https://github.com/JasonOracle/tiku)
- **Gitee 镜像**: [https://gitee.com/jason-oracle/tiku](https://gitee.com/jason-oracle/tiku)
- **English Docs**: [README.en.md](./README.en.md)
- 📱 **C 端最新线上体验**: [智题库 (Cloudflare Pages)](https://tiku-toc-new.pages.dev/#/)
- ⚡ **云端 API 文档**: [https://tiku-api.vercel.app/docs](https://tiku-api.vercel.app/docs)
- 🎨 **v1.5 C 端全景快照指南**: [docs/v1.5_c_showcase.md](./docs/v1.5_c_showcase.md)
- 🖥️ **v1.4 B 端全景快照指南**: [docs/v1.4_showcase.md](./docs/v1.4_showcase.md)

---

## 🌐 线上与本地服务体验

| 端 / 服务 | 访问入口 | 测试账号 / 密码 | 说明 |
| :--- | :--- | :--- | :--- |
| **📱 C 端移动端 (公网最新)** | [https://tiku-toc-new.pages.dev](https://tiku-toc-new.pages.dev/#/) | `13900000001` / `123456` | Cloudflare Pages 托管，直连云端 TiDB 题库 |
| **💻 B 端管理后台 (本地)** | `http://localhost/admin` | `13800000012` / `123456` | 皓石集团企业管理员 (Admin) |
| **👑 B 端平台超管 (本地)** | `http://localhost/admin` | `13800000000` / `123456` | 平台最高超级管理员 (Super Admin) |
| **⚡ FastAPI 接口文档** | `https://tiku-api.vercel.app/docs` | — | OpenAPI / Swagger 交互式文档 |

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

- **v1.0 (MVP 基础闭环)**：
  - 打通单选、多选、判断客观题的录入、组卷、PC/H5 答题与自动秒级算分全链路，跑通产品第一代可行性模型。
- **v1.1 (数据治理与试卷锁定)**：
  - **试卷生命周期与锁定防篡改**：引入试卷“已上架锁定”机制（禁止考试期间随意篡改试题破坏严肃性），及格线百分比向上取整计算；
  - **分类与题目数据防护墙**：建立分类快照（`category_name`）与删除引用阻断保护，杜绝误删分类导致试卷题目孤儿化；
  - **C 端体验升级**：上线个人中心（SVG 头像与答卷记录）、考场误触防退出拦截，全面确立 SVG 矢量渲染规范。
- **v1.2 (AI-Native 能力跃升)**：
  - 引入填空题与主观简答题引擎；
  - 接入大模型实现主观题 AI 全托管/预批改阅卷；引入试卷按出题人隔离、成员额度管理与双域审计留痕。
- **v1.3 (私有知识库 RAG 命题与状态机治理)**：
  - **私有知识库与 RAG 命题闭环**：接入私有文档切片检索与向量召回，AI 出题自动标注原文切片依据，支持侧边抽屉原文高亮溯源；
  - **严苛的数据资产守卫**：确立试卷 `draft → published → archived` 状态机流转（归档终态不可逆锁定）；
  - **服务端权威防作弊**：开考入口锁定服务端开考时刻，杜绝客户端篡改本地时钟作弊。
- **v1.4 (SaaS 多租户架构与智能 Agent 交互革命)**：
  - **真正多租户隔离**：实现教育培训机构（如星雅教育）与企业合规考核（如皓石集团）的数据逻辑隔离与权限加固；
  - **AI 智能出题助手深度落地**：对话式批量出题卡片、智能组卷、安全合规防泄题拦截，消息与卡片执行状态数据库持久化（`action_card_data`）；
  - **自动化快照工程**：内置 Playwright 自动化截屏与文档生成引擎，双击批处理脚本即可一键生成系统最新图文快照。
- **v1.5 (C 端跨端原生重塑 · Apple 钛金微光风 - 最新已交付)**：
  - **设计系统升维**：全面推行 **Apple 钛金微光风 (Apple Light-Titanium Glassmorphism)** 规范，采用 `#fbfbfd` 冷钛白通透底盘搭配双色温漫反射呼吸微光；
  - **技术底座重塑**：从纯 H5 全面迁移重塑为 `uni-app` (Vue 3.5 + TypeScript + Vite + Pinia) 跨端原生工程；
  - **彻底去除外部抽象卡片**：单选、多选、双大胶囊判断、填空、简答全题型原生展开，拒绝多层黑盒组件嵌套，彻底杜绝移动端白屏与计算错位；
  - **考务级安全防泄题**：考试未核验公开（`pending_verification`）期间，在 DOM 层面物理阻断标准答案与试题解析的渲染；
  - **全链路云端交付**：前端成功上线 Cloudflare Pages（`https://tiku-toc-new.pages.dev`），后端托管于 Vercel Serverless，直连 TiDB Cloud 分布式数据库。

---

## 📸 系统全景快照 (Showcase)

### 一、v1.5 C 端移动端全景展示 (Apple 钛金微光风)

> 完整的高清图文指南请参阅 👉 **[v1.5 C端全景功能快照与视觉规范指南](./docs/v1.5_c_showcase.md)**

| 暮光微光登录 (Login) | 任务大厅首页 (Home) | 在线沉浸考场 (Exam) |
| :---: | :---: | :---: |
| ![C端登录](./docs/images/v1.5/01_toc_login.png) | ![C端首页](./docs/images/v1.5/02_toc_home.png) | ![C端考场](./docs/images/v1.5/03_toc_exam.png) |

| 我的测评进度 (Records) | 成绩复盘报告 (Report) | 个人中心与错题 (Profile) |
| :---: | :---: | :---: |
| ![我的测试](./docs/images/v1.5/04_toc_records.png) | ![成绩报告](./docs/images/v1.5/05_toc_report_done.png) | ![个人中心](./docs/images/v1.5/06_toc_profile.png) |

---

### 二、B 端管理后台全景展示 (v1.4 PC 桌面端)

> 完整的高清快照指南请参阅 👉 **[v1.4 系统功能快照与架构指南](./docs/v1.4_showcase.md)**

| 数据看板 (Dashboard) | 题目资产管理 (Questions) |
| :---: | :---: |
| ![数据看板](./docs/images/v1.4/01_tob_dashboard.png) | ![题目管理](./docs/images/v1.4/02_tob_resources.png) |

| AI 智能出题助手 (AI Assistant) | 试卷考核中心 (Exams) |
| :---: | :---: |
| ![AI 智能助手](./docs/images/v1.4/04_tob_ai_assistant.png) | ![试卷管理](./docs/images/v1.4/03_tob_tasks.png) |

---

## 🏗️ 模块技术拓扑

```
tiku/
├── backend/                  # FastAPI 核心（SaaS 多租户架构、JWT鉴权、AI出题与阅卷引擎）
├── tob/                      # B端管理后台（Vue 3.5 + Element Plus + Pinia + Vite）
├── toc-new/                  # [v1.5 最新交付] C端跨端全新工程（uni-app + Vue 3.5 + TS + Vite）
├── docs/                     # 系统对外版本展示与部署指南中心
│   ├── v1.5_c_showcase.md    # v1.5 C端 Apple 钛金微光风全景指南
│   ├── v1.4_showcase.md      # v1.4 B端系统功能快照报告
│   ├── deploy-free-cloud.md  # 零成本公网在线部署实战指南 (TiDB + Vercel + Cloudflare)
│   └── images/               # 各版本高清实况截屏资源
├── history/                  # 历史版本开发需求与方案归档（含 improveUI.v1.5.md, v1.4/v1.3 底稿）
├── scripts/                  # 自动化与快照工程
│   ├── snapshot_v1.5_c.py    # v1.5 C端 Playwright 自动化截屏与文档生成器
│   └── snapshot_showcase.py  # v1.4 B端自动化截屏脚本
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
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 2. 启动 B 端后台 (Vue 3 + Vite)
cd ../tob
pnpm install
pnpm dev

# 3. 启动 C 端考生端 (uni-app + Vite)
cd ../toc-new
pnpm install
pnpm dev:h5
```

---

## 🤖 关于本项目：AI-Native 研发范式实践

这个项目不仅是一套开箱即用的多租户智能题库系统，更是**人机协同与 AI 辅助软件工程 (AI-Driven Development) 的实战范式**：

1. **严格的宪法与行为约束**：通过根目录 [`agent.md`](./agent.md) 确立工程最高行为准则，实现“沟通即文档”、“零上下文损耗”与严格的数据隔离铁律。
2. **跨版本大更迭死生快照**：建立“第一阶段需求冻结 -> 第二阶段宪法重审 -> 第三阶段死生快照打 Tag 归档”的标准升版机制，确保每一代演进都有迹可循、随时可回滚。
3. **自动化自解释工程**：不仅编写业务代码，还构建了全自动页面快照生成器（`scripts/snapshot_v1.5_c.py` 与 `生成v1.5快照介绍文档.bat`），双击脚本即可全自动化生成最新实况文档。

---

## 📚 核心规范导航

- **[`agent.md`](./agent.md)** — **最高优先级！** AI Agent 进入本项目必须遵从的核心法律。
- **[`progress.md`](./progress.md)** — 项目实时事实来源、当前任务清单与踩坑指南。
- **[`product.md`](./product.md)** — 最新产品需求规格说明书 (PRD)。
- **[`tech-spec.md`](./tech-spec.md)** — 架构设计与技术规范白皮书。
- **[`api-contract.md`](./api-contract.md)** — 双端 API 契约与防泄题接口规范。
- **[`docs/`](./docs/)** — **对外展示中心**：各版本全景功能快照报告与高清图片。
- **[`history/`](./history/)** — **历史底稿归档区**：历代版本的 PRD、技术方案与进度历史记录。
