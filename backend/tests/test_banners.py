"""Banner 模块回归：上限3启用、链接校验、C端隔离、秒数设置、报告总分字段"""


def _admin(client):
    client.post("/api/v1/admin/auth/init", json={"username": "admin_bn", "password": "adminpassword"})
    t = client.post("/api/v1/admin/auth/login", json={"username": "admin_bn", "password": "adminpassword"}).json()["data"]["token"]
    return {"Authorization": f"Bearer {t}"}


def _mk(client, ah, img="preset:1", link_type="none", link_value="", enabled=True, sort=0):
    return client.post("/api/v1/admin/banners", json={
        "image_url": img, "link_type": link_type, "link_value": link_value,
        "sort_order": sort, "is_enabled": enabled,
    }, headers=ah)


def test_max_three_enabled(client):
    ah = _admin(client)
    for i in range(3):
        r = _mk(client, ah, img=f"preset:{i + 1}", sort=i)
        assert r.status_code == 201
    r4 = _mk(client, ah, img="preset:4")
    assert r4.status_code == 400
    # 禁用的可建
    r5 = _mk(client, ah, img="preset:5", enabled=False)
    assert r5.status_code == 201
    # 把禁用的打开同样被拦
    b5 = r5.json()["data"]["id"]
    assert client.put(f"/api/v1/admin/banners/{b5}", json={"is_enabled": True}, headers=ah).status_code == 400


def test_link_validation(client):
    ah = _admin(client)
    assert _mk(client, ah, link_type="external", link_value="").status_code == 400
    assert _mk(client, ah, link_type="internal", link_value="profile").status_code == 400
    assert _mk(client, ah, link_type="internal", link_value="/profile").status_code == 201


def test_client_sees_only_enabled_with_interval(client):
    ah = _admin(client)
    _mk(client, ah, img="preset:1", sort=1)
    _mk(client, ah, img="preset:2", sort=0, enabled=False)
    client.put("/api/v1/admin/banners/settings", json={"interval_seconds": 6}, headers=ah)
    r = client.get("/api/v1/banners")
    assert r.status_code == 200
    assert r.json()["data"]["interval_seconds"] == 6
    items = r.json()["data"]["items"]
    assert len(items) == 1 and items[0]["image_url"] == "preset:1"


def test_report_has_total_scores(client):
    client.post("/api/v1/admin/auth/init", json={"username": "admin_rp", "password": "adminpassword"})
    at = client.post("/api/v1/admin/auth/login", json={"username": "admin_rp", "password": "adminpassword"}).json()["data"]["token"]
    ah = {"Authorization": f"Bearer {at}"}
    cat = client.post("/api/v1/admin/categories", json={"name": "c", "target_type": "exam"}, headers=ah).json()["data"]
    q = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "t?", "options": [{"key": "A", "text": "a"}],
        "answer": ["A"], "score": 25, "category_id": cat["id"],
    }, headers=ah).json()["data"]
    ex = client.post("/api/v1/admin/exams", json={
        "title": "e", "category_id": cat["id"], "status": "published", "question_ids": [q["id"]],
    }, headers=ah).json()["data"]
    client.post("/api/v1/auth/register", json={"username": "u_rp", "password": "pw123456", "nickname": "推广学员", "gender": "female", "phone": "13900010001"})
    ut = client.post("/api/v1/auth/login", json={"username": "u_rp", "password": "pw123456", "nickname": "推广学员", "gender": "female", "phone": "13900010001"}).json()["data"]["token"]
    uh = {"Authorization": f"Bearer {ut}"}
    rec = client.post("/api/v1/records/start", json={"exam_id": ex["id"]}, headers=uh).json()["data"]["record_id"]
    rep = client.post("/api/v1/records/submit", json={"record_id": rec, "user_answers": {str(q["id"]): ["A"]}, "time_spent": 10}, headers=uh).json()["data"]
    assert rep["total_score"] == 25
    assert rep["pass_score"] == 15
