"""
[变更日志]
修改时间：2026-09-06 17:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增 SenseNova (商汤日日新) 大模型客户端: OpenAI 兼容协议 + JSON 输出鲁棒解析 + 优雅降级]
"""
import os
import re
import json
import httpx
from typing import List, Dict, Optional

# 开发期统一使用商汤日日新大模型 (免费)。凭证读取宿主机用户系统环境变量, 不落盘 .env
# OpenAI 兼容网关: https://token.sensenova.cn/v1 (模型如 sensenova-6.7-flash-lite)
DEFAULT_API_URL = "https://token.sensenova.cn/v1/chat/completions"
DEFAULT_MODEL = "sensenova-6.8-flash-lite"


class AiServiceError(Exception):
    """AI 调用失败 (网络/鉴权/格式), 上层捕获后走人工兜底流程"""


def get_ai_config() -> Dict[str, Optional[str]]:
    # 用 or 兜底: 容器环境可能注入空字符串变量, 不能让空串覆盖默认值
    return {
        "api_key": os.getenv("SENSENOVA_API_KEY") or None,
        "api_url": os.getenv("SENSENOVA_API_URL") or DEFAULT_API_URL,
        "model": os.getenv("SENSENOVA_MODEL") or DEFAULT_MODEL,
    }


def ai_available() -> bool:
    """AI 能力是否可用 (未配置 Key 时 B 端功能优雅降级, 阅卷走人工)"""
    return bool(get_ai_config()["api_key"])


def chat_completion(
    prompt: str,
    system: str = "你是一名严谨、专业的中文助理。",
    json_mode: bool = False,
    temperature: float = 0.3,
    timeout: float = 90.0,
    retries: int = 2,
) -> str:
    """单轮调用大模型, 返回文本。任何失败抛 AiServiceError (调用方负责兜底)。
    429 限流/瞬时 5xx 自动退避重试 (免费档限流常见)。"""
    cfg = get_ai_config()
    if not cfg["api_key"]:
        raise AiServiceError("未配置 SENSENOVA_API_KEY，AI 能力不可用")

    messages = [{"role": "system", "content": system}]
    if json_mode:
        messages[-1]["content"] += "\n strictly output valid JSON only, without any extra text."
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    last_err: Optional[str] = None
    import time
    for attempt in range(retries + 1):
        try:
            resp = httpx.post(cfg["api_url"], json=payload, headers=headers, timeout=timeout)
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                last_err = f"大模型接口返回 {resp.status_code}"
                time.sleep(4 * (attempt + 1))  # 退避重试
                continue
            if resp.status_code != 200:
                raise AiServiceError(f"大模型接口返回 {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content if isinstance(content, str) else str(content)
        except AiServiceError:
            raise
        except Exception as e:
            if attempt < retries:
                last_err = f"大模型调用失败: {e}"
                time.sleep(4 * (attempt + 1))
                continue
            raise AiServiceError(f"大模型调用失败: {e}")
    raise AiServiceError(last_err or "大模型调用失败")


def extract_json(text: str):
    """从大模型返回文本中鲁棒提取 JSON (支持 ```json 代码块 / 裸对象 / 裸数组)。
    解析失败抛 AiServiceError, 由上层走回退机制 (退回 pending_grading / 人工)。"""
    if not text or not text.strip():
        raise AiServiceError("大模型返回内容为空")

    candidates = []
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        candidates.append(fence.group(1))
    candidates.append(text)

    for cand in candidates:
        cand = cand.strip()
        try:
            return json.loads(cand)
        except Exception:
            pass
        # 尝试截取第一个 { ... } 或 [ ... ] 平衡块
        for open_ch, close_ch in (("{", "}"), ("[", "]")):
            start = cand.find(open_ch)
            if start == -1:
                continue
            depth = 0
            for i in range(start, len(cand)):
                if cand[i] == open_ch:
                    depth += 1
                elif cand[i] == close_ch:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(cand[start:i + 1])
                        except Exception:
                            break
            break
    raise AiServiceError("大模型返回的 JSON 格式无法解析")
