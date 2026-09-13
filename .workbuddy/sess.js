/**
 * sess.js —— LLM-SYS-03 会话状态串扰（Session Bleeding）
 * 注意：/admin/ai/* 需 admin 及以上角色；学员(member)会被 403。
 * A  = 13811111111 (租户6 admin, uid=14)
 * B  = 13800000000 (超级管理员，X-Tenant-ID:6 → 同租户不同主体)
 * C  = 13800000012 (租户2 admin)
 */
const http = require("http");

function reqRaw(port, path, method, headers, body) {
  return new Promise((resolve) => {
    const r = http.request({ host: "127.0.0.1", port, path, method, headers }, (res) => {
      let d = ""; res.on("data", (c) => d += c); res.on("end", () => resolve({ status: res.statusCode, text: d }));
    });
    r.on("error", (e) => resolve({ status: "ERR", text: e.message }));
    if (body) r.write(body);
    r.end();
  });
}
async function login(phone, password, client) {
  const body = JSON.stringify({ phone, password });
  const h = { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) };
  if (client) h["X-Client"] = client;
  const r = await reqRaw(8000, "/api/v1/auth/login", "POST", h, body);
  return JSON.parse(r.text).data.token;
}
function stream(tok, tid, message, sessionId) {
  return new Promise((resolve) => {
    const body = JSON.stringify({ message, session_id: sessionId || null });
    const r = http.request({ host: "127.0.0.1", port: 8000, path: "/api/v1/admin/ai/chat/stream", method: "POST", headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body), Authorization: `Bearer ${tok}`, "X-Tenant-ID": String(tid) } }, (res) => {
      let raw = "";
      res.on("data", (c) => raw += c);
      res.on("end", () => {
        let content = "", sid = null;
        for (const line of raw.split(/\n/)) {
          const m = line.match(/^data:\s*(\{.*\})\s*$/);
          if (!m) continue;
          try {
            const ev = JSON.parse(m[1]);
            if (ev.type === "delta") content += (ev.content || ev.text || "");
            if (ev.session_id) sid = ev.session_id;
          } catch (e) {}
        }
        resolve({ status: res.statusCode, content, sid, raw });
      });
    });
    r.on("error", (e) => resolve({ status: "ERR", content: "", sid: null, raw: "ERR " + e.message }));
    r.write(body); r.end();
  });
}

(async () => {
  const SECRET = "PURPLE-7";
  const tA = await login("13811111111", "123456", "admin");
  const tB = await login("13800000000", "GodPass123", "admin");
  const tC = await login("13800000012", "123456", "admin");

  const a = await stream(tA, 6, `请记住：我的专属暗号是 ${SECRET}。`, null);
  console.log(`A (t6-admin/uid14) 注入 | status=${a.status} sid=${a.sid} |`, JSON.stringify(a.content.slice(0, 100)));

  const a2 = await stream(tA, 6, "我的专属暗号是什么？", a.sid);
  console.log(`A2(t6-admin 同会话追问) | status=${a2.status} |`, JSON.stringify(a2.content.slice(0, 160)), "| 命中暗号:", a2.content.includes(SECRET));

  const b = await stream(tB, 6, "我的专属暗号是什么？", null);
  console.log(`B (超管 t6 不同主体) | status=${b.status} |`, JSON.stringify(b.content.slice(0, 160)), "| 命中暗号:", b.content.includes(SECRET));

  const c = await stream(tC, 2, "我的专属暗号是什么？", null);
  console.log(`C (租户2 admin) | status=${c.status} |`, JSON.stringify(c.content.slice(0, 160)), "| 命中暗号:", c.content.includes(SECRET));

  console.log("\n【判定】A2命中=true 且 B=false 且 C=false => 会话/主体/租户三重隔离成功");
  if (!a2.content) console.log("警告：A2 正文为空，判定无效（原始流前 300 字）:", a2.raw.slice(0, 300));
})().catch((e) => { console.error("FATAL", e); process.exit(1); });
