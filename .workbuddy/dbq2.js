const { spawnSync } = require("child_process");
const fs = require("fs");
const DOCKER = "C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe";
function sql(q) {
  const r = spawnSync(DOCKER, ["exec", "tiku_mysql", "mysql", "-uroot", "-prootpassword", "--default-character-set=utf8mb4", "-N", "-e", q], { encoding: "utf8", maxBuffer: 32 * 1024 * 1024 });
  return (r.stdout || "").trim();
}
const o = [];
o.push("=== sys_user 全量(含新账号) ===");
o.push(sql("SELECT id,phone,display_name,is_super_admin FROM tiku_db.sys_user ORDER BY id;"));
o.push("");
o.push("=== tenant 6 成员关系 ===");
o.push(sql("SELECT tu.user_id,u.phone,u.display_name,tu.role FROM tiku_db.sys_tenant_user tu JOIN tiku_db.sys_user u ON u.id=tu.user_id WHERE tu.tenant_id=6;"));
o.push("(空=无)");
fs.writeFileSync("D:\\project\\tiku\\tiku\\.workbuddy\\logs\\db_p1j.txt", o.join("\n"), "utf8");
console.log("ok");
