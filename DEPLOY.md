# 智题库 TiKu 生产部署手册（运维直接执行）

> 适用 v1.4 多租户 SaaS 底座。本地开发默认 SQLite/MySQL，**严禁开发机直连生产库**（agent.md 第 7 条）。

## 1. 本地开发（默认）

```powershell
# 后端（默认连本地 MySQL；未装 MySQL 可用 SQLite 冒烟）
cd backend
$env:DATABASE_URL = "sqlite:///./dev.db"   # 仅本地冒烟
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# 前端
cd ..\tob; pnpm dev --port 5173
cd ..\toc; pnpm dev --port 5174
```

## 2. 本机 Docker 全栈（MySQL 8.0，推荐预演）

```powershell
docker compose up -d          # mysql 3306，backend 8000，nginx 80
docker exec tiku_nginx nginx -s reload   # backend重建后必执行
```

* `tiku_init.sql` 会在 **全新 volume** 时自动执行建表；已有数据的 volume 不会重复执行（幂等 `IF NOT EXISTS`，也可手动重放）。
* 首个上帝账号：`POST /api/v1/super-admin/bootstrap {"phone":"13800000000","password":"...≥6位"}`（全库无用户时有效，此后永久自锁 403）。
* 入口：C 端 `http://localhost/`，B 端 `http://localhost/admin/login`，文档 `http://localhost/docs`。
* 环境变量（`.env` 或 shell）：`SECRET_KEY`（必改）、`XIAO_HONG_SHU_API_KEY[_2]`、`SENSENOVA_API_KEY[_2]`、`AGNES_API_KEY[_2]`、`TIDB_VECTOR=0`（本地保持 0）。

## 3. 云端生产（TiDB Cloud Serverless + Render/Vercel）

1. TiDB Cloud 建库 → 取 MySQL 兼容连接串。
2. 导入表结构：`mysql -h <TIDB_HOST> -P 4000 -u <USER> -p <DB> < tiku_init.sql`。
3. 后端（Render，按 `render.yaml`）：配 `DATABASE_URL`（TiDB 串）、`SECRET_KEY`（生成值）、AI Key、`TIDB_VECTOR=0`（默认；向量见 §4）。
4. 前端：`tob/dist` → `/admin/`，`toc/dist` → `/`（Nginx 或 Pages，`nginx.conf` 为准；发版后 Ctrl+Shift+R 硬刷）。
5. 上线后第一件事：调一次 `/super-admin/bootstrap` 建上帝账号（之后自锁）。

## 4. TiDB Vector 启用（可选，默认关闭）

1. 生产 TiDB 执行 `tiku_init.sql` 末尾【TiDB Vector 备用段】（加 `embedding_vec VECTOR(1536)` 列 + 回填）。
2. 后端环境变量：`TIDB_VECTOR=1`（`EMBED_DIM` 与维度一致，默认 1536）。
3. 重启后端。检索自动切原生 `VEC_COSINE_DISTANCE`；向量缺失行自动跳过，异常回退 LIKE。
4. **本地/SQLite/MySQL 环境永远保持 `TIDB_VECTOR=0`，严禁开发机连云库验证。**

## 5. 验证清单

* `cd backend; python -m pytest tests/ -q`（本地，SQLite 内存，全绿）
* `python scripts/e2e_selftest.py http://localhost`（全 31 项，含真实 AI 调用）
* `cd tob; pnpm build` / `cd toc; pnpm build`
