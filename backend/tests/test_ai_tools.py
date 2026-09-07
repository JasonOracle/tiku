# -*- coding: utf-8 -*-
"""AI 工具链路回归: execute_tool/create_question_draft 真实形状 payload (防 500 回归)."""
from app.models.question import Question


def _bootstrap(client):
    client.post("/api/v1/admin/auth/init", json={"username": "root", "password": "rootpassword"})
    super_token = client.post("/api/v1/admin/auth/login", json={"username": "root", "password": "rootpassword"}).json()["data"]["token"]
    ah = {"Authorization": f"Bearer {super_token}"}
    client.post("/api/v1/admin/members", json={"username": "creator_ai", "password": "pass1234", "role": "creator"}, headers=ah)
    c_token = client.post("/api/v1/admin/auth/login", json={"username": "creator_ai", "password": "pass1234"}).json()["data"]["token"]
    ch = {"Authorization": f"Bearer {c_token}"}
    return ah, ch


def _execute(client, headers, args):
    return client.post("/api/v1/admin/ai/chat/execute_tool", json={
        "tool_name": "create_question_draft", "tool_call_id": "call_test", "arguments": args,
    }, headers=headers)


def test_execute_model_shape_payload(client, db_session):
    """大模型真实形状: options [{text, correct}] + 文本答案 -> 200, 归一化为 key"""
    ah, _ = _bootstrap(client)
    r = _execute(client, ah, {
        "type": "single",
        "title": "灭火器的使用方法中，下列哪项是错误的？",
        "options": [{"text": "拔掉保险销", "correct": False}, {"text": "站在下风向喷射", "correct": True}],
        "answer": ["站在下风向喷射"],
        "difficulty": "easy", "score": 5, "explanation": "应站上风向",
    })
    assert r.status_code == 200, r.text
    qid = r.json()["data"]["question_id"]
    q = db_session.query(Question).filter(Question.id == qid).one()
    assert q.options == [{"key": "A", "text": "拔掉保险销"}, {"key": "B", "text": "站在下风向喷射"}]
    assert q.answer == ["B"]
    assert q.source == "ai"


def test_execute_standard_shape_and_creator_role(client, db_session):
    """标准形状 + creator 出题人有权执行"""
    _, ch = _bootstrap(client)
    r = _execute(client, ch, {
        "type": "multiple", "title": "多选?",
        "options": [{"key": "A", "text": "a"}, {"key": "B", "text": "b"}],
        "answer": ["A", "B"], "difficulty": "medium", "score": 10,
    })
    assert r.status_code == 200, r.text
    qid = r.json()["data"]["question_id"]
    q = db_session.query(Question).filter(Question.id == qid).one()
    assert q.answer == ["A", "B"]


def test_execute_validation_400(client):
    """缺题干/非法题型/填空空数 mismatch -> 400 中文, 不 500"""
    ah, _ = _bootstrap(client)
    assert _execute(client, ah, {"type": "single", "title": "", "answer": ["A"]}).status_code == 400
    assert _execute(client, ah, {"type": "nope", "title": "t", "answer": ["A"]}).status_code == 400
    assert _execute(client, ah, {"type": "fill", "title": "只有一空___", "answer": [["a"], ["b"]]}).status_code == 400


def _execute_exam(client, headers, args):
    return client.post("/api/v1/admin/ai/chat/execute_tool", json={
        "tool_name": "create_exam_draft", "tool_call_id": "call_exam", "arguments": args,
    }, headers=headers)


def test_execute_exam_draft_creates_exam_with_questions(client, db_session):
    """组卷工具: 缺省保护 + 题目入库 + 试卷关联 + 总分重算"""
    from app.models.exam import Exam, ExamQuestion
    ah, _ = _bootstrap(client)
    r = _execute_exam(client, ah, {
        "title": "消防安全知识测试卷",
        "questions": [
            {"type": "single", "title": "灭火器用于?", "options": [{"text": "灭火", "correct": True}, {"text": "装饰", "correct": False}], "answer": ["灭火"], "score": 20},
            {"type": "judge", "title": "火警电话119?", "answer": ["A"], "score": 10},
        ],
    })
    assert r.status_code == 200, r.text
    exam_id = r.json()["data"]["exam_id"]
    exam = db_session.query(Exam).filter(Exam.id == exam_id).one()
    assert exam.status == "draft" and exam.grading_mode == "manual"
    assert (exam.end_time - exam.start_time).days >= 6
    links = db_session.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.sort_order).all()
    assert len(links) == 2 and exam.total_score == 30 and exam.pass_score == 18
    q1 = db_session.query(Question).filter(Question.id == links[0].question_id).one()
    assert q1.options == [{"key": "A", "text": "灭火"}, {"key": "B", "text": "装饰"}] and q1.answer == ["A"]


def test_execute_exam_draft_validation_400(client):
    """空标题/空题目列表 -> 400"""
    ah, _ = _bootstrap(client)
    assert _execute_exam(client, ah, {"title": "", "questions": []}).status_code == 400
    assert _execute_exam(client, ah, {"title": "t", "questions": []}).status_code == 400


def test_personal_stats_counts_own_questions(client):
    """个人数据感知: 出题人查到自己创建的题数, 全局数含他人"""
    ah, ch = _bootstrap(client)
    for i in range(2):
        r = client.post("/api/v1/admin/questions", json={
            "type": "single", "title": f"我的题{i}?", "options": [{"key": "A", "text": "a"}], "answer": ["A"]}, headers=ch)
        assert r.status_code == 201, r.text
    r = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "超管的题?", "options": [{"key": "A", "text": "a"}], "answer": ["A"]}, headers=ah)
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/admin/ai/chat/execute_tool", json={
        "tool_name": "get_database_stats", "tool_call_id": "call_stats", "arguments": {}}, headers=ch)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["current_user"]["created_questions_count"] == 2
    assert data["current_user"]["created_exams_count"] == 0
    assert data["global_stats"]["total_questions"] == 3


def test_list_all_exams_super_only_with_creators(client, db_session):
    """全站试卷归属: 超管可见出题人, 出题人越权 403"""
    from app.models.exam import Exam
    ah, ch = _bootstrap(client)
    r = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "归属题?", "options": [{"key": "A", "text": "a"}], "answer": ["A"]}, headers=ch)
    qid = r.json()["data"]["id"]
    r = client.post("/api/v1/admin/exams", json={
        "title": "归属卷", "question_ids": [qid]}, headers=ch)
    assert r.status_code == 201, r.text
    r = client.post("/api/v1/admin/ai/chat/execute_tool", json={
        "tool_name": "list_all_exams", "tool_call_id": "call_all", "arguments": {"limit": 20}}, headers=ah)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["total"] == 1
    assert data["exams"][0]["creator"] == "creator_ai"
    assert data["exams"][0]["question_count"] == 1
    assert data["exams"][0]["category"] == "未分类"
    assert data["by_category"] == {"未分类": 1}
    r = client.post("/api/v1/admin/ai/chat/execute_tool", json={
        "tool_name": "list_all_exams", "tool_call_id": "call_all2", "arguments": {}}, headers=ch)
    assert r.status_code == 403
