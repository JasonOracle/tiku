/**
 * pwdrive.js —— playwright-cli 批处理驱动器
 *
 * 背景：本机 PowerShell 沙箱内 .NET 文件读取异常（ReadAllText 返回空），
 *       且 PowerShell 5.1 向原生命令传参会吞掉双引号，中文/长文本极易被破坏。
 *       故改用 Node 作为驱动层：文件读取与子进程参数传递均为确定的 UTF-8。
 *
 * 约束：沙箱会在一次工具调用结束后回收整个进程树，浏览器无法跨调用存活。
 *       因此每次调用 = 一次完整浏览器会话；登录态用 state-save / state-load 落盘复用。
 *
 * 用法： node pwdrive.js <命令文件> [日志文件]
 * 命令文件：每行一条指令，`|` 分隔参数；`#` 开头为注释；支持伪指令 sleep|<毫秒>
 */
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const NODE = process.execPath;
const PCLI = "C:\\Users\\Administrator\\.workbuddy\\binaries\\node\\workspace\\node_modules\\@playwright\\cli\\playwright-cli.js";
const CWD = "D:\\project\\tiku\\tiku";

const cmdFile = process.argv[2];
const logFile = process.argv[3] || path.join(CWD, ".workbuddy", "logs", "pwdrive.log");

if (!cmdFile) {
  console.error("用法: node pwdrive.js <命令文件> [日志文件]");
  process.exit(1);
}

const out = [];
function log(s) {
  out.push(s);
  console.log(s);
}

const raw = fs.readFileSync(cmdFile, "utf8");
const lines = raw.split(/\r?\n/).map((l) => l.trim()).filter((l) => l !== "" && !l.startsWith("#"));

log(`# pwdrive 启动 | 命令文件=${path.basename(cmdFile)} | 有效指令=${lines.length}`);
log(`# ${new Date().toISOString()}`);

function sleepSync(ms) {
  const sab = new SharedArrayBuffer(4);
  Atomics.wait(new Int32Array(sab), 0, 0, ms);
}

let idx = 0;
for (const line of lines) {
  idx++;
  const parts = line.split("|").map((s) => s.trim());
  const cmd = parts[0];

  if (cmd === "sleep") {
    const ms = parseInt(parts[1] || "1000", 10);
    log(`\n----- [${idx}] sleep ${ms}ms`);
    sleepSync(ms);
    continue;
  }

  const args = parts.slice();
  log(`\n===== [${idx}] ${args.join(" ")}`);
  try {
    const r = spawnSync(NODE, [PCLI, ...args], {
      cwd: CWD,
      encoding: "utf8",
      maxBuffer: 64 * 1024 * 1024,
    });
    const text = `${r.stdout || ""}${r.stderr || ""}`.trim();
    log(text || "(无输出)");
  } catch (e) {
    log("EXCEPTION: " + e.message);
  }
  sleepSync(500);
}

log(`\n# pwdrive 结束 | 共执行 ${idx} 条指令`);
fs.mkdirSync(path.dirname(logFile), { recursive: true });
fs.writeFileSync(logFile, out.join("\n"), "utf8");
