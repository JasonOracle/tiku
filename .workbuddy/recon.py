"""前置侦察：核对账号矩阵 + AI 网关连通性（只读探测）"""
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1"


def req(method, path, body=None, headers=None, timeout=180):
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


print("=== 1. 账号矩阵核对 ===")
for phone in ["10000000000", "13800000000", "13800000012", "13811111111", "13911111101"]:
    st, d = req("POST", "/api/v1/auth/login", {"phone": phone, "password": "123456"})
    if isinstance(d, dict) and d.get("code") == 200:
        u = d["data"]["user"]
        print(f"  {phone}: 登录成功 | display_name={u.get('display_name')} | super={u.get('is_super_admin')} | tenant={d['data'].get('default_tenant_id')}")
    else:
        print(f"  {phone}: 失败 -> {st} {str(d)[:120]}")

print("\n=== 2. 超管登录并探测 AI 网关 ===")
st, d = req("POST", "/api/v1/auth/login", {"phone": "13800000000", "password": "123456"})
if not (isinstance(d, dict) and d.get("code") == 200):
    print("  超管登录失败，终止:", d)
    raise SystemExit(1)
tok = d["data"]["token"]
tid = d["data"]["default_tenant_id"]
H = {"Authorization": "Bearer " + tok, "X-Tenant-ID": str(tid or 1)}
print(f"  超管 token 获取成功，default_tenant_id={tid}")

st, d = req("GET", "/api/v1/admin/ai/config", headers=H)
print(f"  AI 配置: {st} {json.dumps(d, ensure_ascii=False)[:300]}")

st, d = req("POST", "/api/v1/admin/ai/config/test", {}, headers=H)
print(f"  AI 网关连通: {st} {json.dumps(d, ensure_ascii=False)[:300]}")
