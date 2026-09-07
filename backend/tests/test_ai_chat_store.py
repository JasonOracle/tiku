# -*- coding: utf-8 -*-
"""企业级会话流水回归: 会话 CRUD/归属隔离/游标分页/execute_tool 卡片状态持久."""
from app.models.ai_chat import AiChatSession, AiChatMessage


def _bootstrap(client):
    client.post("/api/v1/admin/auth/init", json={"username": "root", "password": "rootpassword"})
    super_token = client.post("/api/v1/admin/auth/login", json={"username": "root", "password": "rootpassword"}).json()["data"]["token"]
    ah = {"Authorization": f"Bearer {super_token}"}
    client.post("/api/v1/admin/members", json={"username": "creator_c", "password": "pass1234", "role": "creator"}, headers=ah)
    c_token = client.post("/api/v1/admin/auth/login", json={"username": "creator_c", "password": "pass1234"}).json()["data"]["token"]
    return ah, {"Authorization": f"Bearer {c_token}"}


def test_session_crud_and_ownership(client):
    ah, ch = _bootstrap(client)
    s = client.post("/api/v1/admin/ai/sessions", headers=ch).json()["data"]
    assert s["title"] == "新对话"
    lst = client.get("/api/v1/admin/ai/sessions", headers=ch).json()["data"]["items"]
    assert [x["id"] for x in lst] == [s["id"]]
    # 超管看不到出题人的会话 (严格按本人隔离)
    assert client.get("/api/v1/admin/ai/sessions", headers=ah).json()["data"]["items"] == []
    # 重命名 + 非法重命名
    r = client.put(f"/api/v1/admin/ai/sessions/{s['id']}", json={"title": "消防"}, headers=ch)
    assert r.status_code == 200 and r.json()["data"]["title"] == "消防"
    assert client.put(f"/api/v1/admin/ai/sessions/{s['id']}", json={"title": "x"}, headers=ah).status_code == 404
    # 归属外删除 -> 404, 本人删除 -> 200
    assert client.delete(f"/api/v1/admin/ai/sessions/{s['id']}", headers=ah).status_code == 404
    assert client.delete(f"/api/v1/admin/ai/sessions/{s['id']}", headers=ch).status_code == 200


def test_cursor_pagination_asc_and_has_more(client, db_session):
    _, ch = _bootstrap(client)
    s = client.post("/api/v1/admin/ai/sessions", headers=ch).json()["data"]
    for i in range(25):
        db_session.add(AiChatMessage(session_id=s["id"], role="user" if i % 2 == 0 else "assistant", content=f"m{i}"))
    db_session.commit()
    page1 = client.get(f"/api/v1/admin/ai/sessions/{s['id']}/messages", params={"limit": 20}, headers=ch).json()["data"]
    assert [m["content"] for m in page1["items"]] == [f"m{i}" for i in range(5, 25)]
    assert page1["has_more"] is True
    page2 = client.get(f"/api/v1/admin/ai/sessions/{s['id']}/messages",
                       params={"before_id": page1["next_cursor"], "limit": 20}, headers=ch).json()["data"]
    assert [m["content"] for m in page2["items"]] == [f"m{i}" for i in range(5)]
    assert page2["has_more"] is False


def test_execute_tool_persists_card_status(client, db_session):
    ah, _ = _bootstrap(client)
    s = client.post("/api/v1/admin/ai/sessions", headers=ah).json()["data"]
    card_msg = AiChatMessage(
        session_id=s["id"], role="assistant", content="即将执行",
        action_card_data={"kind": "tool", "tool_name": "create_question_draft", "status": "pending",
                          "arguments": {"type": "single", "title": "t?", "answer": ["A"]}},
    )
    db_session.add(card_msg)
    db_session.commit()
    r = client.post("/api/v1/admin/ai/chat/execute_tool", json={
        "tool_name": "create_question_draft", "tool_call_id": "call_x", "message_id": card_msg.id,
        "arguments": {"type": "single", "title": "t?", "answer": ["A"]}}, headers=ah)
    assert r.status_code == 200, r.text
    db_session.refresh(card_msg)
    assert card_msg.action_card_data["status"] == "executed"
    # 漫游重拉: 状态不回退
    items = client.get(f"/api/v1/admin/ai/sessions/{s['id']}/messages", headers=ah).json()["data"]["items"]
    assert items[-1]["action_card_data"]["status"] == "executed"
