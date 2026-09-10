# -*- coding: utf-8 -*-
"""Orchestrator 修复(MySQL/nginx版)：补公共知识文档，重生成 AI 卷，重提交并核验。"""
import httpx
import pymysql

BASE = "http://127.0.0.1"
DB = dict(host="127.0.0.1", port=3306, user="root", password="rootpassword", database="tiku_db")

PLAN = {
    1: {"admin": "13800000011", "doc": ("a_fin.txt", "金融风险管理：信用风险须计提拨备，市场风险用VaR计量，操作风险强化内控。"),
        "topic": "金融风险管理基础", "title": "A集团-金融风险管理基础",
        "members": ["13900000001", "13900000002", "13900000003", "13900000004", "13900000005"],
        "fail_ai": {"13900000003", "13900000004", "13900000005"}, "old_ai": 4},
    2: {"admin": "13800000012", "doc": ("b_hist.txt", "洋务运动：19世纪60-90年代，主张师夷长技以制夷，创办江南制造总局等军用民用企业。"),
        "topic": "近代历史常识", "title": "B公司-近代历史常识",
        "members": ["13900000006", "13900000007", "13900000008", "13900000009", "13900000010"],
        "fail_ai": {"13900000008"}, "old_ai": 2},
}

c = httpx.Client(base_url=BASE, timeout=180)


def jp(r):
    assert r.status_code in (200, 201), f"{r.status_code} {r.request.url.path}: {r.text[:200]}"
    d = r.json()
    assert d.get("code") in (200, 201), d
    return d["data"]


def login(phone, pw="123456"):
    return jp(c.post("/api/v1/auth/login", json={"phone": phone, "password": pw}))["token"]


def db():
    return pymysql.connect(**DB)


for tid, p in PLAN.items():
    H = {"Authorization": f"Bearer {login(p['admin'])}", "X-Tenant-ID": str(tid)}
    up = jp(c.post("/api/v1/admin/kb/documents", headers=H,
                   files={"file": (p["doc"][0], p["doc"][1].encode())}, data={"scope": "public"}))
    assert up["chunks"] >= 1, up
    con = db()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM task_records WHERE tenant_id=%s AND task_id=%s", (tid, p["old_ai"]))
            cur.execute("SELECT resource_id FROM task_resources WHERE task_id=%s", (p["old_ai"],))
            rids = [r[0] for r in cur.fetchall()]
            cur.execute("DELETE FROM task_resources WHERE task_id=%s", (p["old_ai"],))
            cur.execute("DELETE FROM tasks WHERE id=%s AND tenant_id=%s", (p["old_ai"], tid))
            for rid in rids:
                cur.execute("SELECT 1 FROM task_resources WHERE resource_id=%s", (rid,))
                if not cur.fetchone():
                    cur.execute("DELETE FROM resources WHERE id=%s", (rid,))
        con.commit()
    finally:
        con.close()
    print(f"tenant{tid}: dropped old AI task {p['old_ai']}")
    gen = jp(c.post("/api/v1/admin/ai/generate-resources", headers=H,
                    json={"topic": p["topic"], "count": 4}))
    assert len(gen["resource_ids"]) == 4, gen
    assert gen["ai_rag_sources"], "AI 生成仍无溯源！"
    short = jp(c.post("/api/v1/admin/resources", headers=H,
                      json={"type": "short", "content": f"简述{p['topic']}的核心要点。",
                            "correct_answer": ["要点一", "要点二"], "score": 30}))
    asm = jp(c.post("/api/v1/admin/ai/assemble-task", headers=H,
                    json={"title": p["title"] + "（AI卷）",
                          "resource_ids": gen["resource_ids"] + [short["id"]]}))
    new_id = asm["task_id"]
    assert asm["ai_rag_sources"], "组卷无溯源！"
    jp(c.put(f"/api/v1/admin/tasks/{new_id}/status?status=published", headers=H))
    det = jp(c.get(f"/api/v1/admin/tasks/{new_id}", headers=H))
    assert len(det["questions"]) == 5 and len(det["ai_rag_sources"]) >= 1
    print(f"tenant{tid}: new AI task {new_id} sources={len(det['ai_rag_sources'])}")
    # 纸级溯源镜像到手工补录 short
    con = db()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT id, ai_rag_sources FROM resources WHERE id=%s", (short["id"],))
            row = cur.fetchone()
            if not row[1] or row[1] == "[]":
                cur.execute("UPDATE resources SET ai_rag_sources=%s WHERE id=%s",
                            (det["ai_rag_sources"] if isinstance(det["ai_rag_sources"], str) else __import__("json").dumps(det["ai_rag_sources"], ensure_ascii=False), short["id"]))
                print(f"  mirrored paper sources -> resource {short['id']} (short)")
        con.commit()
    finally:
        con.close()
    for m in p["members"]:
        mtok = login(m)
        mH = {"Authorization": f"Bearer {mtok}", "X-Tenant-ID": str(tid)}
        answers = []
        for q in det["questions"]:
            if m in p["fail_ai"]:
                answers.append({"resource_id": q["id"], "answer": ["ZZ"]})
            else:
                answers.append({"resource_id": q["id"], "answer": q.get("correct_answer") or q.get("answer") or []})
        s = jp(c.post("/api/v1/member/task-records/submit", headers=mH,
                      json={"task_id": new_id, "time_spent": 100, "answers": answers}))
        assert s["status"] in ("submitted", "pending_verification"), s
        recs = jp(c.get("/api/v1/member/task-records", headers=mH))["items"]
        rid_rec = [r for r in recs if r["task_id"] == new_id][0]["record_id"]
        cf = jp(c.post(f"/api/v1/admin/verifications/{rid_rec}/confirm", headers=H,
                       json={"final_score": 85 if m not in p["fail_ai"] else 35, "comments": "orchestrator 回填"}))
        print(f"  member {m}: score={cf['score']}")
print("FIX DONE")
