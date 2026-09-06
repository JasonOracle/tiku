"""v1.2 回归测试：填空/简答题引擎、多选半对、AI阅卷链路、RBAC、时间窗口、额度资产化、审计留痕"""
import json
import pytest
from datetime import datetime, timedelta, date

from app.services import ai_service
from app.services.ai_grading import SessionLocal as _ignored


# ---------- 公共脚手架 ----------

def _bootstrap(client):
    """初始化超管 + 老师 + C端用户, 返回句柄"""
    client.post("/api/v1/admin/auth/init", json={"username": "root_gov", "password": "rootpassword"})
    super_token = client.post("/api/v1/admin/auth/login", json={"username": "root_gov", "password": "rootpassword"}).json()["data"]["token"]
    ah = {"Authorization": f"Bearer {super_token}"}
    # 建一个老师
    client.post("/api/v1/admin/members", json={"username": "teacher_wang", "password": "teapass123", "ai_quota_limit": 5}, headers=ah)
    t_token = client.post("/api/v1/admin/auth/login", json={"username": "teacher_wang", "password": "teapass123"}).json()["data"]["token"]
    th = {"Authorization": f"Bearer {t_token}"}
    # C端用户
    client.post("/api/v1/auth/register", json={"username": "stu01", "password": "stupass123"})
    u_token = client.post("/api/v1/auth/login", json={"username": "stu01", "password": "stupass123"}).json()["data"]["token"]
    uh = {"Authorization": f"Bearer {u_token}"}
    qcat = client.post("/api/v1/admin/categories", json={"name": "题类", "target_type": "question"}, headers=ah).json()["data"]
    ecat = client.post("/api/v1/admin/categories", json={"name": "卷类", "target_type": "exam"}, headers=ah).json()["data"]
    return {"ah": ah, "th": th, "uh": uh, "qcat": qcat, "ecat": ecat}


def _mk_q(client, headers, q_type="single", title="题?", answer=None, options=None, score=10, grading_points=None):
    payload = {
        "type": q_type, "title": title,
        "options": options if options is not None else ([{"key": "A", "text": "a"}, {"key": "B", "text": "b"}] if q_type in ("single", "multiple") else []),
        "answer": answer if answer is not None else ["A"],
        "score": score,
    }
    if grading_points is not None:
        payload["grading_points"] = grading_points
    r = client.post("/api/v1/admin/questions", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()["data"]


def _mk_exam(client, headers, ecat_id, q_ids, status="published", title="卷", **extra):
    payload = {"title": title, "category_id": ecat_id, "status": status, "question_ids": q_ids}
    payload.update(extra)
    r = client.post("/api/v1/admin/exams", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()["data"]


def _start_and_submit(client, uh, exam_id, answers, time_spent=60):
    st = client.post("/api/v1/records/start", json={"exam_id": exam_id}, headers=uh)
    assert st.status_code == 200, st.text
    rec = st.json()["data"]["record_id"]
    sub = client.post("/api/v1/records/submit", json={"record_id": rec, "user_answers": answers, "time_spent": time_spent}, headers=uh)
    return rec, sub


# ---------- 评分引擎: 填空 / 多选半对 ----------

def test_fill_question_grading(client):
    """填空题: 一空多答命中 / 大小写与首尾空格归一 / 空数不匹配判错"""
    s = _bootstrap(client)
    q = _mk_q(client, s["ah"], q_type="fill", title="中国首都是___，简称___。",
              answer=[["北京", "北京市"], ["京"]], options=[])
    ex = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="填空卷")

    # 全对 (命中备选答案 + 归一化去空格)
    rec, sub = _start_and_submit(client, s["uh"], ex["id"], {str(q["id"]): ["北京市", " 京 "]})
    assert sub.status_code == 200
    rep = sub.json()["data"]
    assert rep["score"] == 10 and rep["passed"] is True

    # 部分空错误 → 0 分
    rec2, sub2 = _start_and_submit(client, s["uh"], ex["id"], {str(q["id"]): ["北京", "沪"]})
    assert sub2.json()["data"]["score"] == 0


def test_multiple_half_credit(client):
    """多选半对机制: 漏选(真子集)得一半, 错选得 0, 全对得满分"""
    s = _bootstrap(client)
    q = _mk_q(client, s["ah"], q_type="multiple", title="多选?", answer=["A", "B"], score=10)
    ex = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="多选卷", pass_percent=50)

    _, sub_all = _start_and_submit(client, s["uh"], ex["id"], {str(q["id"]): ["A", "B"]})
    assert sub_all.json()["data"]["score"] == 10

    _, sub_half = _start_and_submit(client, s["uh"], ex["id"], {str(q["id"]): ["A"]})
    assert sub_half.json()["data"]["score"] == 5   # 漏选得一半
    assert sub_half.json()["data"]["partial_count"] == 1

    _, sub_zero = _start_and_submit(client, s["uh"], ex["id"], {str(q["id"]): ["A", "C"]})
    assert sub_zero.json()["data"]["score"] == 0   # 错选不得分


def test_fill_blank_count_validation(client):
    """填空题防崩溃校验: ___ 数量必须等于答案二维数组长度"""
    s = _bootstrap(client)
    r = client.post("/api/v1/admin/questions", json={
        "type": "fill", "title": "只有一空___", "answer": [["a"], ["b"]], "options": []
    }, headers=s["ah"])
    assert r.status_code == 400


# ---------- 简答题: 待批阅 → 人工确认 ----------

def test_short_question_pending_then_teacher_confirm(client):
    """简答题: 交卷后 pending_grading 不出分; 老师定分确认后发布成绩"""
    s = _bootstrap(client)
    q1 = _mk_q(client, s["ah"], q_type="single", title="客观?", answer=["A"], score=60)
    q2 = _mk_q(client, s["ah"], q_type="short", title="简述?", answer=["要点A"], score=40,
               grading_points=["要点A"])
    ex = _mk_exam(client, s["th"], s["ecat"]["id"], [q1["id"], q2["id"]], title="简答卷",
                  is_ai_auto_grade=False)

    rec, sub = _start_and_submit(client, s["uh"], ex["id"],
                                 {str(q1["id"]): ["A"], str(q2["id"]): ["我答了要点A"]})
    assert sub.status_code == 200
    rep = sub.json()["data"]
    assert rep["status"] == "pending_grading" and rep["pending"] is True
    assert rep["score"] == 0 and rep["passed"] is False
    # 降级查看: 标准答案与解析隐藏
    assert rep["analysis_locked"] is True
    assert all(item["correct_answer"] in ([], [None]) or not item["correct_answer"] for item in rep["questions_analysis"])

    # 老师批阅: 详情含踩分点与学生原文
    detail = client.get(f"/api/v1/admin/grading/records/{rec}", headers=s["th"]).json()["data"]
    short_entry = [q for q in detail["questions"] if q["type"] == "short"][0]
    assert short_entry["grading_points"] == ["要点A"]
    assert "要点A" in short_entry["user_answer"][0]
    assert detail["objective_score"] == 60

    # 未全部定分 → 400
    r_half = client.post(f"/api/v1/admin/grading/records/{rec}/confirm",
                         json={"scores": {str(q2["id"]): 30}}, headers=s["th"])
    # 只有1道简答题, 不缺 → 应成功; 客观60 + 简答30 = 90
    assert r_half.status_code == 200, r_half.text
    final = client.get(f"/api/v1/records/{rec}/report", headers=s["uh"]).json()["data"]
    assert final["status"] == "submitted" and final["score"] == 90 and final["passed"] is True
    assert final["pending"] is False


# ---------- AI 阅卷: 全托管 / 预批改 / 失败兜底 ----------

@pytest.fixture()
def mock_ai(monkeypatch):
    """伪造大模型 + 将 AI 阅卷的后台会话指向测试库"""
    from sqlalchemy.orm import sessionmaker
    import conftest as cf  # pytest 的 conftest 模块实例 (与测试共享同一 engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=cf.engine)

    calls = {"n": 0}

    def fake_chat(prompt, system="", json_mode=False, temperature=0.3, timeout=90.0):
        calls["n"] += 1
        if calls.get("fail"):
            raise ai_service.AiServiceError("模拟大模型宕机")
        # 从 prompt 中提取 question_id 与满分, 按满分给分 (模拟踩点全中)
        import re
        qids = re.findall(r'"question_id": (\d+)', prompt)
        fulls = re.findall(r'"full_score": (\d+)', prompt)
        results = [{"question_id": int(q), "score": int(f), "comment": "AI评语: 踩点全中"}
                   for q, f in zip(qids, fulls)]
        return json.dumps({"results": results}, ensure_ascii=False)

    monkeypatch.setattr(ai_service, "chat_completion", fake_chat)
    monkeypatch.setattr(ai_service, "ai_available", lambda: True)
    monkeypatch.setattr("app.services.ai_grading.SessionLocal", TestSession)
    return calls


def test_ai_auto_grade_full_hosting(client, mock_ai):
    """AI 全托管: 交卷 → 后台 AI 批阅 → 直接发布成绩"""
    s = _bootstrap(client)
    q1 = _mk_q(client, s["ah"], q_type="single", title="客1?", answer=["A"], score=50)
    q2 = _mk_q(client, s["ah"], q_type="short", title="主1?", answer=["参考"], score=50, grading_points=["参考"])
    ex = _mk_exam(client, s["th"], s["ecat"]["id"], [q1["id"], q2["id"]], title="全托管卷",
                  is_ai_auto_grade=True)

    rec, sub = _start_and_submit(client, s["uh"], ex["id"],
                                 {str(q1["id"]): ["A"], str(q2["id"]): "学生作答".join([]) or ["学生作答"]})
    assert sub.json()["data"]["status"] in ("pending_grading", "submitted")

    final = client.get(f"/api/v1/records/{rec}/report", headers=s["uh"]).json()["data"]
    assert final["status"] == "submitted"          # AI 批完直接发布
    assert final["score"] == 100                    # 客观50 + AI给50
    assert final["pending"] is False
    # 老师收到站内信
    notes = client.get("/api/v1/admin/notifications", headers=s["th"]).json()["data"]
    assert any("全托管" in n["title"] or "批阅" in n["title"] for n in notes["items"])


def test_ai_pre_grading_requires_review(client, mock_ai):
    """预批改模式: AI 仅给建议分, 老师一键采信后发布"""
    s = _bootstrap(client)
    q1 = _mk_q(client, s["ah"], q_type="short", title="主?", answer=["参考"], score=20, grading_points=["参考"])
    ex = _mk_exam(client, s["th"], s["ecat"]["id"], [q1["id"]], title="预批改卷", is_ai_auto_grade=False)

    rec, sub = _start_and_submit(client, s["uh"], ex["id"], {str(q1["id"]): ["作答内容"]})
    assert sub.json()["data"]["status"] == "pending_grading"
    # 预批改模式不自动终算
    final = client.get(f"/api/v1/records/{rec}/report", headers=s["uh"]).json()["data"]
    assert final["status"] == "pending_grading"

    # 一键采信 AI 评分
    r = client.post(f"/api/v1/admin/grading/records/{rec}/confirm", json={"accept_ai": True}, headers=s["th"])
    assert r.status_code == 200, r.text
    assert r.json()["data"]["score"] == 20


def test_ai_failure_falls_back_to_manual(client, mock_ai):
    """AI 宕机兜底: 批阅失败写入 error, 记录留在待批阅, 可重新触发"""
    s = _bootstrap(client)
    q1 = _mk_q(client, s["ah"], q_type="short", title="主?", answer=["参考"], score=20)
    ex = _mk_exam(client, s["th"], s["ecat"]["id"], [q1["id"]], title="兜底卷", is_ai_auto_grade=True)

    mock_ai["fail"] = 1
    rec, sub = _start_and_submit(client, s["uh"], ex["id"], {str(q1["id"]): ["作答"]})
    detail = client.get(f"/api/v1/admin/grading/records/{rec}", headers=s["th"]).json()["data"]
    assert detail["status"] == "pending_grading"
    assert detail["ai_error"], "AI 失败必须记录错误信息"

    # 恢复 AI 后重新触发
    mock_ai["fail"] = 0
    r = client.post(f"/api/v1/admin/grading/records/{rec}/retry-ai", headers=s["th"])
    assert r.status_code == 200
    final = client.get(f"/api/v1/records/{rec}/report", headers=s["uh"]).json()["data"]
    assert final["status"] == "submitted"


# ---------- 时间窗口 / 惰性收卷 / 解析锁 ----------

def test_exam_window_guards(client):
    """未开始/已结束拦截 + 组卷时间锁校验 (time_limit ≤ 区间)"""
    s = _bootstrap(client)
    q = _mk_q(client, s["ah"], answer=["A"])
    future = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    past = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")

    ex_up = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="未开始卷",
                     status="published", start_time=future)
    r = client.post("/api/v1/records/start", json={"exam_id": ex_up["id"]}, headers=s["uh"])
    assert r.status_code == 400 and "尚未开始" in r.json()["detail"]

    ex_past = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="已结束卷",
                       status="published", start_time=past, end_time=(datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S"))
    r2 = client.post("/api/v1/records/start", json={"exam_id": ex_past["id"]}, headers=s["uh"])
    assert r2.status_code == 400 and "已结束" in r2.json()["detail"]

    # 时间悖论: 区间 60 分钟却要求考 90 分钟 → 前后端双层拦截 (后端 400)
    r3 = client.post("/api/v1/admin/exams", json={
        "title": "悖论卷", "category_id": s["ecat"]["id"], "question_ids": [q["id"]],
        "time_limit": 90,
        "start_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": (datetime.now() + timedelta(minutes=60)).strftime("%Y-%m-%dT%H:%M:%S"),
    }, headers=s["ah"])
    assert r3.status_code == 400 and "不能大于" in r3.json()["detail"]


def test_lazy_close_zombie_records_and_analysis_lock(client):
    """惰性收卷: 过 end_time 的 in_progress 记录在查询时被强制收卷; 解析锁随 end_time 解锁"""
    s = _bootstrap(client)
    q = _mk_q(client, s["ah"], answer=["A"], score=100)
    ex = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="僵尸卷", status="published",
                  end_time=(datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S"))

    st = client.post("/api/v1/records/start", json={"exam_id": ex["id"]}, headers=s["uh"])
    rec = st.json()["data"]["record_id"]
    client.post("/api/v1/records/submit", json={"record_id": rec, "user_answers": {str(q["id"]): ["A"]}, "time_spent": 10}, headers=s["uh"])

    # end_time 未到: 已出分但解析锁定 (防泄题)
    rep1 = client.get(f"/api/v1/records/{rec}/report", headers=s["uh"]).json()["data"]
    assert rep1["analysis_locked"] is True
    assert all(not item["correct_answer"] for item in rep1["questions_analysis"])

    # 时间流逝 (把 end_time 改到过去), 打开我的测试触发惰性收卷与解锁
    past = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")
    client.put(f"/api/v1/admin/exams/{ex['id']}", json={"end_time": past}, headers=s["ah"])
    mt = client.get("/api/v1/records/my-tests", headers=s["uh"]).json()["data"]
    assert any(c["exam_id"] == ex["id"] and c["latest_status"] == "submitted" for c in mt["completed"])
    rep2 = client.get(f"/api/v1/records/{rec}/report", headers=s["uh"]).json()["data"]
    assert rep2["analysis_locked"] is False
    assert rep2["questions_analysis"][0]["correct_answer"] == ["A"]


def test_my_tests_three_buckets(client):
    """我的测试: 未开始/进行中/已考试 三桶聚合, 卡片反映最新一次作答"""
    s = _bootstrap(client)
    q = _mk_q(client, s["ah"], answer=["A"], score=100)
    future = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    ex_up = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="未开始", status="published", start_time=future)
    ex_now = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="进行中", status="published")
    ex_done = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="已考完", status="published")
    _start_and_submit(client, s["uh"], ex_done["id"], {str(q["id"]): ["A"]})

    mt = client.get("/api/v1/records/my-tests", headers=s["uh"]).json()["data"]
    ids_up = [c["exam_id"] for c in mt["upcoming"]]
    ids_on = [c["exam_id"] for c in mt["ongoing"]]
    ids_done = [c["exam_id"] for c in mt["completed"]]
    assert ex_up["id"] in ids_up and ex_up["id"] not in ids_on
    assert ex_now["id"] in ids_on
    assert ex_done["id"] in ids_done and mt["completed"][0]["attempts"] >= 1


# ---------- RBAC / 题目锁定 / 额度 / 审计 / 成员 ----------

def test_rbac_exam_isolation(client):
    """试卷隔离: 老师只能管理自己创建的试卷, 超管全览"""
    s = _bootstrap(client)
    q = _mk_q(client, s["th"], answer=["A"])
    ex_teacher = _mk_exam(client, s["th"], s["ecat"]["id"], [q["id"]], title="王老师的卷")
    # 老师2
    client.post("/api/v1/admin/members", json={"username": "teacher_li", "password": "teapass123"}, headers=s["ah"])
    li_token = client.post("/api/v1/admin/auth/login", json={"username": "teacher_li", "password": "teapass123"}).json()["data"]["token"]
    li = {"Authorization": f"Bearer {li_token}"}
    # 李老师编辑王老师的卷 → 403
    r = client.put(f"/api/v1/admin/exams/{ex_teacher['id']}", json={"title": "篡改"}, headers=li)
    assert r.status_code == 403
    # 李老师列表看不到王老师的卷
    lst = client.get("/api/v1/admin/exams", headers=li).json()["data"]
    assert all(item["id"] != ex_teacher["id"] for item in lst["items"])
    # 超管可见
    lst_super = client.get("/api/v1/admin/exams", headers=s["ah"]).json()["data"]
    assert any(item["id"] == ex_teacher["id"] for item in lst_super["items"])


def test_question_locked_when_referenced_by_published(client):
    """题目锁定防篡改: 被上架/归档卷引用后编辑被拦, 复制新题可用"""
    s = _bootstrap(client)
    q = _mk_q(client, s["th"], answer=["A"])
    _mk_exam(client, s["th"], s["ecat"]["id"], [q["id"]], title="引用卷", status="published")
    r = client.put(f"/api/v1/admin/questions/{q['id']}", json={"title": "改题干"}, headers=s["th"])
    assert r.status_code == 400 and "只读" in r.json()["detail"]
    # 复制产生新题
    rc = client.post(f"/api/v1/admin/questions/{q['id']}/copy", headers=s["th"])
    assert rc.status_code == 201
    assert "副本" in rc.json()["data"]["title"]


def test_ai_question_generation_with_quota(client, mock_ai):
    """AI出题: 额度扣减 + 预览不入库 + 二次确认批量入库(source=ai) + 额度耗尽拦截"""
    s = _bootstrap(client)
    mock_ai_current = mock_ai
    fake_payload = json.dumps({"questions": [{
        "type": "single", "title": "AI生成题?", "options": [{"key": "A", "text": "x"}, {"key": "B", "text": "y"}],
        "answer": ["A"], "explanation": "解析", "difficulty": "easy", "score": 10}]}, ensure_ascii=False)

    def fake_gen(prompt, system="", json_mode=False, temperature=0.3, timeout=90.0):
        return fake_payload
    ai_service.chat_completion = fake_gen

    # 老师额度 5
    r1 = client.post("/api/v1/admin/ai/questions/generate",
                     json={"material": "Python并发编程", "count": 1, "q_type": "single"}, headers=s["th"])
    assert r1.status_code == 200
    preview = r1.json()["data"]["questions"]
    assert preview[0]["source"] == "ai"
    status1 = client.get("/api/v1/admin/ai/status", headers=s["th"]).json()["data"]
    assert status1["quota_remaining"] == 4

    # 二次确认入库
    rb = client.post("/api/v1/admin/questions/batch", json=preview, headers=s["th"])
    assert rb.status_code == 201
    lst = client.get("/api/v1/admin/questions?keyword=AI生成题", headers=s["th"]).json()["data"]["items"]
    assert lst and lst[0]["source"] == "ai"

    # 额度耗尽拦截 (再扣4次后为0)
    for _ in range(4):
        client.post("/api/v1/admin/ai/questions/generate",
                    json={"material": "更多题目材料内容", "count": 1, "q_type": "single"}, headers=s["th"])
    r_ex = client.post("/api/v1/admin/ai/questions/generate",
                       json={"material": "额度耗尽后的请求", "count": 1, "q_type": "single"}, headers=s["th"])
    assert r_ex.status_code == 400 and "额度" in r_ex.json()["detail"]

    # 超管即时补充
    members = client.get("/api/v1/admin/members", headers=s["ah"]).json()["data"]["items"]
    tid = [m for m in members if m["username"] == "teacher_wang"][0]["id"]
    rr = client.post(f"/api/v1/admin/members/{tid}/refill", json={"amount": 3}, headers=s["ah"])
    assert rr.status_code == 200
    status2 = client.get("/api/v1/admin/ai/status", headers=s["th"]).json()["data"]
    assert status2["quota_remaining"] == 3


def test_ai_exam_generation_forces_draft(client, mock_ai):
    """AI组卷: 复用题库 + 强制 Draft + 站内信通知"""
    s = _bootstrap(client)
    existing = _mk_q(client, s["th"], title="题库已有题?", answer=["A"])

    def fake_gen(prompt, system="", json_mode=False, temperature=0.3, timeout=90.0):
        return json.dumps({
            "title": "AI组装的安全测试卷",
            "items": [
                {"question_id": existing["id"]},
                {"new_question": {"type": "judge", "title": "AI新生成判断题?", "options": [],
                                  "answer": ["A"], "explanation": "", "difficulty": "easy"}},
            ],
        }, ensure_ascii=False)
    ai_service.chat_completion = fake_gen

    r = client.post("/api/v1/admin/ai/exams/generate", json={
        "description": "组一份50分的安全测试卷",
        "specs": [{"q_type": "single", "count": 1}, {"q_type": "judge", "count": 1}],
    }, headers=s["th"])
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["question_count"] == 2 and data["new_questions"] == 1
    # 强制草稿
    det = client.get(f"/api/v1/admin/exams/{data['exam_id']}", headers=s["th"]).json()["data"]
    assert det["status"] == "draft" and det["creator_name"] == "teacher_wang"
    # 站内信
    notes = client.get("/api/v1/admin/notifications", headers=s["th"]).json()["data"]
    assert any("组卷" in n["title"] for n in notes["items"])


def test_members_rbac_and_disable(client):
    """成员管理 RBAC: 老师不可访问; 禁用后登录被拒"""
    s = _bootstrap(client)
    assert client.get("/api/v1/admin/members", headers=s["th"]).status_code == 403
    members = client.get("/api/v1/admin/members", headers=s["ah"]).json()["data"]["items"]
    tid = [m for m in members if m["username"] == "teacher_wang"][0]["id"]
    client.put(f"/api/v1/admin/members/{tid}", json={"status": False}, headers=s["ah"])
    r = client.post("/api/v1/admin/auth/login", json={"username": "teacher_wang", "password": "teapass123"})
    assert r.status_code == 403
    client.put(f"/api/v1/admin/members/{tid}", json={"status": True}, headers=s["ah"])
    assert client.post("/api/v1/admin/auth/login", json={"username": "teacher_wang", "password": "teapass123"}).status_code == 200


def test_audit_logs_written(client):
    """双域审计: 写操作全量留痕, 超管可查, 老师不可查"""
    s = _bootstrap(client)
    q = _mk_q(client, s["th"], answer=["A"])
    logs = client.get("/api/v1/admin/audit", headers=s["ah"]).json()["data"]
    assert logs["total"] >= 1
    assert any(l["action_type"] == "create" and l["target_type"] == "question" for l in logs["items"])
    assert client.get("/api/v1/admin/audit", headers=s["th"]).status_code == 403


def test_resume_in_progress_record(client):
    """续答: 同卷 in_progress 期间重复 start 不新建记录"""
    s = _bootstrap(client)
    q = _mk_q(client, s["ah"], answer=["A"])
    ex = _mk_exam(client, s["ah"], s["ecat"]["id"], [q["id"]], title="续答卷")
    r1 = client.post("/api/v1/records/start", json={"exam_id": ex["id"]}, headers=s["uh"]).json()["data"]
    r2 = client.post("/api/v1/records/start", json={"exam_id": ex["id"]}, headers=s["uh"]).json()["data"]
    assert r1["record_id"] == r2["record_id"]
    assert r2["end_time"] is None and r2["server_now"]
