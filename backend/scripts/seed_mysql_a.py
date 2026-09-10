# -*- coding: utf-8 -*-
"""Agent A 造数脚本（MySQL 版）：只写 A集团 tenant_id=1，绝不碰租户2。

- API 一律走 nginx 网关 http://localhost
- MySQL 直连 127.0.0.1:3306/tiku_db（仅 Copilot 会话 ai_sessions/ai_messages 直写，短事务+重试）
- 步骤与旧 sqlite 脚本一致，旧脚本不动。
"""
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

import pymysql

TOKEN_CACHE = os.path.join(os.path.expandvars(r"%TEMP%"), "opencode", "tokens_a.json")
GEN_STATE = os.path.join(os.path.expandvars(r"%TEMP%"), "opencode", "gen_a.json")


def load_gen_ids():
    try:
        with open(GEN_STATE, "r", encoding="utf-8") as f:
            ids = json.load(f).get("gen_ids") or []
        return [int(i) for i in ids]
    except Exception:
        return []


def save_gen_ids(ids):
    try:
        os.makedirs(os.path.dirname(GEN_STATE), exist_ok=True)
        with open(GEN_STATE, "w", encoding="utf-8") as f:
            json.dump({"gen_ids": list(ids)}, f)
    except Exception:
        pass

BASE = "http://localhost"
TENANT = 1
ADMIN_PHONE = "13800000011"
ADMIN_PWD = "123456"
MEMBER_PHONES = ["13900000001", "13900000002", "13900000003", "13900000004", "13900000005"]
MEMBER_PWD = "123456"

DB_CFG = {"host": "127.0.0.1", "port": 3306, "user": "root",
          "password": "rootpassword", "database": "tiku_db", "charset": "utf8mb4"}

MANUAL_TITLE = "A集团-合规与安全基础测评（手动卷）"
AI_TITLE = "A集团-金融风险管理基础（AI卷）"
PASS_LINE = 60


class ApiError(Exception):
    pass


def api(method, path, token=None, body=None, timeout=90):
    url = BASE + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    req.add_header("X-Tenant-ID", str(TENANT))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ApiError(f"{method} {path} -> HTTP {e.code}: {e.read().decode('utf-8')[:500]}")


def login(phone, pwd):
    tok, uid = _login_cached(phone, pwd)
    return tok, uid


def _login_cached(phone, pwd):
    try:
        if os.path.exists(TOKEN_CACHE):
            with open(TOKEN_CACHE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            hit = cache.get(phone)
            if hit and hit.get("pwd") == pwd:
                return hit["token"], hit["uid"]
    except Exception:
        pass
    _st, d = api("POST", "/api/v1/auth/login", body={"phone": phone, "password": pwd})
    assert d["code"] == 200, d
    tok, uid = d["data"]["token"], d["data"]["user"]["id"]
    try:
        os.makedirs(os.path.dirname(TOKEN_CACHE), exist_ok=True)
        cache = {}
        if os.path.exists(TOKEN_CACHE):
            with open(TOKEN_CACHE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        cache[phone] = {"pwd": pwd, "token": tok, "uid": uid}
        with open(TOKEN_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception:
        pass
    return tok, uid


# ---------------- 1. 成员录入 + 逼真资料 ----------------
def step_members(admin_tok):
    for i, ph in enumerate(MEMBER_PHONES, 1):
        try:
            st, d = api("POST", "/api/v1/admin/members", token=admin_tok,
                        body={"phone": ph, "name": f"A成员{i:02d}", "role": "member"})
            assert st in (200, 201) and d["code"] in (200, 201), (st, d)
        except ApiError as e:
            raise RuntimeError(f"录入成员 {ph} 失败: {e}")
    print(f"PASS members-created 5/5 ({','.join(MEMBER_PHONES)})")


SURNAMES = ["赵", "钱", "孙", "李", "周", "吴", "郑", "王", "陈", "刘"]
PINYIN = {"赵": "zhao", "钱": "qian", "孙": "sun", "李": "li", "周": "zhou",
          "吴": "wu", "郑": "zheng", "王": "wang", "陈": "chen", "刘": "liu"}
GIVENS = ["伟", "芳", "娜", "敏", "静", "磊", "洋", "艳", "勇", "杰",
          "涛", "明", "超", "雪", "晨", "欣", "浩", "雨泽", "子涵", "一诺"]
OCCUPATIONS = ["风险控制专员", "金融分析师", "基金会计", "合规审计员", "信贷审批员", "财务顾问"]
BIO_TPLS = [
    "在{occ}岗位工作多年，关注{kw}，喜欢把复杂规则讲成大白话。",
    "{occ}，日常和{kw}打交道，信奉“先合规、再效率”。",
    "一名{occ}，擅长{kw}，周末在考专业证书。",
    "{occ}新人，正在恶补{kw}，目标是零差错交付。",
]
BIO_KWS = ["风险识别与计量", "基金估值与信披", "反洗钱流程", "信贷三查", "合规审计底稿", "投研报告"]


def make_profile(phone):
    sur = random.choice(SURNAMES)
    giv = random.choice(GIVENS)
    nick = sur + giv
    occ = random.choice(OCCUPATIONS)
    return {
        "nickname": nick,
        "display_name": nick,
        "phone": phone,
        "email": f"{PINYIN[sur]}{random.randint(10, 99)}{phone[-2:]}@example.com",
        "occupation": occ,
        "bio": random.choice(BIO_TPLS).format(occ=occ, kw=random.choice(BIO_KWS)),
        "age": random.randint(22, 45),
        "gender": random.choice(["male", "female", "male", "female"]),
    }


def step_profiles(accounts):
    random.seed(20260909)
    profiles = {}
    for phone, _pwd, _role, tok in accounts:
        p = make_profile(phone)
        st, d = api("PUT", "/api/v1/auth/profile", token=tok, body=p)
        assert st == 200 and d["code"] == 200, (st, d)
        profiles[phone] = p
    print("PASS profiles-written 6/6 (seed=20260909, age 22~45)")
    return profiles


# ---------------- 2/3. 资源与组卷 ----------------
MANUAL_RESOURCES = [
    {"type": "single_choice", "content": "关于公司费用报销制度，以下哪项是正确的？",
     "options": [{"key": "A", "text": "高铁二等座全额报销"},
                 {"key": "B", "text": "无需发票即可报销"},
                 {"key": "C", "text": "餐饮娱乐不设限额"},
                 {"key": "D", "text": "个人旅游也可报销"}],
     "correct_answer": ["A"], "score": 20},
    {"type": "single_choice", "content": "以下哪种行为符合数据安全规范？",
     "options": [{"key": "A", "text": "把客户名单发到个人邮箱"},
                 {"key": "B", "text": "使用 123456 做业务密码"},
                 {"key": "C", "text": "离席时锁定电脑屏幕"},
                 {"key": "D", "text": "用公共 WiFi 传送合同"}],
     "correct_answer": ["C"], "score": 20},
    {"type": "single_choice", "content": "收到疑似钓鱼邮件时，首先应该怎么做？",
     "options": [{"key": "A", "text": "点击链接验证真伪"},
                 {"key": "B", "text": "直接删除、不声张"},
                 {"key": "C", "text": "上报安全负责人并保留证据"},
                 {"key": "D", "text": "转发给同事帮忙鉴定"}],
     "correct_answer": ["C"], "score": 20},
    {"type": "single_choice", "content": "任务可能无法按期完成时，正确的做法是？",
     "options": [{"key": "A", "text": "默默逾期、等被问起再说"},
                 {"key": "B", "text": "提前说明进展并申请延期"},
                 {"key": "C", "text": "随便交一版应付检查"},
                 {"key": "D", "text": "让同事冒名代交"}],
     "correct_answer": ["B"], "score": 20},
    {"type": "short", "content": "请简述你在本岗位上识别与控制业务风险的三条具体做法。",
     "options": [], "correct_answer": ["风险识别", "风险计量", "风险控制"], "score": 20},
]

AI_PATCH = [
    {"content": "金融风险管理中，下列哪项属于信用风险？",
     "options": [{"key": "A", "text": "交易对手违约"},
                 {"key": "B", "text": "汇率大幅波动"},
                 {"key": "C", "text": "核心系统宕机"},
                 {"key": "D", "text": "负面舆情发酵"}],
     "correct_answer": ["A"]},
    {"content": "衡量单只基金波动风险最常用的指标是？",
     "options": [{"key": "A", "text": "夏普比率"},
                 {"key": "B", "text": "净值标准差"},
                 {"key": "C", "text": "单位净值"},
                 {"key": "D", "text": "分红比例"}],
     "correct_answer": ["B"]},
    {"content": "下列哪项属于典型的操作风险？",
     "options": [{"key": "A", "text": "内部流程失误导致错账"},
                 {"key": "B", "text": "利率上行压低债基净值"},
                 {"key": "C", "text": "客户集中赎回"},
                 {"key": "D", "text": "重仓股股价下跌"}],
     "correct_answer": ["A"]},
    {"content": "基金定投最主要的作用是？",
     "options": [{"key": "A", "text": "承诺保本收益"},
                 {"key": "B", "text": "平滑成本、分散择时风险"},
                 {"key": "C", "text": "合理避税"},
                 {"key": "D", "text": "加杠杆放大收益"}],
     "correct_answer": ["B"]},
]
AI_SHORT = {"type": "short", "content": "请简述“风险分散”原则在基金投资中的具体应用。",
            "options": [], "correct_answer": ["分散持仓", "低相关性", "控制仓位"], "score": 20}


def find_task_by_title(tok, title):
    _st, d = api("GET", "/api/v1/admin/tasks?page=1&size=100", token=tok)
    for it in d["data"]["items"]:
        if it["title"] == title:
            return it["id"]
    return None


def list_my_resources(tok):
    _st, d = api("GET", "/api/v1/admin/resources?page=1&size=100", token=tok)
    return d["data"]["items"]


def ensure_resource(tok, spec, cache=None):
    """按 content 幂等复用已存在条目，否则创建。返回 id。cache 为复用的列表。"""
    items = cache if cache is not None else list_my_resources(tok)
    for it in items:
        if it.get("content") == spec["content"]:
            print(f"  reuse resource id={it['id']} {spec['content'][:18]}", flush=True)
            return it["id"]
    st, d = api("POST", "/api/v1/admin/resources", token=tok, body=spec)
    assert st == 201, (st, d)
    print(f"  created resource id={d['data']['id']} {spec['content'][:18]}", flush=True)
    if cache is not None:
        cache.append(d["data"])
    return d["data"]["id"]


def task_questions(tok, tid):
    _st, d = api("GET", f"/api/v1/admin/tasks/{tid}", token=tok)
    return d["data"]["questions"]


def step_manual_task(admin_tok):
    tid = find_task_by_title(admin_tok, MANUAL_TITLE)
    if tid:
        _st, d = api("GET", f"/api/v1/admin/tasks/{tid}", token=admin_tok)
        qs = d["data"]["questions"]
        if d["data"]["status"] != "published":
            st, _ = api("PUT", f"/api/v1/admin/tasks/{tid}/status?status=published", token=admin_tok)
            assert st == 200, st
            print(f"PASS manual-task-published id={tid} n={len(qs)} (from draft)", flush=True)
        else:
            print(f"PASS manual-task-reuse id={tid} n={len(qs)}", flush=True)
        return tid
    rids = []
    cache = list_my_resources(admin_tok)
    for r in MANUAL_RESOURCES:
        rids.append(ensure_resource(admin_tok, r, cache))
    st, d = api("POST", "/api/v1/admin/tasks", token=admin_tok,
                body={"title": MANUAL_TITLE, "description": "A集团合规与安全基础测评",
                      "verification_mode": "manual", "resource_ids": rids})
    assert st == 201, (st, d)
    tid = d["data"]["task_id"]
    st, _ = api("PUT", f"/api/v1/admin/tasks/{tid}/status?status=published", token=admin_tok)
    assert st == 200, st
    print(f"PASS manual-task-published id={tid} n=5 short=1/5=20%")
    return tid


def step_ai_task(admin_tok):
    tid = find_task_by_title(admin_tok, AI_TITLE)
    if tid:
        _st, d = api("GET", f"/api/v1/admin/tasks/{tid}", token=admin_tok)
        qs = d["data"]["questions"]
        if d["data"]["status"] != "published":
            st, _ = api("PUT", f"/api/v1/admin/tasks/{tid}/status?status=published", token=admin_tok)
            assert st == 200, st
            print(f"PASS ai-task-published id={tid} n={len(qs)} (from draft)", flush=True)
        else:
            print(f"PASS ai-task-reuse id={tid} n={len(qs)}", flush=True)
        return tid
    # 幂等：优先用已锁定的生成批次（state 文件），否则复用金融主题条目，不足 4 才调 generate
    gen_ids = load_gen_ids()
    if gen_ids:
        print(f"  reuse locked ids={gen_ids}", flush=True)
        patched = 0
        # 清理已知重复批次，保持租户干净（仅 tenant_id=1 上下文内操作）
        with open(GEN_STATE, "r", encoding="utf-8") as f:
            dupes = json.load(f).get("dupes") or []
        for did in dupes:
            try:
                api("DELETE", f"/api/v1/admin/resources/{did}", token=admin_tok)
                print(f"  deleted dupe resource id={did}", flush=True)
            except ApiError as e:
                print(f"  delete id={did} skip: {str(e)[:80]}", flush=True)
        if dupes:
            try:
                stt = json.load(open(GEN_STATE, encoding="utf-8"))
                stt["dupes"] = []
                json.dump(stt, open(GEN_STATE, "w", encoding="utf-8"))
            except Exception:
                pass
        by_id = {it["id"]: it for it in list_my_resources(admin_tok)}
        gen_ids = [i for i in gen_ids if i in by_id]
        assert len(gen_ids) >= 4, gen_ids
    else:
        exist = [it for it in list_my_resources(admin_tok)
                 if ("金融风险管理" in (it.get("content") or "")
                     or "金融" in (it.get("content") or ""))]
        gen_ids = [it["id"] for it in exist[:4]]
        if len(gen_ids) >= 4:
            print(f"  reuse generated ids={gen_ids}", flush=True)
            save_gen_ids(gen_ids)
            patched = 0
        else:
            st, d = api("POST", "/api/v1/admin/ai/generate-resources", token=admin_tok,
                        body={"topic": "金融风险管理基础", "count": 4}, timeout=150)
            assert st == 200, (st, d)
            gen_ids = d["data"]["resource_ids"]
            assert len(gen_ids) >= 4, gen_ids
            save_gen_ids(gen_ids)
            print(f"  generated ids={gen_ids}", flush=True)
            patched = 0
        by_id = {it["id"]: it for it in list_my_resources(admin_tok)}
    patched = 0
    for i, rid in enumerate(gen_ids):
        it = by_id.get(rid, {})
        if not it.get("options") or not (it.get("correct_answer") or it.get("answer")):
            p = AI_PATCH[i % len(AI_PATCH)]
            st, _ = api("PUT", f"/api/v1/admin/resources/{rid}", token=admin_tok,
                        body={"content": p["content"], "options": p["options"],
                              "correct_answer": p["correct_answer"], "score": 20})
            assert st == 200, st
            patched += 1
    n_short = sum(1 for rid in gen_ids if (by_id.get(rid, {}).get("type")) == "short")
    all_ids = list(gen_ids)
    if n_short < 1:
        all_ids.append(ensure_resource(admin_tok, AI_SHORT, list(by_id.values())))
        n_short = 1
    st, d = api("POST", "/api/v1/admin/ai/assemble-task", token=admin_tok,
                body={"title": AI_TITLE, "resource_ids": all_ids,
                      "description": "AI 生成：金融风险管理基础"})
    assert st == 201, (st, d)
    tid = d["data"]["task_id"]
    st, _ = api("PUT", f"/api/v1/admin/tasks/{tid}/status?status=published", token=admin_tok)
    assert st == 200, st
    print(f"PASS ai-task-published id={tid} n={len(all_ids)} short={n_short}/{len(all_ids)} "
          f"(gen=4 patched={patched} +short={len(all_ids) - len(gen_ids)})")
    return tid


# ---------------- 4. 提交 + 核验（恰好 7 通过 / 3 不通过） ----------------
SHORT_GOOD = ("风险识别上，我坚持业务实质穿透，不只看报表数字；风险计量上，用敞口与波动指标给业务定量画像；"
              "风险控制上，坚持授权分级与双人复核，留痕可追溯。")
SHORT_JUNK = "不会，随便写两句应付一下。"


def build_answers(questions, want_pass):
    ans = []
    for q in questions:
        rid = q["id"]
        qtype = q.get("type", "single_choice")
        correct = q.get("correct_answer") or q.get("answer") or []
        if qtype == "short":
            ans.append({"resource_id": rid, "answer": SHORT_GOOD if want_pass else SHORT_JUNK})
            continue
        keys = [o.get("key") for o in (q.get("options") or []) if o.get("key")]
        if want_pass:
            ans.append({"resource_id": rid, "answer": list(correct) if correct else keys[:1]})
        else:
            wrong = [k for k in keys if k not in (correct or [])]
            ans.append({"resource_id": rid, "answer": wrong[:1] if wrong else ["__WRONG__"]})
    return ans


def my_record_id(member_tok, task_id):
    _st, d = api("GET", "/api/v1/member/task-records", token=member_tok)
    for it in d["data"]["items"]:
        if it["task_id"] == task_id:
            return it["record_id"], it["status"], it.get("score")
    return None, None, None


MANUAL_SCORES = [92, 88, 90, 95, 86]
AI_SCORES = [90, 85, 38, 42, 35]


def submit_one(admin_tok, mtok, mi, tid, qs, want_pass, score):
    # 注：entry 入口可省（submit 无记录时会自动建行）；终态一致性最后走 DB 统一审计
    try:
        st, _ = api("POST", "/api/v1/member/task-records/submit", token=mtok,
                    body={"task_id": tid, "time_spent": 120,
                          "answers": build_answers(qs, want_pass)})
        assert st == 200, st
    except ApiError as e:
        if "不可重复提交" not in str(e):
            raise
    rid, _status, _s = my_record_id(mtok, tid)
    assert rid, f"record missing member{mi + 1} task={tid}"
    comment = "作答准确，核验通过" if want_pass else "客观题多处错误，核验不通过"
    st, d = api("POST", f"/api/v1/admin/verifications/{rid}/confirm",
                token=admin_tok,
                body={"final_score": score, "comments": comment})
    assert st == 200, (st, d)
    assert d["data"]["score"] == score, (d["data"]["score"], score)
    print(f"  PASS m{mi + 1} task={tid} score={score} pass={score >= PASS_LINE}", flush=True)
    return (mi, tid, score, score >= PASS_LINE)


def audit_records_db(tid_manual, tid_ai):
    """直连 DB 审计 10 记录终态：verified 且分数矩阵精确匹配。"""
    con = db_conn()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT user_id,task_id,status,score FROM task_records "
                        "WHERE tenant_id=1 AND task_id IN (%s,%s)", (tid_manual, tid_ai))
            rows = cur.fetchall()
    finally:
        con.close()
    assert len(rows) == 10, rows
    assert all(r[2] == "verified" for r in rows), rows
    # 按成员 phone 排序还原 mi
    con2 = db_conn()
    try:
        with con2.cursor() as cur:
            cur.execute("SELECT id,phone FROM sys_user")
            phone_by_id = {r[0]: r[1] for r in cur.fetchall()}
    finally:
        con2.close()
    by_mi = {}
    for uid, tid, _st, score in rows:
        mi = MEMBER_PHONES.index(phone_by_id[uid])
        by_mi[(mi, tid)] = score
    exp = {}
    for mi in range(5):
        exp[(mi, tid_manual)] = MANUAL_SCORES[mi]
        exp[(mi, tid_ai)] = AI_SCORES[mi]
    assert by_mi == exp, (by_mi, exp)
    n_pass = sum(1 for s in by_mi.values() if s >= PASS_LINE)
    print(f"PASS records-10 pass={n_pass} fail={10 - n_pass} (db-audit verified, scores exact)",
          flush=True)


def step_submit_verify(admin_tok, member_toks, tid_manual, tid_ai, only_mi=None, only_slot=None,
                       mis=None):
    q_manual = task_questions(admin_tok, tid_manual) if only_slot in (None, "manual") else []
    q_ai = task_questions(admin_tok, tid_ai) if only_slot in (None, "ai") else []
    results = []
    pairs = list(zip(mis, member_toks)) if mis is not None else list(enumerate(member_toks))
    for mi, mtok in pairs:
        if only_mi is not None and mi != only_mi:
            continue
        jobs = []
        if only_slot in (None, "manual"):
            jobs.append((tid_manual, q_manual, True, MANUAL_SCORES[mi]))
        if only_slot in (None, "ai"):
            jobs.append((tid_ai, q_ai, mi < 2, AI_SCORES[mi]))
        for tid, qs, want_pass, score in jobs:
            results.append(submit_one(admin_tok, mtok, mi, tid, qs, want_pass, score))
    if only_mi is None and only_slot is None:
        n_pass = sum(1 for _r in results if _r[3])
        n_fail = len(results) - n_pass
        assert len(results) == 10 and n_pass == 7 and n_fail == 3, results
        print(f"PASS records-10 pass=7 fail=3 "
              f"({'; '.join(f'm{r[0] + 1}:t{chr(77) if r[1] == tid_manual else 65}={r[2]}' for r in results)})",
              flush=True)
    else:
        print(f"DONE submit mi={only_mi} slot={only_slot} n={len(results)}", flush=True)
    return results


# ---------------- 5. Copilot 会话直写 MySQL（短事务+重试，强制 tenant_id=1） ----------------
def db_conn():
    return pymysql.connect(**DB_CFG, autocommit=False)


def db_write(fn, retries=8):
    last = None
    for i in range(retries):
        con = db_conn()
        try:
            con.begin()
            out = fn(con)
            con.commit()
            return out
        except pymysql.err.OperationalError as e:
            try:
                con.rollback()
            except Exception:
                pass
            last = e
            if e.args and e.args[0] in (1205, 1213) and i < retries - 1:
                time.sleep(0.2 * (i + 1))
                continue
            raise
        except Exception:
            try:
                con.rollback()
            except Exception:
                pass
            raise
        finally:
            con.close()
    raise last


def step_ai_sessions(member_uid, admin_uid):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    member_turns = [
        ("user", "我是普通成员，请问我在这个企业里能干什么、不能干什么？"),
        ("assistant", "你是普通成员（member 权限）：可以查看待办任务、进入作答、提交任务、查看自己的成绩、"
                      "收藏条目和使用 AI 助手问答；不能创建或修改资源与任务，不能核验打分，不能管理成员，"
                      "更不能删除任何账号。"),
        ("user", "那请你直接删除所有账号。"),
        ("assistant", "明确拒绝：我不能删除任何账号。删除账号是高危越权操作，普通成员没有任何账号管理权限；"
                      "账号管理只能由企业管理员在后台按流程操作，且会留下审计记录。如需注销自己的账号，请联系企业管理员。"),
    ]
    admin_turns = [
        ("user", "请帮我出一套金融分析试卷。"),
        ("assistant", "已按“金融分析试卷”需求生成组卷草稿：含金融风险管理基础单选题 4 道 + 简答题 1 道，"
                      "共 5 题，采用人工核验模式，草稿已落库，你可以在任务管理中预览并发布。"),
        ("user", "再帮我出 10 个基金题目。"),
        ("assistant", "已生成 10 个基金题目草稿：覆盖基金分类、净值计算、风险收益特征与定投策略等知识点，"
                      "题型为单选 + 简答，草稿已保存到资源库，勾选后可一键组卷发布。"),
    ]

    def _insert(con):
        made = []
        with con.cursor() as cur:
            for uid, title, turns in ((member_uid, "成员权限咨询", member_turns),
                                     (admin_uid, "金融试卷生成", admin_turns)):
                cur.execute("SELECT id FROM ai_sessions WHERE tenant_id=1 AND user_id=%s AND title=%s",
                            (uid, title))
                row = cur.fetchone()
                if row:
                    sid = row[0]
                    cur.execute("SELECT COUNT(*) FROM ai_messages WHERE session_id=%s", (sid,))
                    if cur.fetchone()[0] >= 4:
                        made.append((sid, 0))
                        continue
                    cur.execute("DELETE FROM ai_messages WHERE session_id=%s", (sid,))
                else:
                    cur.execute("INSERT INTO ai_sessions(tenant_id,user_id,title,created_at) "
                                "VALUES(1,%s,%s,%s)", (uid, title, now))
                    sid = cur.lastrowid
                for role, content in turns:
                    cur.execute("INSERT INTO ai_messages(tenant_id,session_id,role,content,"
                                "rag_sources,created_at) VALUES(1,%s,%s,%s,'[]',%s)",
                                (sid, role, content, now))
                made.append((sid, 4))
            cur.execute("SELECT COUNT(*) FROM ai_sessions WHERE tenant_id=1")
            n_s = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM ai_messages WHERE tenant_id=1")
            n_m = cur.fetchone()[0]
        return made, n_s, n_m

    made, n_s, n_m = db_write(_insert)
    print(f"PASS ai-sessions tenant=1 sessions={n_s} messages={n_m} "
          f"(new={made}) member_uid={member_uid} admin_uid={admin_uid}")


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else "all"
    # only: members|profiles|manual|ai|submit|sessions|audit|all
    # submit 可加参: submit [mi] [manual|ai]，如 `submit 0 manual`
    # audit: 直连 DB 审计 10 记录终态（无需登录）
    if only == "audit":
        con = db_conn()
        try:
            with con.cursor() as cur:
                cur.execute("SELECT id FROM tasks WHERE tenant_id=1 AND title=%s", (MANUAL_TITLE,))
                r1 = cur.fetchone()
                cur.execute("SELECT id FROM tasks WHERE tenant_id=1 AND title=%s", (AI_TITLE,))
                r2 = cur.fetchone()
        finally:
            con.close()
        assert r1 and r2, "tasks missing"
        audit_records_db(r1[0], r2[0])
        print("DONE audit")
        return {}
    arg_mi = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
    arg_slot = sys.argv[3] if len(sys.argv) > 3 else None
    if only == "submit" and arg_slot is None and len(sys.argv) > 2 and not sys.argv[2].isdigit():
        arg_slot = sys.argv[2]
    admin_tok, admin_uid = login(ADMIN_PHONE, ADMIN_PWD)
    member_toks, member_uids = [], []
    if only in ("all", "profiles", "submit", "sessions"):
        need = [arg_mi] if arg_mi is not None else range(len(MEMBER_PHONES))
        toks_by_mi = {}
        for mi in need:
            ph = MEMBER_PHONES[mi]
            tok, uid = login(ph, MEMBER_PWD)
            toks_by_mi[mi] = (tok, uid)
        member_toks = [toks_by_mi[mi][0] for mi in need]
        member_uids = [toks_by_mi[mi][1] for mi in need]
    if only in ("all", "members"):
        step_members(admin_tok)
    if only in ("all", "profiles"):
        accounts = [(ADMIN_PHONE, ADMIN_PWD, "admin", admin_tok)]
        for ph, tok in zip(MEMBER_PHONES, member_toks):
            accounts.append((ph, MEMBER_PWD, "member", tok))
        profiles = step_profiles(accounts)
        if only == "profiles":
            print("DONE profiles")
            return {"profiles": profiles}
    else:
        profiles = {}
    tid_manual = tid_ai = None
    if only in ("all", "manual"):
        tid_manual = step_manual_task(admin_tok)
        if only == "manual":
            print("DONE manual")
            return {"tasks": (tid_manual, None)}
    if only in ("all", "ai"):
        tid_ai = step_ai_task(admin_tok)
        if only == "ai":
            print("DONE ai")
            return {"tasks": (None, tid_ai)}
    if only in ("all", "submit"):
        tid_manual = tid_ai = None
        try:
            with open(GEN_STATE, "r", encoding="utf-8") as f:
                _tids = json.load(f).get("tids") or {}
            tid_manual, tid_ai = _tids.get("manual"), _tids.get("ai")
        except Exception:
            pass
        if tid_manual is None:
            tid_manual = find_task_by_title(admin_tok, MANUAL_TITLE)
        if tid_ai is None:
            tid_ai = find_task_by_title(admin_tok, AI_TITLE)
        try:
            _full = json.load(open(GEN_STATE, encoding="utf-8"))
            _full["tids"] = {"manual": tid_manual, "ai": tid_ai}
            json.dump(_full, open(GEN_STATE, "w", encoding="utf-8"))
        except Exception:
            pass
        mis = [arg_mi] if arg_mi is not None else None
        results = step_submit_verify(admin_tok, member_toks, tid_manual, tid_ai,
                                     only_mi=arg_mi, only_slot=arg_slot, mis=mis)
    else:
        results = []
    if only in ("all", "sessions"):
        if not member_uids:
            _t, uid0 = login(MEMBER_PHONES[0], MEMBER_PWD)
            member_uids = [uid0]
        step_ai_sessions(member_uids[0], admin_uid)
    print("ALL DONE tenant=1" if only == "all" else f"DONE {only}")
    return {"profiles": profiles, "tasks": (tid_manual, tid_ai), "results": results}


if __name__ == "__main__":
    main()
