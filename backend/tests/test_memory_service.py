"""
[变更日志]
修改时间：2026-09-09
AI模型：OpenCode / Gemini 底层
修改内容：[新增 test_memory_service.py: 验证 Mem0 本地与云端双轨加载逻辑]
"""
import pytest
from app.services import memory_service


def test_memory_service_local_mode(monkeypatch):
    """未配置 MEM0_API_KEY 时走本地模式 (或者优雅降级)"""
    monkeypatch.delenv("MEM0_API_KEY", raising=False)
    monkeypatch.setattr(memory_service, "_client", None)
    
    # remember 与 recall 绝不抛出任何未捕获异常
    memory_service.remember(1, "我偏好出选择题", "好的收到")
    res = memory_service.recall(1, "出题偏好")
    assert isinstance(res, str)


def test_memory_service_cloud_mode(monkeypatch):
    """配置 MEM0_API_KEY 时尝试走 MemoryClient"""
    monkeypatch.setenv("MEM0_API_KEY", "m0-fake-test-key")
    monkeypatch.setattr(memory_service, "_client", None)

    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.added = []
        def add(self, messages, user_id):
            self.added.append((messages, user_id))
        def search(self, query, user_id, limit=3):
            return [{"memory": "偏好单选题"}]

    import mem0
    monkeypatch.setattr(mem0, "MemoryClient", DummyClient)

    client = memory_service.get_client()
    assert client is not None
    assert client.api_key == "m0-fake-test-key"
    assert memory_service._client_mode == "cloud"

    memory_service.remember(1, "喜欢客观题", "收到")
    assert len(client.added) == 1
    recalled = memory_service.recall(1, "题型")
    assert "偏好单选题" in recalled
