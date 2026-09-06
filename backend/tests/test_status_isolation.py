"""P0/P1 状态隔离回归测试：draft 不可见、不可开考、已上架锁定、B端详情可读"""
def _setup_admin_and_user(client):
    client.post("/api/v1/admin/auth/init", json={"username": "admin_iso", "password": "adminpassword"})
    admin_login = client.post("/api/v1/admin/auth/login", json={"username": "admin_iso", "password": "adminpassword"})
    admin_token = admin_login.json()["data"]["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    client.post("/api/v1/auth/register", json={"username": "user_iso", "password": "userpassword", "nickname": "隔离学员", "gender": "female", "phone": "13900010004"})
    user_login = client.post("/api/v1/auth/login", json={"username": "user_iso", "password": "userpassword", "nickname": "隔离学员", "gender": "female", "phone": "13900010004"})
    user_token = user_login.json()["data"]["token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    cat_res = client.post("/api/v1/admin/categories", json={"name": "隔离分类", "icon": "fire", "sort_order": 1}, headers=admin_headers)
    cat_id = cat_res.json()["data"]["id"]
    q_res = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "隔离题目?",
        "options": [{"key": "A", "text": "a"}, {"key": "B", "text": "b"}],
        "answer": ["A"], "score": 10, "category_id": cat_id
    }, headers=admin_headers)
    q_id = q_res.json()["data"]["id"]
    return admin_headers, user_headers, cat_id, q_id


def test_draft_exam_invisible_and_cannot_start(client):
    admin_headers, user_headers, cat_id, q_id = _setup_admin_and_user(client)
    exam_res = client.post("/api/v1/admin/exams", json={
        "title": "草稿卷", "category_id": cat_id, "status": "draft",
        "question_ids": [q_id]
    }, headers=admin_headers)
    assert exam_res.status_code == 201
    exam_id = exam_res.json()["data"]["id"]

    # C端列表不可见
    lst = client.get("/api/v1/exams?page=1&size=10", headers=user_headers)
    assert lst.status_code == 200
    ids = [x["id"] for x in lst.json()["data"]["items"]]
    assert exam_id not in ids

    # C端详情404
    det = client.get(f"/api/v1/exams/{exam_id}", headers=user_headers)
    assert det.status_code == 404

    # C端不可开考
    st = client.post("/api/v1/records/start", json={"exam_id": exam_id}, headers=user_headers)
    assert st.status_code == 404


def test_admin_can_get_exam_detail_even_draft(client):
    admin_headers, user_headers, cat_id, q_id = _setup_admin_and_user(client)
    exam_res = client.post("/api/v1/admin/exams", json={
        "title": "草稿卷2", "category_id": cat_id, "status": "draft",
        "question_ids": [q_id]
    }, headers=admin_headers)
    exam_id = exam_res.json()["data"]["id"]
    det = client.get(f"/api/v1/admin/exams/{exam_id}", headers=admin_headers)
    assert det.status_code == 200
    assert len(det.json()["data"]["questions"]) == 1


def test_published_exam_locks_question_update(client):
    admin_headers, user_headers, cat_id, q_id = _setup_admin_and_user(client)
    exam_res = client.post("/api/v1/admin/exams", json={
        "title": "发布卷", "category_id": cat_id, "status": "published",
        "question_ids": [q_id]
    }, headers=admin_headers)
    exam_id = exam_res.json()["data"]["id"]
    # 新建第二题用于尝试篡改组卷
    q2 = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "第二题?",
        "options": [{"key": "A", "text": "a"}, {"key": "B", "text": "b"}],
        "answer": ["B"], "score": 10, "category_id": cat_id
    }, headers=admin_headers)
    q2_id = q2.json()["data"]["id"]
    upd = client.put(f"/api/v1/admin/exams/{exam_id}", json={"question_ids": [q_id, q2_id]}, headers=admin_headers)
    assert upd.status_code == 400


def test_exam_stats_board_no_500(client):
    admin_headers, user_headers, cat_id, q_id = _setup_admin_and_user(client)
    exam_res = client.post("/api/v1/admin/exams", json={
        "title": "统计卷", "category_id": cat_id, "status": "published",
        "question_ids": [q_id]
    }, headers=admin_headers)
    exam_id = exam_res.json()["data"]["id"]
    start = client.post("/api/v1/records/start", json={"exam_id": exam_id}, headers=user_headers)
    record_id = start.json()["data"]["record_id"]
    client.post("/api/v1/records/submit", json={
        "record_id": record_id, "user_answers": {str(q_id): ["A"]}, "time_spent": 30
    }, headers=user_headers)
    stats = client.get(f"/api/v1/admin/exams/{exam_id}/stats", headers=admin_headers)
    assert stats.status_code == 200
    assert stats.json()["data"]["total_participants"] == 1
