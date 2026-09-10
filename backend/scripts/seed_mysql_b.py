# -*- coding: utf-8 -*-
"""Agent B: B公司(tenant_id=2) MySQL 造数脚本 —— 只写租户2,绝不碰租户1.

地基: 全新 MySQL 空库 tiku_db, API 一律走 nginx 网关 http://localhost.
流程(全部经 API,除 Copilot 会话直连 MySQL 落库):
1. 经 POST /admin/members 录入 5 成员 13900000006~13900000010(默认密码123456),
   并用 random.seed(20260910) 生成逼真资料,经 PUT /auth/profile 写入.
2. 手动卷:建 5 道条目(第5道固定 type=short),组卷 publish(verification_mode=manual).
3. AI 卷:POST /admin/ai/generate-resources topic=近代历史常识 count=4,
   空 options/correct 兜底稿做人工补齐;若 short 不足则补 1 道近代史 short,组卷 publish.
4. 5 成员每人交 2 卷=10 条记录(先 GET /member/tasks/{id}/entry 锁定开考,再 submit),
   控制恰好 7 通过 / 3 不通过;manual 卷逐条 confirm 定终态 verified(全部 confirm).
5. Copilot:直连 MySQL(ai_sessions/ai_messages,短事务+重试)插 B管理员 1 会话 2 条,强制 tenant_id=2.
幂等:任务/资源按 title/content 复用;提交遇"重复"则回读 record 再 confirm 纠分.
"""
import json
import random
import time
import urllib.request
import urllib.error

try:
    import pymysql
except ImportError:
    pymysql = None

BASE = "http://127.0.0.1"  # 即 nginx 网关 :80(与 http://localhost 同一网关;本机 localhost 先解析 ::1 回退慢 21s,故用字面 IPv4)
V1 = BASE + "/api/v1"
TENANT = 2

MYSQL = dict(host="127.0.0.1", port=3306, user="root", password="rootpassword",
             database="tiku_db", charset="utf8mb4", autocommit=False)

ADMIN_PHONE = "13800000012"
ADMIN_PW = "123456"
MEMBER_PHONES = ["13900000006", "13900000007", "13900000008", "13900000009", "13900000010"]
MEMBER_PW = "123456"
MEMBER_NAMES = ["陈静", "林伟", "黄芳", "周磊", "吴敏"]

MANUAL_TITLE = "B公司·行政与合规手册测评(手动卷)"
AI_TITLE = "B公司·近代历史常识测评(AI卷)"


def api(method, path, token=None, tenant=None, body=None, query=""):
    url = V1 + path + query
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    if tenant is not None:
        req.add_header("X-Tenant-ID", str(tenant))
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"code": e.code, "message": str(e)}


def login(phone, pw):
    st, r = api("POST", "/auth/login", body={"phone": phone, "password": pw})
    assert st == 200 and r.get("code") == 200, f"login {phone} failed: {st} {r}"
    return r["data"]["token"], r["data"]["user"]["id"]


# ---------------- 1. 成员 + 资料 ----------------
def step_members(admin_tok):
    for phone, name in zip(MEMBER_PHONES, MEMBER_NAMES):
        st, r = api("POST", "/admin/members", token=admin_tok, tenant=TENANT,
                    body={"phone": phone, "name": name, "role": "member"})
        # 任务约定:HTTP 200 即成功(包络 code 201);容忍 201
        assert st in (200, 201), f"create member {phone} failed: {st} {r}"
    print(f"PASS members=5 phones={','.join(MEMBER_PHONES)}", flush=True)


def step_profiles():
    random.seed(20260910)
    surnames = ["陈", "林", "黄", "周", "吴", "郑", "王", "李"]
    givens = ["静", "伟", "芳", "磊", "敏", "涛", "雪", "超", "琳", "浩", "燕", "杰"]
    ens = ["chenjing", "linwei", "huangfang", "zhoulei", "wumin", "zhengtao",
           "wangxue", "lichao", "liulin", "zhaohao", "zhouyan", "wujie"]
    occupations = ["产品经理", "软件工程师", "运营专员", "财务会计",
                   "市场营销", "人事专员", "客服代表", "数据分析师"]
    bio_tpls = [
        "{nickname}是B公司{occupation},热爱学习,坚持每周复盘,座右铭是日拱一卒。",
        "B公司{occupation}{nickname},注重细节与效率,业余喜欢阅读近代史与长跑。",
        "{nickname},现任B公司{occupation},擅长跨部门协作,相信把小事做到极致。",
        "作为B公司{occupation},{nickname}坚持客户第一,目标是每年掌握一项新技能。",
    ]
    accounts = [(ADMIN_PHONE, ADMIN_PW)] + [(p, MEMBER_PW) for p in MEMBER_PHONES]
    profiles = {}
    for phone, pw in accounts:
        tok, _ = login(phone, pw)
        nickname = random.choice(surnames) + random.choice(givens)
        email = f"{random.choice(ens)}{random.randint(10, 99)}@b-corp.cn"
        age = random.randint(22, 45)
        gender = random.choices(["male", "female", "secret"], weights=[45, 45, 10])[0]
        occupation = random.choice(occupations)
        bio = random.choice(bio_tpls).format(nickname=nickname, occupation=occupation)
        st, r = api("PUT", "/auth/profile", token=tok, body={
            "display_name": nickname, "nickname": nickname, "email": email,
            "occupation": occupation, "bio": bio, "age": age, "gender": gender,
            "phone": phone})
        assert st == 200, f"profile {phone} failed: {st} {r}"
        profiles[phone] = {"nickname": nickname, "email": email, "age": age,
                           "gender": gender, "occupation": occupation, "bio": bio}
    print("PASS profiles=6 seed=20260910 " + ";".join(
        f"{p}/{v['nickname']}/{v['age']}岁/{v['gender']}/{v['occupation']}" for p, v in profiles.items()),
        flush=True)
    return profiles


# ---------------- 2/3. 资源与组卷 ----------------
MANUAL_QS = [
    {"type": "single_choice", "content": "【B】B公司弹性工作制规定核心在岗时间是以下哪一项?",
     "options": [{"key": "A", "text": "10:00-16:00"}, {"key": "B", "text": "09:00-18:00全程在岗"},
                 {"key": "C", "text": "任意时间均可"}, {"key": "D", "text": "仅周末在岗"}],
     "correct_answer": ["A"], "score": 10},
    {"type": "single_choice", "content": "【B】B公司差旅住宿标准中,一线城市每晚报销上限是?",
     "options": [{"key": "A", "text": "300元"}, {"key": "B", "text": "500元"},
                 {"key": "C", "text": "800元"}, {"key": "D", "text": "实报实销"}],
     "correct_answer": ["C"], "score": 10},
    {"type": "multiple", "content": "【B】根据B公司信息安全规范,以下哪些属于禁止行为?",
     "options": [{"key": "A", "text": "将客户数据发送到个人邮箱"},
                 {"key": "B", "text": "使用公司VPN访问内网"},
                 {"key": "C", "text": "在公共场合谈论未发布产品细节"},
                 {"key": "D", "text": "使用统一身份认证登录"}],
     "correct_answer": ["A", "C"], "score": 10},
    {"type": "fill", "content": "【B】B公司客户服务热线是____(请填写完整号码)。",
     "options": [], "correct_answer": ["400-800-2012"], "score": 10},
    {"type": "short", "content": "【B】B公司价值观强调“客户第一”,请结合你的岗位简述如何在日常工作中践行(50字以上)。",
     "options": [], "correct_answer": ["参考要点:主动倾听客户需求、承诺响应时效、记录反馈闭环、跨部门协同解决客户问题。"],
     "score": 10},
]

AI_PATCH = [
    {"content": "【B·历史】虎门销烟发生在哪一年?主持者是谁?",
     "options": [{"key": "A", "text": "1839年,林则徐"}, {"key": "B", "text": "1840年,琦善"},
                 {"key": "C", "text": "1894年,李鸿章"}, {"key": "D", "text": "1900年,荣禄"}],
     "correct_answer": ["A"]},
    {"content": "【B·历史】洋务运动前期提出的口号是什么?",
     "options": [{"key": "A", "text": "师夷长技以制夷"}, {"key": "B", "text": "自强"},
                 {"key": "C", "text": "求富"}, {"key": "D", "text": "维新变法"}],
     "correct_answer": ["B"]},
    {"content": "【B·历史】辛亥革命武昌起义爆发于哪一年?",
     "options": [{"key": "A", "text": "1898年"}, {"key": "B", "text": "1905年"},
                 {"key": "C", "text": "1911年"}, {"key": "D", "text": "1919年"}],
     "correct_answer": ["C"]},
    {"content": "【B·历史】五四运动爆发的直接导火索是什么?",
     "options": [{"key": "A", "text": "巴黎和会上中国外交失败"}, {"key": "B", "text": "虎门销烟"},
                 {"key": "C", "text": "甲午海战"}, {"key": "D", "text": "八国联军侵华"}],
     "correct_answer": ["A"]},
]
AI_SHORT = {"type": "short", "content": "【B·历史】请简述洋务运动的主要内容及其历史作用(80字以上)。",
            "options": [],
            "correct_answer": ["参考要点:19世纪60-90年代,主张师夷长技以制夷,创办军事/民用工业、兴办新式教育、派遣留学生;客观上刺激中国资本主义发展,但未改变半殖民地半封建命运。"],
            "score": 10}


def _find_task(admin_tok, title):
    st, r = api("GET", "/admin/tasks", token=admin_tok, tenant=TENANT,
                query="?page=1&size=100")
    assert st == 200, f"list tasks failed: {st} {r}"
    for it in r["data"]["items"]:
        if it["title"] == title:
            return it["id"]
    return None


def _ensure_task(admin_tok, title, rids, mode, via_assemble=False):
    tid = _find_task(admin_tok, title)
    if tid is not None:
        st, r = api("PUT", f"/admin/tasks/{tid}/status", token=admin_tok,
                    tenant=TENANT, query="?status=published")
        assert st == 200, f"publish reuse {tid} failed: {st} {r}"
        return tid
    if via_assemble:
        st, r = api("POST", "/admin/ai/assemble-task", token=admin_tok,
                    tenant=TENANT,
                    body={"title": title, "description": "B公司AI组卷:近代历史常识",
                          "resource_ids": rids, "verification_mode": mode})
        assert st in (200, 201), f"assemble task failed: {st} {r}"
        tid = r["data"]["task_id"]
    else:
        st, r = api("POST", "/admin/tasks", token=admin_tok, tenant=TENANT,
                    body={"title": title, "description": "B公司测评",
                          "verification_mode": mode, "resource_ids": rids})
        assert st in (200, 201), f"create task failed: {st} {r}"
        tid = r["data"]["task_id"]
    st, r = api("PUT", f"/admin/tasks/{tid}/status", token=admin_tok,
                tenant=TENANT, query="?status=published")
    assert st == 200, f"publish task {tid} failed: {st} {r}"
    return tid


def _list_resources(admin_tok, size=200):
    st, r = api("GET", "/admin/resources", token=admin_tok, tenant=TENANT,
                query=f"?page=1&size={size}")
    assert st == 200, f"list resources failed: {st} {r}"
    return r["data"]["items"]


def step_manual(admin_tok):
    existing = {it["content"]: it for it in _list_resources(admin_tok)}
    manual_ids = []
    for q in MANUAL_QS:
        if q["content"] in existing:
            manual_ids.append(existing[q["content"]]["id"])
        else:
            st, r = api("POST", "/admin/resources", token=admin_tok,
                        tenant=TENANT, body=q)
            assert st in (200, 201), f"create resource failed: {st} {r}"
            manual_ids.append(r["data"]["id"])
    assert len(manual_ids) == 5
    tid = _ensure_task(admin_tok, MANUAL_TITLE, manual_ids, "manual")
    st, r = api("GET", f"/admin/tasks/{tid}", token=admin_tok, tenant=TENANT)
    assert st == 200, f"task detail {tid} failed: {st} {r}"
    qs = r["data"]["questions"]
    n_short = sum(1 for q in qs if q["type"] == "short")
    print(f"PASS manual_task={tid} questions={len(qs)} short={n_short} "
          f"short_ratio={n_short}/{len(qs)}", flush=True)
    return tid


def step_ai(admin_tok):
    tid = _find_task(admin_tok, AI_TITLE)
    if tid is not None:
        st, r = api("GET", f"/admin/tasks/{tid}", token=admin_tok, tenant=TENANT)
        assert st == 200, f"reuse ai detail failed: {st} {r}"
        qs = r["data"]["questions"]
        n_short = sum(1 for q in qs if q["type"] == "short")
        print(f"PASS ai_task_reuse={tid} questions={len(qs)} short={n_short} "
              f"short_ratio={n_short}/{len(qs)}", flush=True)
        return tid
    st, r = api("POST", "/admin/ai/generate-resources", token=admin_tok,
                tenant=TENANT, body={"topic": "近代历史常识", "count": 4})
    assert st == 200, f"ai generate failed: {st} {r}"
    gen_ids = list(r["data"].get("resource_ids") or [])
    assert len(gen_ids) >= 4, f"ai ids异常: {gen_ids}"
    print(f"PASS ai_generate topic=近代历史常识 count=4 ids={gen_ids} msg={r.get('message')}", flush=True)
    by_id = {it["id"]: it for it in _list_resources(admin_tok)}
    patched = 0
    for i, rid in enumerate(gen_ids):
        it = by_id.get(rid, {})
        if not it.get("options") or not (it.get("correct_answer") or it.get("answer")):
            p = AI_PATCH[i % len(AI_PATCH)]
            st2, r2 = api("PUT", f"/admin/resources/{rid}", token=admin_tok,
                          tenant=TENANT,
                          body={"content": p["content"], "options": p["options"],
                                "correct_answer": p["correct_answer"], "score": 10})
            assert st2 == 200, f"patch ai {rid} failed: {st2} {r2}"
            patched += 1
    by_id = {it["id"]: it for it in _list_resources(admin_tok)}
    n_short = sum(1 for rid in gen_ids if by_id.get(rid, {}).get("type") == "short")
    all_ids = list(gen_ids)
    if n_short < 1:
        st, r = api("POST", "/admin/resources", token=admin_tok, tenant=TENANT,
                    body=AI_SHORT)
        assert st in (200, 201), f"补 short 失败: {st} {r}"
        all_ids.append(r["data"]["id"])
        n_short = 1
        print(f"PASS ai_short补录 id={r['data']['id']}", flush=True)
    assert len(all_ids) == 5, f"AI 卷题数异常: {all_ids}"
    tid = _ensure_task(admin_tok, AI_TITLE, all_ids, "manual", via_assemble=True)
    st, r = api("GET", f"/admin/tasks/{tid}", token=admin_tok, tenant=TENANT)
    qs = r["data"]["questions"]
    n_short = sum(1 for q in qs if q["type"] == "short")
    print(f"PASS ai_task={tid} questions={len(qs)} short={n_short} "
          f"short_ratio={n_short}/{len(qs)} (gen=4 patched={patched} +short={len(all_ids) - len(gen_ids)})",
          flush=True)
    return tid


# ---------------- 4. 提交 + 核验 ----------------
SHORT_GOOD = ("践行客户第一:主动倾听需求并记录工单,承诺2小时内响应;重要问题建群协同,"
              "每日同步进展直至闭环;每周复盘客户反馈,把共性问题沉淀为流程改进。")
SHORT_JUNK = "随便写写,不会。"


def build_answers(questions, want_pass):
    ans = []
    for q in questions:
        rid, qtype = q["id"], q.get("type", "single_choice")
        correct = q.get("correct_answer") or q.get("answer") or []
        if qtype == "short":
            ans.append({"resource_id": rid, "answer": SHORT_GOOD if want_pass else SHORT_JUNK})
            continue
        keys = [o.get("key") for o in (q.get("options") or []) if o.get("key")]
        if want_pass:
            if qtype == "multiple":
                ans.append({"resource_id": rid, "answer": list(correct) if correct else keys[:1]})
            elif qtype == "fill":
                ans.append({"resource_id": rid, "answer": (correct[0] if correct else "400-800-2012")})
            else:
                ans.append({"resource_id": rid, "answer": (correct[0] if correct else (keys[0] if keys else "A"))})
        else:
            if qtype == "multiple":
                wrong = [k for k in keys if k not in (correct or [])]
                ans.append({"resource_id": rid, "answer": wrong[:1] if wrong else ["__WRONG__"]})
            elif qtype == "fill":
                ans.append({"resource_id": rid, "answer": "不知道"})
            else:
                wrong = next((k for k in keys if not correct or k != correct[0]), None)
                ans.append({"resource_id": rid, "answer": (wrong or "__WRONG__")})
    return ans


def my_record_id(member_tok, task_id):
    st, r = api("GET", "/member/task-records", token=member_tok, tenant=TENANT)
    assert st == 200, f"my records failed: {st} {r}"
    for it in r["data"]["items"]:
        if it["task_id"] == task_id:
            return it["record_id"]
    return None


def step_submit_verify(admin_tok, tid_manual, tid_ai):
    st, r = api("GET", f"/admin/tasks/{tid_manual}", token=admin_tok, tenant=TENANT)
    mqs = r["data"]["questions"]
    st, r = api("GET", f"/admin/tasks/{tid_ai}", token=admin_tok, tenant=TENANT)
    aqs = r["data"]["questions"]
    m_total = sum(q.get("score") or 10 for q in mqs)
    a_total = sum(q.get("score") or 10 for q in aqs)
    pass_line_m = int(m_total * 0.6)
    pass_line_a = int(a_total * 0.6)
    # 不通过 3 条 = (13900000008-AI, 13900000009-手动, 13900000010-手动)
    FAIL = {(MEMBER_PHONES[2], tid_ai), (MEMBER_PHONES[3], tid_manual),
            (MEMBER_PHONES[4], tid_manual)}
    member_toks = {}
    for p in MEMBER_PHONES:
        tok, _ = login(p, MEMBER_PW)
        member_toks[p] = tok
    results = []
    for phone in MEMBER_PHONES:
        mtok = member_toks[phone]
        for tid, qs, total, pline in ((tid_manual, mqs, m_total, pass_line_m),
                                      (tid_ai, aqs, a_total, pass_line_a)):
            ok = (phone, tid) not in FAIL
            try:
                api("GET", f"/member/tasks/{tid}/entry", token=mtok, tenant=TENANT)
            except Exception:
                pass
            st, r = api("POST", "/member/task-records/submit", token=mtok,
                        tenant=TENANT,
                        body={"task_id": tid, "time_spent": 120,
                              "answers": build_answers(qs, ok)})
            if st != 200:
                assert "重复" in str(r) or "不可重复" in str(r), \
                    f"submit {phone}/{tid} failed: {st} {r}"
            rid = my_record_id(mtok, tid)
            assert rid, f"record missing {phone} task={tid}"
            final = total if ok else 12
            st3, r3 = api("POST", f"/admin/verifications/{rid}/confirm",
                          token=admin_tok, tenant=TENANT,
                          body={"final_score": final,
                                "comments": "B公司核验:达标" if ok else "B公司核验:客观题多错,需重学"})
            assert st3 == 200, f"confirm {rid} failed: {st3} {r3}"
            passed = final >= pline
            assert passed == ok, f"服务端 score 判定漂移 {phone}/{tid}: final={final} pline={pline}"
            results.append({"phone": phone, "task_id": tid, "record_id": rid,
                            "score": r3["data"]["score"], "passed": passed})
    n_pass = sum(1 for x in results if x["passed"])
    n_fail = len(results) - n_pass
    assert len(results) == 10 and n_pass == 7 and n_fail == 3, results
    st, r = api("GET", "/admin/verifications/pending", token=admin_tok, tenant=TENANT)
    assert st == 200, f"pending failed: {st} {r}"
    print(f"PASS records=10 pass=7 fail=3 manual_total={m_total} ai_total={a_total} "
          f"pending_left={len(r['data']['items'])}", flush=True)
    return results


# ---------------- 5. Copilot 直写 MySQL ----------------
def mysql_conn():
    assert pymysql is not None, "缺 pymysql,请先 pip install pymysql"
    return pymysql.connect(**MYSQL)


def step_ai_session(admin_uid):
    q = "请给我出一道近代历史题目,我想练习一下近代历史常识。"
    a = ("题目:虎门销烟发生在哪一年?主持者是谁? "
         "A.1839年,林则徐 B.1840年,琦善 C.1894年,李鸿章 D.1900年,荣禄。"
         "答案:A。解析:1839年6月,林则徐在广东虎门海滩当众销毁收缴的鸦片,"
         "展示了中华民族反抗外来侵略的坚定决心,是中国近代史的重要开端事件之一。")
    last = None
    for attempt in range(8):
        con = mysql_conn()
        try:
            con.begin()
            with con.cursor() as cur:
                cur.execute("DELETE m FROM ai_messages m JOIN ai_sessions s ON s.id=m.session_id "
                            "WHERE s.tenant_id=2 AND s.user_id=%s", (admin_uid,))
                cur.execute("DELETE FROM ai_sessions WHERE tenant_id=2 AND user_id=%s", (admin_uid,))
                cur.execute("INSERT INTO ai_sessions(tenant_id,user_id,title) VALUES(2,%s,'近代历史题目咨询')",
                            (admin_uid,))
                sid = cur.lastrowid
                cur.execute("INSERT INTO ai_messages(tenant_id,session_id,role,content,rag_sources) "
                            "VALUES(2,%s,'user',%s,'[]')", (sid, q))
                cur.execute("INSERT INTO ai_messages(tenant_id,session_id,role,content,rag_sources) "
                            "VALUES(2,%s,'assistant',%s,'[]')", (sid, a))
            con.commit()
            with con.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM ai_sessions WHERE tenant_id=2 AND user_id=%s", (admin_uid,))
                assert cur.fetchone()[0] == 1
                cur.execute("SELECT COUNT(*) FROM ai_messages WHERE tenant_id=2 AND session_id=%s", (sid,))
                assert cur.fetchone()[0] == 2
            print(f"PASS ai_session=1 ai_messages=2 tenant=2 sid={sid}", flush=True)
            return sid
        except Exception as e:
            last = e
            try:
                con.rollback()
            except Exception:
                pass
            if attempt < 7:
                time.sleep(0.3 * (attempt + 1))
                continue
            raise
        finally:
            try:
                con.close()
            except Exception:
                pass
    raise RuntimeError(f"MySQL 落会话重试仍失败: {last}")


def main():
    assert TENANT == 2, "绝不碰租户1"
    admin_tok, admin_uid = login(ADMIN_PHONE, ADMIN_PW)
    step_members(admin_tok)
    profiles = step_profiles()
    tid_manual = step_manual(admin_tok)
    tid_ai = step_ai(admin_tok)
    results = step_submit_verify(admin_tok, tid_manual, tid_ai)
    sid = step_ai_session(admin_uid)
    print("ALL DONE tenant=2", flush=True)
    return {"profiles": profiles, "tasks": (tid_manual, tid_ai),
            "results": results, "sid": sid}


if __name__ == "__main__":
    main()
