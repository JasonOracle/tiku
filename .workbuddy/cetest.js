/**
 * cetest.js —— C 端全生命周期（APP-01~05）
 * 用法: node cetest.js <app3|app4|app2|app5>
 * 说明：直接调用 C 端 H5 实际使用的 member 接口（与页面同源同契约），
 *       UI 层已在 APP-01 通过浏览器实测过一次，其余走接口以保证确定性与可重复性。
 */
const { spawnSync } = require("child_process");
const BASE = "http://127.0.0.1:8000";
const DOCKER = "C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe";

function sql(q) {
  const r = spawnSync(DOCKER, ["exec", "tiku_mysql", "mysql", "-uroot", "-prootpassword", "--default-character-set=utf8mb4", "-N", "-e", "use tiku_db; " + q], { encoding: "utf8" });
  return (r.stdout || "").trim();
}
async function login(phone, client) {
  const h = { "Content-Type": "application/json" };
  if (client) h["X-Client"] = client;
  const r = await fetch(`${BASE}/api/v1/auth/login`, { method: "POST", headers: h, body: JSON.stringify({ phone, password: "123456" }) });
  const j = await r.json();
  if (!j.data || !j.data.token) throw new Error("login fail " + phone + " " + JSON.stringify(j));
  return j.data.token;
}
const H = (t, tid) => ({ "Content-Type": "application/json", Authorization: `Bearer ${t}`, "X-Tenant-ID": String(tid) });

(async () => {
  const step = process.argv[2];

  if (step === "app3") {
    // APP-03 防泄题脱敏：学员 13911111101 提交混合卷(task 39, 含简答) -> pending_verification & correct_answer=null
    const st = await login("13911111101");
    const admin = await login("13811111111", "admin");
    // 取 task39 的题目与正确答案（测试者视角）
    const rows = sql("SELECT tr.resource_id, tr.score, r.type, r.correct_answer FROM task_resources tr JOIN resources r ON r.id=tr.resource_id WHERE tr.task_id=39 ORDER BY tr.sort_order;");
    const lines = rows.split(/\r?\n/).filter(Boolean).map(l => l.split("\t"));
    const answers = [];
    for (const [rid, score, type, ca] of lines) {
      let caN = [];
      try { caN = JSON.parse(ca || "[]"); } catch (e) { caN = [ca]; }
      let ans;
      if (type === "short" || type === "short_answer") ans = "测评作答：略";
      else if (type === "judge") ans = [String(caN[0] || "").toUpperCase() === "FALSE" ? "B" : "A"];
      else if (type === "single" || type === "single_choice") ans = [String(caN[0] || "").toUpperCase()];
      else ans = Array.isArray(caN) ? caN.map(x => String(x).toUpperCase()) : [String(caN).toUpperCase()];
      answers.push({ resource_id: Number(rid), answer: ans });
    }
    const r = await fetch(`${BASE}/api/v1/member/task-records/submit`, { method: "POST", headers: H(st, 6), body: JSON.stringify({ task_id: 39, answers }) });
    const j = await r.json();
    console.log("APP-03 submit:", r.status, JSON.stringify(j).slice(0, 220));
    const rid = j.data && j.data.record_id;
    const res = await fetch(`${BASE}/api/v1/member/task-records/${rid}`, { headers: H(st, 6) });
    const rj = await res.json();
    const d = rj.data || {};
    const withCA = (d.items || []).filter(i => i.correct_answer !== null && i.correct_answer !== undefined);
    console.log("APP-03 result status:", d.status, "| pending:", d.pending, "| 返回正确答案条数:", withCA.length, "(应为 0)");
  }

  if (step === "app4") {
    // APP-04 未及格：创建纯客观卷 -> 学员 13911111105 全部答错 -> 0 分 / 未及格
    const admin = await login("13811111111", "admin");
    const gen = await fetch(`${BASE}/api/v1/admin/ai/exams/generate`, { method: "POST", headers: H(admin, 6), body: JSON.stringify({ title: "WB客观题测试卷", description: "网络安全客观题", specs: [{ q_type: "single", count: 5 }] }) });
    const gj = await gen.json();
    const tid = gj.data && (gj.data.task_id || gj.data.exam_id);
    console.log("APP-04 created exam task:", tid, "| ", JSON.stringify(gj).slice(0, 120));
    await fetch(`${BASE}/api/v1/admin/tasks/${tid}/status?status=published`, { method: "PUT", headers: H(admin, 6) });
    sql(`UPDATE tasks SET deadline = DATE_ADD(NOW(), INTERVAL 2 DAY), start_time = NULL WHERE id=${tid};`);
    // 取正确答案，构造全部错误答案
    const rows = sql(`SELECT tr.resource_id, r.correct_answer FROM task_resources tr JOIN resources r ON r.id=tr.resource_id WHERE tr.task_id=${tid};`);
    const answers = [];
    for (const line of rows.split(/\r?\n/).filter(Boolean)) {
      const [rid, ca] = line.split("\t");
      let caN = []; try { caN = JSON.parse(ca || "[]"); } catch (e) { caN = [ca]; }
      const correct = String(caN[0] || "A").toUpperCase();
      const wrong = ["A", "B", "C", "D"].find(k => k !== correct) || "D";
      answers.push({ resource_id: Number(rid), answer: [wrong] });
    }
    const st = await login("13911111105");
    const r = await fetch(`${BASE}/api/v1/member/task-records/submit`, { method: "POST", headers: H(st, 6), body: JSON.stringify({ task_id: tid, answers }) });
    const sj = await r.json();
    console.log("APP-04 submit:", r.status, JSON.stringify(sj).slice(0, 200));
    const rid = sj.data && sj.data.record_id;
    const res = await fetch(`${BASE}/api/v1/member/task-records/${rid}`, { headers: H(st, 6) });
    const rj = await res.json();
    console.log("APP-04 result:", JSON.stringify({ status: rj.data && rj.data.status, score: rj.data && rj.data.score, passed: rj.data && rj.data.passed }));
    console.log("APP-04 不及格档人数(管理端统计依据):", sql(`SELECT COUNT(*) FROM task_records WHERE task_id=${tid} AND score < 60;`));
  }

  if (step === "app2") {
    // APP-02 未开始态拦截：把 task39 开考时间设为未来，学员 13911111102 强行进入
    const admin = await login("13811111111", "admin");
    sql("UPDATE tasks SET start_time = DATE_ADD(NOW(), INTERVAL 1 DAY) WHERE id=39;");
    const st = await login("13911111102");
    const r = await fetch(`${BASE}/api/v1/member/tasks/39/entry`, { headers: H(st, 6) });
    const txt = await r.text();
    console.log("APP-02 未到开考时间强行 entry ->", r.status, txt.slice(0, 200));
    console.log("APP-02 判定:", r.status === 403 || r.status === 400 ? "PASS 被拦截" : "FAIL 未被拦截（可提前开考）");
    sql("UPDATE tasks SET start_time = NULL WHERE id=39;"); // 还原
    console.log("APP-02 已还原 start_time=NULL");
  }

  if (step === "app5") {
    // APP-05 缺考：task39 截止时间设为过去，学员 13911111103 从未进入
    sql("UPDATE tasks SET deadline = DATE_SUB(NOW(), INTERVAL 1 DAY) WHERE id=39;");
    const before = sql("SELECT COUNT(*) FROM task_records WHERE task_id=39 AND user_id=(SELECT id FROM sys_user WHERE phone='13911111103');");
    const st = await login("13911111103");
    const r = await fetch(`${BASE}/api/v1/member/member-tasks`, { headers: H(st, 6) });
    const j = await r.json();
    const item = ((j.data && j.data.items) || []).find(i => i.task_id === 39);
    console.log("APP-05 缺考学员记录数(应=0):", before);
    console.log("APP-05 member-tasks 中 task39 状态:", item ? JSON.stringify({ status: item.status, deadline: item.deadline, record_id: item.record_id }) : "(未返回该卷)");
    const e = await fetch(`${BASE}/api/v1/member/tasks/39/entry`, { headers: H(st, 6) });
    console.log("APP-05 过截止后强行 entry ->", e.status, (await e.text()).slice(0, 160));
    sql("UPDATE tasks SET deadline = NULL WHERE id=39;"); // 还原
    console.log("APP-05 已还原 deadline=NULL");
  }
})().catch((e) => { console.error("FATAL", e); process.exit(1); });
