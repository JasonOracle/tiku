"""数据治理回归测试：分类/题目/试卷删除守卫、分类快照、空卷拦截、导入行级分类"""
import io
import openpyxl


def _setup(client):
    client.post("/api/v1/admin/auth/init", json={"username": "admin_gov", "password": "adminpassword"})
    admin_token = client.post("/api/v1/admin/auth/login", json={"username": "admin_gov", "password": "adminpassword"}).json()["data"]["token"]
    ah = {"Authorization": f"Bearer {admin_token}"}
    client.post("/api/v1/auth/register", json={"username": "user_gov", "password": "userpassword"})
    user_token = client.post("/api/v1/auth/login", json={"username": "user_gov", "password": "userpassword"}).json()["data"]["token"]
    uh = {"Authorization": f"Bearer {user_token}"}
    qcat = client.post("/api/v1/admin/categories", json={"name": "题分类A", "icon": "f", "sort_order": 1, "target_type": "question"}, headers=ah).json()["data"]
    ecat = client.post("/api/v1/admin/categories", json={"name": "卷分类A", "icon": "f", "sort_order": 1, "target_type": "exam"}, headers=ah).json()["data"]
    q = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "治理题?", "options": [{"key": "A", "text": "a"}, {"key": "B", "text": "b"}],
        "answer": ["A"], "score": 10, "category_id": qcat["id"]
    }, headers=ah).json()["data"]
    return ah, uh, qcat, ecat, q


def _make_exam(client, ah, ecat_id, q_ids, status="draft", title="治理卷"):
    r = client.post("/api/v1/admin/exams", json={
        "title": title, "category_id": ecat_id, "status": status, "question_ids": q_ids
    }, headers=ah)
    assert r.status_code == 201
    return r.json()["data"]


def test_delete_category_in_use_blocked(client):
    ah, uh, qcat, ecat, q = _setup(client)
    _make_exam(client, ah, ecat["id"], [q["id"]])
    r1 = client.delete(f"/api/v1/admin/categories/{qcat['id']}", headers=ah)
    assert r1.status_code == 400
    r2 = client.delete(f"/api/v1/admin/categories/{ecat['id']}", headers=ah)
    assert r2.status_code == 400


def test_delete_question_blocked_by_published(client):
    ah, uh, qcat, ecat, q = _setup(client)
    _make_exam(client, ah, ecat["id"], [q["id"]], status="published", title="上架卷")
    r = client.delete(f"/api/v1/admin/questions/{q['id']}", headers=ah)
    assert r.status_code == 400


def test_delete_question_draft_only_unlinks_and_recalcs(client):
    ah, uh, qcat, ecat, q = _setup(client)
    q2 = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "第二题?", "options": [{"key": "A", "text": "a"}],
        "answer": ["A"], "score": 20, "category_id": qcat["id"]
    }, headers=ah).json()["data"]
    ex = _make_exam(client, ah, ecat["id"], [q["id"], q2["id"]], title="草稿卷")
    assert ex["total_score"] == 30
    r = client.delete(f"/api/v1/admin/questions/{q['id']}", headers=ah)
    assert r.status_code == 200
    det = client.get(f"/api/v1/admin/exams/{ex['id']}", headers=ah).json()["data"]
    assert len(det["questions"]) == 1
    assert det["total_score"] == 20


def test_delete_exam_guards(client):
    ah, uh, qcat, ecat, q = _setup(client)
    # 有作答的上架卷不可删
    ex1 = _make_exam(client, ah, ecat["id"], [q["id"]], status="published", title="有人考卷")
    st = client.post("/api/v1/records/start", json={"exam_id": ex1["id"]}, headers=uh)
    rec = st.json()["data"]["record_id"]
    client.post("/api/v1/records/submit", json={"record_id": rec, "user_answers": {str(q["id"]): ["A"]}, "time_spent": 10}, headers=uh)
    assert client.delete(f"/api/v1/admin/exams/{ex1['id']}", headers=ah).status_code == 400
    # 下架后仍不可删（归档终态）
    client.put(f"/api/v1/admin/exams/{ex1['id']}/status?status=archived", headers=ah)
    assert client.delete(f"/api/v1/admin/exams/{ex1['id']}", headers=ah).status_code == 400
    # 零作答上架卷：先下架也不给删？可删？——口径：仅draft零记录可删
    ex2 = _make_exam(client, ah, ecat["id"], [q["id"]], status="published", title="无人上架卷")
    assert client.delete(f"/api/v1/admin/exams/{ex2['id']}", headers=ah).status_code == 400
    # draft零记录可删
    ex3 = _make_exam(client, ah, ecat["id"], [q["id"]], title="草稿可删卷")
    assert client.delete(f"/api/v1/admin/exams/{ex3['id']}", headers=ah).status_code == 200


def test_submit_empty_answers_rejected(client):
    ah, uh, qcat, ecat, q = _setup(client)
    ex = _make_exam(client, ah, ecat["id"], [q["id"]], status="published", title="空卷拦截卷")
    rec = client.post("/api/v1/records/start", json={"exam_id": ex["id"]}, headers=uh).json()["data"]["record_id"]
    r = client.post("/api/v1/records/submit", json={"record_id": rec, "user_answers": {}, "time_spent": 3}, headers=uh)
    assert r.status_code == 400


def test_create_question_defaults_first_category(client):
    ah, uh, qcat, ecat, q = _setup(client)
    r = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "无分类题?", "options": [{"key": "A", "text": "a"}],
        "answer": ["A"], "score": 10
    }, headers=ah)
    assert r.status_code == 201
    assert r.json()["data"]["category_id"] == qcat["id"]


def _xlsx_bytes(header, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


HDR = ["题型", "题干", "选项A", "选项B", "选项C", "选项D", "答案", "解析", "难度", "分数", "分类"]


def test_import_row_category_autocreate_and_fallback(client):
    ah, uh, qcat, ecat, q = _setup(client)
    buf = _xlsx_bytes(HDR, [
        ["single", "新分类题?", "a", "b", "", "", "A", "", "中等", 10, "导入新分类"],
        ["single", "空分类题?", "a", "b", "", "", "A", "", "中等", 10, ""],
    ])
    r = client.post("/api/v1/admin/questions/import", files={"file": ("t.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, headers=ah)
    assert r.status_code == 200
    assert r.json()["data"]["imported_count"] == 2
    cats = client.get("/api/v1/admin/categories?target_type=question", headers=ah).json()["data"]
    names = [c["name"] for c in cats]
    assert "导入新分类" in names


def test_import_legacy_no_category_col_falls_back(client):
    ah, uh, qcat, ecat, q = _setup(client)
    buf = _xlsx_bytes(HDR[:-1], [["single", "老模板题?", "a", "b", "", "", "A", "", "中等", 10]])
    r = client.post("/api/v1/admin/questions/import", files={"file": ("t.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, headers=ah)
    assert r.status_code == 200
    assert r.json()["data"]["imported_count"] == 1
    lst = client.get("/api/v1/admin/questions?keyword=老模板题", headers=ah).json()["data"]["items"]
    assert lst and lst[0]["category_id"] == qcat["id"]


def test_import_skips_unsupported_types(client):
    ah, uh, qcat, ecat, q = _setup(client)
    buf = _xlsx_bytes(HDR, [
        ["short", "简答题?", "", "", "", "", "略", "", "中等", 10, ""],
        ["single", "正常题?", "a", "b", "", "", "A", "", "中等", 10, ""],
    ])
    r = client.post("/api/v1/admin/questions/import", files={"file": ("t.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}, headers=ah)
    assert r.status_code == 200
    assert r.json()["data"]["imported_count"] == 1
    assert r.json()["data"].get("skipped_count", 0) == 1


def test_publish_snapshots_category_name(client):
    ah, uh, qcat, ecat, q = _setup(client)
    ex = _make_exam(client, ah, ecat["id"], [q["id"]], status="published", title="快照卷")
    assert ex.get("category_name") == "卷分类A"
    # 分类删除被拦（有卷在用），改名后快照不变
    client.put(f"/api/v1/admin/categories/{ecat['id']}", json={"name": "改名后"}, headers=ah)
    det = client.get(f"/api/v1/admin/exams/{ex['id']}", headers=ah).json()["data"]
    assert det.get("category_name") == "卷分类A"
