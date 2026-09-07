# 智题库 (TiKu) 零成本公网在线预览部署全指南 (bushu.md)

本指南旨在帮助开发者在**没有自有云服务器、零资金投入**的前提下，将智题库（TiKu）完整系统（FastAPI 后端 + Vue3 B端管理后台 + Vue3 C端学员H5 + 兼容 MySQL 的云数据库）部署到全球公网，获得永久在线的预览链接，适合展示在个人简历、GitHub 作品集或向面试官实机演示。

---

## 🏗️ 整体部署架构一览

```
                      +------------------------------------------+
                      |         客户端浏览器 / 手机微信扫码       |
                      +--------------------+---------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
       +-------------------------+                   +-------------------------+
       |   B 端后台 (tob)        |                   |   C 端学员 (toc)        |
       |  托管: Cloudflare Pages |                   |  托管: Cloudflare Pages |
       |  (或 Vercel)            |                   |  (或 Vercel)            |
       +------------+------------+                   +------------+------------+
                    |                                             |
                    +----------------------+----------------------+
                                           | API 请求 (/api/v1/...)
                                           v
                             +---------------------------+
                             |    后端 API (FastAPI)     |
                             |    托管: Render.com       |
                             |    (免费 Web Service 容器)|
                             +-------------+-------------+
                                           |
                                           v
                             +---------------------------+
                             |   TiDB Cloud (Serverless) |
                             |   (100% 兼容 MySQL 协议)  |
                             |   (免费 5GB 永久云数据库) |
                             +---------------------------+
```

---

## 第一步：创建免费云数据库 (TiDB Cloud)

> **为什么选 TiDB Cloud？**  
> PingCAP 研发的分布式数据库，原生 100% 兼容 MySQL 5.7/8.0 协议，无需自行购买云主机安装 MySQL，注册即赠送 **5GB 永久免费**存储空间，自动提供公网连接地址与 SSL。

### 1.1 注册并创建集群
1. 打开官网：[https://tidbcloud.com/](https://tidbcloud.com/)，使用 GitHub 或 Google 账号直接登录。
2. 点击 **Create Cluster**，选择 **Serverless**（类型选择 Free）。
3. Region（区域）建议选择靠近国内的地区（如：`ap-northeast-1 Tokyo` 或 `ap-southeast-1 Singapore`），延迟最低。
4. Cluster Name 命名为 `tiku-db`，点击 **Create**。

### 1.2 获取数据库连接串
1. 集群就绪后，点击进入集群详情，点击右上角 **Connect** 按钮。
2. 在连接方式中选择 **General** 或 **SQLAlchemy / Python**：
   - 记录你的：
     - `Host`: 如 `gateway01.ap-northeast-1.prod.aws.tidbcloud.com`
     - `Port`: `4000`
     - `User`: 如 `2xxx.root`
     - `Password`: 创建时你设定的密码（如果忘记可点击 Reset Password）
3. 组合出 SQLAlchemy 驱动连接字符串（格式如下）：
   ```env
   DATABASE_URL=mysql+pymysql://<用户名>:<密码>@<Host>:4000/tiku?ssl_verify_cert=true&ssl_verify_identity=true
   ```
   > 提示：TiDB 默认初始库名可能不是 `tiku`，可先写 `/test` 或通过客户端创建 `CREATE DATABASE tiku;`。

---

## 第二步：云端部署 Python FastAPI 后端 (Koyeb - 100% 免绑卡推荐)

> **为什么首选 Koyeb？**  
> 1. **完全免绑信用卡**：支持 GitHub 账号一键授权登录，永久免费额度无需任何银行卡验证，彻底避开 Stripe/外币卡 3DS 拦截风险；  
> 2. **原生支持 Buildpack & Docker**：自动识别 Python 3.10+ / FastAPI 项目；  
> 3. **全球边缘加速 & HTTPS**：自动分配 `.koyeb.app` 免费域名与 SSL 证书；  
> *(备选：如果已有海外信用卡且通过了 Stripe 验证，也可以使用 Render.com)*

### 2.1 注册并创建 Koyeb Service
1. 打开官网：[https://app.koyeb.com/](https://app.koyeb.com/)，点击 **Sign in with GitHub** 直接登录。
2. 登录后进入控制台，点击右上角 **Create Service**。
3. 部署来源选择 **GitHub**。
4. 在仓库列表中找到并选中你的 `tiku` 仓库（首次使用点击授权 Install Koyeb GitHub App）。

### 2.2 填写构建与运行参数 (App Configuration)
* **Branch**: `master`
* **Work Directory (工作目录)**: 点击展开高级选项，填写 `backend` （**关键：必须指向后端目录**）
* **Builder**: 保持默认的 **Buildpack**（会自动识别 requirements.txt 并安装 Python 依赖）
* **Build Command**: 留空（Buildpack 会自动执行 `pip install -r requirements.txt`）
* **Run Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
  *(或者 `uvicorn app.main:app --host 0.0.0.0 --port $PORT`)*
* **Instance Type (实例规格)**: 选择 **Free (Nano)**（$0/month，512MB 内存，免绑卡可用）
* **Regions**: 默认通常分配 `Frankfurt (fra)` 或 `Washington D.C. (was)`，选默认即可。
* **Exposed Port (暴露端口)**: 默认是 `8000`（与 Run Command 端口一致），Path 为 `/`，协议选 `HTTP`。

### 2.3 配置环境变量 (Environment Variables)
在 **Environment variables** 区域逐个添加：

| Key (变量名) | Value 示例 | 说明 |
| :--- | :--- | :--- |
| `DATABASE_URL` | `mysql+pymysql://2kQ7...:4000/test?ssl_ca=/etc/ssl/certs/ca-certificates.crt&ssl_verify_cert=true&ssl_verify_identity=true` | 第一步获取的 TiDB 连接串 |
| `ENVIRONMENT` | `production` | 生产模式 |
| `SECRET_KEY` | `tiku-prod-secret-key-random-token-2026` | 32位随机密钥 |
| `CORS_ORIGINS` | `*` | 跨域放行 |

### 2.4 点击 Deploy 并获取公网地址
1. 点击最底部的 **Deploy** 按钮。
2. 等待 1~2 分钟，页面上方会显示构建与运行日志，状态变为绿色的 **Healthy**。
3. 复制 Koyeb 分配的公网访问网址，格式类似于：
   `https://tiku-api-xxxx.koyeb.app`
4. 验证后端：在浏览器打开 `https://tiku-api-xxxx.koyeb.app/docs`，若能正常打开 Swagger 接口文档，说明后端与 TiDB 云数据库已经 100% 连通上线！

---

### 💡 备选方案：Render.com (适合已有外币信用卡用户)
如果已有支持海外消费的信用卡并通过了 Stripe 验证，也可以在 [render.com](https://render.com/) 创建 Web Service：
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **环境变量**: 同上表。

---

## 第三步：部署前端 B 端后台与 C 端学员端 (Cloudflare Pages)

> **为什么选 Cloudflare Pages？**  
> 全球最快 CDN 加速网络，国内访问极其顺畅，完全免费且**永不休眠**，无限带宽。

### 3.1 部署 B 端管理后台 (`tob`)

1. 打开 [Cloudflare Dashboard](https://dash.cloudflare.com/)，注册/登录账号。
2. 点击左侧菜单 **Workers 和 Pages** $\rightarrow$ **创建** $\rightarrow$ 选择 **Pages** $\rightarrow$ **连接到 Git**。
3. 选择你的 `tiku` 仓库，点击 **开始设置**。
4. **构建配置填入以下参数**：
   * **项目名称**: `tiku-tob`（自定义）
   * **生产分支**: `master`
   * **框架预设**: `Vite`
   * **根目录**: `tob` （**重要：指向 B 端前端目录**）
   * **构建命令**: `pnpm build`
   * **构建输出目录**: `dist`
5. **配置后端 API 反向代理（避免浏览器跨域）**：
   在 `tob` 目录下，Cloudflare Pages 原生支持 `_redirects` 配置文件。
   在本地 `tob/public/` 下确保存在（或新建）一个名为 `_redirects` 的文件，内容只有一行：
   ```txt
   /api/*  https://tiku-api.onrender.com/api/:splat  200
   /*      /index.html                               200
   ```
   *(将 `https://tiku-api.onrender.com` 替换为你在第二步得到的 Render 真实地址)*
6. 点击 **保存并部署**。
7. 部署完毕后，你将获得一个全球公网可访问的专属网址：
   `https://tiku-tob.pages.dev`

---

### 3.2 部署 C 端移动端/学员考试系统 (`toc`)

与 B 端完全相同的方式部署 C 端：
1. 回到 Cloudflare Pages，再次点击 **连接到 Git**，选同一仓库。
2. **构建配置**：
   * **项目名称**: `tiku-toc`
   * **根目录**: `toc` （**重要：指向 C 端前端目录**）
   * **构建命令**: `pnpm build`
   * **构建输出目录**: `dist`
3. 同样在 `toc/public/` 下配置 `_redirects`：
   ```txt
   /api/*  https://tiku-api.onrender.com/api/:splat  200
   /*      /index.html                               200
   ```
4. 点击 **保存并部署**，获取 C 端学员答题专属网址：
   `https://tiku-toc.pages.dev`

---

## 第四步：初始化初始数据 (超级管理员账号与题库)

因为连接的是全新的 TiDB 云数据库，初次运行数据库为空，你需要初始化一个超级管理员账号用于登录：

### 方式 A：通过本地脚本直连初始化（最推荐）
在本地终端，将 `backend/.env` 中的 `DATABASE_URL` 临时替换为第一步得到的 TiDB 云连接串，然后在本地执行初始化：
```bash
cd backend
python seed_rbac_users.py
```
* 执行完成后，数据库中将自动注入超管账号：
  * **超管账号**：`super_admin`
  * **初始密码**：`admin123`

---

## 🎯 最终效果验证与作品集展示

部署完成后，你已经拥有了一套生产级、公网全互联的企业级 SaaS 平台：

1. **B 端管理工作台**：`https://tiku-tob.pages.dev`
   - 使用 `super_admin` / `admin123` 登录；
   - 体验题海共享、AI 智能组卷、AI 智能助管（微信式游标翻页）、主观题在线抽屉阅卷；
2. **C 端学员在线考场**：`https://tiku-toc.pages.dev`
   - 支持移动端自适应，手机微信扫码直接参与模拟测试与防作弊时间窗口答题；
3. **后端 API 文档 (Swagger)**：`https://tiku-api.onrender.com/docs`
   - 完整的自动化交互式接口契约，向面试官全方位展示你的工程规范水平。

---

## 常见排错指南 (FAQ)

### Q1: Render 首次部署提示缺少依赖报错怎么办？
* 确保 `backend/requirements.txt` 中包含所有必需依赖（由于项目升级到了 v1.7 版本，部分依赖已替换如 pyjwt、bcrypt）：
  ```txt
  fastapi>=0.110.0
  uvicorn[standard]>=0.28.0
  sqlalchemy>=2.0.28
  pymysql>=1.1.0
  pydantic>=2.6.4
  pydantic-settings>=2.2.1
  pyjwt>=2.8.0
  bcrypt>=4.1.0
  python-multipart>=0.0.9
  openpyxl>=3.1.2
  pytest>=8.1.1
  httpx>=0.27.0
  ```

### Q2: 访问前端时提示 API 网络超时或 502？
* 检查 Render 控制台的 Web Service 是否正在从休眠中启动，初次冷启动大约需要 30 秒；
* 检查 Cloudflare Pages 的 `_redirects` 文件是否已正确配置 Render 后端地址并推送到 Git。

### Q3: 为什么选择 Cloudflare 而不是纯 Vercel？
* Vercel 对国内网络部分地区有偶尔的 DNS 污染，而 Cloudflare Pages 的 Anycast 全球节点对国内电信、联通、移动的解析更加通用稳定。两者操作完全一致，可按喜好选择。
