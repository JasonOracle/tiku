"""Mem0 记忆服务回归：关闭态零依赖可用、失败静默、用户隔离键"""
import os
from app.services import memory_service


def test_disabled_returns_safe_defaults(monkeypatch):
    monkeypatch.setenv("MEM0_ENABLED", "0")
    memory_service._client = None
    assert memory_service.get_client() is None
    assert memory_service.recall(1, "教什么") == ""
    memory_service.remember(1, "u", "a")  # 不抛
    assert memory_service.user_key(7) == "admin:7"


def test_recall_failure_degrades_silently(monkeypatch):
    monkeypatch.setenv("MEM0_ENABLED", "1")
    memory_service._client = None

    class Boom:
        def search(self, *a, **k):
            raise RuntimeError("no backend")

    monkeypatch.setattr(memory_service, "get_client", lambda: Boom())
    assert memory_service.recall(1, "偏好") == ""


def test_remember_failure_never_raises(monkeypatch):
    monkeypatch.setenv("MEM0_ENABLED", "1")
    memory_service._client = None

    class Boom:
        def add(self, *a, **k):
            raise RuntimeError("no backend")

    monkeypatch.setattr(memory_service, "get_client", lambda: Boom())
    memory_service.remember(1, "我教高三数学", "好的")
