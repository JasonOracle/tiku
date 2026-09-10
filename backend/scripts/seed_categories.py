# -*- coding: utf-8 -*-
"""建分类（两租户各 12 资源 + 8 任务）并回填任务/条目归属。经 nginx，打上帝+管理员 token。"""
import httpx

BASE = "http://127.0.0.1"
RES_CATS = ["金融类", "工程类", "自考类", "历史类", "考公类", "土木类",
            "计算机类", "医学类", "法律类", "英语类", "数学类", "综合素质类"]
TASK_CATS = ["趣味知识", "专业问答", "心理测试", "月底测验",
             "入职培训", "季度考核", "技能认证", "模拟考试"]
ADMINS = {1: "13800000011", 2: "13800000012"}

c = httpx.Client(base_url=BASE, timeout=60)


def jp(r):
    assert r.status_code in (200, 201), f"{r.status_code} {r.request.url.path}: {r.text[:200]}"
    d = r.json()
    assert d.get("code") in (200, 201), d
    return d["data"]


def login(phone, pw="123456"):
    return jp(c.post("/api/v1/auth/login", json={"phone": phone, "password": pw}))["token"]


KEYMAP = [("金融", "金融类"), ("风险", "金融类"), ("VaR", "金融类"), ("基金", "金融类"),
          ("拨备", "金融类"), ("历史", "历史类"), ("洋务", "历史类"), ("虎门", "历史类"),
          ("代码", "计算机类"), ("网络", "计算机类"), ("数据库", "计算机类"),
          ("疾病", "医学类"), ("药品", "医学类"), ("合同", "法律类"), ("法规", "法律类"),
          ("单词", "英语类"), ("语法", "英语类"), ("函数", "数学类"), ("几何", "数学类")]

for tid, adm in ADMINS.items():
    H = {"Authorization": f"Bearer {login(adm)}", "X-Tenant-ID": str(tid)}
    rc, tc = {}, {}
    for name in RES_CATS:
        rc[name] = jp(c.post("/api/v1/admin/categories", headers=H,
                             json={"name": name, "target_type": "resource"}))["id"]
    for name in TASK_CATS:
        tc[name] = jp(c.post("/api/v1/admin/categories", headers=H,
                             json={"name": name, "target_type": "task"}))["id"]
    print(f"tenant{tid}: resource_cats={len(rc)} task_cats={len(tc)}")
    # 任务归属
    tasks = jp(c.get("/api/v1/admin/tasks", headers=H, params={"page": 1, "size": 50}))["items"]
    for t in tasks:
        title = t["title"]
        if "金融" in title:
            cat = tc["专业问答"]
        elif "历史" in title:
            cat = tc["趣味知识"]
        elif "合规" in title or "行政" in title:
            cat = tc["月底测验"]
        else:
            cat = tc["专业问答"]
        jp(c.put(f"/api/v1/admin/tasks/{t['id']}", headers=H, json={"category_id": cat}))
        print(f"  task {t['id']}《{title[:14]}》-> cat {cat}")
    # 条目归属
    res = jp(c.get("/api/v1/admin/resources", headers=H, params={"page": 1, "size": 100}))["items"]
    n = 0
    for r in res:
        content = r.get("content") or ""
        cat = None
        for kw, cname in KEYMAP:
            if kw in content:
                cat = rc[cname]
                break
        if cat is None:
            cat = rc["自考类"]
        jp(c.put(f"/api/v1/admin/resources/{r['id']}", headers=H, json={"category_id": cat}))
        n += 1
    print(f"  resources assigned: {n}")
    # 断言
    tasks2 = jp(c.get("/api/v1/admin/tasks", headers=H, params={"page": 1, "size": 50}))["items"]
    assert all(t["category_id"] for t in tasks2), "任务分类非空断言失败"
    res2 = jp(c.get("/api/v1/admin/resources", headers=H, params={"page": 1, "size": 100}))["items"]
    assert all(r["category_id"] for r in res2), "条目分类非空断言失败"
print("CATEGORIES DONE")
