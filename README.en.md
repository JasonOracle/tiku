# TiKu — Enterprise Multi-Tenant Smart Quiz & Online Assessment System

A modern, lightweight AI-Native assessment and examination platform: **B-end SaaS Management Console** (Question Assets, Intelligent Exam Assembly, Grading Center, AI Question-Generation Assistant, Multi-tenant Isolation) + **C-end Mobile Examinee App** (Quiz, Timed Exams, Answer Sheet Drawer, Anti-leakage Reports, Favorites) + **FastAPI Core Backend**.

- **GitHub Repository**: [https://github.com/JasonOracle/tiku](https://github.com/JasonOracle/tiku)
- **Gitee Mirror**: [https://gitee.com/jason-oracle/tiku](https://gitee.com/jason-oracle/tiku)
- **Chinese Documentation**: [README.md](./README.md)
- 📱 **Live C-End Mobile App**: [TiKu Examinee WebApp (Cloudflare Pages)](https://tiku-toc-new.pages.dev/#/)
- ⚡ **Cloud OpenAPI Docs**: [https://tiku-api.vercel.app/docs](https://tiku-api.vercel.app/docs)
- 🎨 **v1.5 C-End Showcase Guide**: [docs/v1.5_c_showcase.md](./docs/v1.5_c_showcase.md)
- 🖥️ **v1.4 B-End Showcase Guide**: [docs/v1.4_showcase.md](./docs/v1.4_showcase.md)

---

## 🌐 Public & Local Service Access

| Service / App | URL Entry | Demo Credentials | Role Description |
| :--- | :--- | :--- | :--- |
| **📱 C-End Mobile (Public Live)** | [https://tiku-toc-new.pages.dev](https://tiku-toc-new.pages.dev/#/) | `13900000001` / `123456` | Cloudflare Pages hosted, connected to cloud TiDB |
| **💻 B-End Admin Console (Local)** | `http://localhost/admin` | `13800000012` / `123456` | Haoshi Group Enterprise Admin |
| **👑 B-End Super Admin (Local)** | `http://localhost/admin` | `13800000000` / `123456` | Platform Super Administrator |
| **⚡ FastAPI Interactive Docs** | `https://tiku-api.vercel.app/docs` | — | OpenAPI / Swagger interactive schema |

---

## 📈 Milestones & Progressive Evolution

This project strictly adheres to an **agile, progressive development** lifecycle, ensuring every iteration delivers verifiable software artifacts and frozen snapshots:

```
┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐
│  v1.0 MVP │──>│ v1.1 Data │──>│v1.2 AI Grd│──>│v1.3 KB RAG│──>│v1.4 SaaS  │──>│v1.5 Titani│
│Objective  │   │Lock & Safe│   │Fill/Essay │   │Source-text│   │Multi-tenan│   │Uni-app OS │
└───────────┘   └───────────┘   └───────────┘   └───────────┘   └───────────┘   └───────────┘
  Archived(v1.0)  Archived(v1.1)  Archived(v1.2)  Archived(v1.3)  Archived(v1.4)  Delivered(1.5)
```

- **v1.0 (MVP Closed Loop)**:
  - Completed single/multiple choice and true/false questions, exam assembly, PC/H5 test-taking, and automated instant scoring.
- **v1.1 (Data Governance & Exam Lock)**:
  - **Exam Locking & Immutability**: Introduced "published locking" to prevent modifying questions during ongoing tests, with rounded pass percentage calculations;
  - **Category & Question Safeguards**: Snapshotting `category_name` and deletion reference checks to prevent orphaned exam items;
  - **C-End Experience**: Profile center with SVG avatars, submission history, exam exit prevention modals, and pure SVG rendering standards.
- **v1.2 (AI-Native Upgrade)**:
  - Added fill-in-the-blank and essay questions; integrated SenseNova LLM for automated essay pre-grading; introduced instructor isolation and audit logs.
- **v1.3 (Private Knowledge Base RAG & State Machine Governance)**:
  - **RAG-Driven Question Generation**: Integrated vector retrieval over private document chunks, automatically highlighting source text in drawer overlays;
  - **Strict Asset Lifecycle**: Formalized the immutable `draft → published → archived` exam lifecycle;
  - **Server-Authoritative Anti-Cheating**: Exam timer locked server-side upon first entry to prevent client clock manipulation.
- **v1.4 (SaaS Multi-Tenancy & Agent Interaction Revolution)**:
  - **Strict Multi-Tenant Isolation**: Complete logical data isolation between educational institutions (e.g., Xingya Education) and enterprise compliance training (e.g., Haoshi Group);
  - **Deep AI Agent Integration**: Conversational batch question generation, dynamic drafting cards, anti-leakage guards, and full history persistence (`action_card_data`);
  - **Automated Snapshot Engineering**: Built-in Playwright automated headless screenshot and Markdown generation engine (`scripts/snapshot_showcase.py`).
- **v1.5 (Cross-Platform Geek Remodel · Apple Light-Titanium Design - Latest Delivered)**:
  - **Apple Light-Titanium Glassmorphism**: High-transparency `#fbfbfd` titanium background with dual-temperature subtle diffuse micro-glow;
  - **Core Engine Rebuild**: Transitioned from legacy H5 to `uni-app` (Vue 3.5 + TypeScript + Vite + Pinia) cross-platform native codebase;
  - **Zero-Glue Native Layout**: Native inline rendering for single/multiple choice, dual-capsule boolean, fill-in-the-blank, and essay textareas, eliminating white screen glitches;
  - **Physical Anti-Leakage Defense**: Completely blocks rendering of standard answers and question explanations in the DOM while under verification (`pending_verification`);
  - **Serverless Production Delivery**: Front-end deployed on Cloudflare Pages (`https://tiku-toc-new.pages.dev`), back-end on Vercel Serverless, linked to TiDB Cloud distributed database.

---

## 📸 System Snapshots (Showcase)

### I. v1.5 C-End Examinee Mobile Client (Apple Light-Titanium)

> For the comprehensive visual specification guide, see 👉 **[v1.5 C-End Showcase & Visual Spec Guide](./docs/v1.5_c_showcase.md)**

| Twilight Login | Assessment Lobby (Home) | Immersive Exam Room |
| :---: | :---: | :---: |
| ![Login](./docs/images/v1.5/01_toc_login.png) | ![Home](./docs/images/v1.5/02_toc_home.png) | ![Exam](./docs/images/v1.5/03_toc_exam.png) |

| Assessment Progress (Records) | Score Review Report | Profile & Favorites |
| :---: | :---: | :---: |
| ![Records](./docs/images/v1.5/04_toc_records.png) | ![Report](./docs/images/v1.5/05_toc_report_done.png) | ![Profile](./docs/images/v1.5/06_toc_profile.png) |

---

### II. v1.4 B-End SaaS Admin Console (Desktop PC)

> For the comprehensive snapshot guide, see 👉 **[v1.4 Showcase & System Architecture](./docs/v1.4_showcase.md)**

| Dashboard | Question Bank Assets |
| :---: | :---: |
| ![Dashboard](./docs/images/v1.4/01_tob_dashboard.png) | ![Questions](./docs/images/v1.4/02_tob_resources.png) |

| AI Assistant & Drafting Cards | Exam Assembly & Management |
| :---: | :---: |
| ![AI Assistant](./docs/images/v1.4/04_tob_ai_assistant.png) | ![Exams](./docs/images/v1.4/03_tob_tasks.png) |

---

## 🏗️ Project Structure

```
tiku/
├── backend/                  # FastAPI core (SaaS multi-tenancy, JWT, AI engine)
├── tob/                      # B-end admin console (Vue 3.5 + Element Plus + Pinia)
├── toc-new/                  # [v1.5 Latest] C-end uni-app + Vue 3.5 + TS cross-platform app
├── docs/                     # Public showcase & deployment guides
│   ├── v1.5_c_showcase.md    # v1.5 C-end Apple Light-Titanium walkthrough
│   ├── v1.4_showcase.md      # v1.4 B-end walkthrough report
│   ├── deploy-free-cloud.md  # Zero-cost cloud deployment guide (TiDB + Vercel + Cloudflare)
│   └── images/               # High-resolution screenshots for docs & README
├── history/                  # Historical specification archives (contains v1.3, v1.4, improveUI specs)
├── scripts/                  # Automation & headless screenshot engine
│   ├── snapshot_v1.5_c.py    # v1.5 C-end Playwright screenshot generator
│   └── snapshot_showcase.py  # v1.4 B-end automated capture script
├── nginx.conf                # Unified reverse proxy
└── docker-compose.yml        # Docker container orchestration
```

---

## 🚀 Quick Start

### Docker Compose (Recommended for Local Full-Stack)

```bash
# Start MySQL 8.0, FastAPI backend, and Nginx reverse proxy
docker compose up -d

# Reload Nginx after static build updates
docker exec tiku_nginx nginx -s reload
```

---

## 🤖 AI-Native Engineering Paradigm

This project serves as an **AI-Native Software Engineering (AI-Driven Development) benchmark**:

1. **Strict Constitutional Guardrails**: Standardized through root [`agent.md`](./agent.md), ensuring zero context degradation, explicit multi-tenant isolation, and transparent changes.
2. **Milestone Snapshots & Immutability**: Implementing frozen requirements -> architecture review -> snapshot archiving lifecycle to maintain strict auditability.
3. **Automated Documentation**: Self-documenting architecture via Playwright headless screenshot engines (`scripts/snapshot_v1.5_c.py`).

---

## 📚 Specifications Directory

- **[`agent.md`](./agent.md)** — **Highest Priority!** AI Agent rules of engagement and code ethics.
- **[`progress.md`](./progress.md)** — Project source of truth, roadmap, and operational guidelines.
- **[`product.md`](./product.md)** — Current Product Requirements Document (PRD).
- **[`tech-spec.md`](./tech-spec.md)** — Technical specification and architecture whitepaper.
- **[`api-contract.md`](./api-contract.md)** — Dual-end API contract and data privacy specifications.
- **[`docs/`](./docs/)** — Showcase and deployment documentation center.
- **[`history/`](./history/)** — Historical archives and previous version draft specifications.
