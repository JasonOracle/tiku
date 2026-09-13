"""超管口令候选验证 + 越权影子租户探测"""
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1"


def login(phone, pwd):
    data = json.dumps({"phone": phone, "password": pwd}).encode()
    r = urllib.request.Request(BASE + "/api/v1/auth/login", data=data,
                               headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            d = json.loads(resp.read().decode())
            return d
    except urllib.error.HTTPError as e:
        return {"err": e.code, "body": e.read().decode()[:200]}
    except Exception as e:
        return {"err": "EXC", "body": str(e)}


CANDIDATES = ["GodPass123", "admin123", "123456", "tiku123456", "root123456"]
print("=== 超管 13800000000 口令候选 ===")
ok = None
for p in CANDIDATES:
    d = login("13800000000", p)
    if d.get("code") == 200:
        print(f"  [命中] 口令 = {p}")
        ok = d
        break
    else:
        print(f"  失败 {p} -> {d.get('err')}")

if ok:
    u = ok["data"]["user"]
    print("  user:", json.dumps(u, ensure_ascii=False))
    print("  default_tenant_id:", ok["data"].get("default_tenant_id"))
    print("  joined_tenants:", json.dumps(ok["data"].get("joined_tenants"), ensure_ascii=False))
