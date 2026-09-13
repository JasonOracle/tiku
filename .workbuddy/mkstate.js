/**
 * mkstate.js —— 用接口登录并生成 playwright storageState 文件
 * 用法: node mkstate.js <phone> <password> <tenantId|-> <outName> [role]
 * 例:   node mkstate.js 13800000012 123456 2 admin-t2 admin
 */
const fs = require("fs");
const path = require("path");
const BASE = "http://127.0.0.1:8000";

(async () => {
  const [phone, password, tenantId, outName, role] = process.argv.slice(2);
  const r = await fetch(`${BASE}/api/v1/auth/login`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Client": "admin" },
    body: JSON.stringify({ phone, password }),
  });
  const j = await r.json().catch(() => ({}));
  if (!j.data || !j.data.token) throw new Error("login failed " + r.status + " " + JSON.stringify(j));
  const d = j.data;
  const ls = [
    { name: "tiku_tob_token", value: d.token },
    { name: "tiku_tob_username", value: d.user.display_name || phone },
    { name: "tiku_tob_role", value: d.user.is_super_admin ? "super_admin" : (role || "admin") },
  ];
  if (tenantId && tenantId !== "-") ls.push({ name: "tiku_tob_tenant", value: String(tenantId) });
  if (d.user.is_super_admin) ls.push({ name: "tiku_tob_super", value: "1" });
  const state = { cookies: [], origins: [{ origin: "http://127.0.0.1", localStorage: ls }] };
  const out = path.join("D:\\project\\tiku\\tiku\\.workbuddy", `auth-${outName}.json`);
  fs.writeFileSync(out, JSON.stringify(state, null, 2), "utf8");
  console.log("wrote", out, "| user:", d.user.phone, "| tenants:", JSON.stringify(d.joined_tenants));
})().catch((e) => { console.error("FATAL", e.message); process.exit(1); });
