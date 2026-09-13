/**
 * api.js —— 接口级测试（不依赖浏览器）
 * 用法: node api.js <step>
 *   publish     发布 task 39 并让学员端可见
 *   member      C 端学员查任务列表
 *   ratelimit   LLM-SYS-01 突发防刷探测
 *   overflow    LLM-SYS-02 超大上下文
 *   idem        LLM-SYS-05 组卷幂等性重放
 */
const BASE = "http://127.0.0.1:8000";

async function login(phone, password, client) {
  const headers = { "Content-Type": "application/json" };
  if (client) headers["X-Client"] = client;
  const r = await fetch(`${BASE}/api/v1/auth/login`, {
    method: "POST", headers, body: JSON.stringify({ phone, password }),
  });
  const j = await r.json().catch(() => ({}));
  if (!j.data || !j.data.token) throw new Error("login failed: " + r.status + " " + JSON.stringify(j));
  return j.data.token;
}

async function admin() { return login("13811111111", "123456", "admin"); }
async function student(phone) { return login(phone, "123456"); }

const A = (t) => ({ "Content-Type": "application/json", Authorization: `Bearer ${t}`, "X-Tenant-ID": "6" });

const step = process.argv[2] || "publish";

(async () => {
  if (step === "publish") {
    const t = await admin();
    const r = await fetch(`${BASE}/api/v1/admin/tasks/39/status?status=published`, { method: "PUT", headers: A(t) });
    console.log("publish task39:", r.status, await r.text());
    const lr = await fetch(`${BASE}/api/v1/admin/tasks?page=1&page_size=50`, { headers: A(t) });
    const lj = await lr.json();
    const items = (lj.data && (lj.data.items || lj.data)) || [];
    console.log("admin tasks:", JSON.stringify(items.slice(0, 3)));
  }

  if (step === "member") {
    for (const phone of ["13911111101", "13911111105"]) {
      const t = await student(phone);
      const r = await fetch(`${BASE}/api/v1/member/member-tasks`, { headers: A(t) });
      const j = await r.json();
      const items = (j.data && j.data.items) || [];
      console.log(`member ${phone} tasks:`, JSON.stringify(items.map(i => ({ task_id: i.task_id, title: i.title, status: i.status, deadline: i.deadline, start_time: i.start_time }))));
      // 越权探测：尝试进入不属于自己的 task 999
      const e = await fetch(`${BASE}/api/v1/member/tasks/999/entry`, { headers: A(t) });
      console.log(`member ${phone} entry#999:`, e.status, (await e.text()).slice(0, 120));
    }
  }

  if (step === "ratelimit") {
    const t = await admin();
    const N = 100;
    const body = JSON.stringify({ material: "网络安全基础", types: ["single"], count: 1, difficulty: "medium" });
    const t0 = Date.now();
    const tasks = [];
    for (let i = 0; i < N; i++) {
      tasks.push(fetch(`${BASE}/api/v1/admin/ai/questions/generate`, { method: "POST", headers: A(t), body })
        .then(async (r) => r.status).catch((e) => "ERR:" + e.message));
    }
    const codes = await Promise.all(tasks);
    const hist = {};
    for (const c of codes) hist[c] = (hist[c] || 0) + 1;
    console.log(`ratelimit burst N=${N} in ${Date.now() - t0}ms ->`, JSON.stringify(hist));
    console.log("429 count:", hist[429] || 0);
  }

  if (step === "overflow") {
    const t = await admin();
    const big = "无".repeat(200000); // 20 万字符
    const body = JSON.stringify({ message: big, session_id: null });
    const r = await fetch(`${BASE}/api/v1/admin/ai/chat/stream`, { method: "POST", headers: A(t), body });
    console.log("overflow chat/stream:", r.status, "resp:", (await r.text()).slice(0, 200));
    const r2 = await fetch(`${BASE}/api/v1/admin/ai/questions/generate`, {
      method: "POST", headers: A(t),
      body: JSON.stringify({ material: big, types: ["single"], count: 1 }),
    });
    console.log("overflow questions/generate:", r2.status, "resp:", (await r2.text()).slice(0, 200));
  }

  if (step === "xtenant") {
    const t = await admin(); // 13811111111 只属于租户 6
    for (const tid of ["1", "999"]) {
      const r = await fetch(`${BASE}/api/v1/admin/tasks?page=1&page_size=10`, {
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}`, "X-Tenant-ID": tid },
      });
      console.log(`admin(tenant6) -> X-Tenant-ID:${tid} :`, r.status, (await r.text()).slice(0, 160));
    }
  }

  if (step === "idem") {
    const t = await admin();
    const before = await (await fetch(`${BASE}/api/v1/admin/tasks?page=1&page_size=100`, { headers: A(t) })).json();
    const cnt = (b) => ((b.data && (b.data.items || b.data)) || []).length;
    const n0 = cnt(before);
    const body = JSON.stringify({ title: "幂等性重放测试卷", description: "幂等性测试", specs: [{ q_type: "single", count: 2 }] });
    const r1 = await fetch(`${BASE}/api/v1/admin/ai/exams/generate`, { method: "POST", headers: A(t), body });
    const j1 = await r1.json().catch(() => ({}));
    console.log("idem #1:", r1.status, JSON.stringify(j1).slice(0, 160));
    const r2 = await fetch(`${BASE}/api/v1/admin/ai/exams/generate`, { method: "POST", headers: A(t), body });
    const j2 = await r2.json().catch(() => ({}));
    console.log("idem #2:", r2.status, JSON.stringify(j2).slice(0, 160));
    const after = await (await fetch(`${BASE}/api/v1/admin/tasks?page=1&page_size=100`, { headers: A(t) })).json();
    const n1 = cnt(after);
    console.log(`tasks before=${n0} after=${n1} delta=${n1 - n0} (期望 delta=0 表示幂等)`);
  }
})().catch((e) => { console.error("FATAL", e); process.exit(1); });
