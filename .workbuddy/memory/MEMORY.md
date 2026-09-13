# 智题库 TiKu —— 项目长期备忘

## 服务架构与启动

- 一键启动：`docker compose up -d`（项目根目录）。容器：`tiku_mysql`(3306) / `tiku_backend`(8000) / `tiku_nginx`(80)。
- 网关路由（`nginx.conf`）：`/admin/` → `tob/dist`；`/` → `toc-new/dist/build/h5`；`/api/v1/`、`/docs`、`/uploads/` → backend:8000。
- 本地入口：
  - C 端移动端（H5 产物）http://127.0.0.1/ ｜ 测试账号 `13900000001 / 123456`
  - B 端管理后台 http://127.0.0.1/admin ｜ 企业管理员 `13800000012 / 123456`、平台超管 `13800000000 / 123456`
  - API 文档 http://127.0.0.1:8000/docs
- 分端开发模式（热更新）：后端 `uvicorn app.main:app --reload --port 8000`；B 端 `pnpm dev`(5173)；C 端 `pnpm dev:h5`(5174)。

## 本机环境坑（已实测）

- **Bash 工具不可用**（PATH 缺基础命令），统一用 PowerShell。
- **docker CLI 不在 PATH**，绝对路径：
  `C:\Users\Administrator\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe`
- `wsl.exe` 被安全策略拉黑，禁调用。
- PowerShell 不回显 stdout → `Out-File` 后 Read；中文乱码仅为控制台编码问题。

## 关键约定

- **B 端入口必须带结尾斜杠 `http://127.0.0.1/admin/`**。nginx `location /admin/` 只匹配带斜杠路径，
  访问 `/admin` 会掉进 `location /` 被 C 端 SPA 兜底接管（返回 200 的 C 端页面，极迷惑）。
  已在 `nginx.conf` 加 `location = /admin { return 301 /admin/; }` 兜住。
- **只改 nginx.conf → 热重载即可**：`docker exec tiku_nginx nginx -t && docker exec tiku_nginx nginx -s reload`。
- **改 docker-compose.yml 的挂载路径 → 必须重建容器**：Windows 挂载卷下 nginx 不会感知 compose 变更，
  旧容器会继续挂旧路径（典型症状：C 端根路径 403 而 `/admin/` 正常）。
  修复命令：`docker compose up -d --no-deps nginx`。
- 前端改代码后需重新 `pnpm build`（或重启 dev），并注意 B 端 build base 为 `/admin/`。
- 数据库账号：`root / rootpassword`，库名 `tiku_db`；表前缀 `sys_`（用户/租户）、业务表无前缀。
- 文档优先级：`progress.md` > `tech-spec.md` > `product.md` / `api-contract.md`（详见 `agent.md` 第 1 条）。

## 自动化测试（playwright-cli 驱动）约定

- **浏览器自动化驱动器**：`.workbuddy/pwdrive.js`（Node 读命令文件逐条执行 playwright-cli，一个进程 = 一个会话）。
  命令文件每行 `命令|参数`，支持 `sleep|<ms>`。浏览器**不能跨工具调用存活**，登录态靠 `state-save/state-load`。
- **严禁硬编码 ref**：playwright-cli 的 `ref` 每次 snapshot 后重排，弹窗元素跨会话必然漂移。
  统一用 `run-code --filename=<js>` + `getByRole(role,{name})` 角色定位器（`exact:true` 消歧）。
- **接口探针**：`.workbuddy/api.js`（登录/发布/限流/幂等/跨租户）、`cetest.js`（C 端 APP）、`sess.js`（会话隔离）、`overflow2.js`。
- **测试账号**（本次造数，可复用）：租户 6 `WB测试机构`；管理员 `13811111111/123456`；
  学员 `13911111101~105/123456`；超管 `13800000000/GodPass123`。
- **接口铁律**：除登录外所有业务接口必须带 `X-Tenant-ID` 头；`/admin/ai/*` 需 admin 及以上角色。
- 验收产物：根目录 `test-report.md`。

