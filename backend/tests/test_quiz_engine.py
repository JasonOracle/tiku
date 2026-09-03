def test_full_quiz_lifecycle(client):
    # 1. 初始化管理员并登录
    client.post("/api/v1/admin/auth/init", json={"username": "admin_quiz", "password": "adminpassword"})
    admin_login = client.post("/api/v1/admin/auth/login", json={"username": "admin_quiz", "password": "adminpassword"})
    admin_token = admin_login.json()["data"]["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. 创建试卷分类
    cat_res = client.post("/api/v1/admin/categories", json={"name": "消防知识", "icon": "fire", "sort_order": 1}, headers=admin_headers)
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["data"]["id"]

    # 3. 创建题目 (单选题与多选题，单题各 50 分)
    q1_res = client.post("/api/v1/admin/questions", json={
        "type": "single",
        "title": "发生火灾时优先使用哪种灭火器？",
        "options": [{"key": "A", "text": "干粉灭火器"}, {"key": "B", "text": "水流"}],
        "answer": ["A"],
        "explanation": "干粉灭火器适用范围广",
        "score": 50,
        "category_id": cat_id
    }, headers=admin_headers)
    q1_id = q1_res.json()["data"]["id"]

    q2_res = client.post("/api/v1/admin/questions", json={
        "type": "multiple",
        "title": "火灾逃生正确做法包括哪些？",
        "options": [{"key": "A", "text": "用湿毛巾捂住口鼻"}, {"key": "B", "text": "弯腰低姿前行"}, {"key": "C", "text": "乘坐普通电梯"}],
        "answer": ["A", "B"],
        "explanation": "严禁乘坐电梯",
        "score": 50,
        "category_id": cat_id
    }, headers=admin_headers)
    q2_id = q2_res.json()["data"]["id"]

    # 4. 创建组装试卷并直接上线发布
    exam_res = client.post("/api/v1/admin/exams", json={
        "title": "2026年消防安全基础测试卷",
        "category_id": cat_id,
        "is_timed": True,
        "time_limit": 15,
        "status": "published",
        "is_recommended": True,
        "questions": [
            {"question_id": q1_id, "score": 50, "sort_order": 1},
            {"question_id": q2_id, "score": 50, "sort_order": 2}
        ]
    }, headers=admin_headers)
    assert exam_res.status_code == 201
    exam_id = exam_res.json()["data"]["id"]

    # 5. C端注册用户并登录
    client.post("/api/v1/auth/register", json={"username": "test_user", "password": "userpassword"})
    user_login = client.post("/api/v1/auth/login", json={"username": "test_user", "password": "userpassword"})
    user_token = user_login.json()["data"]["token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 6. C端开启答题
    start_res = client.post("/api/v1/records/start", json={"exam_id": exam_id}, headers=user_headers)
    assert start_res.status_code == 200
    record_id = start_res.json()["data"]["record_id"]
    assert len(start_res.json()["data"]["questions"]) == 2

    # 7. 提交答卷 (全对：得分100，及格)
    submit_res = client.post("/api/v1/records/submit", json={
        "record_id": record_id,
        "user_answers": {
            str(q1_id): ["A"],
            str(q2_id): ["A", "B"]
        },
        "time_spent": 120
    }, headers=user_headers)
    assert submit_res.status_code == 200
    report = submit_res.json()["data"]
    assert report["score"] == 100
    assert report["passed"] is True
    assert report["correct_count"] == 2

    # 8. 重复提交防重拦截拦截测试
    repeat_submit = client.post("/api/v1/records/submit", json={
        "record_id": record_id,
        "user_answers": {str(q1_id): ["A"]},
        "time_spent": 130
    }, headers=user_headers)
    assert repeat_submit.status_code == 400

    # 9. 题目收藏与取消收藏
    fav_res = client.post("/api/v1/favorites", json={"question_id": q1_id}, headers=user_headers)
    assert fav_res.status_code == 201

    fav_list = client.get("/api/v1/favorites", headers=user_headers)
    assert fav_list.status_code == 200
    assert fav_list.json()["data"]["total"] == 1

    del_fav = client.delete(f"/api/v1/favorites/{q1_id}", headers=user_headers)
    assert del_fav.status_code == 200
