"""AI 网关连通性 + 大模型真实出题冒烟（用现有租户 2 管理员，只读/低副作用）"""
import json
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1"


def req(method, path, body=None, headers=None, timeout=240):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    r = urllib.request.Request(BASE + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]
    except Exception as e:
        return -1, f"EXC {e}"


st, d = req("POST", "/api/v1/auth/login", {"phone": "13800000012", "password": "123456"})
tok = d["data"]["token"]
tid = d["data"]["default_tenant_id"]
H = {"Authorization": "Bearer " + tok, "X-Tenant-ID": str(tid)}
print(f"tenant={tid} 登录成功")

print("\n--- AI 配置 ---")
st, d = req("GET", "/api/v1/admin/ai/config", headers=H)
print(st, json.dumps(d, ensure_ascii=False)[:400])

print("\n--- AI 网关连通测试 ---")
t0 = time.time()
st, d = req("POST", "/api/v1/admin/ai/config/test", {}, headers=H)
print(f"{st} ({time.time()-t0:.1f}s) {json.dumps(d, ensure_ascii=False)[:400]}")
