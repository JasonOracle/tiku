# 智题库 TiKu — 企业级多租户智能题库与在线考核闭环系统

轻量、现代化的 AI-Native 测评与考试平台：**B 端 SaaS 管理大屏**（题库资产/智能组卷/阅卷大厅/AI智能出题助手/成员与机构多租户隔离）+ **C 端移动端轻测评**（支持刷题/考试/答题卡/防泄题报告/错题收藏）+ **FastAPI 核心后端**。

- **GitHub**: [https://github.com/JasonOracle/tiku](https://github.com/JasonOracle/tiku)
- **Gitee**: [https://gitee.com/jason-oracle/tiku](https://gitee.com/jason-oracle/tiku)
- **English Docs**: [README.en.md](./README.en.md)
- **v1.4 功能快照与全景展示**: [docs/v1.4_showcase.md](./docs/v1.4_showcase.md)

---

## 📈 版本演进之路 (Milestones & Evolution)

本项目采用规范严谨的**敏捷递进开发**范式，每一个版本均具备清晰的阶段定位、物理成果物与可追溯的死生快照：

```
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│  v1.0 MVP │──>│ v1.1 治理 │──>│v1.2 AI阅卷│──>│v1.3 RAG命题│──>│v1.4 SaaS化│──>│ v1.5 Geek │
│基础客观题 │   │锁定/数据防│   │填空简答AI │   │私有文库溯源│   │多租户/卡片│   │Uni-app重塑│
└───────────┘   └───────────┘   └───────────┘   └───────────┘   └───────────┘   └───────────┘
  已归档(v1.0)    已归档(v1.1)    已归档(v1.2)    已归档(v1.3)    已归档(v1.4)    正在推进...
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
- **v1.4 (SaaS 多租户架构与智能 Agent 交互革命 - 当前稳定版)**：
  - **真正多租户隔离**：实现教育培训机构（如星雅教育）与企业合规考核（如皓石集团）的数据逻辑隔离与权限加固；
  - **AI 智能出题助手深度落地**：对话式批量出题卡片、智能组卷、安全合规防泄题拦截，消息与卡片执行状态数据库持久化（`action_card_data`）；
  - **自动化快照工程**：内置 Playwright 自动化截屏与文档生成引擎，双击批处理脚本即可一键生成系统最新图文快照。
- **v1.5 (C 端跨端原生重塑 · Apple 钛金微光风 - 最新已交付)**：
  - 采用 `uni-app` (Vue 3.5 + TS + Vite) 全面重塑 C 端移动端，奠定 **Apple 钛金微光风 (Light-Titanium Glassmorphism)** 视觉规范；
  - 彻底去除外部抽象卡片与多层黑盒嵌套，单选、多选、双大胶囊判断、填空与高对比度文本域原生内联，杜绝移动端白屏；
  - 强化考场简答题与填空题输入可视度（纯白微阴影背景 + 实体冷灰边框 + 深空蓝微光聚焦光晕）；
  - 统一成绩报告页内置标准白色微质感 Navbar（`solid` 模式），与出分看板及保密盾牌浑然天成；
  - 新增全自动无头快照脚本 `scripts/snapshot_v1.5_c.py` 与双击即跑的 `生成v1.5快照介绍文档.bat`。

---

## 📸 系统全景快照 (Showcase)

### 一、v1.5 C 端移动端全景展示 (Apple 钛金微光风)

> 完整的高清快照指南请参阅 👉 **[v1.5 C端全景功能快照与视觉规范指南](./docs/v1.5_c_showcase.md)**

| 暮光微光登录 (Login) | 任务大厅首页 (Home) | 在线沉浸考场 (Exam) |
| :---: | :---: | :---: |
| ![C端登录](./docs/images/v1.5/01_toc_login.png) | ![C端首页](./docs/images/v1.5/02_toc_home.png) | ![C端考场](./docs/images/v1.5/03_toc_exam.png) |

| 我的测评进度 (Records) | 成绩复盘报告 (Report) | 个人中心 (Profile) |
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
├── toc/                      # C端轻量答题端（Vue 3.5 H5）
├── toc-new/                  # [v1.5 演进中] C端跨端全新工程（uni-app + Wot Design Uni）
├── docs/                     # 系统对外版本展示中心（图文产品介绍与各端实况快照）
│   ├── v1.4_showcase.md      # v1.4 版本全景展示报告
│   └── images/v1.4/          # 12 张高清页面实况截图（供 README 与展示文档直接引用）
├── history/                  # 历史版本核心开发规范存档（包含 v1.3/v1.4 需求与进度底稿）
├── scripts/                  # 运维与自动化工具
│   ├── snapshot_showcase.py  # 全自动无头浏览器截图与文档生成引擎
│   └── ...
├── nginx.conf                # 统一网关路由（反代后端、B端、C端）
└── docker-compose.yml        # Docker 一键编排容器栈
```

---

## 🚀 快速启动

### 方式一：Docker Compose 一键启动（生产与集成）

```bash
# 启动 MySQL 8.0、FastAPI 后端与 Nginx 网关
docker compose up -d

# 若更新了前端静态资源或后端配置，重载 Nginx
docker exec tiku_nginx nginx -s reload
```

| 服务入口 | 访问地址 | 默认体验账号 / 密码 | 角色说明 |
| :--- | :--- | :--- | :--- |
| **B 端管理后台** | `http://localhost/admin` | `13800000012` / `123456` | 皓石集团管理员 (Admin) |
| **B 端超级管理** | `http://localhost/admin` | `13800000000` / `123456` | 平台超级管理员 (Super Admin) |
| **C 端考生端** | `http://localhost` | `13900000006` / `123456` | 皓石集团员工 (Member) |
| **Swagger API** | `http://localhost/docs` | — | FastAPI 交互式接口文档 |

---

## 🤖 关于本项目：AI-Native 研发范式实践

这个项目不仅是一套开箱即用的多租户智能题库系统，更是**人机协同与 AI 辅助软件工程 (AI-Driven Development) 的实战范式**：

1. **严格的宪法与行为约束**：通过根目录 [`agent.md`](./agent.md) 确立工程最高行为准则，实现“沟通即文档”、“零上下文损耗”与严格的数据隔离铁律。
2. **跨版本大更迭死生快照**：建立“第一阶段需求冻结 -> 第二阶段宪法重审 -> 第三阶段死生快照打 Tag 归档”的标准升版机制，确保每一代演进都有迹可循、随时可回滚。
3. **自动化自解释工程**：不仅编写业务代码，还构建了全自动页面快照生成器（`scripts/snapshot_showcase.py` 与 `生成v1.4快照介绍文档.bat`），实现软件自举式文档化。

---

## 📚 核心规范导航

- **[`agent.md`](./agent.md)** — **最高优先级！** AI Agent 进入本项目必须遵从的核心法律。
- **[`progress.md`](./progress.md)** — 项目实时事实来源、当前任务清单与踩坑指南。
- **[`product.md`](./product.md)** — 最新产品需求规格说明书 (PRD)。
- **[`tech-spec.md`](./tech-spec.md)** — 架构设计与技术规范白皮书。
- **[`api-contract.md`](./api-contract.md)** — 双端 API 契约与防泄题接口规范。
- **[`docs/`](./docs/)** — **对外展示中心**：各版本全景功能快照报告与高清图片。
- **[`history/`](./history/)** — **历史底稿归档区**：历代版本的 PRD、技术方案与进度历史记录（含 `progress_v1.3_legacy.md` 与 `v1.4` 系列）。
