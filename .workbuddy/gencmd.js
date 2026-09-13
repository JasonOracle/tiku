// 生成 5 个「录入 C 端考生」命令文件
// 关键：快照调用序列必须与探针（cmd-p2x.txt）完全镜像，否则 ref 编号会漂移
const fs = require("fs");

const STUDENTS = [
  ["13911111101", "WB学员01"],
  ["13911111102", "WB学员02"],
  ["13911111103", "WB学员03"],
  ["13911111104", "WB学员04"],
  ["13911111105", "WB学员05"],
];

const tpl = (phone, name, idx) =>
  [
    "# 阶段二 · 录入 C 端考生 " + phone,
    "open|http://127.0.0.1/admin/",
    "sleep|2500",
    "state-load|.workbuddy/auth-admin-wb6.json",
    "sleep|500",
    "reload",
    "sleep|3000",
    "goto|http://127.0.0.1/admin/members",
    "sleep|3000",
    "fill|f2e87|zzz-nomatch-member",
    "sleep|1500",
    "snapshot|--filename=p2x-pre.yaml",
    "click|f2e90",
    "sleep|2000",
    "snapshot|--filename=p2x-dialog.yaml",
    "fill|f2e213|" + phone,
    "fill|f2e219|" + name,
    "sleep|600",
    "click|f2e300",
    "sleep|3000",
    "snapshot|--filename=p2s" + idx + "-result.yaml",
    "screenshot|--filename=p2s" + idx + "-result.png",
  ].join("\n");

STUDENTS.forEach(([p, n], i) => {
  const f = `D:\\project\\tiku\\tiku\\.workbuddy\\cmd-p2s${i + 1}.txt`;
  fs.writeFileSync(f, tpl(p, n, i + 1), "utf8");
  console.log("written " + f);
});
