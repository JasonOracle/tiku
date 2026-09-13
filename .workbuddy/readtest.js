const fs = require("fs");
const p = "D:/project/tiku/tiku/.workbuddy/cmd-p1a.txt";
const s = fs.readFileSync(p, "utf8");
const lines = s.split(/\r?\n/).filter((l) => l.trim() !== "" && !l.trim().startsWith("#"));
console.log("len=" + s.length);
console.log("allLines=" + s.split(/\r?\n/).length);
console.log("effLines=" + lines.length);
console.log("first=" + lines[0]);
