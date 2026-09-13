const http = require("http");
function req(path, method, headers, body) {
  return new Promise((resolve) => {
    const r = http.request({ host: "127.0.0.1", port: 8000, path, method, headers }, (res) => {
      let d = ""; res.on("data", (c) => d += c); res.on("end", () => resolve(d));
    });
    r.on("error", (e) => resolve("ERR " + e.message));
    if (body) r.write(body); r.end();
  });
}
(async () => {
  const lb = JSON.stringify({ phone: "13911111101", password: "123456" });
  const lj = JSON.parse(await req("/api/v1/auth/login", "POST", { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(lb) }, lb));
  const tok = lj.data.token;
  const body = JSON.stringify({ message: "请回答：1+1等于几？", session_id: null });
  const raw = await req("/api/v1/admin/ai/chat/stream", "POST", { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body), Authorization: `Bearer ${tok}`, "X-Tenant-ID": "6" }, body);
  console.log("RAW LEN", raw.length);
  console.log(raw.slice(0, 2500));
})();
