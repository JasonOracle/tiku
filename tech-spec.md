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

### 2.1 多账号并发登录与抢先提交逻辑 (First-Submit-Wins)
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
```
