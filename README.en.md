# TiKu — Online Quiz Platform

Lightweight assessment platform: mobile H5 for examinees (quiz/exam/report/favorites) + SaaS admin console (question bank, exam assembly, publish workflow, analytics) + FastAPI backend.

- **GitHub**: [https://github.com/JasonOracle/tiku](https://github.com/JasonOracle/tiku)
- **Gitee**: [https://gitee.com/jason-oracle/tiku](https://gitee.com/jason-oracle/tiku)

- Backend: `backend/` — Python 3.12 + FastAPI + SQLAlchemy 2.0 + MySQL 8.0, JWT (7d, 5-min submit grace), pessimistic-lock submit, passive timeout settlement
- Admin: `tob/` — Vue 3 + Element Plus + Pinia, built with `base: /admin/`
- Client: `toc/` — Vue 3 H5, served at `/`
- Deploy: `docker-compose.yml` in root (MySQL + backend + Nginx); `nginx.conf` proxies `/api/v1/` to backend
- Import template: `sample_questions.xlsx` (data sheet first + “导入说明” guide sheet)

中文版：[README.md](./README.md)

## 🤖 About This Project: A Journey in AI-Assisted Development

This project is more than just a quiz platform; it serves as a **practical exploration of AI-Driven Development**. Through deep collaboration with AI, I completed the entire lifecycle from 0 to 1:

1. **Requirement Analysis & Documentation**: Through continuous dialogues, I clarified my needs to the AI, step-by-step generating a comprehensive [Product Requirements Document (PRD)](./product.md), [Technical Specification](./tech-spec.md), and [API Contract](./api-contract.md).
2. **Exploration & Validation**: Utilizing AI Agent skills, we quickly generated a simple product demo. During this process, the AI provided valuable optimization suggestions, which helped me deeply understand the true "boundaries of AI capabilities."
3. **Continuity & Rule Setting**: To solve context loss caused by multiple sessions or exits, we established exclusive development rules:
   - Created a [Progress Document](./progress.md) to record the experience and current progress of each development phase.
   - Introduced a **"careful inspection and document anti-conflict"** logic to prevent the AI from generating conflicting documentation or code when updating existing files.

Through this project, I hope to provide a reference for independent developers or teams looking to leverage AI for efficient development.

> **🚧 MVP Disclaimer**
> 
> This project is currently in its **MVP (Minimum Viable Product)** stage, designed specifically to **quickly validate the project logic** and the AI-assisted development workflow.
> 
> To keep the project lightweight and ensure rapid delivery, the current version only supports objective questions (single choice, multiple choice, true/false) with automatic grading. **The following advanced features are planned for the next iteration (V2):**
> - **Short-answer and Fill-in-the-blank questions**
> - **Manual grading** capabilities in the admin console
> - **Multi-account Role-Based Access Control (RBAC)** and enterprise organizational structures

## Layout

```
tiku/
├── backend/        # FastAPI (app/api/v1 client, app/api/admin console, tests/ — 18 pytest cases)
├── tob/            # admin console (dev port 5173)
├── toc/            # client H5 (dev port 5174)
├── nginx.conf      # /api/v1/→backend, /admin/→tob, /→toc
├── sample_questions.xlsx
├── agent.md product.md tech-spec.md api-contract.md progress.md
```

## Quick start (Docker)

```powershell
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

- **`agent.md`** — **HIGHEST PRIORITY!** Core rules and guidelines for AI agents and new models. Must be read before any other document.
- `progress.md` — progress/pitfalls/§8 handoff checklist
- `api-contract.md` — API contracts (incl. 400 guards)
- `tech-spec.md` — technical design (§2.5 governance edition)
- `product.md` — PRD
