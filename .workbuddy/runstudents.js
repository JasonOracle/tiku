/**
 * runstudents.js —— 逐个录入 C 端考生并即时校验
 * 用法: node runstudents.js 2 3 4 5   （参数为待录入的学员序号）
 *
 * 设计原因：Element Plus 弹窗渲染存在时序抖动，会导致 playwright-cli 的 ref 编号漂移。
 * 因此每次录入后立即查库校验，失败的单独重试，避免"批量跑完才发现全挂"。
 */
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const NODE = process.execPath;
const PWDIR = "D:\\project\\tiku\\tiku\\.workbuddy";
const PCLI = "C:\\Users\\Administrator\\.workbuddy\\binaries\\node\\workspace\\node_modules\\@playwright\\cli\\playwright-cli.js";
const CWD = "D:\\project\\tiku\\tiku";
const DOCKER = "C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe";

const STUDENTS = {
  1: ["13911111101", "WB学员01"],
  2: ["13911111102", "WB学员02"],
  3: ["13911111103", "WB学员03"],
  4: ["13911111104", "WB学员04"],
  5: ["13911111105", "WB学员05"],
};

function buildCmds(phone, name, idx) {
  return [
    "# 录入 " + phone,
    "open|http://127.0.0.1/admin/",
    "sleep|2500",
    "state-load|.workbuddy/auth-admin-wb6.json",
    "sleep|500",
    "reload",
    "sleep|3000",
    "goto|http://127.0.0.1/admin/members",
    "sleep|3500",
    "fill|f2e87|zzz-nomatch-member",
    "sleep|2500",
    "snapshot|--filename=p2x-pre.yaml",
    "click|f2e90",
    "sleep|4500",
    "snapshot|--filename=p2x-dialog.yaml",
    "fill|f2e213|" + phone,
    "fill|f2e219|" + name,
    "sleep|1200",
    "click|f2e300",
    "sleep|4500",
    "snapshot|--filename=p2s" + idx + "-result.yaml",
    "screenshot|--filename=p2s" + idx + "-result.png",
  ].join("\n");
}

function exists(phone) {
  const r = spawnSync(DOCKER, ["exec", "tiku_mysql", "mysql", "-uroot", "-prootpassword", "-N", "-e",
    `SELECT COUNT(*) FROM tiku_db.sys_user WHERE phone='${phone}';`], { encoding: "utf8" });
  return parseInt((r.stdout || "0").trim(), 10) > 0;
}

const targets = process.argv.slice(2).map(Number);
for (const idx of targets) {
  const [phone, name] = STUDENTS[idx];
  if (exists(phone)) {
    console.log(`SKIP  ${phone} 已存在`);
    continue;
  }
  const cmdFile = path.join(PWDIR, `cmd-p2s${idx}.txt`);
  fs.writeFileSync(cmdFile, buildCmds(phone, name, idx), "utf8");
  spawnSync(NODE, [path.join(PWDIR, "pwdrive.js"), cmdFile, path.join(PWDIR, "logs", `p2s${idx}.log`)], {
    encoding: "utf8", cwd: CWD, maxBuffer: 64 * 1024 * 1024,
  });
  console.log(`RUN   ${phone} -> ${exists(phone) ? "OK 已落库" : "FAIL 未落库"}`);
}
