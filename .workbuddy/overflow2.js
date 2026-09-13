/**
 * overflow2.js —— LLM-SYS-02 超大上下文溢出：分别打 网关(80) 与 后端(8000)，稳健捕获状态码
 */
const http = require("http");

function post(port, path, bodyStr, headers) {
  return new Promise((resolve) => {
    const req = http.request(
      { host: "127.0.0.1", port, path, method: "POST", headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(bodyStr), ...headers } },
      (res) => {
        let data = "";
        res.on("data", (c) => { data += c; if (data.length > 400) req.destroy(); });
        res.on("end", () => resolve({ status: res.statusCode, body: data.slice(0, 200) }));
        res.on("error", (e) => resolve({ status: res.statusCode, body: "STREAM_ERR " + e.message, partial: data.slice(0, 200) }));
      }
    );
    req.on("error", (e) => resolve({ status: "ERR", body: e.message }));
    req.write(bodyStr);
    req.end();
  });
}

(async () => {
  // 取 token
  const loginBody = JSON.stringify({ phone: "13811111111", password: "123456" });
  const login = await new Promise((resolve) => {
    const req = http.request({ host: "127.0.0.1", port: 8000, path: "/api/v1/auth/login", method: "POST", headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(loginBody), "X-Client": "admin" } }, (res) => {
      let d = ""; res.on("data", (c) => d += c); res.on("end", () => resolve(JSON.parse(d)));
    });
    req.write(loginBody); req.end();
  });
  const token = login.data.token;
  const H = { Authorization: `Bearer ${token}`, "X-Tenant-ID": "6" };

  const big = "无".repeat(200000); // 20 万汉字 ≈ 600KB
  console.log("payload bytes:", Buffer.byteLength(big));

  // 1) 网关 nginx:80 （验证 client_max_body_size / 网关层拦截）
  const viaNginx = await post(80, "/api/v1/admin/ai/questions/generate", JSON.stringify({ material: big, types: ["single"], count: 1 }), H);
  console.log("[nginx:80 ] questions/generate ->", viaNginx.status, viaNginx.body);

  // 2) 后端直连 8000
  const viaBackend = await post(8000, "/api/v1/admin/ai/questions/generate", JSON.stringify({ material: big, types: ["single"], count: 1 }), H);
  console.log("[back :8000] questions/generate ->", viaBackend.status, viaBackend.body);

  // 3) 后端健康存活探测
  const health = await new Promise((resolve) => {
    http.get({ host: "127.0.0.1", port: 8000, path: "/docs" }, (res) => { res.resume(); resolve(res.statusCode); }).on("error", (e) => resolve("ERR " + e.message));
  });
  console.log("[health] GET /docs ->", health, "(200 = 后端未崩溃)");
})();
