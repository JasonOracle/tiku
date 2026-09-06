# 智题库 (TiKu) 产品技术说明书 (Technical Specification)

## 1. 架构总览与项目结构

### 1.1 项目三元架构
```
tiku/
tiku/
├── toc/                     # C端移动端 Web 项目 (Vue3 + Vite + Vue Router)
│   ├── src/
│   │   ├── views/           # 页面视图 (IndexView, QuizView, ReportView, FavoriteView, ProfileView, HistoryView)
│   │   ├── components/      # 核心组件 (NavBar 统一导航, CoverArt 矢量封面, BannerCarousel 轮播)
│   │   ├── router/          # 路由配置
│   │   └── utils/http.ts    # Axios 统一封装与拦截器
│   └── public/              # 静态资源与 SVG 插画
├── tob/                     # B端 SaaS 管理后台 (Vue3 + Element Plus)
│   ├── src/
│   │   ├── views/
│   │   │   ├── questions/   # 题海管理 (列表+Excel导入)
│   │   │   ├── exams/       # 试卷组卷与配置 (支持封面上传)
│   │   │   ├── categories/  # 分类管理
│   │   │   └── users/       # 用户与答题明细
│   │   ├── store/           # Pinia (Token存储: tiku_tob_token)
│   │   └── utils/request.ts # HTTP 拦截器
├── backend/                 # FastAPI 后端项目 (Python 3.12)
│   ├── app/
│   │   ├── api/             # 路由控制
│   │   │   ├── v1/          # C端 API (/api/v1/*)
│   │   │   └── admin/       # B端 API (/api/v1/admin/*)
│   │   ├── core/            # 配置、JWT (7天有效)、数据库连接
│   │   ├── models/          # SQLAlchemy ORM 数据模型
│   │   ├── uploads/         # 本地图片/媒体上传目录
│   │   └── services/        # 核心业务逻辑 (评分引擎/被动超时结算/悲观锁)
│   └── tests/               # pytest 自动化集成与单元测试
├── api-contract.md          # 接口契约测试文档
├── product.md               # 产品需求规格说明书
└── direction-approved.md    # 选定设计语言规范
```

---

## 2. 关键核心机制与设计方案

### 2.1 MVP 版本架构范围限制
> **注意**：本项目当前处于 MVP（最小可行性产品）阶段。为保证核心逻辑的快速跑通，当前技术架构与数据库设计**仅支持客观题型（单选、多选、判断）及全自动评分引擎**。
> 简答题/填空题设计、后台人工阅卷工作流状态机，以及多账号角色权限管理（RBAC 鉴权机制）的表结构与 API，均被推迟至 V2 版本迭代，当前不包含在内。

### 2.2 多账号并发登录与抢先提交逻辑 (First-Submit-Wins)
- **Token 隔离与生命周期**：
  - C端 (`toc`) 保存 Key 为 `tiku_toc_token`。
  - B端 (`tob`) 保存 Key 为 `tiku_tob_token`。
  - Token 有效期设为 7 天 (7*24h)，交卷时支持 5 分钟宽限期验证，防止考试中途断连。
- **防止重复交卷悲观锁处理 (Python/FastAPI)**：
  ```python
  def submit_exam_record(db: Session, record_id: int, user_id: int, answers: list):
      # 悲观锁锁定答题记录
      record = db.query(ExamRecord).filter(
          ExamRecord.id == record_id, 
          ExamRecord.user_id == user_id
      ).with_for_update().first()

      if not record:
          raise HTTPException(404, "答题记录不存在")
      
      if record.status != "in_progress":
          raise HTTPException(400, "该试卷答题记录已被提交结算，请勿重复提交！")
      
      # 检查是否已在客户端超期
      record.status = "submitted"
      record.submit_time = datetime.now()
      db.commit()
      return record
  ```

### 2.2 考试超时与“幽灵记录”被动结算机制
在 C端调用 `POST /api/v1/records/start` 或查询试卷详情时，服务端会自动检查该用户未完成的 `in_progress` 记录：
```python
def cleanup_expired_records(db: Session, user_id: int):
    # 查找所有当前已超期的 in_progress 记录
    now = datetime.now()
    records = db.query(ExamRecord).join(Exam).filter(
        ExamRecord.user_id == user_id,
        ExamRecord.status == "in_progress",
        Exam.is_timed == True,
        # 加上 2 分钟缓冲网络容错
        func.timestampdiff(func.MINUTE, ExamRecord.start_time, now) > (Exam.time_limit + 2)
    ).all()
    
    for r in records:
        r.status = "timeout"
        r.submit_time = now
    db.commit()
```

### 2.3 文件上传与 Nginx 静态文件代理
- 上传接口：`POST /api/v1/admin/upload`
- 存储路径：`backend/app/uploads/`
- Nginx 反向代理配置：
  ```nginx
  location /uploads/ {
      alias /app/uploads/;
      expires 30d;
  }
  ```

### 2.4 分页数据结构设计 (Standardized Pagination)
所有列表接口返回格式统一包装：
```python
class PageResponse(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    total_pages: int
    has_next: bool
    items: List[T]
```

### 2.5 数据模型字段扩展与算法调整（2026-09-04 治理版）
1. **试卷生命周期与组卷**：
   - 增加 `is_random` 布尔值，用于控制 C 端答题乱序引擎。
   - B 端组卷引入 `checkbox-group` 批量管理（题海多选删除、弹窗备选批量加入、已选题批量移除）及已选题目的拖拽排序。
   - `draft → published → archived`，`archived` 为彻底终态。下架 = `published → archived`；上架经 `ensure_publishable` 校验有效分类并写入 `category_name` 快照。
2. **删除守卫矩阵**：分类被引用拦；题目被 published/archived 卷引用拦（报卷名），仅 draft 引用联动移除 + `recalc_exam_totals` 重算；试卷仅 draft 零作答可删。
3. **空卷拦截**：`submit_exam_record_with_lock` 零作答 400；C端 0 作答离开/超时不提交。
4. **导入行级分类**：按表头“分类”列逐题归入（不存在自动新建，空取第一项）；`short/fill` 预留题型跳过计数；读首工作表（`sheetnames[0]`）。
5. **同源部署**：前后端 `baseURL: ''` 走 Nginx `/api/v1/` 代理；`vite server.proxy` 保开发；B端 401 跳 `/admin/login`；backend 重建后必须 `nginx -s reload`。
6. **第一项口径**：分类列表 `(sort_order,id)` 双排序，前端默认与后端兜底同源。
7. **Banner 模块**：`banners`（image/link三态/sort/enabled，上限3启用）+ `banner_settings` 单行（interval 2–10s）；C端合一接口 `{interval_seconds, items}`；1张静显、>1自播+手滑、0张回退推荐 Hero；内部跳转仅 `/` 开头。
8. **C端 UI 改版**（效果图为准）：抽公共 `TabBar.vue`；封面 `CoverArt.vue` 移除所有渐变/底色，纯渲染 raw SVG；报告圆环按真实总分；引入 `AppModal.vue` 实现毛玻璃自定义弹窗全面替换原生 `confirm/alert`。

### 2.6 原数据模型字段扩展与算法调整（历史）
1. **ExamCategory 分类模型**：
   - 增加 `target_type`: 分类用途标识（`question` 题目分类 / `exam` 试卷分类，默认 `exam`）。
2. **Question 题目模型**：
   - `category_id`: 外键关联 `target_type='question'` 的题目分类。
   - `score`: 题目默认分值（`int`，默认 10）。
3. **Exam 试卷模型**：
   - `category_id`: 外键关联 `target_type='exam'` 的试卷分类。
   - `status`: 三态（`draft` 待上架 / `published` 已上架 / `archived` 已归档冻结，终态不可逆）。
   - `category_name`: 上架时写入的分类名称快照，展示层优先使用。
   - `is_random`: 题目是否随机打乱呈现（`bool`，默认 `false`）。
   - `pass_percent`: 及格百分比（`int`，0-100，默认 60）。
   - `total_score` 计算规则：由试卷关联的所有 `Question.score` 动态求和。
   - `pass_score` 计算规则：`Math.ceil(total_score * pass_percent / 100.0)` 向上取整。
4. **C 端 ProfileView 与考情看板数据流**：
   - 个人中心实时调用 `/api/v1/users/me/stats` 获取作答场次与综合通过率。
   - B 端试卷列表对 `status='published'` 试卷锁定编辑，点击调用 `/api/v1/admin/exams/{id}/stats` 获取考情看板明细。

---

## 3. 部署架构设计 (Docker Containerization)

### 3.1 Nginx 反向代理配置与容器拓扑
```
                     ┌───────────────────────────────────────────┐
                     │          Debian NAS Docker 宿主机          │
                     │                                           │
 浏览器 (tob) ──────►│  Nginx 容器 (Port 80/443)                 │
 手机 H5 (toc) ──────►│    ├── /api/v1/admin  ──► backend:8000     │
                     │    ├── /api/v1        ──► backend:8000     │
                     │    ├── /uploads/      ──► backend/uploads │
                     │    ├── /admin         ──► tob 静态构建产物   │
                     │    └── /              ──► toc 静态构建产物   │
                     │                                           │
                     │  FastAPI 容器 (Port 8000)                 │
                     │    └── MySQL 容器 (Port 3306)              │
                     └───────────────────────────────────────────┘

---

## 4. v1.2 版本实现指北 (Implementation Guide for AI Developer)

> **✅ v1.2 已于 2026-09-06 全量落地（ZCode GLM）**：下方 Step 1–5 全部实现并通过 39 项 pytest 与实库真 AI 阅卷验证。接手者请以下方【落地实况】为准，并同步阅读 `progress.md` §6.0/§7.6。
>
> **【落地实况 · 大模型接入定案】**
> - API Key：宿主机用户系统环境变量 `SENSENOVA_API_KEY`，代码 `os.getenv()` 读取；`D:\docker\docker-compose.yml` 已透传 `SENSENOVA_*` 至容器。
> - **网关与模型（实测有效）**：`https://token.sensenova.cn/v1/chat/completions` + `sensenova-6.8-flash-lite`（免费档）。老网关 `api.sensenova.cn` 会返回 Forbidden；`sensenova-6.7-flash-lite` 无路由；`deepseek-v4-flash/glm-5.2` 免费档配额不足；`deepseek-v4-pro` 为思考型（content 为空）勿用作阅卷。可用模型清单：`GET /v1/models`。
> - 兜底实测有效：模型输出 markdown 代码块/多余文字时，`ai_service.extract_json` 可鲁棒提取 JSON。

> **⚠️ 致接手此项目的 AI 或人类开发者**：
> 下方是严格按照 MVP（最小可行性产品）和“AI平权”原则拆解的技术落地步骤。若遇技术瓶颈，请严格参考下方的**【平替方案/兜底逻辑】**，切勿自行增加过度复杂的设计。

### Step 1: 数据库核心表结构扩展 (MySQL / SQLAlchemy)
- **`admins` 表**：新增 `role` (enum: 'super_admin', 'admin', 'ai') 和 `daily_ai_quota` (int, default: 0)。
  - *兜底方案*：如果不写定时任务恢复每天的额度，可直接改存 `quota_reset_date`，每次扣减前校验日期并重置。
- **`questions` 表**：
  - 新增 `is_deleted` (bool, default: false) 实现软删除。
  - 修改 `answer` 字段：必须兼容 JSON 数组（供填空题使用）。
- **`exams` 表**：新增 `start_time` (datetime), `end_time` (datetime), `is_ai_auto_grade` (bool, default: false)。
- **`exam_records` 表**：
  - 修改 `status` 枚举，新增 `pending_grading`（待批阅）。
  - 新增字段 `ai_grading_result` (JSON, 存储 AI 预批改的详情与建议分数)。
- **新增 `audit_logs` 表**：记录双域留痕（id, admin_id, action_type, before_data, after_data, created_at）。

### Step 2: 题库重构与客观题/填空题引擎升级
- **填空题多空校验**：
  - 在 `POST /api/v1/admin/questions` 中，如果 `type == 'fill'`，后端强制执行：`question.title.count('___') == len(json.loads(question.answer))`，不等则抛 `HTTP 400`。
- **多选题半对机制**：
  - 修改原交卷接口 `/api/v1/records/submit` 的评分引擎。多选题的判断逻辑变为：`如果 user_answer 是 correct_answer 的真子集，得 50% 分；只要存在交集以外的元素，得 0 分`。

### Step 3: 僵尸卷子“懒惰求值” (Lazy Evaluation)
- **技术实现**：在获取 C 端试卷列表 (`GET /api/v1/exams`) 和 B 端阅卷大厅时，拦截查询前置动作。
  - `UPDATE exam_records SET status = 'submitted' WHERE status = 'in_progress' AND now() > start_time + time_limit`。
  - *平替方案*：绝不能用 Celery/Redis。哪怕只在 `POST /api/v1/records/submit` 被别的接口碰巧触发时清理，也比部署定时任务强。必须保持 0 运维基建。

### Step 4: AI 全托管阅卷底层调度 (FastAPI BackgroundTasks)
- **开发期指定大模型 (SenseNova)**：
  - **重要约束**：开发期间统一使用**商汤日日新大模型 (SenseNova)**，因其免费。
  - **凭证获取**：API Key **已配置在宿主机电脑的用户系统环境变量中**，无需在 `.env` 中强行写死，代码中直接 `os.getenv('XXX')` 读取即可。
  - **接口文档参考**：[商汤大模型开发文档](https://platform.sensenova.cn/docs)
- **原子化 Prompt 阅卷**：学生交卷且包含主观题时，主线程立刻返回 `200 交卷成功，批阅中`。
- **后台协程**：使用 `fastapi.BackgroundTasks` 传入一个 `grade_exam_async` 函数。
  - 提取该卷所有简答题和考生答案，拼凑成单次 JSON Prompt。
  - 请求商汤日日新 API 进行阅卷。
  - 成功则写库。如果抛出超时或解析异常，则回滚并将记录置为 `pending_grading` 抛给人工大厅。
  - *平替方案*：如果大模型 JSON 返回一直格式错乱，可要求大模型使用最简单的 Markdown 代码块输出，后端用正则提取。

### Step 5: B 端 AI Copilot 的“前端状态注入” (Preamble Injection)
- **前端工作**：在发出 `/api/v1/admin/ai/chat` 请求时，Vue/Pinia 取出当前 Dashboard 的 `pending_count` 等数据，硬拼在用户输入的 text 前面：`[System: 待批阅10份, 余量15] 用户说: xxxx`。
- **后端工作**：纯透传给大模型大模型接口，不涉及任何 RAG 或数据库查表。
  - *兜底方案*：若前端状态难以抓取，就发送一个空的 `[System: 您是题库助手]`，让模型纯做泛知识问答。坚决不写复杂的 Text-to-SQL。
```
