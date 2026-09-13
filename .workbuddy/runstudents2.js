/**
 * runstudents2.js —— 用 run-code 角色定位器批量录入 C 端考生（规避 ref 漂移）
 *
 * 背景：playwright-cli 的 ref 编号在每次 snapshot 后都会重排，弹窗内的元素
 *       （手机号 / 姓名 / 保存）在不同会话中编号不同，硬编码 ref 必然失败。
 *       改用 `run-code --filename=<js>`，用 getByRole(role,{name}) 角色定位器驱动，
 *       完全不依赖 ref，也不再手写 CSS Selector。
 *
 * 用法: node runstudents2.js 2 3 4 5   （参数 = 学员序号）
 */
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const NODE = process.execPath;
const PWDIR = "D:\\project\\tiku\\tiku\\.workbuddy";
const CWD = "D:\\project\\tiku\\tiku";
const DOCKER = "C:\\Users\\Administrator\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe";

const STUDENTS = {
  1: ["13911111101", "WB学员01"],
  2: ["13911111102", "WB学员02"],
  3: ["13911111103", "WB学员03"],
  4: ["13911111104", "WB学员04"],
  5: ["13911111105", "WB学员05"],
};

function rcSrc(phone, name) {
  return `async (page) => {
  await page.getByRole('button', { name: '录入成员' }).click();
  await page.waitForTimeout(1600);
  await page.getByRole('textbox', { name: '* 手机号' }).fill('${phone}');
  await page.getByRole('textbox', { name: '姓名', exact: true }).fill('${name}');
  await page.waitForTimeout(600);
  await page.getByRole('button', { name: '保存' }).click();
  await page.waitForTimeout(2800);
}
`;
}

function cmdSrc(rcRel) {
  return [
    "# 录入会话",
    "open|http://127.0.0.1/admin/",
    "sleep|2500",
    "state-load|.workbuddy/auth-admin-wb6.json",
    "sleep|500",
    "reload",
    "sleep|3500",
    "goto|http://127.0.0.1/admin/members",
    "sleep|3500",
    "run-code|--filename=" + rcRel,
    "sleep|2000",
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
  const rcRel = `.workbuddy/rc-s${idx}.js`;
  fs.writeFileSync(path.join(PWDIR, `rc-s${idx}.js`), rcSrc(phone, name), "utf8");
  const cmdFile = path.join(PWDIR, `cmd-rs${idx}.txt`);
  fs.writeFileSync(cmdFile, cmdSrc(rcRel), "utf8");
  spawnSync(NODE, [path.join(PWDIR, "pwdrive.js"), cmdFile, path.join(PWDIR, "logs", `rs${idx}.log`)], {
    encoding: "utf8", cwd: CWD, maxBuffer: 64 * 1024 * 1024,
  });
  console.log(`RUN   ${phone} -> ${exists(phone) ? "OK 已落库" : "FAIL 未落库"}`);
}
