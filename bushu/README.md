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

## 第二步：云端部署 Python FastAPI 后端 (Render.com)

> **为什么选 Render？**  
> 支持直接连接 GitHub 仓库自动拉取代码部署，原生支持 Python 3.10+ 环境，免费提供独立二级域名与全站 HTTPS。

### 2.1 注册并新建 Web Service
1. 打开 [https://render.com/](https://render.com/)，使用 GitHub 登录。
2. 点击右上角 **New +** $\rightarrow$ **Web Service**。
3. 选择 **Build and deploy from a Git repository**，选中你的 `tiku` 仓库并点击 Connect。

### 2.2 填写构建与运行参数
* **Name**: `tiku-api`（自定义名称）
* **Region**: 选择与数据库相近的地区（如 `Singapore` 或 `Oregon`）
* **Branch**: `master`（或你的主分支）
* **Root Directory**: `backend` （**非常重要：填写项目的后端根目录**）
* **Runtime**: `Python 3`
* **Build Command**:
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt
  ```
* **Start Command**:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
* **Instance Type**: 选择 **Free**

### 2.3 配置环境变量 (Environment Variables)
在下方 **Environment Variables** 点击 **Add Environment Variable** 添加必要配置：

| Key | Value 示例 | 说明 |
| :--- | :--- | :--- |
| `DATABASE_URL` | `mysql+pymysql://...:4000/tiku?ssl_verify_cert=true` | 第一步获取的 TiDB 连接串 |
| `ENVIRONMENT` | `production` | 生产模式（开启更严密的跨域与日志） |
| `SECRET_KEY` | `your_custom_jwt_secret_key_random_string` | JWT 加密密钥（可随机敲32位字符串） |
| `SENSENOVA_API_KEY` | `your_sensenova_key` | 商汤日日新模型 Key（若有） |
| `XIAO_HONG_SHU_API_KEY` | `your_dots_key` | Dots.ai 高速模型 Key（若有） |

### 2.4 点击创建并等待部署
1. 点击 **Create Web Service**，系统将自动执行依赖安装、建表与服务启动。
2. 观察控制台日志（Logs），看到 `Application startup complete.` 即表示后端启动成功！
3. 复制 Render 顶部为你分配的公网网址，例如：
   `https://tiku-api.onrender.com`
4. 在浏览器中打开 `https://tiku-api.onrender.com/docs`，若能正常看到 Swagger API 交互文档，说明后端 100% 成功！

> 💡 **冷启动提示**：Render 免费版实例在无请求 15 分钟后会进入轻微休眠。首次打开可能需要等待 30 秒“唤醒”，后续运行速度完全正常。

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
