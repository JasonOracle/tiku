# TiKu — Online Quiz Platform

Lightweight assessment platform: mobile H5 for examinees (quiz/exam/report/favorites) + SaaS admin console (question bank, exam assembly, publish workflow, analytics) + FastAPI backend.

- Backend: `backend/` — Python 3.12 + FastAPI + SQLAlchemy 2.0 + MySQL 8.0, JWT (7d, 5-min submit grace), pessimistic-lock submit, passive timeout settlement
- Admin: `tob/` — Vue 3 + Element Plus + Pinia, built with `base: /admin/`
- Client: `toc/` — Vue 3 H5, served at `/`
- Deploy: `D:/docker/docker-compose.yml` (MySQL + backend + Nginx); `nginx.conf` proxies `/api/v1/` to backend
- Import template: `sample_questions.xlsx` (data sheet first + “导入说明” guide sheet)

中文版：[README.md](./README.md)

## Layout

```
tiku/
├── backend/        # FastAPI (app/api/v1 client, app/api/admin console, tests/ — 18 pytest cases)
├── tob/            # admin console (dev port 5173)
├── toc/            # client H5 (dev port 5174)
├── nginx.conf      # /api/v1/→backend, /admin/→tob, /→toc
├── sample_questions.xlsx
├── product.md tech-spec.md api-contract.md progress.md
```

## Quick start (Docker)

```powershell
cd D:\docker
docker compose up -d          # mysql :3306, backend :8000, nginx :80
docker exec tiku_nginx nginx -s reload   # required after backend rebuild
```

| Entry | URL |
| :--- | :--- |
| Client | http://localhost/ |
| Admin | http://localhost/admin/login (hard-refresh **Ctrl+Shift+R** after deploys) |
| API/Swagger | http://localhost/api/v1/, http://localhost/docs |

Test account: admin `admreg / AdmReg123`; client users self-register. MySQL: `root/rootpassword@127.0.0.1:3306/tiku_db`.

## Local dev

```powershell
cd backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
cd tob; pnpm dev --port 5173
cd toc; pnpm dev --port 5174
```

Both frontends use a relative `baseURL` (same-origin via Nginx in prod; Vite dev proxy for `/api`, `/uploads`).

## Verify

```powershell
cd backend; python -m pytest tests/ -v        # 18 passed
cd ..\tob; pnpm build
cd ..\toc; pnpm build
```

## Governance rules (see progress.md §7)

- Exam lifecycle `draft → published → archived`; **archived is terminal** (no edit/delete/re-publish); publishing requires a valid category and snapshots `category_name`
- Delete guards: categories/questions blocked when referenced; exams deletable only as untouched drafts
- No empty submits: zero-answer submit returns 400; client never auto-submits blank papers
- Import: per-row “分类” column (auto-create missing, fallback to first); `short`/`fill` types reserved and skipped with counts; new questions default to the first category

## Docs

- `progress.md` — progress/pitfalls/§8 handoff checklist (new models read first)
- `api-contract.md` — API contracts (incl. 400 guards)
- `tech-spec.md` — technical design (§2.5 governance edition)
- `product.md` — PRD
