"""
[变更日志]
修改时间：2026-09-06 17:30:00
AI模型：ZCode (GLM)
修改内容：[v1.2 新增 SenseNova (商汤日日新) 大模型客户端: OpenAI 兼容协议 + JSON 输出鲁棒解析 + 优雅降级]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[AI 网关切换: 默认首选高速模型 (OpenAI 兼容, 环境变量 XIAO_HONG_SHU_API_KEY[_2]), 保留原有供应商作故障转移; 新增 chat_completion_stream SSE 流式复用]
修改时间：2026-09-07
AI模型：Muse Spark
修改内容：[流式解析加固: 兼容内容块数组形态 + 空包诊断日志(delta 字段形状)]
"""
import os
import re
import json
import httpx
from typing import List, Dict, Optional, Generator, Any

# 高速主力模型 (OpenAI 兼容协议)。凭证读取宿主机用户系统环境变量, 不落盘 .env
DEFAULT_DOTS_API_URL = "https://note3-prev-api.askdiandian.com/v1/chat/completions"
DEFAULT_DOTS_MODEL = "dots3-note-prev"
# 历史供应商网关 (仅作故障转移兜底)
DEFAULT_API_URL = "https://token.sensenova.cn/v1/chat/completions"
DEFAULT_MODEL = "sensenova-6.8-flash-lite"


class AiServiceError(Exception):
    """AI 调用失败 (网络/鉴权/格式), 上层捕获后走人工兜底流程"""


_shared_client: Optional["httpx.Client"] = None


def _get_shared_client() -> "httpx.Client":
    """进程级共享连接池 (Keep-Alive 复用 TLS/TCP, 首字延迟优化)。"""
    global _shared_client
    if _shared_client is None:
        _shared_client = httpx.Client(
            http2=False,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _shared_client


def get_ai_providers() -> List[Dict[str, str]]:
    """获取所有已配置的 AI 提供商候选列表，按优先顺序排序:
    1. 高速主力模型 (KEY1): XIAO_HONG_SHU_API_KEY
    2. 高速主力模型 (KEY2): XIAO_HONG_SHU_API_KEY2
    3. SenseNova (KEY1): SENSENOVA_API_KEY (故障转移兜底)
    4. SenseNova (KEY2): SENSENOVA_API_KEY2
    5. Agnes 2.5 Flash (KEY1): AGNES_API_KEY
    6. Agnes 2.5 Flash (KEY2): AGNES_API_KEY2
    """
    providers = []

    # 1-2. 高速主力模型 (OpenAI 兼容)
    dots_url = os.getenv("XIAO_HONG_SHU_API_URL") or DEFAULT_DOTS_API_URL
    dots_model = os.getenv("XIAO_HONG_SHU_MODEL") or DEFAULT_DOTS_MODEL
    dk1 = os.getenv("XIAO_HONG_SHU_API_KEY") or None
    if dk1:
        providers.append({
            "name": "Dots (Key 1)",
            "api_url": dots_url,
            "api_key": dk1,
            "model": dots_model,
        })
    dk2 = os.getenv("XIAO_HONG_SHU_API_KEY2") or None
    if dk2:
        providers.append({
            "name": "Dots (Key 2)",
            "api_url": dots_url,
            "api_key": dk2,
            "model": dots_model,
        })
    
    # 1. SenseNova KEY 1
    sk1 = os.getenv("SENSENOVA_API_KEY") or None
    if sk1:
        providers.append({
            "name": "SenseNova (Key 1)",
            "api_url": os.getenv("SENSENOVA_API_URL") or DEFAULT_API_URL,
            "api_key": sk1,
            "model": os.getenv("SENSENOVA_MODEL") or DEFAULT_MODEL,
        })
        
    # 2. SenseNova KEY 2
    sk2 = os.getenv("SENSENOVA_API_KEY2") or None
    if sk2:
        providers.append({
            "name": "SenseNova (Key 2)",
            "api_url": os.getenv("SENSENOVA_API_URL") or DEFAULT_API_URL,
            "api_key": sk2,
            "model": os.getenv("SENSENOVA_MODEL") or DEFAULT_MODEL,
        })
        
    # 3. Agnes 2.5 Flash KEY 1
    ak1 = os.getenv("AGNES_API_KEY") or None
    if ak1:
        providers.append({
            "name": "Agnes 2.5 Flash (Key 1)",
            "api_url": os.getenv("AGNES_API_URL") or "https://apihub.agnes-ai.com/v1/chat/completions",
            "api_key": ak1,
            "model": os.getenv("AGNES_MODEL") or "agnes-2.5-flash",
        })
        
    # 4. Agnes 2.5 Flash KEY 2
    ak2 = os.getenv("AGNES_API_KEY2") or None
    if ak2:
        providers.append({
            "name": "Agnes 2.5 Flash (Key 2)",
            "api_url": os.getenv("AGNES_API_URL") or "https://apihub.agnes-ai.com/v1/chat/completions",
            "api_key": ak2,
            "model": os.getenv("AGNES_MODEL") or "agnes-2.5-flash",
        })
        
    return providers


def get_ai_config() -> Dict[str, Optional[str]]:
    # 用 or 兜底: 容器环境可能注入空字符串变量, 不能让空串覆盖默认值
    providers = get_ai_providers()
    if providers:
        return providers[0]
    return {
        "name": "SenseNova (None)",
        "api_key": None,
        "api_url": DEFAULT_API_URL,
        "model": DEFAULT_MODEL,
    }


def ai_available() -> bool:
    """AI 能力是否可用 (只要配置了任一 API Key 即表示可用)"""
    return len(get_ai_providers()) > 0


def chat_completion(
    prompt: str,
    system: str = "你是一名严谨、专业的中文助理。",
    json_mode: bool = False,
    temperature: float = 0.3,
    timeout: float = 90.0,
    retries: int = 1,
    tools: Optional[List[dict]] = None,
    tool_choice: Optional[str] = "auto",
    history: Optional[List[dict]] = None,
) -> tuple[Optional[str], Optional[List[dict]]]:
    """单轮调用大模型, 返回文本。按顺序故障转移 (SenseNova Key1 -> Key2 -> Agnes Key1 -> Key2)。
    任何提供商失败抛异常后自动切下一个 API Key。"""
    providers = get_ai_providers()
    if not providers:
        raise AiServiceError("未配置任何有效的 AI API Key (SENSENOVA_API_KEY / SENSENOVA_API_KEY2 / AGNES_API_KEY / AGNES_API_KEY2)")

    messages = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    if json_mode:
        messages[-1]["content"] += "\n strictly output valid JSON only, without any extra text."
    
    if prompt:
        messages.append({"role": "user", "content": prompt})

    import time
    last_errors = []

    for provider in providers:
        payload = {
            "model": provider["model"],
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json",
        }
        
        for attempt in range(retries + 1):
            try:
                resp = _get_shared_client().post(provider["api_url"], json=payload, headers=headers, timeout=timeout)
                if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                    time.sleep(2 * (attempt + 1))  # 内部微小退避重试
                    continue
                if resp.status_code != 200:
                    err_msg = f"{provider['name']} 接口返回 {resp.status_code}: {resp.text[:200]}"
                    last_errors.append(err_msg)
                    break  # 切下一个 provider
                data = resp.json()
                message = data["choices"][0]["message"]
                content = message.get("content")
                if isinstance(content, str):
                    content = content
                elif content is not None:
                    content = str(content)
                tool_calls = message.get("tool_calls")
                return content, tool_calls
            except Exception as e:
                if attempt < retries:
                    time.sleep(2 * (attempt + 1))
                    continue
                err_msg = f"{provider['name']} 调用异常: {e}"
                last_errors.append(err_msg)
                break  # 切下一个 provider

    raise AiServiceError("所有配置的 AI 服务均调用失败: " + " | ".join(last_errors))


def _build_messages(prompt: str, system: str, history: Optional[List[dict]], json_mode: bool = False) -> List[dict]:
    messages = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    if json_mode:
        messages[-1]["content"] += "\n strictly output valid JSON only, without any extra text."
    if prompt:
        messages.append({"role": "user", "content": prompt})
    return messages


def chat_completion_stream(
    prompt: str,
    system: str = "你是一名严谨、专业的中文助理。",
    temperature: float = 0.5,
    timeout: float = 120.0,
    tools: Optional[List[dict]] = None,
    tool_choice: Optional[str] = "auto",
    history: Optional[List[dict]] = None,
) -> Generator[Dict[str, Any], None, None]:
    """SSE 流式调用 (OpenAI stream 协议), 按优先顺序故障转移。

    yield 事件:
    - {"type": "delta", "text": "..."} 增量文本
    - {"type": "tool_calls", "tool_calls": [...]} 模型请求工具调用 (同非流式返回结构)
    - {"type": "done"} 本轮流结束 (无工具调用时)
    - {"type": "error", "message": "..."} 本轮失败 (上层可切下一个 provider, 此处已内聚处理)
    """
    providers = get_ai_providers()
    if not providers:
        yield {"type": "error", "message": "未配置任何有效的 AI API Key"}
        return

    messages = _build_messages(prompt, system, history)
    last_error = ""
    for provider in providers:
        payload = {
            "model": provider["model"],
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
        headers = {
            "Authorization": f"Bearer {provider['api_key']}",
            "Content-Type": "application/json",
        }
        try:
            with _get_shared_client().stream("POST", provider["api_url"], json=payload, headers=headers,
                              timeout=httpx.Timeout(connect=10.0, read=timeout, write=10.0, pool=10.0)) as resp:
                if resp.status_code != 200:
                    last_error = f"{provider['name']} 接口返回 {resp.status_code}"
                    continue  # 切下一个 provider
                saw_any = False
                saw_text = False
                delta_keys: set = set()
                tool_frags: Dict[int, dict] = {}
                for line in resp.iter_lines():
                    if not line:
                        continue
                    text_line = line.decode("utf-8") if isinstance(line, bytes) else line
                    if not text_line.startswith("data:"):
                        continue
                    data_str = text_line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                    except Exception:
                        continue
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    delta = (choices[0].get("delta") or {})
                    try:
                        delta_keys.update(delta.keys())
                    except Exception:
                        pass
                    content_piece = delta.get("content")
                    # 兼容内容块数组形态 ([{"type": "text", "text": "..."}])
                    if isinstance(content_piece, list):
                        parts = []
                        for p in content_piece:
                            if isinstance(p, dict):
                                parts.append(str(p.get("text") or p.get("content") or ""))
                            else:
                                parts.append(str(p))
                        content_piece = "".join(parts)
                    if content_piece:
                        saw_any = True
                        saw_text = True
                        yield {"type": "delta", "text": content_piece}
                    for tc in (delta.get("tool_calls") or []):
                        idx = tc.get("index", 0)
                        frag = tool_frags.setdefault(idx, {"id": "", "name": "", "arguments": ""})
                        if tc.get("id"):
                            frag["id"] = tc["id"]
                        func = tc.get("function") or {}
                        if func.get("name"):
                            frag["name"] = func["name"]
                        if func.get("arguments"):
                            frag["arguments"] += func["arguments"]
                if tool_frags:
                    normalized = [
                        {"id": frag["id"], "function": {"name": frag["name"], "arguments": frag["arguments"]}}
                        for _, frag in sorted(tool_frags.items())
                    ]
                    yield {"type": "tool_calls", "tool_calls": normalized}
                else:
                    if not saw_text:
                        print(f"[ai_stream] empty completion provider={provider['name']} delta_keys={sorted(delta_keys)}")
                    yield {"type": "done"}
                return
        except Exception as e:
            last_error = f"{provider['name']} 调用异常: {e}"
            continue  # 切下一个 provider
    yield {"type": "error", "message": "所有配置的 AI 服务均调用失败: " + last_error}


def extract_json(text: str):
    """从大模型返回文本中鲁棒提取 JSON (支持 ```json 代码块 / 裸对象 / 裸数组 / 非标准 JSON 修正)。
    解析失败抛 AiServiceError, 由上层走回退机制 (退回 pending_grading / 人工)。"""
    if not text or not text.strip():
        raise AiServiceError("大模型返回内容为空")

    candidates = []
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        candidates.append(fence.group(1))
    candidates.append(text)

    # 用正则精准捕获最宽的 { ... } 或 [ ... ]
    m_obj = re.search(r"\{[\s\S]*\}", text)
    if m_obj:
        candidates.append(m_obj.group(0))
    m_arr = re.search(r"\[[\s\S]*\]", text)
    if m_arr:
        candidates.append(m_arr.group(0))

    for cand in candidates:
        cand = cand.strip()
        if not cand:
            continue
        try:
            return json.loads(cand)
        except Exception:
            pass

        # 针对常见非标准 JSON 语法进行正则清洗修复
        cleaned = cand
        # 1. 移除 JSON 内控制字符
        cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", " ", cleaned)
        # 2. 移除数组/对象尾部逗号 (trailing commas): , } 或 , ]
        cleaned = re.sub(r",\s*([\}\]])", r"\1", cleaned)
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # 3. 尝试括号平衡计数截取第一个 { ... } 或 [ ... ]
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
                        sub = cand[start : i + 1]
                        try:
                            return json.loads(sub)
                        except Exception:
                            # 尝试对子串也清理尾部逗号
                            try:
                                return json.loads(re.sub(r",\s*([\}\]])", r"\1", sub))
                            except Exception:
                                break
            break

    raise AiServiceError("大模型返回的 JSON 格式无法解析")
