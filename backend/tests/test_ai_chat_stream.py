# -*- coding: utf-8 -*-
"""SSE 流回归: 纯文本流 / 工具调用流 / 异常中断兜底 (mock 模型层, 真走网关/落库)."""
import json
from app.services import ai_service
from app.models.ai_chat import AiChatMessage


def _bootstrap(client):
    client.post("/api/v1/admin/auth/init", json={"username": "root", "password": "rootpassword"})
    tok = client.post("/api/v1/admin/auth/login", json={"username": "root", "password": "rootpassword"}).json()["data"]["token"]
    return {"Authorization": f"Bearer {tok}"}


def _new_session(client, h):
    return client.post("/api/v1/admin/ai/sessions", headers=h).json()["data"]["id"]


def _sse_events(text):
    evs = []
    for frame in text.split("\n\n"):
        line = frame.strip()
        if line.startswith("data:"):
            evs.append(json.loads(line[5:].strip()))
    return evs


def test_stream_plain_text_persists(client, db_session, monkeypatch):
    """纯文本流: delta 逐字 + done 带双 ID + 用户/助手双落库"""
    def fake_stream(*a, **k):
        yield {"type": "delta", "text": "你好"}
        yield {"type": "delta", "text": "呀"}
        yield {"type": "done"}
    monkeypatch.setattr(ai_service, "chat_completion_stream", fake_stream)
    h = _bootstrap(client)
    sid = _new_session(client, h)
    r = client.post("/api/v1/admin/ai/chat/stream", json={
        "message": "hi", "display_text": "hi", "history": [], "session_id": sid}, headers=h)
    assert r.status_code == 200, r.text
    evs = _sse_events(r.text)
    assert [e["text"] for e in evs if e["type"] == "delta"] == ["你好", "呀"]
    done = [e for e in evs if e["type"] == "done"][0]
    assert done["user_message_id"] and done["assistant_message_id"]
    rows = db_session.query(AiChatMessage).filter(AiChatMessage.session_id == sid).order_by(AiChatMessage.id).all()
    assert [(m.role, m.content) for m in rows] == [("user", "hi"), ("assistant", "你好呀")]


def test_stream_tool_call_low_risk(client, db_session, monkeypatch):
    """工具流: 首轮 tool_calls -> 低风险自动执行 -> 次轮文本 -> done 落库"""
    calls = {"n": 0}

    def fake_stream(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            yield {"type": "tool_calls", "tool_calls": [
                {"id": "call_1", "function": {"name": "get_database_stats", "arguments": "{}"}}]}
            yield {"type": "done"}
        else:
            yield {"type": "delta", "text": "共0题"}
            yield {"type": "done"}
    monkeypatch.setattr(ai_service, "chat_completion_stream", fake_stream)
    h = _bootstrap(client)
    sid = _new_session(client, h)
    r = client.post("/api/v1/admin/ai/chat/stream", json={
        "message": "统计", "display_text": "统计", "history": [], "session_id": sid}, headers=h)
    assert r.status_code == 200, r.text
    evs = _sse_events(r.text)
    assert any(e["type"] == "delta" and e["text"] == "共0题" for e in evs)
    assert any(e["type"] == "done" and e["assistant_message_id"] for e in evs)
    rows = db_session.query(AiChatMessage).filter(AiChatMessage.session_id == sid).all()
    assert len(rows) == 2 and rows[1].content == "共0题"


def test_stream_abort_persists_partial_and_hides_internals(client, db_session, monkeypatch):
    """中断兜底: 次轮抛异常 -> 通用错误(不泄内部名) + 半截文本落库"""
    def fake_stream(*a, **k):
        yield {"type": "delta", "text": "半截"}
        raise RuntimeError("boom_acc_main_secret")
    monkeypatch.setattr(ai_service, "chat_completion_stream", fake_stream)
    h = _bootstrap(client)
    sid = _new_session(client, h)
    r = client.post("/api/v1/admin/ai/chat/stream", json={
        "message": "hi", "display_text": "hi", "history": [], "session_id": sid}, headers=h)
    assert r.status_code == 200, r.text
    evs = _sse_events(r.text)
    errs = [e for e in evs if e["type"] == "error"]
    assert errs and "boom_acc_main_secret" not in errs[0]["message"]
    rows = db_session.query(AiChatMessage).filter(AiChatMessage.session_id == sid).order_by(AiChatMessage.id).all()
    assert len(rows) == 2 and rows[1].content == "半截"


def test_stream_empty_second_turn_falls_back_to_tool_summary(client, db_session, monkeypatch):
    """空包兜底: 归纳轮零 delta -> 按工具结果拼装非空回复并落库"""
    calls = {"n": 0}

    def fake_stream(*a, **k):
        calls["n"] += 1
        if calls["n"] == 1:
            yield {"type": "tool_calls", "tool_calls": [
                {"id": "call_1", "function": {"name": "get_my_exams", "arguments": "{}"}}]}
            yield {"type": "done"}
        else:
            yield {"type": "done"}
    monkeypatch.setattr(ai_service, "chat_completion_stream", fake_stream)
    h = _bootstrap(client)
    sid = _new_session(client, h)
    r = client.post("/api/v1/admin/ai/chat/stream", json={
        "message": "我有几套卷", "display_text": "我有几套卷", "history": [], "session_id": sid}, headers=h)
    assert r.status_code == 200, r.text
    evs = _sse_events(r.text)
    deltas = [e["text"] for e in evs if e["type"] == "delta"]
    assert deltas and all(t.strip() for t in deltas)
    rows = db_session.query(AiChatMessage).filter(AiChatMessage.session_id == sid).order_by(AiChatMessage.id).all()
    assert len(rows) == 2 and rows[1].content.strip() and "0 套" in rows[1].content


def test_stream_plain_empty_falls_back_to_retry_hint(client, db_session, monkeypatch):
    """空包兜底: 纯文本轮零 delta 无卡片 -> 重试提示而非空库"""
    def fake_stream(*a, **k):
        yield {"type": "done"}
    monkeypatch.setattr(ai_service, "chat_completion_stream", fake_stream)
    h = _bootstrap(client)
    sid = _new_session(client, h)
    r = client.post("/api/v1/admin/ai/chat/stream", json={
        "message": "hi", "display_text": "hi", "history": [], "session_id": sid}, headers=h)
    assert r.status_code == 200, r.text
    rows = db_session.query(AiChatMessage).filter(AiChatMessage.session_id == sid).order_by(AiChatMessage.id).all()
    assert len(rows) == 2 and rows[1].content.strip()
