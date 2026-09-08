"""RAG 私有库回归：上传切片/进度/检索/归属隔离/删除/溯源透传"""


def _admin(client, name="admin_rag"):
    client.post("/api/v1/admin/auth/init", json={"username": name, "password": "adminpassword"})
    t = client.post("/api/v1/admin/auth/login", json={"username": name, "password": "adminpassword"}).json()["data"]["token"]
    return {"Authorization": f"Bearer {t}"}


def _member(client, ah, username="teacher_rag"):
    client.post("/api/v1/admin/members", json={"username": username, "password": "pw123456"}, headers=ah)
    t = client.post("/api/v1/admin/auth/login", json={"username": username, "password": "pw123456"}).json()["data"]["token"]
    return {"Authorization": f"Bearer {t}"}


def _upload(client, h, text="消防安全第一课：灭火器分干粉、二氧化碳两类。火警电话119。", name="doc.txt"):
    return client.post("/api/v1/admin/rag/documents", files={"file": (name, text.encode("utf-8"), "text/plain")}, headers=h)


def test_upload_split_search_delete(client, monkeypatch):
    from app.api.admin import admin_rag
    from app.services import embedding_service
    monkeypatch.setattr(embedding_service, "embed_texts", lambda texts: [[float(len(t)), 1.0] for t in texts])
    ah = _admin(client)
    r = _upload(client, ah)
    assert r.status_code == 201, r.text
    doc = r.json()["data"]
    assert doc["total_chunks"] >= 1 and doc["status"] == "done"
    assert doc["done_chunks"] == doc["total_chunks"]

    st = client.get(f"/api/v1/admin/rag/documents/{doc['id']}", headers=ah).json()["data"]
    assert st["status"] == "done"

    s = client.post("/api/v1/admin/rag/search", json={"query": "灭火器有几类", "limit": 3}, headers=ah).json()["data"]
    assert len(s["items"]) >= 1 and "灭火器" in s["items"][0]["text"]

    c = client.get("/api/v1/admin/rag/chunks", params={"ids": str(s["items"][0]["id"])}, headers=ah).json()["data"]
    assert c["items"][0]["filename"] == "doc.txt"

    assert client.delete(f"/api/v1/admin/rag/documents/{doc['id']}", headers=ah).status_code == 200
    assert client.get("/api/v1/admin/rag/documents", headers=ah).json()["data"]["items"] == []


def test_rag_ownership_isolation(client, monkeypatch):
    from app.services import embedding_service
    monkeypatch.setattr(embedding_service, "embed_texts", lambda texts: [[1.0] for _ in texts])
    ah = _admin(client)
    th = _member(client, ah)
    doc = _upload(client, ah).json()["data"]
    # 出题人看不到超管文档
    assert client.get(f"/api/v1/admin/rag/documents/{doc['id']}", headers=th).status_code == 403
    assert client.post("/api/v1/admin/rag/search", json={"query": "消防", "limit": 3}, headers=th).json()["data"]["items"] == []
    assert client.delete(f"/api/v1/admin/rag/documents/{doc['id']}", headers=th).status_code == 403


def test_generate_with_doc_ids_attaches_source_ref(client, monkeypatch):
    from app.services import ai_service, embedding_service
    from app.models.rag import DocLibrary
    monkeypatch.setattr(embedding_service, "embed_texts", lambda texts: [[1.0] for _ in texts])

    def fake_chat(prompt, system="", json_mode=False, temperature=0.3, timeout=90.0):
        assert "私有文库资料" in prompt
        import json as _json
        return _json.dumps({"questions": [{
            "type": "single", "title": "灭火器有几类？",
            "options": [{"key": "A", "text": "两类"}], "answer": ["A"],
            "explanation": "", "difficulty": "easy", "score": 10}]}, ensure_ascii=False), None
    monkeypatch.setattr(ai_service, "chat_completion", fake_chat)
    ah = _admin(client)
    doc = _upload(client, ah).json()["data"]
    r = client.post("/api/v1/admin/ai/questions/generate", json={
        "material": "出1道消防题", "types": ["single"], "count": 1, "difficulty": "easy",
        "doc_ids": [doc["id"]]}, headers=ah)
    assert r.status_code == 200, r.text
    items = r.json()["data"]["questions"]
    assert len(items) == 1 and items[0]["source_ref"]
    assert items[0]["source_ref"][0]["doc_id"] == doc["id"]
