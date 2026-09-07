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


def _mk_q(i=0):
    return {"type": "single", "title": f"AI题{i}?", "options": [{"key": "A", "text": "x"}, {"key": "B", "text": "y"}],
            "answer": ["A"], "explanation": "", "difficulty": "easy", "score": 10}


def _fake_n(captured, n):
    """构造返回 n 道题的 chat_completion 替身, 并捕获 prompt 供断言"""
    def fake_chat(prompt, system="", json_mode=False, temperature=0.3, timeout=90.0):
        captured["prompt"] = prompt
        return json.dumps({"questions": [_mk_q(i) for i in range(n)]}, ensure_ascii=False), None
    return fake_chat


def test_ai_gen_advanced_options_all_or_nothing(client, monkeypatch):
    """AI出题高级选项: 部分填写 400; 全空 AI 自主(不硬截默认5); 全填以高级选项为准 (material 冲突文字被忽略)"""
    ah = _bootstrap(client)
    me = client.get("/api/v1/admin/auth/me", headers=ah).json()["data"]
    client.post(f"/api/v1/admin/members/{me['id']}/refill", headers=ah, json={"amount": 20})

    captured = {}
    monkeypatch.setattr(ai_service, "ai_available", lambda: True)

    # 部分填写 → 400
    monkeypatch.setattr(ai_service, "chat_completion", _fake_n(captured, 6))
    r_part = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "电脑知识生成3道题内容", "count": 5})
    assert r_part.status_code == 400 and "完整填写" in r_part.json()["detail"]

    # 全空 → AI 自主, 返回几道保留几道 (v1.5: 不再硬截回默认 5)
    r_empty = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "随便出点电脑知识题目"})
    assert r_empty.status_code == 200
    assert len(r_empty.json()["data"]["questions"]) == 6

    # 全填 + 材料写"3道题" → 以高级选项 5 题为准, prompt 含硬性要求
    r_full = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "电脑知识生成3道题", "types": ["single"], "count": 5, "difficulty": "easy"})
    assert r_full.status_code == 200
    assert len(r_full.json()["data"]["questions"]) == 5
    assert "恰好 5 道" in captured["prompt"] and "以此为准" in captured["prompt"]


def test_ai_gen_material_count_priority_and_cap_v15(client, monkeypatch):
    """v1.5: 材料指定数量优先于默认5(说10道出10道); AI 超量按上限10截断并提示; count>10 直接 422"""
    ah = _bootstrap(client)
    me = client.get("/api/v1/admin/auth/me", headers=ah).json()["data"]
    client.post(f"/api/v1/admin/members/{me['id']}/refill", headers=ah, json={"amount": 20})

    captured = {}
    monkeypatch.setattr(ai_service, "ai_available", lambda: True)

    # 材料写"生成10道" + 高级选项全空 → 10 道全保留 (修复: 之前被默认 5 硬截成 5 道)
    monkeypatch.setattr(ai_service, "chat_completion", _fake_n(captured, 10))
    r10 = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "生成10道关于键盘历史的题目，随机题型"})
    assert r10.status_code == 200
    assert len(r10.json()["data"]["questions"]) == 10
    assert "严格按材料指定的数量" in captured["prompt"] and "不得超过 10 道" in captured["prompt"]

    # AI 返回 12 道 (材料要求超出上限) → 截断到 10 且 message 带截断说明
    monkeypatch.setattr(ai_service, "chat_completion", _fake_n(captured, 12))
    r_cap = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "生成12道关于键盘历史的题目，随机题型"})
    assert r_cap.status_code == 200
    assert len(r_cap.json()["data"]["questions"]) == 10
    assert "已按上限截断" in r_cap.json()["message"]

    # 高级选项数量 > 上限 → pydantic 校验 422
    r_over = client.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "电脑知识生成很多题", "types": ["single"], "count": 11, "difficulty": "easy"})
    assert r_over.status_code == 422


def test_list_questions_ok_after_ai_questions(client):
    """AI 题目入库后题目列表必须 200 (回归: options 字符串曾拖垮全表)"""
    ah = _bootstrap(client)
    client.post("/api/v1/admin/questions/batch", json=[{
        "type": "judge", "title": "判断题?", "source": "ai", "score": 10,
        "options": ["正确", "错误"], "answer": ["A"],
    }], headers=ah)
    r = client.get("/api/v1/admin/questions", headers=ah)
    assert r.status_code == 200
