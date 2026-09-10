"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[彻底清洗重写：多租户 SaaS 全链路自测（引导→入驻→资源→任务→提交→核验→知识库→AI溯源→运营），可重复执行，用法: python scripts/e2e_selftest.py [BASE_URL]]
"""
import sys
import time
from datetime import datetime

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
GOD_PHONE = sys.argv[2] if len(sys.argv) > 2 else "13800000000"
GOD_PASS = "GodPass123"
STAMP = datetime.now().strftime("%m%d%H%M%S")
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'PASS' if ok else 'FAIL'} {name}" + (f" -- {detail}" if detail else ""))
    return ok


def jp(r, expect=(200, 201)):
    """解包 {code, data}; 失败抛异常带路径与摘要"""
    if r.status_code not in expect:
        raise AssertionError(f"[{r.status_code}] {r.request.method} {r.request.url.path}: {r.text[:200]}")
    d = r.json()
    if d.get("code") not in (200, 201):
        raise AssertionError(f"code={d.get('code')}: {d.get('message')}")
    return d["data"]


def main():
    c = httpx.Client(base_url=BASE, timeout=180)
    print(f"=== 智题库 SaaS 全链路自测 | 目标: {BASE} | {datetime.now():%Y-%m-%d %H:%M:%S} ===\n")

    # ---------- 0. 空库引导 ----------
    print("[0] 空库引导上帝账号")
    b = c.post("/api/v1/super-admin/bootstrap", json={"phone": GOD_PHONE, "password": GOD_PASS})
    if b.status_code == 201:
        check("空库引导创建上帝", True, GOD_PHONE)
    else:
        check("引导通道已自锁（非空库）", b.status_code == 403, f"{b.status_code}")
    god = jp(c.post("/api/v1/auth/login", json={"phone": GOD_PHONE, "password": GOD_PASS}))
    check("上帝登录", god["user"]["is_super_admin"] is True)
    gh = {"Authorization": f"Bearer {god['token']}"}

    # ---------- 1. 建企业 + 录入管理员 ----------
    print("[1] 企业入驻")
    tenant = jp(c.post("/api/v1/super-admin/tenants", json={"name": f"自测企业{STAMP}"}, headers=gh))
    tid = tenant["tenant_id"]
    gh_t = {**gh, "X-Tenant-ID": str(tid)}
    ADMIN_PHONE = f"139{int(STAMP) % 10000000:07d}1"
    jp(c.post("/api/v1/admin/members", json={"phone": ADMIN_PHONE, "name": "自测管理员", "role": "admin"}, headers=gh_t))
    admin = jp(c.post("/api/v1/auth/login", json={"phone": ADMIN_PHONE, "password": "123456"}))
    check("管理员静默建号+登录直达", admin["default_tenant_id"] == tid, f"tenant={tid}")
    H = {"Authorization": f"Bearer {admin['token']}", "X-Tenant-ID": str(tid)}

    # ---------- 2. 分类 + 资源 ----------
    print("[2] 资源库")
    rcat = jp(c.post("/api/v1/admin/categories", json={"name": f"自测资源{STAMP}", "target_type": "resource"}, headers=H))
    tcat = jp(c.post("/api/v1/admin/categories", json={"name": f"自测任务{STAMP}", "target_type": "task"}, headers=H))
    check("新建资源/任务分类", bool(rcat["id"] and tcat["id"]))
    mk = lambda **kw: jp(c.post("/api/v1/admin/resources", json=kw, headers=H))
    r_single = mk(type="single_choice", content="HTTP 默认端口是？",
                  options=[{"key": "A", "text": "80"}, {"key": "B", "text": "443"}],
                  correct_answer=["A"], score=10, category_id=rcat["id"])
    r_multi = mk(type="multiple_choice", content="以下哪些是 HTTP 方法？",
                 options=[{"key": "A", "text": "GET"}, {"key": "B", "text": "POST"}],
                 correct_answer=["A", "B"], score=10, category_id=rcat["id"])
    r_short = mk(type="short", content="简述 HTTPS 的安全改进。", correct_answer=["TLS 加密"],
                 score=30, category_id=rcat["id"])
    check("新建条目", all([r_single["id"], r_multi["id"], r_short["id"]]),
          f"ids={r_single['id']},{r_multi['id']},{r_short['id']}")
    cp = jp(c.post(f"/api/v1/admin/resources/{r_single['id']}/copy", headers=H))
    check("复制条目", cp["id"] != r_single["id"])
    lst = jp(c.get("/api/v1/admin/resources", headers=H, params={"page": 1, "size": 10}))
    check("资源列表", lst["total"] >= 4)

    # ---------- 3. AI 出题/组卷（真实大模型，失败自动降级不断言模型质量） ----------
    print("[3] AI 通道")
    t0 = time.time()
    gen = jp(c.post("/api/v1/admin/ai/generate-resources", headers=H,
                    json={"topic": "Python 基础语法", "count": 2}))
    check("AI 出题落库+溯源", len(gen["resource_ids"]) == 2 and "ai_rag_sources" in gen,
          f"{time.time()-t0:.0f}s")
    asm = jp(c.post("/api/v1/admin/ai/assemble-task", headers=H,
                    json={"title": f"AI任务{STAMP}", "resource_ids": gen["resource_ids"]}))
    check("AI 组卷+溯源", bool(asm.get("task_id")) and "ai_rag_sources" in asm)
    cfg = jp(c.get("/api/v1/admin/ai/config", headers=H))
    check("AI 配置脱敏回显", cfg["source"] == "env" and cfg["chat_api_key_masked"] == "")
    tconn = jp(c.post("/api/v1/admin/ai/config/test", headers=H, json={}))
    check("AI 网关连通", tconn["ok"] is True, f"{tconn['latency_ms']}ms via {tconn['source']}")

    # ---------- 4. 手工任务 + 发布 ----------
    print("[4] 任务下发")
    task = jp(c.post("/api/v1/admin/tasks", headers=H, json={
        "title": f"自测任务{STAMP}", "category_id": tcat["id"], "verification_mode": "manual",
        "resource_ids": [r_single["id"], r_multi["id"]]}))
    task_auto = jp(c.post("/api/v1/admin/tasks", headers=H, json={
        "title": f"自测AI核验任务{STAMP}", "verification_mode": "ai_auto",
        "resource_ids": [r_short["id"]]}))
    check("下发任务", bool(task["task_id"] and task_auto["task_id"]))
    jp(c.put(f"/api/v1/admin/tasks/{task['task_id']}/status?status=published", headers=H))
    jp(c.put(f"/api/v1/admin/tasks/{task_auto['task_id']}/status?status=published", headers=H))
    det = jp(c.get(f"/api/v1/admin/tasks/{task['task_id']}", headers=H))
    check("任务详情含条目", len(det["questions"]) == 2)

    # ---------- 5. 成员入驻 + 待办 ----------
    print("[5] 成员闭环")
    M1, M2 = f"137{int(STAMP) % 10000000:07d}1", f"137{int(STAMP) % 10000000:07d}2"
    jp(c.post("/api/v1/admin/members", json={"phone": M1, "name": "成员一"}, headers=H))
    jp(c.post("/api/v1/admin/members", json={"phone": M2, "name": "成员二"}, headers=H))
    m1 = jp(c.post("/api/v1/auth/login", json={"phone": M1, "password": "123456"}))
    m2 = jp(c.post("/api/v1/auth/login", json={"phone": M2, "password": "123456"}))
    check("成员登录直达企业", m1["default_tenant_id"] == tid and m2["default_tenant_id"] == tid)
    mH1 = {"Authorization": f"Bearer {m1['token']}", "X-Tenant-ID": str(tid)}
    mH2 = {"Authorization": f"Bearer {m2['token']}", "X-Tenant-ID": str(tid)}
    todo = jp(c.get("/api/v1/member/member-tasks", headers=mH1))
    check("待办可见", any(i["task_id"] == task["task_id"] and i["status"] == "pending" for i in todo["items"]))

    # ---------- 6. 作答入口防泄漏 + 提交 ----------
    entry = jp(c.get(f"/api/v1/member/tasks/{task['task_id']}/entry", headers=mH1))
    check("入口无答案泄漏", bool(entry["questions"]) and all(
        "answer" not in q and "correct_answer" not in q for q in entry["questions"]))
    sub = jp(c.post("/api/v1/member/task-records/submit", headers=mH1, json={
        "task_id": task["task_id"], "time_spent": 120,
        "answers": [{"resource_id": r_single["id"], "answer": ["A"]},
                    {"resource_id": r_multi["id"], "answer": ["A", "B"]}]}))
    check("提交成功", sub["status"] == "submitted")
    dup = c.post("/api/v1/member/task-records/submit", headers=mH1,
                 json={"task_id": task["task_id"], "answers": []})
    check("重复提交拦截", dup.status_code == 400)
    recs = jp(c.get("/api/v1/member/task-records", headers=mH1))
    rid = [r for r in recs["items"] if r["task_id"] == task["task_id"]][0]["record_id"]
    rep = jp(c.get(f"/api/v1/member/task-records/{rid}", headers=mH1))
    check("查看结果", rep["status"] == "submitted" and len(rep["items"]) == 2)

    # ---------- 7. AI 核验任务：提交→AI核验→确认 ----------
    entry2 = jp(c.get(f"/api/v1/member/tasks/{task_auto['task_id']}/entry", headers=mH2))
    check("AI任务入口", len(entry2["questions"]) == 1)
    sub2 = jp(c.post("/api/v1/member/task-records/submit", headers=mH2, json={
        "task_id": task_auto["task_id"], "time_spent": 60,
        "answers": [{"resource_id": r_short["id"], "answer": "TLS 加密传输"}]}))
    check("AI核验任务提交转待核验", sub2["status"] == "pending_verification")
    pend = jp(c.get("/api/v1/admin/verifications/pending", headers=H))
    target = [r for r in pend["items"] if r["task_id"] == task_auto["task_id"]]
    check("核验大厅可见", len(target) == 1)
    v = jp(c.post(f"/api/v1/admin/ai/verify/{target[0]['record_id']}", headers=H))
    check("AI 核验落溯源", "ai_rag_sources" in v)
    cf = jp(c.post(f"/api/v1/admin/verifications/{target[0]['record_id']}/confirm", headers=H,
                   json={"final_score": 88, "comments": "e2e"}))
    check("确认定分", cf["score"] == 88)

    # ---------- 8. 隔离 ----------
    other = jp(c.post("/api/v1/super-admin/tenants", json={"name": f"隔离企业{STAMP}"}, headers=gh))
    bad = c.post("/api/v1/admin/resources", json={"content": "越权"},
                 headers={**H, "X-Tenant-ID": str(other["tenant_id"])})
    check("跨租户写入 403", bad.status_code == 403)
    noh = c.post("/api/v1/admin/resources", json={"content": "x"},
                 headers={"Authorization": H["Authorization"]})
    check("缺租户头 400", noh.status_code == 400)

    # ---------- 9. 知识库 + 会话溯源 ----------
    print("[6] 知识库与会话")
    up = jp(c.post("/api/v1/admin/kb/documents", headers=H,
                   files={"file": ("e2e.txt", "报销必须提供发票复印件".encode("utf-8"))},
                   data={"scope": "public"}), expect=(200, 201))
    check("上传公共知识", up["chunks"] >= 1)
    chat = jp(c.post("/api/v1/admin/ai/chat", headers=H, json={"message": "报销需要什么"}))
    check("对话溯源", len(chat.get("ai_rag_sources", [])) >= 1 and chat.get("session_id"))
    ms = jp(c.get(f"/api/v1/admin/ai/sessions/{chat['session_id']}/messages", headers=H))
    check("会话持久化", len(ms["items"]) == 2 and len(ms["items"][1]["ai_rag_sources"]) >= 1)

    # ---------- 10. 运营 ----------
    print("[7] 运营底座")
    st = jp(c.get("/api/v1/admin/dashboard/stats", headers=H))
    check("看板聚合", st["kpi"]["exams"] >= 3 and len(st["trend"]) == 7)
    bn = jp(c.post("/api/v1/admin/banners", headers=H,
                   json={"image_url": "/uploads/e2e.png", "sort_order": 1}), expect=(200, 201))
    mb = jp(c.get("/api/v1/member/banners", headers=H))
    check("横幅上下线", any(b["id"] == bn["id"] for b in mb["items"]))
    au = jp(c.get("/api/v1/admin/audit", headers=H, params={"size": 5}))
    check("审计留痕", au["total"] >= 1)
    nt = jp(c.get("/api/v1/admin/notifications", headers=H))
    check("通知到达", nt["total"] >= 1)

    # ---------- 报告 ----------
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = len(RESULTS) - passed
    print(f"\n=== 自测报告: {passed} 通过 / {failed} 失败 (共{len(RESULTS)}项) ===")
    if failed:
        print("失败项:")
        for name, ok, detail in RESULTS:
            if not ok:
                print(f"  FAIL {name} {detail}")
        sys.exit(1)


if __name__ == "__main__":
    main()
