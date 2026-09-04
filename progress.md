# 智题库 (TiKu) 全栈项目超详细交接与进度的归档文档 (progress.md)

> **最新更新时间**：`2026-09-04 22:55:00`
> **文档目的**：本交接文档为接手的 AI 模型/开发人员提供 100% 细节落地指南，包含代码实现原理、文件目录树、命令清单、数据契约、测试操作步骤及具体避坑 SOP，确保无缝接续开发。

---

## 🕒 变更与同步历史 (Change Logs)

| 更新时间 (YYYY-MM-DD HH:mm:ss) | 记录模型 / Agent | 本周期主要落地事项 | 当前整体进度 |
| :--- | :--- | :--- | :--- |
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
| `2026-09-04 21:35:00` | Gemini 3.1 Pro | **文档查漏补缺与 B 端/C 端需求同步**：1. 同步 B 端菜单层级调整（分类配置前置于题海管理）；2. 同步新建/导入题目时的“无分类阻断拦截”及必填校验；3. 同步题海列表与试卷选题的 `checkbox-group` 多选批量删除机制；4. 同步试卷题目的拖拽排序与 C 端答题 `is_random` 随机乱序机制；5. 备选题库改为模态弹窗形式。全面更新 PRD、技术规范及进度文档。 | **100%** |
| `2026-09-04 22:55:00` | Antigravity Agent | **交接与状态冻结**：1. 彻底修复前序由于 PowerShell 双引号转义导致的 B/C 端 SVG 图片裂开/格式错误（全量改写 10 个 SVG 矢量图，杜绝任何背景色干扰）；2. `tob/src/views/exams/ExamsView.vue` 增加挂载时的 SVG 日志输出以便追踪资源；3. 实库重置默认 admin 账号密码为 `123456`；4. 开发工作流由静态 Docker Nginx 构建切换回本地 Vite 实时开发服务器（5173/5174端口），打通 HMR。 | **100%** |




---

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
*验证成功标准：全量 18 项集成测试全部 PASSED（`test_auth` 3 + `test_quiz_engine` 1 + `test_status_isolation` 3 + `test_governance` 10 + 健康检查）。*

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

> **给新模型的提示**：请在接手后立即阅读本章节，当前项目已完成 **99%**，只剩 3 个细节 Bug / UI 优化待完成。

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

### 6.2 接手后需**立即落地**的 3 个具体任务 (Immediate Tasks)

#### 📌 任务 1: B 端试卷编辑中的备选题库区增加分页 (`tob/src/views/exams/ExamsView.vue`)
- **现状**：组卷弹窗下方“题库备选选择区”当前一次性请求 `size: 100`。
- **需要做**：
  1. 在 `ExamsView.vue` 中为 `poolFilter` 添加 `page: 1, size: 10, total: 0` 分页状态。
  2. 在 `<div class="pool-box">` 的 `<el-table>` 下方添加 `<el-pagination>` 组件。
  3. `loadQuestionPool()` 函数改为调用 `params: { type: poolFilter.type, keyword: poolFilter.keyword, page: poolFilter.page, size: poolFilter.size }`，并将返回的 `res.total` 赋给 `poolFilter.total`。

#### 📌 任务 2: C 端试卷未上架隔离 & 上架状态更新 404 修复
- **现状 A（C 端视效隔离）**：`backend/app/api/v1/exams.py` 中的 `list_exams` 路由需要确保强制只筛选 `status == 'published'` 的试卷（除非显式传入 `status` 过滤）。
- **现状 B（B 端上架 404）**：在 `backend/app/api/admin/admin_exams.py` 中，PUT 路由声明顺序可能导致 `/exams/{exam_id}/status` 被匹配到通用 `/exams/{exam_id}` 路由或响应 404。
  - **解决方案**：检查 `admin_exams.py` 路由声明顺序，将 `@router.put("/{exam_id}/status")` 声明放在 `@router.put("/{exam_id}")` **之前**，或者统一后端路由路径。

#### 📌 任务 3: C 端答题拦截与未答确认警示 (`toc/src/views/quiz/QuizView.vue`)
- **需求**：
  1. **提交按钮**：点“提交试卷”时，统计未作答题目数（`total_questions - answered_count`）。若有未作答题目，弹窗提示：`"您还有 X 道题未作答，确定要直接交卷吗？"`。
  2. **中途离开拦截**：使用 Vue Router 的 `onBeforeRouteLeave` 钩子，以及 `window.onbeforeunload` 监听器。若中途点返回/切换路由，弹窗警告：`"离开页面将自动提交试卷，确定要离开吗？"`。点击“确定”调用 `submitExam()` 提交并放行，点击“取消”取消跳转。

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
- 已上架卷引用的题目内容（题干/答案/分值）：**不锁定编辑**（已知历史口径漂移风险，暂接受）。
- 题目删除口径：**B方案**（仅拦上架/归档引用）。

---

## 8. 接手检查清单（新模型第一时间执行）
1. 读本文件 §7 治理矩阵 + §4 踩坑（尤其 4/5/6/7/8 条）。
2. `python -m pytest tests/ -v` 确认 18 通过；`tob/toc pnpm build` 确认通过。
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

