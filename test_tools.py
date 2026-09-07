import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app.services.ai_service import chat_completion
from app.services.ai_tools_registry import get_allowed_tools

tools = get_allowed_tools("super_admin")

try:
    content, tool_calls = chat_completion(
        prompt="现在题海有多少道题目",
        system="你是智题库平台的 AI 助手。你必须使用提供的工具查询数据库。",
        tools=tools
    )
    print("First call tool_calls:", json.dumps(tool_calls, indent=2, ensure_ascii=False))
    
    if tool_calls:
        tc = tool_calls[0]
        # Simulate admin_ai.py bug
        history = [{"role": "user", "content": "现在题海有多少道题目"}, tc]
        history.append({
            "role": "tool",
            "tool_call_id": tc.get("id"),
            "name": tc.get("function").get("name"),
            "content": json.dumps({"questions_count": 100}, ensure_ascii=False)
        })
        
        content2, tool_calls2 = chat_completion(
            prompt="",
            system="你是智题库平台的 AI 助手。",
            history=history,
            tools=tools
        )
        print("Second call content with bug:", content2)
except Exception as e:
    print("Error with bug:", e)


try:
    if tool_calls:
        tc = tool_calls[0]
        # Simulate correct approach
        history = [{"role": "user", "content": "现在题海有多少道题目"}]
        history.append({
            "role": "assistant",
            "content": "",
            "tool_calls": [tc]
        })
        history.append({
            "role": "tool",
            "tool_call_id": tc.get("id"),
            "name": tc.get("function").get("name"),
            "content": json.dumps({"questions_count": 100}, ensure_ascii=False)
        })
        
        content2, tool_calls2 = chat_completion(
            prompt="",
            system="你是智题库平台的 AI 助手。",
            history=history,
            tools=tools
        )
        print("Second call content (correct):", content2)
except Exception as e:
    print("Error with correct approach:", e)
