"""
[变更日志]
修改时间：2026-09-06 20:30:00
AI模型：ZCode (GLM)
修改内容：[v1.3 全链路自测脚本: 注册资料/批量账号/分类/题目/AI出题/AI组卷/模拟考试(客观即时出分+半对+主观批阅+AI全托管)/昵称展示/我的测试聚合。可重复执行, 用法: python scripts/e2e_selftest.py [BASE_URL]]
"""
import json
import random
import sys
import time
from datetime import datetime

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
ADMIN_USER, ADMIN_PASS = "admin", "123456"
STAMP = datetime.now().strftime("%m%d%H%M%S")
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail else ""))
    return ok


def jp(r, expect=(200, 201)):
    """解包 ResponseModel; 失败抛异常带中文 detail"""
    if r.status_code not in expect:
        raise AssertionError(f"[{r.status_code}] {r.request.method} {r.request.url.path}: {r.text[:200]}")
    d = r.json()
    if d.get("code") not in (200, 201):
        raise AssertionError(f"code={d.get('code')}: {d.get('message')}")
    return d["data"]


def main():
    c = httpx.Client(base_url=BASE, timeout=180)
    print(f"=== 智题库 v1.3 全链路自测 | 目标: {BASE} | {datetime.now():%Y-%m-%d %H:%M:%S} ===\n")

    # ---------- 1. B端管理员登录 ----------
    print("【1】B端管理员登录与造数")
    token = jp(c.post("/api/v1/admin/auth/login", json={"username": ADMIN_USER, "password": ADMIN_PASS}))["token"]
    ah = {"Authorization": f"Bearer {token}"}
    me = jp(c.get("/api/v1/admin/auth/me", headers=ah))
    check("管理员登录", me["role"] == "super_admin", f"{me['username']} ({me['role']})")
    # 确保有 AI 额度 (出题/组卷/聊天用)
    if (me.get("daily_ai_quota") or 0) < 5:
        jp(c.post(f"/api/v1/admin/members/{me['id']}/refill", headers=ah, json={"amount": 10}))
    ai = jp(c.get("/api/v1/admin/ai/status", headers=ah))
    check("AI 服务可用", ai["available"], f"model={ai['model']}, quota={ai['quota_remaining']}")

    # ---------- 2. 新建分类 ----------
    qcat = jp(c.post("/api/v1/admin/categories", headers=ah, json={
        "name": f"自测题库分类{STAMP}", "target_type": "question", "sort_order": 1}))
    ecat = jp(c.post("/api/v1/admin/categories", headers=ah, json={
        "name": f"自测试卷分类{STAMP}", "target_type": "exam", "sort_order": 1}))
    check("新建题目/试卷分类", bool(qcat["id"] and ecat["id"]))

    # ---------- 3. 新建题目 (5 种题型) ----------
    q_single = jp(c.post("/api/v1/admin/questions", headers=ah, json={
        "type": "single", "title": "HTTP 默认端口是?", "category_id": qcat["id"], "score": 10,
        "options": [{"key": "A", "text": "80"}, {"key": "B", "text": "443"}, {"key": "C", "text": "22"}, {"key": "D", "text": "3389"}],
        "answer": ["A"], "explanation": "HTTP 80 / HTTPS 443"}))
    q_multi = jp(c.post("/api/v1/admin/questions", headers=ah, json={
        "type": "multiple", "title": "以下哪些是 HTTP 方法?", "category_id": qcat["id"], "score": 10,
        "options": [{"key": "A", "text": "GET"}, {"key": "B", "text": "POST"}, {"key": "C", "text": "SEND"}, {"key": "D", "text": "DELETE"}],
        "answer": ["A", "B", "D"], "explanation": "SEND 不是 HTTP 方法"}))
    q_judge = jp(c.post("/api/v1/admin/questions", headers=ah, json={
        "type": "judge", "title": "HTTPS 的默认端口是 443。", "category_id": qcat["id"], "score": 10,
        "options": [{"key": "A", "text": "正确"}, {"key": "B", "text": "错误"}],
        "answer": ["A"], "explanation": "HTTPS 默认 443"}))
    q_fill = jp(c.post("/api/v1/admin/questions", headers=ah, json={
        "type": "fill", "title": "中国的首都是___，简称___。", "category_id": qcat["id"], "score": 20,
        "options": [], "answer": [["北京", "北京市"], ["京"]],
        "explanation": "一空多答示例"}))
    q_short = jp(c.post("/api/v1/admin/questions", headers=ah, json={
        "type": "short", "title": "简述 HTTPS 相比 HTTP 的安全改进。", "category_id": qcat["id"], "score": 30,
        "options": [], "answer": ["HTTPS 使用 TLS/SSL 加密传输，并通过证书验证服务器身份，防止窃听与篡改"],
        "grading_points": ["TLS/SSL 加密", "证书验证身份", "防窃听防篡改"], "explanation": "按踩分点给分"}))
    check("新建 5 种题型题目", all(q["id"] for q in [q_single, q_multi, q_judge, q_fill, q_short]),
          f"ids: {q_single['id']},{q_multi['id']},{q_judge['id']},{q_fill['id']},{q_short['id']}")

    # 填空题校验负路径
    bad_fill = c.post("/api/v1/admin/questions", headers=ah, json={
        "type": "fill", "title": "只有一空___", "options": [], "answer": [["a"], ["b"]]})
    check("填空题 ___ 数量校验拦截", bad_fill.status_code == 400)

    # ---------- 4. ✨AI 出题 (真实大模型) ----------
    print("【2】✨AI 出题 (真实调用 SenseNova)")
    t0 = time.time()
    # 负路径: 高级选项部分填写 → 400
    r_part = c.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "围绕 Python 基础语法出题", "count": 2})
    check("AI出题高级选项部分填写 400", r_part.status_code == 400)
    gen = jp(c.post("/api/v1/admin/ai/questions/generate", headers=ah, json={
        "material": "围绕 Python 基础语法出题：变量命名、缩进、列表与元组的区别。材料中说3道，但按高级选项出5道",
        "types": ["single"], "count": 5, "difficulty": "easy", "category_id": qcat["id"]}))
    check("AI出题多题型/数量优先级(高级选项5题为准)", len(gen["questions"]) <= 5 and all(q["type"] == "single" for q in gen["questions"]),
          f"生成{len(gen['questions'])}题 single")
    ai_questions = gen["questions"]
    check("AI 生成题目(预览不入库)", len(ai_questions) >= 1 and all(q["source"] == "ai" for q in ai_questions),
          f"{len(ai_questions)} 题, 耗时 {time.time()-t0:.0f}s")
    batch = jp(c.post("/api/v1/admin/questions/batch", headers=ah, json=ai_questions))
    check("AI 题目二次确认入库", len(batch["question_ids"]) == len(ai_questions))
    # options 结构规范化回归 (曾因字符串 options 拖垮题目列表)
    lst_check = jp(c.get("/api/v1/admin/questions", headers=ah, params={"size": 10}))
    check("题目列表无脏 options(规范化回归)", all(
        (not q["options"]) or isinstance(q["options"][0], dict) for q in lst_check["items"]))

    # ---------- 5. 三份试卷 ----------
    print("【3】组卷与上架")
    # a) 客观卷 (即时出分)
    exam_obj = jp(c.post("/api/v1/admin/exams", headers=ah, json={
        "title": f"自测·客观卷{STAMP}", "category_id": ecat["id"], "status": "published",
        "question_ids": [q_single["id"], q_multi["id"], q_judge["id"]], "time_limit": 30, "pass_percent": 60}))
    # b) 主观卷 (填空+简答 → pending_grading → 阅卷大厅)
    exam_sub = jp(c.post("/api/v1/admin/exams", headers=ah, json={
        "title": f"自测·主观卷{STAMP}", "category_id": ecat["id"], "status": "published",
        "question_ids": [q_fill["id"], q_short["id"]], "time_limit": 30, "pass_percent": 50}))
    check("客观卷/主观卷上架", bool(exam_obj["id"] and exam_sub["id"]),
          f"客观卷{exam_obj['id']}({exam_obj['total_score']}分) 主观卷{exam_sub['id']}({exam_sub['total_score']}分)")

    # ✨AI 智能组卷 (真实大模型)
    t0 = time.time()
    ai_exam = jp(c.post("/api/v1/admin/ai/exams/generate", headers=ah, json={
        "title": f"AI组卷·Python基础{STAMP}",
        "description": "组一份 Python 基础小测卷：2 道单选、1 道判断、1 道简答",
        "specs": [{"q_type": "single", "count": 2}, {"q_type": "judge", "count": 1}, {"q_type": "short", "count": 1}],
        "category_id": ecat["id"], "time_limit": 30, "pass_percent": 50}))
    check("✨AI 智能组卷(强制草稿)", ai_exam["question_count"] >= 4, f"试卷#{ai_exam['exam_id']} 共{ai_exam['question_count']}题(新生成{ai_exam['new_questions']}), 耗时{time.time()-t0:.0f}s")
    ai_exam_detail = jp(c.get(f"/api/v1/admin/exams/{ai_exam['exam_id']}", headers=ah))
    has_short = any(q["type"] == "short" for q in ai_exam_detail["questions"])
    check("AI 试卷为草稿且含简答题", ai_exam_detail["status"] == "draft" and has_short)
    # 上架 AI 卷 (开启 AI 全托管)
    up = c.put(f"/api/v1/admin/exams/{ai_exam['exam_id']}/status?status=published", headers=ah)
    jp(c.put(f"/api/v1/admin/exams/{ai_exam['exam_id']}", headers=ah, json={"is_ai_auto_grade": True}))
    check("AI 试卷人工检查后上架(全托管)", up.status_code == 200)

    # ---------- 6. 批量注册 6 个 C 端账号 ----------
    print("【4】批量注册 C 端账号 (含负路径校验)")
    accounts = [
        ("测试员小张", "male",   "消防讲师", True),
        ("测试员小王", "female", "企业安监员", True),
        ("测试员小李", "male",   "",          True),
        ("测试员小赵", "female", "在校学生",  True),
        ("测试员小陈", "male",   "IT工程师",  True),
        ("测试员小刘", "female", "",          False),  # 第6个不填邮箱/职务, 验证选填缺省
    ]
    user_tokens = []
    phone_base = f"139{int(STAMP) % 10000000:07d}"  # 3+7 = 10位前缀, 追加序号位凑 11 位
    for i, (nick, gender, pos, with_email) in enumerate(accounts):
        uname = f"e2e{STAMP}_{i+1}"
        payload = {
            "username": uname, "password": "E2ePass123", "nickname": nick,
            "gender": gender, "phone": f"{phone_base}{i}", "position": pos,
            "email": f"{uname}@test.com" if with_email else "",
        }
        r = c.post("/api/v1/auth/register", json=payload)
        ok = r.status_code == 201 and r.json()["data"]["nickname"] == nick
        check(f"注册账号 {uname} ({nick}/{('男' if gender=='male' else '女')}/{pos or '无职务'})", ok)
        login = jp(c.post("/api/v1/auth/login", json={"username": uname, "password": "E2ePass123"}))
        user_tokens.append({"token": login["token"], "username": uname, "nickname": nick})
        # GET /users/me 资料回读
        me_res = jp(c.get("/api/v1/users/me", headers={"Authorization": f"Bearer {login['token']}"}))
        assert me_res["phone"] == payload["phone"], f"{uname} 资料回读失败"

    # 负路径: 缺昵称 / 重复手机号 (复用账号0手机号)
    r1 = c.post("/api/v1/auth/register", json={"username": f"neg{STAMP}a", "password": "E2ePass123", "nickname": "", "gender": "male", "phone": f"139{random.randint(10000000, 99999999)}"})
    r2 = c.post("/api/v1/auth/register", json={"username": f"neg{STAMP}b", "password": "E2ePass123", "nickname": "重复手机号", "gender": "female", "phone": f"{phone_base}0"})
    check("负路径: 缺昵称 400 / 重复手机号 400", r1.status_code == 400 and r2.status_code == 400,
          f"{r1.json().get('detail')} | {r2.json().get('detail')}")

    def uh(i):
        return {"Authorization": f"Bearer {user_tokens[i]['token']}"}

    # ---------- 7. 模拟考试 ----------
    print("【5】模拟 C 端考试")
    qs = {"single": q_single["id"], "multi": q_multi["id"], "judge": q_judge["id"]}

    # 7.1 客观卷: acc1 全对 (即时出分 30/30), acc2 多选漏选 (半对: 10 + 5 + 10 = 25/30)
    st1 = jp(c.post("/api/v1/records/start", headers=uh(0), json={"exam_id": exam_obj["id"]}))
    sub1 = jp(c.post("/api/v1/records/submit", headers=uh(0), json={
        "record_id": st1["record_id"], "time_spent": 300,
        "user_answers": {str(qs["single"]): ["A"], str(qs["multi"]): ["A", "B", "D"], str(qs["judge"]): ["A"]}}))
    check("客观卷全对即时出分", sub1["status"] == "submitted" and sub1["score"] == 30 and sub1["passed"],
          f"{sub1['score']}/30")

    st2 = jp(c.post("/api/v1/records/start", headers=uh(1), json={"exam_id": exam_obj["id"]}))
    sub2 = jp(c.post("/api/v1/records/submit", headers=uh(1), json={
        "record_id": st2["record_id"], "time_spent": 200,
        "user_answers": {str(qs["single"]): ["A"], str(qs["multi"]): ["A"], str(qs["judge"]): ["A"]}}))
    check("多选漏选得半分(错选不得分)", sub2["status"] == "submitted" and sub2["score"] == 25 and sub2["partial_count"] == 1,
          f"{sub2['score']}/30, 半对{sub2['partial_count']}题")

    # 7.2 主观卷: acc3 填空全对 + 简答作答 → pending_grading → 老师定分发布
    st3 = jp(c.post("/api/v1/records/start", headers=uh(2), json={"exam_id": exam_sub["id"]}))
    sub3 = jp(c.post("/api/v1/records/submit", headers=uh(2), json={
        "record_id": st3["record_id"], "time_spent": 600,
        "user_answers": {str(q_fill["id"]): ["北京市", " 京 "], str(q_short["id"]): ["HTTPS 用 TLS 加密，端口 443，但没提证书"]}}))
    check("含简答题交卷转待批阅", sub3["status"] == "pending_grading" and sub3["pending"] and sub3["analysis_locked"],
          f"pending_count={sub3['pending_count']}")
    # 报告降级: 标准答案被隐藏
    rep3 = jp(c.get(f"/api/v1/records/{st3['record_id']}/report", headers=uh(2)))
    check("待批阅降级查看(锁答案)", all(not it["correct_answer"] for it in rep3["questions_analysis"]))

    # 阅卷大厅: 老师看到昵称 → 定分发布 (TLS踩中1点给15)
    hall = jp(c.get("/api/v1/admin/grading/records", headers=ah, params={"exam_id": exam_sub["id"]}))
    target = [r for r in hall["items"] if r["record_id"] == st3["record_id"]]
    check("阅卷大厅列表(含考生昵称)", bool(target) and target[0]["nickname"] == "测试员小李",
          f"nickname={target[0]['nickname']}, 客观分={target[0]['objective_score']}")
    det = jp(c.get(f"/api/v1/admin/grading/records/{st3['record_id']}", headers=ah))
    check("批阅详情含踩分点与AI建议", any(q["type"] == "short" and q["grading_points"] for q in det["questions"]))
    conf = jp(c.post(f"/api/v1/admin/grading/records/{st3['record_id']}/confirm", headers=ah,
                     json={"accept_ai": False, "scores": {str(q_short["id"]): 15}}))
    rep3b = jp(c.get(f"/api/v1/records/{st3['record_id']}/report", headers=uh(2)))
    check("人工定分发布(填空20+简答15=35及格)", rep3b["status"] == "submitted" and rep3b["score"] == 35 and rep3b["passed"],
          f"{rep3b['score']}/50")

    # 7.3 AI 卷: acc4/acc5 真实 AI 全托管批阅
    print("【6】AI 全托管阅卷 (真实调用大模型)")
    ai_scores = []
    for idx in (3, 4):
        st = jp(c.post("/api/v1/records/start", headers=uh(idx), json={"exam_id": ai_exam["exam_id"]}))
        answers = {}
        for q in st["questions"]:
            qid = str(q["id"])
            if q["type"] in ("single", "judge"):
                answers[qid] = [q["options"][0]["key"]] if q.get("options") else ["A"]
            elif q["type"] == "short":
                # 认真作答 = 复述题干并给出要点式展开 (AI 按语义给分); 敷衍作答 = 答非所问
                answers[qid] = [
                    f"我认为这道题考察的是：{q['title']}。要点如下：第一，需要理解其基本定义；第二，要结合实际应用场景说明其作用与优势；第三，注意与相邻概念的区别。以上是我的完整作答。"
                ] if idx == 3 else ["不知道，随便写的答案"]
            else:
                answers[qid] = []
        sub = jp(c.post("/api/v1/records/submit", headers=uh(idx), json={
            "record_id": st["record_id"], "time_spent": 400, "user_answers": answers}))
        # 等待后台 AI 批阅完成 (全托管模式自动发布)
        final = None
        for _ in range(30):
            time.sleep(3)
            final = jp(c.get(f"/api/v1/records/{st['record_id']}/report", headers=uh(idx)))
            if final["status"] == "submitted":
                break
        ok = final and final["status"] == "submitted"
        comment = next((it["comment"] for it in final["questions_analysis"] if it["comment"]), "")
        ai_scores.append(final["score"])
        check(f"AI 全托管批阅并发布 ({user_tokens[idx]['nickname']})", bool(ok),
              f"{final['score']}/{final['total_score']} 分 | AI评语: {comment[:40]}")
    check("AI 阅卷建议落库(评语与得分写入)", all(s >= 0 for s in ai_scores) and ai_scores[0] >= ai_scores[1],
          f"得分: {ai_scores}")

    # ---------- 8. 展示与聚合校验 ----------
    print("【7】展示与聚合校验")
    users_list = jp(c.get("/api/v1/admin/users", headers=ah, params={"size": 100}))
    e2e_users = [u for u in users_list["items"] if u["username"].startswith(f"e2e{STAMP}")]
    check("B端用户列表含昵称/性别/手机号", len(e2e_users) == 6 and all(u["nickname"] and u["phone"] and u["gender"] for u in e2e_users),
          f"共{len(e2e_users)}个自测账号")

    records_list = jp(c.get("/api/v1/admin/users/records", headers=ah, params={"size": 20}))
    has_nick = any(r["nickname"] for r in records_list["items"])
    check("B端答题明细带昵称", has_nick)

    stats_board = jp(c.get(f"/api/v1/admin/exams/{exam_obj['id']}/stats", headers=ah))
    check("考情看板带昵称(2人作答)", stats_board["total_participants"] == 2 and all(r["nickname"] for r in stats_board["user_records"]))

    mytests = jp(c.get("/api/v1/records/my-tests", headers=uh(1)))
    has_done = any(c["exam_id"] == exam_obj["id"] for c in mytests["completed"])
    check("C端我的测试·已考试聚合", has_done, f"completed={len(mytests['completed'])}场")

    # 再考一次 (多记录)
    st_re = jp(c.post("/api/v1/records/start", headers=uh(1), json={"exam_id": exam_obj["id"]}))
    check("C端再考一次(新建作答记录)", bool(st_re["record_id"]) and st_re["record_id"] != st2["record_id"])

    # 消息中心
    notes = jp(c.get("/api/v1/admin/notifications", headers=ah, params={"size": 5}))
    check("消息中心有通知(组卷草稿等)", notes["total"] >= 1)

    # 审计
    audit = jp(c.get("/api/v1/admin/audit", headers=ah, params={"size": 5}))
    check("审计日志双域留痕", audit["total"] >= 1)

    # ---------- 报告 ----------
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    failed = len(RESULTS) - passed
    print(f"\n=== 自测报告: {passed} 通过 / {failed} 失败 (共{len(RESULTS)}项) ===")
    test_accounts = [f"{u['username']} / E2ePass123 ({u['nickname']})" for u in user_tokens]
    print("自测账号清单(保留为演示数据):")
    for a in test_accounts:
        print(f"  - {a}")
    print("造数试卷: 客观卷#{exam} 主观卷#{sub} AI卷#{ai}".format(exam=exam_obj["id"], sub=exam_sub["id"], ai=ai_exam["exam_id"]))
    if failed:
        print("失败项:")
        for name, ok, detail in RESULTS:
            if not ok:
                print(f"  ❌ {name} {detail}")
        sys.exit(1)


if __name__ == "__main__":
    main()
