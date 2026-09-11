# -*- coding: utf-8 -*-
"""
[变更日志]
修改时间：2026-09-12
AI模型：Agnes-3.0-flash (ZCode)
修改内容：[/retake 语义整体迁移为 /continue 并补齐 can_continue 四条件真值矩阵：manual+含简答+审核中+未到期 才允许继续测试；继续测试必须保留 answers 且入口接口原样透传 my_answers；已核验、已截止、纯客观定稿卷、AI 全托管卷四类一律拒绝]
修改时间：2026-09-12
AI模型：Agnes-3.0-flash (ZCode)
修改内容：[新增回归用例外壳：manual 含简答卷交卷后必须转 pending_verification 进人工核验池、member-tasks 下发 can_retake、截止前重考原地重置记录、/me/stats 四项统计与动态及格线通过率口径]

纯 v1.4 多租户 SaaS 回归：登录/隔离/成员/资源/任务/提交/核验/知识库/AI溯源/上帝视图。
"""
from app.models.saas import SysTenant, SysUser, SysTenantUser, Task, TaskRecord
from app.core.security import get_password_hash


def _seed(db):
    db.add(SysTenant(id=101, name="企业A"))
    db.add(SysTenant(id=102, name="企业B"))
    db.add(SysUser(id=1, phone="10000000000", password_hash=get_password_hash("godpw"),
                   display_name="god", is_super_admin=True))
    db.add(SysUser(id=2, phone="13800138000", password_hash=get_password_hash("123456"),
                   display_name="A管理员"))
    db.add(SysUser(id=9, phone="13900000009", password_hash=get_password_hash("123456"),
                   display_name="B管理员"))
    db.flush()
    db.add(SysTenantUser(tenant_id=101, user_id=2, role="admin"))
    db.add(SysTenantUser(tenant_id=102, user_id=9, role="admin"))
    db.commit()


def _login(client, phone, pw="123456"):
    r = client.post("/api/v1/auth/login", json={"phone": phone, "password": pw})
    assert r.status_code == 200, r.text
    return r.json()["data"]


def _h(token, tid):
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": str(tid)}


def test_register_closed(client):
    r = client.post("/api/v1/auth/register", json={})
    assert r.status_code == 410


def test_login_returns_tenants(client, db_session):
    _seed(db_session)
    data = _login(client, "13800138000")
    assert data["default_tenant_id"] == 101
    assert data["joined_tenants"][0]["role"] == "admin"


def test_tenant_isolation_forbidden(client, db_session):
    _seed(db_session)
    tok = _login(client, "13800138000")["token"]
    r = client.post("/api/v1/admin/resources", json={"content": "越权"},
                    headers=_h(tok, 102))
    assert r.status_code == 403


def test_missing_tenant_header_rejected(client, db_session):
    _seed(db_session)
    tok = _login(client, "13800138000")["token"]
    r = client.post("/api/v1/admin/resources", json={"content": "x"},
                    headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 400


def test_member_onboarding_and_full_task_loop(client, db_session):
    _seed(db_session)
    admin = _login(client, "13800138000")
    H = _h(admin["token"], 101)
    # 录入成员
    r = client.post("/api/v1/admin/members", json={"phone": "13912345678", "name": "张三"}, headers=H)
    assert r.status_code == 200, r.text
    # 成员登录直达
    m = _login(client, "13912345678")
    assert m["default_tenant_id"] == 101
    mH = _h(m["token"], 101)
    # 建资源（含溯源）
    r = client.post("/api/v1/admin/resources",
                    json={"content": "报销需发票", "score": 10, "ai_rag_sources": []}, headers=H)
    rid = r.json()["data"]["id"]
    # 下任务
    r = client.post("/api/v1/admin/tasks",
                    json={"title": "Q3测评", "verification_mode": "manual",
                          "resource_ids": [rid]}, headers=H)
    task_id = r.json()["data"]["task_id"]
    db_session.query(Task).filter(Task.id == task_id).update({"status": "published"})
    db_session.commit()
    # 待办
    todo = client.get("/api/v1/member/tasks", headers=mH)
    assert todo.status_code == 200 and any(i["task_id"] == task_id for i in todo.json()["data"]["items"])
    # 提交 + 防重交
    s = client.post("/api/v1/member/task-records/submit",
                    json={"task_id": task_id, "time_spent": 60,
                          "answers": [{"resource_id": rid, "answer": "A"}]}, headers=mH)
    assert s.status_code == 200
    s2 = client.post("/api/v1/member/task-records/submit",
                     json={"task_id": task_id, "time_spent": 60, "answers": []}, headers=mH)
    assert s2.status_code == 400


def test_kb_scope_and_ai_traceability(client, db_session):
    _seed(db_session)
    admin = _login(client, "13800138000")
    H = _h(admin["token"], 101)
    m = client.post("/api/v1/admin/members", json={"phone": "13912345678"}, headers=H)
    assert m.status_code == 200
    mtok = _login(client, "13912345678")["token"]
    mH = _h(mtok, 101)
    # 管理员上传 public
    up = client.post("/api/v1/admin/kb/documents", headers=H,
                     files={"file": ("handbook.txt", "报销必须提供发票复印件".encode("utf-8"))},
                     data={"scope": "public"})
    assert up.status_code == 200
    # 成员传 public 会被强制 private
    up2 = client.post("/api/v1/member/kb/documents", headers=mH,
                      files={"file": ("note.txt", "我的私密笔记".encode("utf-8"))},
                      data={"scope": "public"})
    assert up2.status_code == 200
    docs = client.get("/api/v1/member/kb/documents", headers=mH).json()["data"]["items"]
    scopes = {d["file_name"]: d["scope"] for d in docs}
    assert scopes.get("handbook.txt") == "public"
    assert scopes.get("note.txt") == "private"
    # AI 对话强制溯源
    chat = client.post("/api/v1/admin/ai/chat", json={"message": "报销"}, headers=H)
    assert chat.status_code == 200
    assert "ai_rag_sources" in chat.json()["data"]
    # AI 出题/组卷强制溯源落库
    gen = client.post("/api/v1/admin/ai/generate-resources",
                      json={"topic": "报销合规", "count": 1}, headers=H)
    assert gen.status_code == 200 and "ai_rag_sources" in gen.json()["data"]
    asm = client.post("/api/v1/admin/ai/assemble-task",
                      json={"title": "AI任务", "resource_ids": gen.json()["data"]["resource_ids"]},
                      headers=H)
    assert asm.status_code == 201 and "ai_rag_sources" in asm.json()["data"]


def test_ops_dashboard_banners_notifications_audit(client, db_session):
    _seed(db_session)
    admin = _login(client, "13800138000")
    H = _h(admin["token"], 101)
    # 看板（空数据亦可出形）
    s = client.get("/api/v1/admin/dashboard/stats", headers=H)
    assert s.status_code == 200
    d = s.json()["data"]
    assert set(["kpi", "trend", "donut", "hot", "recent", "notices", "quota"]) <= set(d.keys())
    assert len(d["trend"]) == 7
    # 横幅 CRUD + 配置
    b = client.post("/api/v1/admin/banners",
                    json={"image_url": "/uploads/x.png", "sort_order": 1}, headers=H)
    assert b.status_code == 201
    bid = b.json()["data"]["id"]
    assert client.get("/api/v1/admin/banners", headers=H).json()["data"][0]["id"] == bid
    assert client.put(f"/api/v1/admin/banners/{bid}", json={"is_enabled": False},
                      headers=H).status_code == 200
    assert client.get("/api/v1/member/banners", headers=H).json()["data"]["items"] == []
    assert client.put("/api/v1/admin/banners/settings", json={"interval_seconds": 6},
                      headers=H).json()["data"]["interval_seconds"] == 6
    assert client.get("/api/v1/admin/banners/settings", headers=H).json()["data"]["interval_seconds"] == 6
    # 上传
    up = client.post("/api/v1/admin/upload", headers=H,
                     files={"file": ("p.png", b"\x89PNG\r\n\x1a\n" + b"0" * 100)})
    assert up.status_code == 201 and up.json()["data"]["url"].startswith("/uploads/")
    # 录入成员产生审计 + 提交产生通知
    client.post("/api/v1/admin/members", json={"phone": "13912345678"}, headers=H)
    a = client.get("/api/v1/admin/audit", headers=H).json()["data"]
    assert a["total"] >= 1 and any("13912345678" in (i["summary"] or "") for i in a["items"])
    mtok = _login(client, "13912345678")["token"]
    mH = _h(mtok, 101)
    r = client.post("/api/v1/admin/resources", json={"content": "条目"}, headers=H)
    t = client.post("/api/v1/admin/tasks",
                    json={"title": "T", "verification_mode": "ai_auto",
                          "resource_ids": [r.json()["data"]["id"]]}, headers=H)
    tid = t.json()["data"]["task_id"]
    db_session.query(Task).filter(Task.id == tid).update({"status": "published"})
    db_session.commit()
    client.post("/api/v1/member/task-records/submit",
                json={"task_id": tid, "answers": []}, headers=mH)
    n = client.get("/api/v1/admin/notifications", headers=H).json()["data"]
    assert n["total"] >= 1 and any("待核验" in i["title"] for i in n["items"])
    assert client.get("/api/v1/admin/notifications/unread-count", headers=H).json()["data"]["count"] >= 1
    assert client.post("/api/v1/admin/notifications/read", json={"ids": None},
                       headers=H).status_code == 200
    assert client.get("/api/v1/admin/notifications/unread-count", headers=H).json()["data"]["count"] == 0
    # 成员看不见管理通知
    assert client.get("/api/v1/admin/notifications", headers=mH).json()["data"]["total"] == 0


def test_ai_session_persistence_and_traceability(client, db_session):
    _seed(db_session)
    admin = _login(client, "13800138000")
    H = _h(admin["token"], 101)
    # 上传公共知识使溯源非空
    client.post("/api/v1/admin/kb/documents", headers=H,
                files={"file": ("h.txt", "报销必须提供发票复印件".encode("utf-8"))},
                data={"scope": "public"})
    # 对话（无 session_id 自动建会话并持久化）
    r = client.post("/api/v1/admin/ai/chat", json={"message": "报销需要什么"}, headers=H)
    assert r.status_code == 200
    d = r.json()["data"]
    assert "ai_rag_sources" in d and len(d["ai_rag_sources"]) >= 1
    sid = d["session_id"]
    assert sid
    # 会话列表与消息持久化
    ss = client.get("/api/v1/admin/ai/sessions", headers=H).json()["data"]["items"]
    assert any(s["id"] == sid for s in ss)
    ms = client.get(f"/api/v1/admin/ai/sessions/{sid}/messages", headers=H).json()["data"]
    assert len(ms["items"]) == 2
    assert ms["items"][1]["role"] == "assistant"
    assert len(ms["items"][1]["ai_rag_sources"]) >= 1
    # 同会话追问
    r2 = client.post("/api/v1/admin/ai/chat", json={"message": "还有呢", "session_id": sid}, headers=H)
    assert r2.json()["data"]["session_id"] == sid
    assert len(client.get(f"/api/v1/admin/ai/sessions/{sid}/messages",
                          headers=H).json()["data"]["items"]) == 4
    # 他人会话不可见
    client.post("/api/v1/admin/members", json={"phone": "13912345678"}, headers=H)
    m2 = _login(client, "13912345678")
    r3 = client.get(f"/api/v1/admin/ai/sessions/{sid}/messages",
                    headers=_h(m2["token"], 101))
    assert r3.status_code == 404
    # 重命名与删除
    assert client.put(f"/api/v1/admin/ai/sessions/{sid}", json={"title": "报销问答"},
                      headers=H).json()["data"]["title"] == "报销问答"
    assert client.delete(f"/api/v1/admin/ai/sessions/{sid}", headers=H).status_code == 200
    assert all(s["id"] != sid for s in
               client.get("/api/v1/admin/ai/sessions", headers=H).json()["data"]["items"])


def test_server_authoritative_timing_anti_cheat(client, db_session):
    from datetime import datetime, timedelta
    _seed(db_session)
    admin = _login(client, "13800138000")
    H = _h(admin["token"], 101)
    client.post("/api/v1/admin/members", json={"phone": "13912345678"}, headers=H)
    m = _login(client, "13912345678")
    mH = _h(m["token"], 101)
    r = client.post("/api/v1/admin/resources", json={"content": "计时条目"}, headers=H)
    rid = r.json()["data"]["id"]
    t = client.post("/api/v1/admin/tasks",
                    json={"title": "限时任务", "is_timed": True, "time_limit": 30,
                          "resource_ids": [rid]}, headers=H).json()["data"]
    tid = t["task_id"]
    db_session.query(Task).filter(Task.id == tid).update({"status": "published"})
    db_session.commit()
    e1 = client.get(f"/api/v1/member/tasks/{tid}/entry", headers=mH).json()["data"]
    assert e1["server_now"] and e1["started_at"]
    e2 = client.get(f"/api/v1/member/tasks/{tid}/entry", headers=mH).json()["data"]
    # 未交卷(pending)状态下再次进入会重置开考时刻，修复崩溃/误退后重进导致用时被错误累加；
    # 但作答记录行必须复用同一条，不得新增。
    assert datetime.fromisoformat(e2["started_at"]) >= datetime.fromisoformat(e1["started_at"])
    assert e2["my_record_id"] == e1["my_record_id"]
    # 伪造超大用时 → 服务端忽略
    s = client.post("/api/v1/member/task-records/submit", headers=mH,
                    json={"task_id": tid, "time_spent": 999999,
                          "answers": [{"resource_id": rid, "answer": "X"}]})
    assert s.status_code == 200
    assert s.json()["data"]["time_spent"] < 600, s.json()["data"]
    # 截止后拒绝提交
    t2 = client.post("/api/v1/admin/tasks", json={"title": "过期任务", "resource_ids": [rid]},
                     headers=H).json()["data"]
    db_session.query(Task).filter(Task.id == t2["task_id"]).update(
        {"status": "published", "deadline": datetime.now() - timedelta(minutes=1)})
    db_session.commit()
    s2 = client.post("/api/v1/member/task-records/submit", headers=mH,
                     json={"task_id": t2["task_id"], "answers": []})
    assert s2.status_code == 400


def test_tenant_ai_config_override_and_masking(client, db_session):
    from app.api.saas.ai import _tenant_provider
    _seed(db_session)
    admin = _login(client, "13800138000")
    H = _h(admin["token"], 101)
    g = client.get("/api/v1/admin/ai/config", headers=H).json()["data"]
    assert g["source"] == "env" and g["chat_api_key_masked"] == ""
    assert client.put("/api/v1/admin/ai/config", headers=H, json={
        "chat_api_url": "https://example.invalid/v1/chat/completions",
        "chat_api_key": "sk-test-12345678", "chat_model": "test-model"}).status_code == 200
    g2 = client.get("/api/v1/admin/ai/config", headers=H).json()["data"]
    assert g2["source"] == "tenant" and g2["chat_api_key_masked"] == "****5678"
    assert g2["chat_api_key_masked"] != "sk-test-12345678"
    prov = _tenant_provider(db_session, 101)
    assert prov and prov["model"] == "test-model"
    # 成员无权查看配置
    client.post("/api/v1/admin/members", json={"phone": "13912345678"}, headers=H)
    m = _login(client, "13912345678")
    assert client.get("/api/v1/admin/ai/config",
                      headers=_h(m["token"], 101)).status_code == 403
    # 关闭开关 → 回退环境
    client.put("/api/v1/admin/ai/config", headers=H, json={"enabled": False})
    assert _tenant_provider(db_session, 101) is None


def test_vector_local_branch_and_tidb_guard(client, db_session):
    import json
    import os
    from app.services.vector_store import rag_search, tidb_vector_enabled
    from app.models.saas import KbDocument, KbChunk
    _seed(db_session)
    assert tidb_vector_enabled() is False, "本地测试环境 TIDB_VECTOR 必须保持关闭"
    doc = KbDocument(tenant_id=101, scope="public", creator_id=2, file_name="v.txt")
    db_session.add(doc)
    db_session.flush()
    db_session.add(KbChunk(tenant_id=101, document_id=doc.id,
                           content="报销必须提供发票", embedding=json.dumps([1.0, 0.0, 0.0])))
    db_session.add(KbChunk(tenant_id=101, document_id=doc.id,
                           content="无关内容", embedding=json.dumps([0.0, 1.0, 0.0])))
    db_session.commit()
    hits = rag_search(db_session, 101, "报销", limit=2, query_vec=[1.0, 0.0, 0.0])
    assert hits and "发票" in hits[0]["chunk_content"] and hits[0]["similarity_score"] > 0.9
    # 无向量回退 LIKE
    hits2 = rag_search(db_session, 101, "报销", limit=2, query_vec=None)
    assert any("发票" in h["chunk_content"] for h in hits2)
    # TiDB 开关置1但无真实云库 → 必须回退本地，不抛异常不连云
    os.environ["TIDB_VECTOR"] = "1"
    try:
        hits3 = rag_search(db_session, 101, "报销", limit=2, query_vec=[1.0, 0.0, 0.0])
        assert hits3 and "发票" in hits3[0]["chunk_content"]
    finally:
        os.environ["TIDB_VECTOR"] = "0"


def test_super_admin_flow(client, db_session):
    _seed(db_session)
    god = _login(client, "10000000000", "godpw")
    assert god["user"]["is_super_admin"] is True
    gh = {"Authorization": f"Bearer {god['token']}"}
    r = client.get("/api/v1/super-admin/tenants", headers=gh)
    assert r.status_code == 200 and len(r.json()["data"]["items"]) == 2
    # 普通成员禁入上帝视图
    mtok = _login(client, "13800138000")["token"]
    r = client.get("/api/v1/super-admin/tenants",
                   headers={"Authorization": f"Bearer {mtok}"})
    assert r.status_code == 403
    # 上帝视察需带头（无头指引 403）
    r = client.post("/api/v1/admin/resources", json={"content": "视察"},
                    headers={"Authorization": f"Bearer {god['token']}"})
    assert r.status_code == 403 and "视察企业" in r.json().get("detail", "")
    r = client.post("/api/v1/admin/resources", json={"content": "视察"},
                    headers=_h(god["token"], 102))
    assert r.status_code == 201


def test_subjective_manual_retake_and_member_stats(client, db_session):
    """回归：manual 含简答卷必须进核验池 + 截止前可重考 + 个人中心统计口径。"""
    from datetime import datetime, timedelta
    _seed(db_session)
    admin = _login(client, "13800138000")
    H = _h(admin["token"], 101)
    client.post("/api/v1/admin/members", json={"phone": "13912345678"}, headers=H)
    m = _login(client, "13912345678")
    mH = _h(m["token"], 101)

    rid1 = client.post("/api/v1/admin/resources",
                       json={"content": "客观题", "type": "single_choice",
                             "correct_answer": ["A"], "score": 10},
                       headers=H).json()["data"]["id"]
    rid2 = client.post("/api/v1/admin/resources",
                       json={"content": "简答题：请简述报销流程", "type": "short", "score": 20},
                       headers=H).json()["data"]["id"]

    # 一、manual 卷含简答题：交卷必须转 pending_verification（而非错误地定稿 submitted）
    t = client.post("/api/v1/admin/tasks",
                    json={"title": "人工卷含简答", "verification_mode": "manual",
                          "resource_ids": [rid1, rid2]},
                    headers=H).json()["data"]
    tid = t["task_id"]
    db_session.query(Task).filter(Task.id == tid).update(
        {"status": "published", "deadline": datetime.now() + timedelta(days=1)})
    db_session.commit()

    s = client.post("/api/v1/member/task-records/submit", headers=mH,
                    json={"task_id": tid, "answers": [
                        {"resource_id": rid1, "answer": "A"},
                        {"resource_id": rid2, "answer": "先粘贴发票再提交审批"}]})
    assert s.status_code == 200, s.text
    assert s.json()["data"]["status"] == "pending_verification", s.json()["data"]
    assert s.json()["data"]["score"] == 10, "客观题应即时判分，简答题不计分"
    rec_id = s.json()["data"]["record_id"]

    # 二、member-tasks 下发 can_continue：manual + 含简答 + 审核中 + 未到期 → True
    items = client.get("/api/v1/member/member-tasks", headers=mH).json()["data"]["items"]
    item = next(i for i in items if i["task_id"] == tid)
    assert item["can_continue"] is True
    assert item["verification_mode"] == "manual"

    # 三、统计：1 场（审核中）；10 分 < 30×60%=18 → 不通过
    st = client.get("/api/v1/member/me/stats", headers=mH).json()["data"]
    assert st["total_exams_taken"] == 1 and st["history_count"] == 1
    assert st["passed_count"] == 0 and st["pass_rate"] == 0.0
    assert st["favorite_count"] == 0

    # 四、继续测试：记录原地退回 pending 且**保留上次作答**，入口接口原样透传供考场回填
    ct = client.post(f"/api/v1/member/tasks/{tid}/continue", headers=mH)
    assert ct.status_code == 200, ct.text
    assert ct.json()["data"]["record_id"] == rec_id
    assert ct.json()["data"]["status"] == "pending"
    assert client.get("/api/v1/member/me/stats",
                      headers=mH).json()["data"]["total_exams_taken"] == 0
    entry = client.get(f"/api/v1/member/tasks/{tid}/entry", headers=mH).json()["data"]
    assert entry["my_status"] == "pending"
    assert entry["my_answers"] == [{"resource_id": rid1, "answer": "A"},
                                   {"resource_id": rid2, "answer": "先粘贴发票再提交审批"}], \
        entry["my_answers"]
    items2 = client.get("/api/v1/member/member-tasks", headers=mH).json()["data"]["items"]
    assert next(i for i in items2 if i["task_id"] == tid)["can_continue"] is False

    # 五、续答后重新交卷：再次回到审核中；强制终审满分 → 通过率 100%
    s2 = client.post("/api/v1/member/task-records/submit", headers=mH,
                     json={"task_id": tid, "answers": [
                         {"resource_id": rid1, "answer": "A"},
                         {"resource_id": rid2, "answer": "已改答"}]})
    assert s2.status_code == 200, s2.text
    assert s2.json()["data"]["status"] == "pending_verification", s2.json()["data"]
    db_session.query(TaskRecord).filter(TaskRecord.id == rec_id).update(
        {"score": 30, "status": "verified"})
    db_session.commit()
    st2 = client.get("/api/v1/member/me/stats", headers=mH).json()["data"]
    assert st2["total_exams_taken"] == 1 and st2["passed_count"] == 1
    assert st2["pass_rate"] == 100.0

    # 六、已核验（已出成绩）不可继续测试
    assert client.post(f"/api/v1/member/tasks/{tid}/continue", headers=mH).status_code == 400

    # 七、已截止不可继续测试
    t2 = client.post("/api/v1/admin/tasks",
                     json={"title": "过期卷", "resource_ids": [rid1]},
                     headers=H).json()["data"]
    db_session.query(Task).filter(Task.id == t2["task_id"]).update(
        {"status": "published", "deadline": datetime.now() + timedelta(days=1)})
    db_session.commit()
    sub2 = client.post("/api/v1/member/task-records/submit", headers=mH,
                       json={"task_id": t2["task_id"],
                             "answers": [{"resource_id": rid1, "answer": "A"}]})
    assert sub2.status_code == 200
    db_session.query(Task).filter(Task.id == t2["task_id"]).update(
        {"deadline": datetime.now() - timedelta(minutes=1)})
    db_session.commit()
    late = client.post(f"/api/v1/member/tasks/{t2['task_id']}/continue", headers=mH)
    assert late.status_code == 400 and "截止" in late.json()["detail"]

    # 八、对照一：manual 纯客观卷交卷即定稿 submitted，且不提供继续测试入口
    t3 = client.post("/api/v1/admin/tasks",
                     json={"title": "人工纯客观卷", "verification_mode": "manual",
                           "resource_ids": [rid1]}, headers=H).json()["data"]
    db_session.query(Task).filter(Task.id == t3["task_id"]).update({"status": "published"})
    db_session.commit()
    s3 = client.post("/api/v1/member/task-records/submit", headers=mH,
                     json={"task_id": t3["task_id"],
                           "answers": [{"resource_id": rid1, "answer": "A"}]})
    assert s3.status_code == 200
    assert s3.json()["data"]["status"] == "submitted", s3.json()["data"]
    items3 = client.get("/api/v1/member/member-tasks", headers=mH).json()["data"]["items"]
    assert next(i for i in items3 if i["task_id"] == t3["task_id"])["can_continue"] is False
    assert client.post(f"/api/v1/member/tasks/{t3['task_id']}/continue",
                       headers=mH).status_code == 400

    # 九、对照二：AI 全托管含简答卷即使处于审核中也不给继续测试（前提是人工审核模式）
    t4 = client.post("/api/v1/admin/tasks",
                     json={"title": "AI卷含简答", "verification_mode": "ai_auto",
                           "resource_ids": [rid1, rid2]}, headers=H).json()["data"]
    db_session.query(Task).filter(Task.id == t4["task_id"]).update(
        {"status": "published", "deadline": datetime.now() + timedelta(days=1)})
    db_session.commit()
    s4 = client.post("/api/v1/member/task-records/submit", headers=mH,
                     json={"task_id": t4["task_id"],
                           "answers": [{"resource_id": rid1, "answer": "A"}]})
    assert s4.status_code == 200
    assert s4.json()["data"]["status"] == "pending_verification"
    items4 = client.get("/api/v1/member/member-tasks", headers=mH).json()["data"]["items"]
    assert next(i for i in items4 if i["task_id"] == t4["task_id"])["can_continue"] is False
    assert client.post(f"/api/v1/member/tasks/{t4['task_id']}/continue",
                       headers=mH).status_code == 400
