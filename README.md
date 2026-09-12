# 智题库 TiKu — 企业级多租户智能题库与在线考核闭环系统

轻量、现代化的 AI-Native 测评与考试平台：**B 端 SaaS 管理大屏**（题库资产/智能组卷/阅卷大厅/AI智能出题助手/成员与机构多租户隔离）+ **C 端移动端轻测评**（支持刷题/考试/答题卡/防泄题报告/错题收藏）+ **FastAPI 核心后端**。

- **GitHub**: [https://github.com/JasonOracle/tiku](https://github.com/JasonOracle/tiku)
- **Gitee**: [https://gitee.com/jason-oracle/tiku](https://gitee.com/jason-oracle/tiku)
- **English Docs**: [README.en.md](./README.en.md)
- **v1.4 功能快照与全景展示**: [docs/v1.4_showcase.md](./docs/v1.4_showcase.md)

---

## 📈 版本演进之路 (Milestones & Evolution)

本项目采用规范严谨的**敏捷递进开发**范式，每一个版本均具备可验证的工程交付物与版本快照：

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     v1.0 MVP    │  ──>  │  v1.2 AI-Native │  ──>  │ v1.4 SaaS & Agent│ ──>  │   v1.5 Geek App │
│  基础客观题闭环 │       │ 简答填空/AI预阅卷│       │多租户/AI对话卡片 │       │Uni-app移动端重塑 │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
  已归档 (v1.0-tag)         已归档 (v1.2-tag)         已归档 (v1.4-final)         当前正在推进中...
```

- **v1.0 (MVP 闭环)**：打通基础单选/多选/判断客观题录入、组卷、PC/H5 考试与自动算分全链路。
- **v1.2 (AI-Native 能力跃升)**：引入填空题与主观简答题引擎；集成大模型实现主观题 AI 全托管/预批改阅卷；引入试卷按老师隔离与审计日志。
- **v1.4 (SaaS 架构与智能 Agent 交互革命 - 当前稳定版)**：
  - **真正的多租户数据隔离**：支持教育培训机构（如星雅教育）与企业合规考核（如皓石集团）逻辑物理隔离与权限加固；
  - **AI 智能助手深度落地**：支持自然语言批量出题、智能组卷、安全合规防泄题校验，会话卡片历史落库持久化（`action_card_data`）；
  - **自动化快照工程**：内置 Playwright 自动化截屏与文档生成引擎，双击即可一键生成版本图文快照。
- **v1.5 (跨端极客重构 - 正在开发)**：
  - 采用 `uni-app` (Vue3 + TS + Vite) + `Wot Design Uni` 全面重塑 C 端移动端；
  - 极客蓝 (Geek Blue) 沉浸式风格，纯 SVG 规范，单题聚焦作答流与安全防泄题动态报告。

---

## 📸 系统全景快照 (v1.4 Showcase)

> 完整的高清快照指南请参阅 👉 **[v1.4 系统功能快照与架构指南](./docs/v1.4_showcase.md)**

### B 端管理后台 (PC 桌面端)

| 数据看板 (Dashboard) | 题目资产管理 (Questions) |
| :---: | :---: |
| ![数据看板](./docs/images/v1.4/01_tob_dashboard.png) | ![题目管理](./docs/images/v1.4/02_tob_resources.png) |

| AI 智能出题助手 (AI Assistant) | 试卷考核中心 (Exams) |
| :---: | :---: |
| ![AI 智能助手](./docs/images/v1.4/04_tob_ai_assistant.png) | ![试卷管理](./docs/images/v1.4/03_tob_tasks.png) |

### C 端考生端 (移动端 iPhone 视口)

| 企业空间首页 | 测评任务列表 | 个人资产中心 |
| :---: | :---: | :---: |
| ![C端首页](./docs/images/v1.4/08_toc_home.png) | ![我的测评](./docs/images/v1.4/09_toc_my_tasks.png) | ![个人中心](./docs/images/v1.4/10_toc_profile.png) |

---

## 🏗️ 模块技术拓扑

```
tiku/
├── backend/                  # FastAPI 核心（SaaS 多租户架构、JWT鉴权、AI出题与阅卷引擎）
├── tob/                      # B端管理后台（Vue 3.5 + Element Plus + Pinia + Vite）
├── toc/                      # C端轻量答题端（Vue 3.5 H5）
├── toc-new/                  # [v1.5 演进中] C端跨端全新工程（uni-app + Wot Design Uni）
├── docs/                     # 系统版本快照与图文产品介绍
│   ├── v1.4_showcase.md      # v1.4 版本全景展示报告
│   └── images/v1.4/          # 12 张高清页面实况截图
├── history/                  # 历史版本核心技术文档存档（v1.3 / v1.4 归档）
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
- **[`history/`](./history/)** — 历代版本的核心技术文档归档区。
