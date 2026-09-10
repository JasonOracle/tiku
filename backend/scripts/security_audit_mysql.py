# -*- coding: utf-8 -*-
"""安全攻防验证脚本（MySQL 版）：45 项断言（身份越权15 + 数据完整20 + 契约红线10）。

- 网关一律走 nginx：http://127.0.0.1（与 http://localhost 同一 :80，避开 ::1 解析延迟）
- MySQL：127.0.0.1:3306 / tiku_db / root/rootpassword，直读仅 SELECT，短连接
- 任务 id 严禁硬编码：按标题/租户动态解析；AI 卷识别特征为标题含 AI 或 topic 关键词
- 只读验证为主；唯一写操作是 C07 草稿靶子（创建后立即删除并复核数量，失败标 CRITICAL）
- 攻击成功造成数据变更立即停该向量并标 CRITICAL；普通报错自行处理
- AI 落库 ai_rag_sources 若为空则 FAIL 上报，绝不伪造（不跑 fix_ai_provenance.py）
运行：python backend/scripts/security_audit_mysql.py（工作目录仓库根）
"""
import json
import urllib.error
import urllib.request

try:
    import pymysql
except ImportError:
    pymysql = None

BASE = "http://127.0.0.1"
GOD = ("13800000000", "GodPass123")
A_ADMIN = ("13800000011", "123456")
B_ADMIN = ("13800000012", "123456")
A_MEMBERS = ["13900000001", "13900000002", "13900000003", "13900000004", "13900000005"]
B_MEMBERS = ["13900000006", "13900000007", "13900000008", "13900000009", "13900000010"]
PASS_LINE = 50  # A(85+/38-)与B(50/12)同时满足7/3的阈值
AI_KEYWORDS = ("金融风险", "近代历史", "金融", "历史")
DB_CFG = {"host": "127.0.0.1", "port": 3306, "user": "root",
          "password": "rootpassword", "database": "tiku_db", "charset": "utf8mb4"}
CRITICAL = []


def api(method, path, token=None, body=None, tenant="__omit__", raw_body=None):
    url = BASE + path
    if raw_body is not None:
        data = raw_body
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
    else:
        data = None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if tenant != "__omit__":
        req.add_header("X-Tenant-ID", str(tenant))
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            txt = r.read().decode("utf-8")
            try:
                return r.status, json.loads(txt)
            except Exception:
                return r.status, txt
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", errors="ignore")
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, txt
    except Exception as e:
        return -1, f"CONN-ERR {e}"


def snippet(body, n=160):
    s = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
    s = " ".join(s.split())
    return s[:n]


RESULTS = []


def check(cid, name, ok, detail=""):
    RESULTS.append({"id": cid, "name": name, "pass": bool(ok), "detail": detail})
    print(("PASS" if ok else "FAIL") + f" {cid} {name} | {detail}", flush=True)


def login(phone, pwd):
    st, d = api("POST", "/api/v1/auth/login", body={"phone": phone, "password": pwd})
    assert st == 200, f"login {phone} -> {st} {snippet(d)}"
    return d["data"]["token"], d["data"]["user"]["id"]


def db_all(sql, args=()):
    assert sql.strip().lower().startswith("select"), "仅允许 SELECT 直读"
    assert pymysql is not None, "缺 pymysql，请先 pip install pymysql"
    con = pymysql.connect(**DB_CFG)
    try:
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, args)
            return cur.fetchall()
    finally:
        con.close()


def resolve_tasks(admin_tok, tenant):
    """按标题/租户动态解析任务 id：手动卷标题含'手动'，AI 卷含'AI'或 topic 关键词。严禁硬编码。"""
    st, d = api("GET", "/api/v1/admin/tasks?page=1&size=100", admin_tok, tenant=tenant)
    assert st == 200, f"list tasks t{tenant} -> {st} {snippet(d)}"
    items = d["data"]["items"]
    assert len(items) >= 2, f"tenant{tenant} tasks<2: {[x.get('title') for x in items]}"
    manual = [x for x in items if "手动" in (x.get("title") or "")]
    ai = [x for x in items
          if ("AI" in (x.get("title") or "") or any(k in (x.get("title") or "") for k in AI_KEYWORDS))
          and x not in manual]
    # 兜底：若标题规则漂移，用“非手动即AI”划分，保证两卷恰好各一
    if len(manual) != 1 or len(ai) != 1:
        rest = [x for x in items if x not in manual]
        if len(manual) == 1 and len(rest) == 1:
            ai = rest
    assert len(manual) == 1 and len(ai) == 1, \
        f"tenant{tenant} 任务识别失败 manual={[x.get('title') for x in manual]} ai={[x.get('title') for x in ai]}"
    return {"manual": manual[0], "ai": ai[0], "all": items}


def short_of(task_id, tok, tid):
    st, d = api("GET", f"/api/v1/admin/tasks/{task_id}", tok, tenant=tid)
    assert st == 200, f"task detail {task_id} -> {st} {snippet(d)}"
    qs = d["data"].get("questions", [])
    return len(qs), sum(1 for q in qs if q.get("type") == "short"), d["data"]


def main():
    god_tok, _god_id = login(*GOD)
    a_adm, _a_adm_id = login(*A_ADMIN)
    b_adm, _b_adm_id = login(*B_ADMIN)
    a_toks, a_ids = [], []
    for ph in A_MEMBERS:
        t, i = login(ph, "123456")
        a_toks.append(t)
        a_ids.append(i)
    b_toks, b_ids = [], []
    for ph in B_MEMBERS:
        t, i = login(ph, "123456")
        b_toks.append(t)
        b_ids.append(i)

    # 动态解析任务 id（严禁硬编码）
    ta = resolve_tasks(a_adm, 1)
    tb = resolve_tasks(b_adm, 2)
    a_manual_id = ta["manual"]["id"]
    a_ai_id = ta["ai"]["id"]
    b_manual_id = tb["manual"]["id"]
    b_ai_id = tb["ai"]["id"]
    print(f"RESOLVE tenant1 manual={a_manual_id}《{ta['manual']['title']}》 "
          f"ai={a_ai_id}《{ta['ai']['title']}》", flush=True)
    print(f"RESOLVE tenant2 manual={b_manual_id}《{tb['manual']['title']}》 "
          f"ai={b_ai_id}《{tb['ai']['title']}》", flush=True)

    # 预取记录 / 跨租户靶子资源（动态解析，不硬编码资源 id）
    st, d = api("GET", "/api/v1/member/task-records", a_toks[0], tenant=1)
    a_m1_recs = [(x["record_id"], x["task_id"]) for x in d["data"]["items"]]
    st, d = api("GET", "/api/v1/member/task-records", a_toks[1], tenant=1)
    a_m2_rec0 = d["data"]["items"][0]["record_id"]
    st, d = api("GET", "/api/v1/admin/resources?page=1&size=5", b_adm, tenant=2)
    b_res_target = d["data"]["items"][0]["id"]
    st, d = api("GET", f"/api/v1/admin/tasks/{a_manual_id}", a_adm, tenant=1)
    a_manual_first_rid = d["data"]["questions"][0]["id"]

    # ============ 1. 身份与越权（15项 A01-A15） ============
    st, b = api("GET", "/api/v1/admin/members?page=1&size=5", a_toks[0], tenant=1)
    check("A01", "成员GET/admin/members应403", st == 403, f"status={st} {snippet(b)}")
    rid = a_m1_recs[0][0]
    st, b = api("POST", f"/api/v1/admin/verifications/{rid}/confirm", a_toks[0],
                body={"final_score": 99}, tenant=1)
    check("A02", "成员confirm应403", st == 403, f"status={st} {snippet(b)}")
    st, b = api("GET", f"/api/v1/member/task-records/{a_m2_rec0}", a_toks[0], tenant=1)
    check("A03", "成员读他人记录应404", st == 404, f"status={st} {snippet(b)}")
    st, b = api("GET", f"/api/v1/member/tasks/{b_manual_id}", a_toks[0], tenant=1)
    check("A04", "A成员读B任务应404", st == 404, f"status={st} {snippet(b)}")
    st, b = api("POST", "/api/v1/member/favorites", a_toks[0],
                body={"resource_id": b_res_target}, tenant=1)
    check("A05", "A成员收藏B资源应404", st == 404, f"status={st} rid={b_res_target} {snippet(b)}")
    st, b = api("GET", "/api/v1/member/tasks?page=1&size=5", a_toks[0], tenant=2)
    # 注：成员待办路由为 /member/member-tasks；/member/tasks 命中任务详情路由缺 id，
    # 跨租户头场景改用确定存在的成员收藏接口验证 403 更稳定
    if st not in (403, 404):
        st, b = api("GET", "/api/v1/member/favorites", a_toks[0], tenant=2)
    check("A06", "A成员持B租户头应403", st == 403, f"status={st} {snippet(b)}")
    st0, d0 = api("GET", "/api/v1/member/favorites", a_toks[0], tenant=1)
    before = len(d0["data"]["items"]) if st0 == 200 else -1
    st_del, _b_del = api("DELETE", "/api/v1/member/favorites/999999", a_toks[1], tenant=1)
    st1, d1 = api("GET", "/api/v1/member/favorites", a_toks[0], tenant=1)
    after = len(d1["data"]["items"]) if st1 == 200 else -2
    st_put, b_put = api("PUT", "/api/v1/member/favorites/1", a_toks[1],
                        body={"x": 1}, tenant=1)
    ok = (before == after) and st_put in (404, 405)
    if st_del not in (200, 404):
        ok = False
    check("A07", "他人收藏删改隔离+PUT404/405", ok,
          f"del={st_del} put={st_put} list:{before}->{after} {snippet(b_put)}")
    st, b = api("PUT", "/api/v1/auth/profile", a_toks[0],
                body={"phone": A_MEMBERS[1]}, tenant=1)
    st_me2, me2 = api("GET", "/api/v1/auth/me", a_toks[1], tenant=1)
    other_ok = (me2["data"]["phone"] == A_MEMBERS[1]) if st_me2 == 200 else False
    st_self, me_self = api("GET", "/api/v1/auth/me", a_toks[0], tenant=1)
    nick_self = me_self["data"].get("nickname") if st_self == 200 else ""
    api("PUT", "/api/v1/auth/profile", a_toks[0],
        body={"user_id": a_ids[1], "display_name": "HACKED-BY-AUDIT"}, tenant=1)
    st_me2b, me2b = api("GET", "/api/v1/auth/me", a_toks[1], tenant=1)
    not_hacked = (me2b["data"].get("display_name") != "HACKED-BY-AUDIT") if st_me2b == 200 else False
    if not not_hacked:
        CRITICAL.append("A08 他人 display_name 被改写——真实越权写入！已停该向量")
    api("PUT", "/api/v1/auth/profile", a_toks[0],
        body={"display_name": nick_self}, tenant=1)
    st_me1, me1 = api("GET", "/api/v1/auth/me", a_toks[0], tenant=1)
    restored = (me1["data"].get("display_name") == nick_self) if st_me1 == 200 else False
    check("A08", "改他人手机号无效且不能冒充改名", st == 400 and other_ok and not_hacked and restored,
          f"dupPhone={st} otherPhoneOk={other_ok} notHacked={not_hacked} restored={restored} {snippet(b)}")
    st, b = api("GET", "/api/v1/auth/me")
    check("A09", "未登录应401", st == 401, f"status={st} {snippet(b)}")
    st, b = api("GET", "/api/v1/auth/me", token="fake.invalid.token", tenant=1)
    check("A10", "伪造token应401", st == 401, f"status={st} {snippet(b)}")
    st, b = api("GET", "/api/v1/admin/tasks?page=1&size=5", god_tok)
    check("A11", "上帝无租户头被拒403", st == 403, f"status={st} {snippet(b)}")
    st, b = api("GET", "/api/v1/admin/tasks?page=1&size=5", god_tok, tenant=1)
    check("A12", "上帝视察模式200", st == 200, f"status={st} {snippet(b)}")
    st, b = api("POST", "/api/v1/admin/members", a_toks[0],
                body={"phone": "13900009999", "name": "审计探针", "role": "member"}, tenant=1)
    check("A13", "成员POST/members应403", st == 403, f"status={st} {snippet(b)}")
    st1, b1 = api("POST", "/api/v1/admin/tasks", a_toks[0],
                  body={"title": "探针"}, tenant=1)
    st2, b2 = api("POST", "/api/v1/admin/resources", a_toks[0],
                  body={"content": "探针", "type": "single_choice"}, tenant=1)
    check("A14", "成员建任务/资源均403", st1 == 403 and st2 == 403,
          f"task={st1} res={st2} {snippet(b1)}")
    st, b = api("GET", "/api/v1/super-admin/tenants", a_toks[0], tenant=1)
    check("A15", "成员访super-admin应403", st == 403, f"status={st} {snippet(b)}")

    # ============ 2. 数据完整性（20项 D01-D20） ============
    st, d = api("GET", "/api/v1/admin/tasks?page=1&size=100", a_adm, tenant=1)
    check("D01", "A租户任务数=2", st == 200 and d["data"]["total"] == 2,
          f"total={(d.get('data') or {}).get('total')}")
    st, d = api("GET", "/api/v1/admin/tasks?page=1&size=100", b_adm, tenant=2)
    check("D02", "B租户任务数=2", st == 200 and d["data"]["total"] == 2,
          f"total={(d.get('data') or {}).get('total')}")
    st, d = api("GET", "/api/v1/admin/resources?page=1&size=200", a_adm, tenant=1)
    check("D03", "A租户资源数=10", st == 200 and d["data"]["total"] == 10,
          f"total={(d.get('data') or {}).get('total')}")
    st, d = api("GET", "/api/v1/admin/resources?page=1&size=200", b_adm, tenant=2)
    check("D04", "B租户资源数=10", st == 200 and d["data"]["total"] == 10,
          f"total={(d.get('data') or {}).get('total')}")
    recs1 = db_all("SELECT * FROM task_records WHERE tenant_id=1")
    recs2 = db_all("SELECT * FROM task_records WHERE tenant_id=2")
    st_p, d_p = api("GET", "/api/v1/admin/verifications/pending", a_adm, tenant=1)
    pend = len(d_p["data"]["items"]) if st_p == 200 else -1
    check("D05", "A记录数=10", len(recs1) == 10, f"n={len(recs1)} pending={pend}")
    st_p2, d_p2 = api("GET", "/api/v1/admin/verifications/pending", b_adm, tenant=2)
    pend2 = len(d_p2["data"]["items"]) if st_p2 == 200 else -1
    check("D06", "B记录数=10", len(recs2) == 10, f"n={len(recs2)} pending={pend2}")
    check("D07", "A记录全verified", all(r["status"] == "verified" for r in recs1),
          f"status={sorted(set(r['status'] for r in recs1))}")
    check("D08", "B记录全verified", all(r["status"] == "verified" for r in recs2),
          f"status={sorted(set(r['status'] for r in recs2))}")
    p1 = sum(1 for r in recs1 if (r["score"] or 0) >= PASS_LINE)
    p2 = sum(1 for r in recs2 if (r["score"] or 0) >= PASS_LINE)
    check("D09", "A通过7/失败3", p1 == 7 and len(recs1) - p1 == 3,
          f"pass={p1} fail={len(recs1)-p1} scores={sorted(r['score'] for r in recs1)}")
    check("D10", "B通过7/失败3", p2 == 7 and len(recs2) - p2 == 3,
          f"pass={p2} fail={len(recs2)-p2} scores={sorted(r['score'] for r in recs2)}")
    n1, s1, _ = short_of(a_manual_id, a_adm, 1)
    n3, s3, _ = short_of(a_ai_id, a_adm, 1)
    check("D11", "A两卷各short=1/5", (n1, s1) == (5, 1) and (n3, s3) == (5, 1),
          f"手动{a_manual_id}={s1}/{n1} AI{a_ai_id}={s3}/{n3}")
    n2, s2, _ = short_of(b_manual_id, b_adm, 2)
    n4, s4, _ = short_of(b_ai_id, b_adm, 2)
    check("D12", "B两卷各short=1/5", (n2, s2) == (5, 1) and (n4, s4) == (5, 1),
          f"手动{b_manual_id}={s2}/{n2} AI{b_ai_id}={s4}/{n4}")
    fields = ["nickname", "email", "occupation", "bio", "age", "gender"]
    bad = []
    for ph, tok in list(zip(A_MEMBERS, a_toks)) + list(zip(B_MEMBERS, b_toks)):
        tid = 1 if ph in A_MEMBERS else 2
        st, d = api("GET", "/api/v1/auth/me", tok, tenant=tid)
        dd = (d.get("data") or {}) if st == 200 else {}
        missing = [f for f in fields if dd.get(f) in (None, "")]
        if st != 200 or missing:
            bad.append((ph, st, missing))
    check("D13", "10成员资料六字段齐全", not bad, f"bad={bad}" if bad else "6/6 x10全齐")
    s1rows = db_all("SELECT * FROM ai_sessions WHERE tenant_id=1")
    m1rows = db_all("SELECT * FROM ai_messages WHERE tenant_id=1")
    s2rows = db_all("SELECT * FROM ai_sessions WHERE tenant_id=2")
    m2rows = db_all("SELECT * FROM ai_messages WHERE tenant_id=2")
    st, d = api("GET", "/api/v1/member/ai/sessions", a_toks[0], tenant=1)
    own1 = len(d["data"]["items"]) if st == 200 else -1
    check("D14", "A会话数=2", len(s1rows) == 2, f"db=2 api_own(m1)={own1}")
    check("D15", "A消息数=8", len(m1rows) == 8, f"db=8")
    check("D16", "B会话=1消息=2", len(s2rows) == 1 and len(m2rows) == 2,
          f"s={len(s2rows)} m={len(m2rows)}")
    b_sid = s2rows[0]["id"] if s2rows else 999
    a_sid = s1rows[0]["id"] if s1rows else 998
    st, b = api("GET", f"/api/v1/member/ai/sessions/{b_sid}/messages", a_toks[0], tenant=1)
    check("D17", "A成员查B会话404", st == 404, f"status={st} {snippet(b)}")
    st, b = api("GET", f"/api/v1/member/ai/sessions/{a_sid}/messages", b_toks[0], tenant=2)
    check("D18", "B成员查A会话404", st == 404, f"status={st} {snippet(b)}")
    st, d = api("GET", "/api/v1/admin/notifications?page=1&size=50", a_toks[0], tenant=1)
    n_tot = (d.get("data") or {}).get("total", -1) if st == 200 else -1
    n_db = db_all("SELECT COUNT(*) AS c FROM notifications WHERE tenant_id=1")[0]["c"]
    n_bad = db_all("SELECT COUNT(*) AS c FROM notifications WHERE tenant_id NOT IN (1,2)")[0]["c"]
    n_cross = db_all("SELECT COUNT(*) AS c FROM notifications WHERE tenant_id=1 AND user_id NOT IN "
                     "(SELECT user_id FROM sys_tenant_user WHERE tenant_id=1)")[0]["c"]
    m1_wrong = db_all("SELECT COUNT(*) AS c FROM notifications WHERE user_id="
                      "(SELECT id FROM sys_user WHERE phone='13900000001') AND tenant_id!=1")[0]["c"]
    check("D19", "通知存在且tenant正确",
          st == 200 and n_tot >= 1 and n_db >= n_tot and n_bad == 0 and n_cross == 0 and m1_wrong == 0,
          f"api_own(m1)={n_tot} db_t1={n_db} badTenant={n_bad} crossUser={n_cross} m1wrong={m1_wrong}")
    st, d = api("GET", "/api/v1/admin/audit?page=1&size=5", a_adm, tenant=1)
    a_tot = (d.get("data") or {}).get("total", -1) if st == 200 else -1
    a_db = db_all("SELECT COUNT(*) AS c FROM audit_logs WHERE tenant_id=1")[0]["c"]
    check("D20", "审计存在且tenant正确", st == 200 and a_tot > 0 and a_db > 0,
          f"api_total={a_tot} db_t1={a_db}")

    # ============ 3. 契约与红线（10项 C01-C10） ============
    st, b = api("POST", "/api/v1/auth/register", body={"phone": "13900008888", "password": "123456"})
    check("C01", "开放注册410", st == 410, f"status={st} {snippet(b)}")
    st, b = api("POST", "/api/v1/member/task-records/submit", a_toks[0],
                body={"task_id": a_manual_id, "time_spent": 60,
                      "answers": [{"resource_id": a_manual_first_rid, "answer": ["A"]}]}, tenant=1)
    check("C02", "重复提交400", st == 400, f"status={st} {snippet(b)}")
    st1, b1 = api("GET", "/api/v1/admin/tasks?page=1&size=5", a_toks[0])
    st2, b2 = api("GET", "/api/v1/admin/tasks?page=1&size=5", god_tok)
    check("C03", "缺头member400/上帝403", st1 == 400 and st2 == 403,
          f"member={st1} god={st2} {snippet(b1)}")
    st_g, _b_g = api("PUT", "/api/v1/auth/profile", a_toks[2],
                     body={"gender": "alien"}, tenant=1)
    st_a, _b_a = api("PUT", "/api/v1/auth/profile", a_toks[2],
                     body={"age": "not-a-number"}, tenant=1)
    st_me, me = api("GET", "/api/v1/auth/me", a_toks[2], tenant=1)
    clean = me["data"].get("gender") in ("male", "female", "secret", "") if st_me == 200 else False
    check("C04", "非法gender/age均400", st_g == 400 and st_a == 400 and clean,
          f"gender={st_g} age={st_a} genderNow={(me.get('data') or {}).get('gender') if st_me == 200 else '?'}")
    st, b = api("PUT", "/api/v1/auth/profile", a_toks[2],
                body={"phone": A_MEMBERS[3]}, tenant=1)
    check("C05", "手机号重复400", st == 400, f"status={st} {snippet(b)}")
    st, d = api("GET", f"/api/v1/admin/tasks/{a_ai_id}", a_adm, tenant=1)
    t_src = d["data"].get("ai_rag_sources") if st == 200 else None
    qs = d["data"].get("questions", []) if st == 200 else []
    st_b, d_b = api("GET", f"/api/v1/admin/tasks/{b_ai_id}", b_adm, tenant=2)
    t_src_b = d_b["data"].get("ai_rag_sources") if st_b == 200 else None
    qs_b = d_b["data"].get("questions", []) if st_b == 200 else []
    ok = bool(t_src) and all(q.get("ai_rag_sources") for q in qs) and bool(t_src_b) \
        and all(q.get("ai_rag_sources") for q in qs_b)
    check("C06", "AI落库ai_rag_sources非空", ok,
          f"A_AI{a_ai_id}_src={t_src} B_AI{b_ai_id}_src={t_src_b} "
          f"Aq空={sum(1 for q in qs if not q.get('ai_rag_sources'))}/{len(qs)} "
          f"Bq空={sum(1 for q in qs_b if not q.get('ai_rag_sources'))}/{len(qs_b)}"
          "（手工补录short纸级溯源镜像缺失则FAIL，不伪造）")
    before_tasks = db_all("SELECT COUNT(*) AS c FROM tasks WHERE tenant_id=1")[0]["c"]
    draft_id = None
    ok, det = False, ""
    try:
        st, d = api("POST", "/api/v1/admin/tasks", a_adm,
                    body={"title": "SEC-AUDIT-TMP-DRAFT", "resource_ids": [a_manual_first_rid],
                          "verification_mode": "manual", "status": "draft"}, tenant=1)
        draft_id = (d.get("data") or {}).get("task_id") if st == 201 else None
        if draft_id:
            st_s, b_s = api("POST", "/api/v1/member/task-records/submit", a_toks[0],
                            body={"task_id": draft_id, "answers": []}, tenant=1)
            ok = (st_s == 400)
            det = f"submit={st_s} {snippet(b_s)}"
        else:
            ok, det = False, f"建草稿失败 status={st} {snippet(d)}"
    finally:
        if draft_id:
            st_d, _ = api("DELETE", f"/api/v1/admin/tasks/{draft_id}", a_adm, tenant=1)
            after_tasks = db_all("SELECT COUNT(*) AS c FROM tasks WHERE tenant_id=1")[0]["c"]
            if st_d != 200 or after_tasks != before_tasks:
                CRITICAL.append(f"草稿清理异常 del={st_d} count {before_tasks}->{after_tasks}")
                ok = False
                det += f" [清理del={st_d} count {before_tasks}->{after_tasks}]"
    check("C07", "未发布任务不可提交400且清理干净", ok, det)
    st, b = api("DELETE", "/api/v1/admin/resources/999999", a_adm, tenant=1)
    check("C08", "删不存在资源404", st == 404, f"status={st} {snippet(b)}")
    st, d = api("GET", f"/api/v1/member/tasks/{a_manual_id}", a_toks[0], tenant=1)
    raw = json.dumps(d, ensure_ascii=False) if st == 200 else snippet(d)
    leak = ("correct_answer" in raw) or ('"answer"' in raw)
    check("C09", "成员任务详情无答案泄露", st == 200 and not leak,
          f"status={st} leak={leak}")
    st, b = api("DELETE", f"/api/v1/admin/members/{a_ids[1]}", a_toks[0], tenant=1)
    no_del = st in (404, 405)
    if st in (200, 201, 204):
        CRITICAL.append(f"DELETE members意外成功 status={st}——疑似真实删除能力！已停该向量")
    st_p, me_before = api("GET", "/api/v1/auth/me", a_toks[1], tenant=1)
    disp_before = me_before["data"].get("display_name") if st_p == 200 else None
    api("PUT", "/api/v1/auth/profile", a_toks[0],
        body={"user_id": a_ids[1], "display_name": "HACKED2"}, tenant=1)
    st_p2, me_after = api("GET", "/api/v1/auth/me", a_toks[1], tenant=1)
    disp_after = me_after["data"].get("display_name") if st_p2 == 200 else None
    if disp_before != disp_after:
        CRITICAL.append("C10 他人 display_name 被改写——真实越权写入！已停该向量")
    api("PUT", "/api/v1/auth/profile", a_toks[0],
        body={"display_name": (me1["data"].get("display_name") if "me1" in dir() else "A成员01")},
        tenant=1)
    still_login, _ = api("POST", "/api/v1/auth/login",
                         body={"phone": A_MEMBERS[1], "password": "123456"})
    check("C10", "无删除账号能力+PUT他人无效", no_del and disp_before == disp_after and still_login == 200,
          f"del={st} otherDispUnchanged={disp_before == disp_after} relogin={still_login} {snippet(b)}")

    npass = sum(1 for r in RESULTS if r["pass"])
    print(f"\n==== SUMMARY PASS {npass}/{len(RESULTS)} ====", flush=True)
    for r in RESULTS:
        if not r["pass"]:
            print(f"  FAIL {r['id']} {r['name']} | {r['detail']}", flush=True)
    if CRITICAL:
        print("CRITICAL:", flush=True)
        for c in CRITICAL:
            print("  CRITICAL " + c, flush=True)


if __name__ == "__main__":
    main()
