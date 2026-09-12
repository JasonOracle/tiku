"""
[变更日志]
修改时间：2026-09-09
AI模型：Muse Spark
修改内容：[彻底清洗重写：AI 网关契约校验（元组解包回归），旧工具注册表调试已删除]
用法: cd backend && python ../test_tools.py（仅校验网关形状，不消耗额度断言内容）
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.ai_service import ai_available, chat_completion, extract_json

print("ai_available:", ai_available())
out = chat_completion(prompt='{"ok": true}', system="只输出JSON。", json_mode=True)
assert isinstance(out, tuple) and len(out) == 2, f"网关必须返回 (content, tool_calls) 元组，实际 {type(out)}"
content, tool_calls = out
print("content type:", type(content).__name__, "| tool_calls:", tool_calls)
parsed = extract_json(content or "")
print("extract_json:", parsed)
print("OK: gateway contract holds")
