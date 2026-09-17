/**
 * [变更日志]
 * 修改时间：2026-09-17
 * AI模型：GLM (CodeBuddy)
 * 修改内容：[1. 移除已物理删除的 toc/ 残留与 docs/v1.5test/ 空目录；2. 待确认区两项全部销号：ops.py 双 router 语义查明并登记入职责表]
 */
/**
 * [变更日志]
 * 修改时间：2026-09-17
 * AI模型：GLM (CodeBuddy)
 * 修改内容：[初版建成：三端职责地图 + 机器可读清单块 + 陷阱区与待确认区；配套自检脚本 scripts/test_project_map.py 三层断言]
 */

# 智题库 (TiKu) 项目地图 (Project Map)

> **定位**：全项目目录的「物理布局 + 读取路由」。只回答**在哪、什么任务去哪**；不回答为什么这样设计（→ `tech-spec.md`）、进展如何（→ `progress.md`）、接口出入参（→ `api-contract.md`）。
>
> **元规则**：本地图的【结构声明】以文件系统实际状态为准（由 `scripts/test_project_map.py` 校验）；【职责语义】在被用户推翻前视为有效。
>
> **设计契约（任何模型修改本文件前必读，勿好心破坏）**：
> ① 粒度锁**目录级** + 极少数入口文件，严禁膨胀为完整文件树；② 凡有机器事实源的信息（`nginx.conf` / `package.json` / `tiku_init.sql`）只路由、绝不复制；③ 只写现状、不写规划；④ 体积预算 ≤150 行，内联日志只保留最近 3 条；⑤ 未查明的目录标【待确认】，禁止编造语义；⑥ 本地图可再生——内容可随时从文件系统 + 四大核心文档重新推导，允许在用户确认后整体重写。

## 0. 机器可读清单（自检脚本唯一解析面；增删目录必须同步此处）

```map-paths
# —— 后端 backend/ ——
backend/
backend/app/
backend/app/main.py            # FastAPI 入口（建表+幂等迁移+路由注册中心）
backend/app/api/
backend/app/api/v1/
backend/app/api/saas/
backend/app/api/deps.py
backend/app/core/
backend/app/services/
backend/app/models/
backend/app/schemas/
backend/app/data/              # 产物区（Mem0 本地存储）
backend/app/uploads/           # 产物区（用户上传文件，运行时生成）
backend/scripts/               # 数据修补/种子/审计脚本（区别于根 scripts/）
backend/tests/
backend/requirements.txt
backend/vercel.json            # 部署三处之一（后端云部署）
# —— B端 tob/ ——
tob/
tob/src/
tob/src/views/
tob/src/components/
tob/src/router/
tob/src/store/
tob/src/utils/
tob/src/assets/                # 资源区
tob/public/                    # 资源区
# —— C端 toc-new/ ——
toc-new/
toc-new/src/
toc-new/src/pages/
toc-new/src/components/
toc-new/src/api/
toc-new/src/stores/
toc-new/src/utils/
toc-new/src/static/            # 资源区
toc-new/src/styles/            # 资源区
toc-new/src/pages.json         # C端路由注册表（uni-app 约定）
toc-new/_redirects             # 部署三处之一（C端 Pages 跳转规则）
# —— 项目级 ——
scripts/                       # 项目级流水线（快照/文档生成/自检，区别于 backend/scripts/）
docs/
history/
assets/                        # 资源区（根级图片素材）
start.bat
nginx.conf                     # 部署三处之一（网关路由唯一真相）
docker-compose.yml
tiku_init.sql                  # 库表种子（结构真相：tech-spec.md / models/saas.py）
render.yaml
DEPLOY.md
README.md                      # 对人类的对外文档，非 AI 事实源
agent.md
progress.md
tech-spec.md
api-contract.md
product.md
```

## 1. 三端边界（路由唯一真相源：`nginx.conf`，此处仅概览）

- `/api/v1/*`、`/docs`、`/uploads/*` → **backend**（FastAPI，默认 :8000）
- `/admin/*` → **tob** B端管理台（构建 base='/admin/'）
- `/` → **toc-new** C端 H5（产物在 `toc-new/dist/build/h5`，注意 uni-app 多层级）
- `/api/v1/auth/`、`/api/v1/admin/ai/`、`/api/v1/member/ai/` 有 nginx 限流（429）

## 2. 目录职责速查

| 路径 | 职责 / 何时去 |
|---|---|
| `backend/app/main.py` | 后端入口：lifespan 建表 + 幂等迁移 + 全部路由注册。接手后端必读第一文件 |
| `backend/app/api/saas/` | 全部业务路由（admin / member 双前缀复用同一 router：ai、kb、tasks、members、categories、ops、super_admin）。改接口在此。**ops.py 运营底座**：admin_router=require_admin（看板/横幅 CRUD/上传/通知/审计），member_router=require_member（仅 C端横幅只读），并导出 write_audit / notify / notify_admins 供全局路由调用 |
| `backend/app/api/v1/auth.py` | 统一登录路由 |
| `backend/app/api/deps.py` | 路由依赖注入（租户上下文等） |
| `backend/app/core/` | config(settings) / database(engine) / security(JWT 鉴权) |
| `backend/app/services/` | ai_service(AI 网关) / memory_service(Mem0) / vector_store(向量检索) / db_migrate(幂等迁移) |
| `backend/app/models/saas.py` | 全部 ORM 模型单文件。改表结构先查 agent.md 第 4 条租户隔离红线 |
| `backend/app/schemas/` | Pydantic 出入参模型 |
| `backend/scripts/` | fix_*（数据修补）/ seed_*（种子）/ security_audit（审计）。改线上数据时谨慎使用 |
| `backend/tests/` | pytest（当前仅 `test_saas_pure.py`） |
| `tob/src/views/` | B端页面；**每个 .vue 配同名 .md 组件文档，改组件必须同步 .md** |
| `tob/src/router/index.ts` | B端路由表（唯一路由文件） |
| `tob/src/store/` | Pinia 状态（user / modelCenter） |
| `tob/src/utils/request.ts` | axios 请求封装 |
| `toc-new/src/pages/` | C端页面（同样 .vue 配 .md 惯例） |
| `toc-new/src/api/` | C端接口层（auth / exam） |
| `toc-new/src/utils/request.ts` | C端请求封装 |
| `scripts/` | 项目级：快照流水线、静态文档生成、e2e 自检、**本地图自检脚本** |
| `docs/` | 部署与展示文档（deploy-free-cloud.md、version_history.md、各版 showcase） |
| `history/` | 大版本归档（三大文档旧版快照、旧计划文件）。查历史真相在此 |

## 3. 启动路由（命令真相源：`start.bat` / 各 `package.json`；端口为动态信息）

- 一键三端：`start.bat`；后端：`cd backend && uvicorn app.main:app --port 8000 --reload`
- B端：`cd tob && pnpm dev`；C端：`cd toc-new && pnpm dev:h5`
- **端口动态**（曾因占用迁至 8001）：以 `progress.md` 最新记录为准

## 4. 陷阱区（AI 无法从文件系统自行推断的知识）

- `backend/app/api/admin/`、`backend/app/api/uploads/`：仅剩历史 pyc / 空目录，源码已并入 `api/saas/`，**勿在此开发**
- **双 scripts/**：根 `scripts/` = 项目级流水线；`backend/scripts/` = 数据修补。找自检脚本去根 `scripts/`
- **部署真相分散三处**：`nginx.conf` + `docker-compose.yml`（根目录）、`backend/vercel.json`、`toc-new/_redirects`——改部署行为三处都要查
- C端目录是 **toc-new**；旧 `toc/`（2026-09-17 403 事故死路径）已物理删除，历史日志中出现 "toc" 字样均指旧版勿混淆
- `backend/` 根下 `e2e.db`、`mock_acceptance.db`、`uvicorn_*.log`、所有 `*.pyc`：运行产物，非源码
- `tob/` 根下 `scan_heavy.py`、`scan_mc.py`：一次性分析脚本，非工程代码

## 5. 待确认（禁止猜测；逐个查明后更新此处并在 progress.md 销号）

当前无待确认项。
