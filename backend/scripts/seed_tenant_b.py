# -*- coding: utf-8 -*-
"""Agent B: B公司(tenant_id=2)造数脚本 —— 只写租户2,绝不碰租户1.

流程(全部经 API,除 AI 对话经直连 SQLite 落库):
1. 经 API 录入 5 成员 13900000006~13900000010(默认密码123456),
   并用 random.seed(20260910) 为 B管理员+5成员生成逼真资料,经 PUT /auth/profile 写入.
2. 手动卷:建 5 道条目(第5道固定 type=short),组卷 publish(verification_mode=manual).
3. AI 卷:调 AI 生成 topic=近代历史常识 count=4,若 short 不足则补 1 道 short,组卷 publish.
4. 5 成员每人交 2 卷=10 条记录,控制恰好 7 通过 / 3 不通过,manual 卷经 confirm 定终态 verified.
5. Copilot 会话:直连 SQLite 插 ai_sessions/ai_messages(B管理员 1 会话 2 消息,tenant_id=2).
"""
import json
import random
import sqlite3
import time
import urllib.request
import urllib.error
import os

BASE = "http://127.0.0.1:8123"
V1 = BASE + "/api/v1"
TENANT = 2
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mock_acceptance.db")

ADMIN_PHONE = "13800000012"
ADMIN_PW = "123456"
MEMBER_PHONES = ["13900000006", "13900000007", "13900000008", "13900000009", "13900000010"]
MEMBER_PW = "123456"
MEMBER_NAMES = ["陈静", "林伟", "黄芳", "周磊", "吴敏"]

MANUAL_TITLE = "B公司·行政与合规手册测评(手动卷)"
AI_TITLE = "B公司·近代历史常识测评(AI卷)"


def api(method, path, token=None, tenant=None, body=None, query=""):
    url = V1 + path + query
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if tenant is not None:
        headers["X-Tenant-ID"] = str(tenant)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"code": e.code, "message": str(e)}


def login(phone, pw):
    st, r = api("POST", "/auth/login", body={"phone": phone, "password": pw})
    assert st == 200 and r.get("code") == 200, f"login {phone} failed: {st} {r}"
    return r["data"]["token"], r["data"]["user"]["id"]


def main():
    random.seed(20260910)
    admin_tok, admin_uid = login(ADMIN_PHONE, ADMIN_PW)
    assert admin_uid, "admin uid missing"
    H2 = {"tok": admin_tok}

    # ---- 1. 录入 5 成员(静默建号,幂等 UPSERT) ----
    member_uids = {}
    for phone, name in zip(MEMBER_PHONES, MEMBER_NAMES):
        st, r = api("POST", "/admin/members", token=admin_tok, tenant=TENANT,
                    body={"phone": phone, "name": name, "role": "member"})
        assert st in (200, 201), f"create member {phone} failed: {st} {r}"
        member_uids[phone] = r["data"]["user_id"]
    print(f"PASS members=5 phones={','.join(MEMBER_PHONES)}")

    # ---- 1b. 逼真资料 random.seed(20260910),经 PUT /auth/profile 写入 ----
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
    accounts = [(ADMIN_PHONE, ADMIN_PW, "B管理员")] + [
        (p, MEMBER_PW, n) for p, n in zip(MEMBER_PHONES, MEMBER_NAMES)]
    profiles = []
    for phone, pw, _ in accounts:
        tok, _ = login(phone, pw)
        nickname = random.choice(surnames) + random.choice(givens)
        email = f"{random.choice(ens)}{random.randint(10, 99)}@b-corp.cn"
        age = random.randint(22, 45)
        gender = random.choices(["male", "female", "secret"], weights=[45, 45, 10])[0]
        occupation = random.choice(occupations)
        bio = random.choice(bio_tpls).format(nickname=nickname, occupation=occupation)
        st, r = api("PUT", "/auth/profile", token=tok, body={
            "display_name": nickname, "nickname": nickname, "email": email,
            "occupation": occupation, "bio": bio, "age": age, "gender": gender})
        assert st == 200, f"profile {phone} failed: {st} {r}"
        profiles.append((phone, nickname, email, age, gender, occupation))
    print("PASS profiles=6 seed=20260910 "
          + ";".join(f"{p}/{n}/{a}岁/{g}/{o}" for p, n, e, a, g, o in profiles))

    # ---- 2. 手动卷:5 道条目(第5道固定 short) ----
    manual_qs = [
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
    st, r = api("GET", "/admin/resources", token=admin_tok, tenant=TENANT,
                query="?page=1&size=200")
    assert st == 200, f"list resources failed: {st} {r}"
    existing = {it["content"]: it for it in r["data"]["items"]}
    manual_ids = []
    for q in manual_qs:
        if q["content"] in existing:
            manual_ids.append(existing[q["content"]]["id"])
        else:
            st2, r2 = api("POST", "/admin/resources", token=admin_tok, tenant=TENANT, body=q)
            assert st2 in (200, 201), f"create resource failed: {st2} {r2}"
            manual_ids.append(r2["data"]["id"])
    assert len(manual_ids) == 5
    manual_task_id = _ensure_task(admin_tok, MANUAL_TITLE, manual_ids, "manual")
    st, r = api("GET", f"/admin/tasks/{manual_task_id}", token=admin_tok, tenant=TENANT)
    mq = r["data"]["questions"]
    mshort = sum(1 for q in mq if q["type"] == "short")
    print(f"PASS manual_task={manual_task_id} questions={len(mq)} short={mshort} "
          f"short_ratio={mshort}/{len(mq)}")

    # ---- 3. AI 卷:generate topic=近代历史常识 count=4,不足 short 则补 ----
    # 若 AI 卷已存在(幂等重跑)则直接复用,不再重复生成
    ai_task_id = _find_task(admin_tok, AI_TITLE)
    if ai_task_id is not None:
        st, r = api("GET", f"/admin/tasks/{ai_task_id}", token=admin_tok, tenant=TENANT)
        aq = r["data"]["questions"]
        ai_qids = [q["id"] for q in aq]
        print(f"PASS ai_task_reuse={ai_task_id} questions={len(aq)}")
    else:
        # 复用上次运行遗留的孤儿 AI 资源(未挂载到任何任务),避免重复调用堆积
        st, r = api("GET", "/admin/resources", token=admin_tok, tenant=TENANT,
                    query="?page=1&size=200")
        st2, r2 = api("GET", f"/admin/tasks/{manual_task_id}", token=admin_tok,
                      tenant=TENANT)
        linked = {q["id"] for q in r2["data"]["questions"]}
        orphans = [it for it in r["data"]["items"] if it["id"] not in linked]
        o_singles = sorted(it["id"] for it in orphans if it["type"] == "single_choice")
        o_shorts = sorted(it["id"] for it in orphans if it["type"] == "short")
        if len(o_singles) >= 4 and o_shorts:
            ai_qids = o_singles[:4] + o_shorts[:1]
            print(f"PASS ai_reuse orphan_ids={ai_qids}")
            ai_task_id = _ensure_task(admin_tok, AI_TITLE, ai_qids, "manual",
                                      via_assemble=True)
        else:
            st, r = api("POST", "/admin/ai/generate-resources", token=admin_tok,
                        tenant=TENANT, body={"topic": "近代历史常识", "count": 4})
            assert st == 200, f"ai generate failed: {st} {r}"
            ai_ids = list(r["data"].get("resource_ids") or [])
            print(f"PASS ai_generate topic=近代历史常识 count=4 ids={ai_ids} msg={r.get('message')}")
            # 检查生成项中 short 是否不足(生成提示为单选,通常无 short),不足则补 1 道近代历史 short
            st, r = api("GET", "/admin/resources", token=admin_tok, tenant=TENANT,
                        query="?page=1&size=200")
            by_id = {it["id"]: it for it in r["data"]["items"]}
            gen_types = [by_id[i]["type"] for i in ai_ids if i in by_id]
            ai_qids = list(ai_ids)
            if "short" not in gen_types:
                st, r = api("POST", "/admin/resources", token=admin_tok, tenant=TENANT, body={
                    "type": "short", "content": "【B·历史】请简述洋务运动的主要内容及其历史作用(80字以上)。",
                    "options": [],
                    "correct_answer": ["参考要点:19世纪60-90年代,主张师夷长技以制夷,创办军事/民用工业、兴办新式教育、派遣留学生;客观上刺激中国资本主义发展,但未改变半殖民地半封建命运。"],
                    "score": 10})
                assert st in (200, 201), f"补 short 失败: {st} {r}"
                ai_qids.append(r["data"]["id"])
                print(f"PASS ai_short补录 id={r['data']['id']}")
            assert len(ai_qids) == 5, f"AI 卷题数异常: {ai_qids}"
            ai_task_id = _ensure_task(admin_tok, AI_TITLE, ai_qids, "manual", via_assemble=True)
    st, r = api("GET", f"/admin/tasks/{ai_task_id}", token=admin_tok, tenant=TENANT)
    aq = r["data"]["questions"]
    ashort = sum(1 for q in aq if q["type"] == "short")
    print(f"PASS ai_task={ai_task_id} questions={len(aq)} short={ashort} "
          f"short_ratio={ashort}/{len(aq)}")

    # ---- 4. 提交:5 人 × 2 卷=10 记录,恰好 7 通过 / 3 不通过 ----
    # 取两卷正确答案(管理员视角含 correct_answer)
    st, r = api("GET", f"/admin/tasks/{manual_task_id}", token=admin_tok, tenant=TENANT)
    mqs = r["data"]["questions"]
    st, r = api("GET", f"/admin/tasks/{ai_task_id}", token=admin_tok, tenant=TENANT)
    aqs = r["data"]["questions"]

    def correct_ans(q):
        ca = q.get("correct_answer") or q.get("answer") or []
        return ca

    def pass_answers(qs):
        out = []
        for q in qs:
            ca = correct_ans(q)
            t = q["type"]
            if t == "single_choice":
                out.append({"resource_id": q["id"], "answer": ca[0] if ca else "A"})
            elif t == "multiple":
                out.append({"resource_id": q["id"], "answer": ca if ca else ["A"]})
            else:
                out.append({"resource_id": q["id"],
                            "answer": ca[0] if ca else "参考作答:合规经营,客户第一。"})
        return out

    def fail_answers(qs):
        out = []
        for q in qs:
            t = q["type"]
            ca = correct_ans(q)
            if t == "single_choice":
                wrong = "D"
                if ca and ca[0] == "D":
                    wrong = "B"
                out.append({"resource_id": q["id"], "answer": wrong})
            elif t == "multiple":
                out.append({"resource_id": q["id"], "answer": ["B"]})
            elif t == "fill":
                out.append({"resource_id": q["id"], "answer": "不知道"})
            else:
                out.append({"resource_id": q["id"], "answer": "随便写写,不会。"})
        return out

    m_total = sum(q.get("score") or 10 for q in mqs)
    a_total = sum(q.get("score") or 10 for q in aqs)
    # 计划:每人交 2 卷;不通过 3 条 = (B3-AI, B4-手动, B5-手动)
    FAIL = {(MEMBER_PHONES[2], ai_task_id), (MEMBER_PHONES[3], manual_task_id),
            (MEMBER_PHONES[4], manual_task_id)}
    member_toks = {}
    for p in MEMBER_PHONES:
        tok, _ = login(p, MEMBER_PW)
        member_toks[p] = tok
    n_pass = n_fail = 0
    for phone in MEMBER_PHONES:
        mtok = member_toks[phone]
        for tid, qs, total in ((manual_task_id, mqs, m_total), (ai_task_id, aqs, a_total)):
            ok = (phone, tid) not in FAIL
            answers = pass_answers(qs) if ok else fail_answers(qs)
            st, r = api("POST", "/member/task-records/submit", token=mtok,
                        tenant=TENANT,
                        body={"task_id": tid, "time_spent": 120, "answers": answers})
            if st != 200:
                # 幂等重跑:已提交则继续走 confirm 纠正分数
                assert "重复" in str(r), f"submit {phone}/{tid} failed: {st} {r}"
            # 查 record_id(成员视角)
            st2, r2 = api("GET", "/member/task-records", token=mtok, tenant=TENANT)
            assert st2 == 200, f"my records failed: {st2} {r2}"
            rid = next(it["record_id"] for it in r2["data"]["items"] if it["task_id"] == tid)
            final = total if ok else 12
            st3, r3 = api("POST", f"/admin/verifications/{rid}/confirm",
                          token=admin_tok, tenant=TENANT,
                          body={"final_score": final,
                                "comments": "B公司核验:达标" if ok else "B公司核验:客观题多错,需重学"})
            assert st3 == 200, f"confirm {rid} failed: {st3} {r3}"
            if ok:
                n_pass += 1
            else:
                n_fail += 1
    assert (n_pass, n_fail) == (7, 3), f"通过/不通过数量异常: {n_pass}/{n_fail}"
    print(f"PASS records=10 pass=7 fail=3 manual_total={m_total} ai_total={a_total}")

    # ---- 5. Copilot 会话:直连 SQLite 落 ai_sessions/ai_messages(tenant_id=2) ----
    _seed_ai_session(admin_uid)
    print("PASS ai_session=1 ai_messages=2 tenant=2")


def _find_task(admin_tok, title):
    st, r = api("GET", "/admin/tasks", token=admin_tok, tenant=TENANT,
                query="?page=1&size=50")
    assert st == 200, f"list tasks failed: {st} {r}"
    for it in r["data"]["items"]:
        if it["title"] == title:
            return it["id"]
    return None


def _ensure_task(admin_tok, title, rids, mode, via_assemble=False):
    tid = _find_task(admin_tok, title)
    if tid is not None:
        api("PUT", f"/admin/tasks/{tid}/status", token=admin_tok,
            tenant=TENANT, query="?status=published")
        return tid
    if via_assemble:
        st, r = api("POST", "/admin/ai/assemble-task", token=admin_tok,
                    tenant=TENANT,
                    body={"title": title, "resource_ids": rids, "verification_mode": mode})
        assert st in (200, 201), f"assemble task failed: {st} {r}"
        tid = r["data"]["task_id"]
    else:
        st, r = api("POST", "/admin/tasks", token=admin_tok, tenant=TENANT,
                    body={"title": title, "description": "B公司测评", "verification_mode": mode,
                          "resource_ids": rids})
        assert st in (200, 201), f"create task failed: {st} {r}"
        tid = r["data"]["task_id"]
    st, r = api("PUT", f"/admin/tasks/{tid}/status", token=admin_tok,
                tenant=TENANT, query="?status=published")
    assert st == 200, f"publish task {tid} failed: {st} {r}"
    return tid


def _seed_ai_session(admin_uid):
    q = "请给我出一道近代历史题目,我想练习一下近代历史常识。"
    a = ("题目:虎门销烟发生在哪一年?主持者是谁? "
         "A.1839年,林则徐 B.1840年,琦善 C.1894年,李鸿章 D.1900年,荣禄。"
         "答案:A。解析:1839年6月,林则徐在广东虎门海滩当众销毁收缴的鸦片,"
         "展示了中华民族反抗外来侵略的坚定决心,是中国近代史的重要开端事件之一。")
    for attempt in range(6):
        try:
            con = sqlite3.connect(DB_PATH, timeout=30)
            try:
                con.execute("PRAGMA busy_timeout=30000")
                cur = con.cursor()
                cur.execute("DELETE FROM ai_messages WHERE tenant_id=2 AND session_id IN "
                            "(SELECT id FROM ai_sessions WHERE tenant_id=2 AND user_id=?)",
                            (admin_uid,))
                cur.execute("DELETE FROM ai_sessions WHERE tenant_id=2 AND user_id=?",
                            (admin_uid,))
                cur.execute("INSERT INTO ai_sessions(tenant_id,user_id,title,created_at) "
                            "VALUES(2,?, '近代历史题目咨询', datetime('now','localtime'))",
                            (admin_uid,))
                sid = cur.lastrowid
                cur.execute("INSERT INTO ai_messages(tenant_id,session_id,role,content,"
                            "rag_sources,created_at) VALUES(2,?,'user',?,'[]',"
                            "datetime('now','localtime'))", (sid, q))
                cur.execute("INSERT INTO ai_messages(tenant_id,session_id,role,content,"
                            "rag_sources,created_at) VALUES(2,?,'assistant',?,'[]',"
                            "datetime('now','localtime'))", (sid, a))
                con.commit()
                cur.execute("SELECT COUNT(*) FROM ai_sessions WHERE tenant_id=2 AND user_id=?",
                            (admin_uid,))
                assert cur.fetchone()[0] == 1
                cur.execute("SELECT COUNT(*) FROM ai_messages WHERE tenant_id=2 AND session_id=?",
                            (sid,))
                assert cur.fetchone()[0] == 2
                return
            finally:
                con.close()
        except sqlite3.OperationalError as e:
            if "locked" in str(e) and attempt < 5:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise
    raise RuntimeError("sqlite database is locked,重试仍失败")


if __name__ == "__main__":
    main()
