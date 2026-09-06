"""v1.4 修复回归: AI options 字符串规范化 / 多选连写拆分 / AI出题高级选项联动校验"""
import json

from app.services import ai_service


def _bootstrap(client):
    client.post("/api/v1/admin/auth/init", json={"username": "root_fix", "password": "rootpassword"})
    token = client.post("/api/v1/admin/auth/login", json={"username": "root_fix", "password": "rootpassword"}).json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_batch_accepts_string_options(client):
    """AI 生成的字符串 options ["A. 甲","乙"] 入库时规范化为 {key,text}, 列表接口不 500"""
    ah = _bootstrap(client)
    payload = [{
        "type": "single", "title": "字符串选项题?", "source": "ai", "score": 10,
        "options": ["A. 应用行为分析", "仅使用药物治疗", "C、完全隔离", "D）不干预"],
        "answer": ["A"],
    }]
    r = client.post("/api/v1/admin/questions/batch", json=payload, headers=ah)
    assert r.status_code == 201, r.text
    qid = r.json()["data"]["question_ids"][0]

    lst = client.get("/api/v1/admin/questions", headers=ah).json()["data"]
    item = [q for q in lst["items"] if q["id"] == qid][0]
    assert item["options"] == [
        {"key": "A", "text": "应用行为分析"},
        {"key": "B", "text": "仅使用药物治疗"},
        {"key": "C", "text": "完全隔离"},
        {"key": "D", "text": "不干预"},
    ]


def test_create_multiple_written_together_expanded(client):
    """多选连写 ["ABC"] 自动拆分为 ["A","B","C"]; 不足两个仍 400"""
    ah = _bootstrap(client)
    r = client.post("/api/v1/admin/questions", json={
        "type": "multiple", "title": "连写多选?", "options": [
            {"key": "A", "text": "a"}, {"key": "B", "text": "b"}, {"key": "C", "text": "c"}],
        "answer": ["ABC"], "score": 10,
    }, headers=ah)
    assert r.status_code == 201, r.text
    assert sorted(r.json()["data"]["answer"]) == ["A", "B", "C"]

    r2 = client.post("/api/v1/admin/questions", json={
        "type": "multiple", "title": "单字母多选?", "options": [{"key": "A", "text": "a"}],
        "answer": ["A"], "score": 10,
    }, headers=ah)
    assert r2.status_code == 400 and "至少两个" in r2.json()["detail"]


def test_single_rejects_multiple_answers(client):
    ah = _bootstrap(client)
    r = client.post("/api/v1/admin/questions", json={
        "type": "single", "title": "单选多答案?", "options": [
            {"key": "A", "text": "a"}, {"key": "B", "text": "b"}],
        "answer": ["A", "B"], "score": 10,
    }, headers=ah)
    assert r.status_code == 400


def test_ai_gen_advanced_options_all_or_nothing(client, monkeypatch):
    """AI出题高级选项: 部分填写 400; 全空用默认; 全填以高级选项为准 (material 冲突文字被忽略)"""
    ah = _bootstrap(client)
    me = client.get("/api/v1/admin/auth/me", headers=ah).json()["data"]
    client.post(f"/api/v1/admin/members/{me['id']}/refill", headers=ah, json={"amount": 20})

    captured = {}

    def fake_chat(prompt, system="", json_mode=False, temperature=0.3, timeout=90.0):
        captured["prompt"] = prompt
        qs = [{"type": "single", "title": "AI题?", "options": [{"key": "A", "text": "x"}, {"key": "B", "text": "y"}],
               "answer": ["A"], "explanation": "", "difficulty": "easy", "score": 10}] * 6
        return json.dumps({"questions": qs}, ensure_ascii=False)

    monkeypatch.setattr(ai_service, "chat_completion", fake_chat)
    monkeypatch.setattr(ai_service, "ai_available", lambda: True)

    # 部分填写 → 400
    r_part = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "电脑知识生成3道题内容", "count": 5})
    assert r_part.status_code == 400 and "完整填写" in r_part.json()["detail"]

    # 全空 → 默认 5 题
    r_empty = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "随便出点电脑知识题目"})
    assert r_empty.status_code == 200
    assert len(r_empty.json()["data"]["questions"]) == 5

    # 全填 + 材料写"3道题" → 以高级选项 5 题为准, prompt 含硬性要求
    r_full = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "电脑知识生成3道题", "types": ["single"], "count": 5, "difficulty": "easy"})
    assert r_full.status_code == 200
    assert len(r_full.json()["data"]["questions"]) == 5
    assert "恰好 5 道" in captured["prompt"] and "以此为准" in captured["prompt"]


def test_list_questions_ok_after_ai_questions(client):
    """AI 题目入库后题目列表必须 200 (回归: options 字符串曾拖垮全表)"""
    ah = _bootstrap(client)
    client.post("/api/v1/admin/questions/batch", json=[{
        "type": "judge", "title": "判断题?", "source": "ai", "score": 10,
        "options": ["正确", "错误"], "answer": ["A"],
    }], headers=ah)
    r = client.get("/api/v1/admin/questions", headers=ah)
    assert r.status_code == 200
