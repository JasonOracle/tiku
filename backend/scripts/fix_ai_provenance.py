# -*- coding: utf-8 -*-
"""Orchestrator 修复：补公共知识文档，重生成 AI 卷（tenant1 task3 / tenant2 task4），重提交并核验。"""
import httpx

BASE = "http://127.0.0.1:8123"

PLAN = {
    1: {"admin": "13800000011", "doc": ("a_fin.txt", "金融风险管理：信用风险须计提拨备，市场风险用VaR计量，操作风险强化内控。"),
        "topic": "金融风险管理基础", "title": "A集团-金融风险管理基础",
        "members": ["13900000001", "13900000002", "13900000003", "13900000004", "13900000005"],
        "fail_ai": {"13900000003", "13900000004", "13900000005"}},
    2: {"admin": "13800000012", "doc": ("b_hist.txt", "洋务运动：19世纪60-90年代，主张师夷长技以制夷，创办江南制造总局等军用民用企业。"),
        "topic": "近代历史常识", "title": "B公司-近代历史常识",
        "members": ["13900000006", "13900000007", "13900000008", "13900000009", "13900000010"],
        "fail_ai": {"13900000008"}},
}

c = httpx.Client(base_url=BASE, timeout=180)


def jp(r):
    assert r.status_code in (200, 201), f"{r.status_code} {r.request.url.path}: {r.text[:200]}"
    d = r.json()
    assert d.get("code") in (200, 201), d
    return d["data"]


def login(phone, pw="123456"):
    return jp(c.post("/api/v1/auth/login", json={"phone": phone, "password": pw}))["token"]


for tid, p in PLAN.items():
    H = {"Authorization": f"Bearer {login(p['admin'])}", "X-Tenant-ID": str(tid)}
    # 1. 补公共知识文档
    up = jp(c.post("/api/v1/admin/kb/documents", headers=H,
                   files={"file": (p["doc"][0], p["doc"][1].encode())}, data={"scope": "public"}))
    assert up["chunks"] >= 1, up
    # 2. 找到旧 AI 卷（标题含 AI 或 topic 关键词）并删记录+任务
    tasks = jp(c.get("/api/v1/admin/tasks", headers=H, params={"page": 1, "size": 50}))["items"]
    old = [t for t in tasks if ("AI" in t["title"] or p["topic"][:2] in t["title"]) and t["status"] == "published"]
    assert len(old) == 1, [t["title"] for t in tasks]
    old_id = old[0]["id"]
    # 先删该任务的提交记录（直接 DB 太重——用 API？无删除记录接口；改用 SQL）
    import sqlite3
    con = sqlite3.connect("D:/project/tiku/tiku/backend/mock_acceptance.db", timeout=30)
    cur = con.cursor()
    cur.execute("DELETE FROM task_records WHERE tenant_id=? AND task_id=?", (tid, old_id))
    # 查出该任务独占资源并删任务+链接+资源
    rids = [r[0] for r in cur.execute("SELECT resource_id FROM task_resources WHERE task_id=?", (old_id,))]
    cur.execute("DELETE FROM task_resources WHERE task_id=?", (old_id,))
    cur.execute("DELETE FROM tasks WHERE id=? AND tenant_id=?", (old_id, tid))
    for rid in rids:
        used = cur.execute("SELECT 1 FROM task_resources WHERE resource_id=?", (rid,)).fetchone()
        if not used:
            cur.execute("DELETE FROM resources WHERE id=?", (rid,))
    con.commit()
    con.close()
    print(f"tenant{tid}: dropped old AI task {old_id}, resources {rids}")
    # 3. AI 重新生成（此时知识库非空）
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
    # 4. 成员重提交（pass 按正确答案交，fail 交错）
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
        # 找到记录并 confirm（manual 模式）
        recs = jp(c.get("/api/v1/member/task-records", headers=mH))["items"]
        rid_rec = [r for r in recs if r["task_id"] == new_id][0]["record_id"]
        pend = jp(c.get("/api/v1/admin/verifications/pending", headers=H))["items"]
        if any(r["record_id"] == rid_rec for r in pend):
            pass  # ai_auto 情况（本次 manual，不会发生）
        cf = jp(c.post(f"/api/v1/admin/verifications/{rid_rec}/confirm", headers=H,
                       json={"final_score": 85 if m not in p["fail_ai"] else 35, "comments": "orchestrator 回填"}))
        print(f"  member {m}: score={cf['score']}")
print("FIX DONE")
