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

## 第二步：云端部署 Python FastAPI 后端 (Zeabur - 100% 免绑卡极速推荐)

> **为什么首选 Zeabur？**  
> 1. **真正免绑卡**：GitHub 账号一键登录，无需任何信用卡/外币卡；  
> 2. **亚太节点极低延迟**：提供东京 (Tokyo) / 新加坡 (Singapore) 优质节点，国内直连响应飞快；  
> 3. **全自动化识别**：自动识别 Python 项目，一键分配 `.zeabur.app` 免费 SSL 域名。

### 2.1 注册并创建 Project
1. 打开官网：[https://zeabur.com/](https://zeabur.com/)，点击右上角 **Login** $\rightarrow$ **Sign in with GitHub**。
2. 登录后进入控制台，点击 **Create Project**（新建项目）。
3. 区域 (Region) 选择 **Asia-Pacific**（例如 `Tokyo` 或 `Singapore`）。

### 2.2 部署后端服务
1. 进入刚创建的项目，点击 **Deploy New Service** $\rightarrow$ 选择 **Git**。
2. 选中你的 `tiku` 仓库（首次使用授权 GitHub 仓库权限）。
3. 选择分支：`master`。
4. **配置工作目录 (Root Directory)**：
   - 在部署弹窗中，将 **Root Directory** 设置为：`backend` （**非常关键：指向后端目录**）。
   - Zeabur 会自动识别到 `requirements.txt` 并完成依赖安装与启动。

### 2.3 配置环境变量 (Environment Variables)
在服务详情页中，点击 **Variables**（环境变量）标签页，逐个添加：

| Key (变量名) | Value 示例 | 说明 |
| :--- | :--- | :--- |
| `DATABASE_URL` | `mysql+pymysql://2kQ7...:4000/test?ssl_ca=/etc/ssl/certs/ca-certificates.crt&ssl_verify_cert=true&ssl_verify_identity=true` | 第一步获取的 TiDB 连接串 |
| `ENVIRONMENT` | `production` | 生产模式 |
| `SECRET_KEY` | `tiku-prod-secret-key-random-token-2026` | 32位随机密钥 |
| `CORS_ORIGINS` | `*` | 跨域放行 |

### 2.4 生成公网域名与验证
1. 环境变量添加后，服务会自动触发重新部署。
2. 点击 **Networking**（网络）标签页，在 **Public Networking** 下点击 **Generate Domain**（生成域名）。
3. 系统会立即为你生成一个免费的公网网址，例如：
   `https://tiku-api.zeabur.app`
4. 验证接口：在浏览器中访问 `https://tiku-api.zeabur.app/docs`，若能正常打开 Swagger 交互文档，后端即正式大功告成！

---

### 💡 备选方案：Render.com (适合已有外币信用卡用户)
如果已有海外信用卡，也可以在 [render.com](https://render.com/) 创建 Web Service：
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
