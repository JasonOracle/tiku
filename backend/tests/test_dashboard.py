"""Dashboard 聚合接口回归：结构完整、计数正确、出题人作用域隔离"""


def _admin(client):
    client.post("/api/v1/admin/auth/init", json={"username": "admin_db", "password": "adminpassword"})
    t = client.post("/api/v1/admin/auth/login", json={"username": "admin_db", "password": "adminpassword"}).json()["data"]["token"]
    return {"Authorization": f"Bearer {t}"}


def test_dashboard_stats_structure_and_counts(client):
    ah = _admin(client)
    cat = client.post("/api/v1/admin/categories", json={"name": "c", "target_type": "exam"}, headers=ah).json()["data"]
    q = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "t?", "options": [{"key": "A", "text": "a"}],
        "answer": ["A"], "score": 10,
    }, headers=ah).json()["data"]
    ex = client.post("/api/v1/admin/exams", json={
        "title": "e", "category_id": cat["id"], "status": "published", "question_ids": [q["id"]],
    }, headers=ah).json()["data"]
    client.post("/api/v1/auth/register", json={"username": "u_db", "password": "pw123456", "nickname": "看板学员", "gender": "male", "phone": "13900010002"})
    ut = client.post("/api/v1/auth/login", json={"username": "u_db", "password": "pw123456", "nickname": "看板学员", "gender": "male", "phone": "13900010002"}).json()["data"]["token"]
    uh = {"Authorization": f"Bearer {ut}"}
    rec = client.post("/api/v1/records/start", json={"exam_id": ex["id"]}, headers=uh).json()["data"]["record_id"]
    client.post("/api/v1/records/submit", json={"record_id": rec, "user_answers": {str(q["id"]): ["A"]}, "time_spent": 10}, headers=uh)

    r = client.get("/api/v1/admin/dashboard/stats", headers=ah)
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["kpi"]["exams"] == 1
    assert d["kpi"]["records"] == 1
    assert len(d["trend"]) == 7 and all({"day", "count", "avg"} <= set(t) for t in d["trend"])
    assert d["donut"] == [{"name": "c", "value": 1}]
    assert d["hot"][0]["title"] == "e" and d["hot"][0]["count"] == 1
    assert len(d["recent"]) == 1 and d["recent"][0]["score"] == 10
    assert {"used_today", "remaining", "limit"} <= set(d["quota"])


def test_dashboard_creator_scoped_to_own(client):
    ah = _admin(client)
    cat = client.post("/api/v1/admin/categories", json={"name": "c2", "target_type": "exam"}, headers=ah).json()["data"]
    q = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "t2?", "options": [{"key": "A", "text": "a"}],
        "answer": ["A"], "score": 10,
    }, headers=ah).json()["data"]
    client.post("/api/v1/admin/exams", json={
        "title": "super卷", "category_id": cat["id"], "status": "published", "question_ids": [q["id"]],
    }, headers=ah)
    client.post("/api/v1/admin/members", json={"username": "teacher_db", "password": "pw123456"}, headers=ah)
    tt = client.post("/api/v1/admin/auth/login", json={"username": "teacher_db", "password": "pw123456"}).json()["data"]["token"]
    th = {"Authorization": f"Bearer {tt}"}
    d = client.get("/api/v1/admin/dashboard/stats", headers=th).json()["data"]
    assert d["kpi"]["exams"] == 0
    assert d["kpi"]["records"] == 0
    assert d["hot"] == [] and d["recent"] == []
