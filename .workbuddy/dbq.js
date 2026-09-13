const { spawnSync } = require("child_process");
const DOCKER = "C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe";

function sql(q) {
  const r = spawnSync(DOCKER, ["exec", "tiku_mysql", "mysql", "-uroot", "-prootpassword", "--default-character-set=utf8mb4", "-N", "-e", q], {
    encoding: "utf8",
    maxBuffer: 32 * 1024 * 1024,
  });
  return (r.stdout || "").trim();
}

const out = [];
out.push("=== 租户列表 ===");
out.push(sql("SELECT id,name,short_name,industry,scale,contact_name,status FROM tiku_db.sys_tenant ORDER BY id;"));
out.push("");
out.push("=== WB测试机构(id=6) 成员 ===");
out.push(sql("SELECT id,phone,display_name,is_super_admin FROM tiku_db.sys_user WHERE id IN (SELECT user_id FROM tiku_db.sys_tenant_user WHERE tenant_id=6) ORDER BY id;"));
out.push("(空表示暂无成员)");
out.push("");
out.push("=== sys_tenant_user 全表 ===");
out.push(sql("SELECT id,tenant_id,user_id,role FROM tiku_db.sys_tenant_user ORDER BY id;"));

const fs = require("fs");
fs.writeFileSync("D:\\project\\tiku\\tiku\\.workbuddy\\logs\\db_p1.txt", out.join("\n"), "utf8");
console.log(out.join("\n"));
