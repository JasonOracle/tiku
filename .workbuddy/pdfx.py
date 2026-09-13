import io
import json
import pypdf

res = {}
for name in ["火星员工守则", "恶意投毒样本"]:
    p = rf"D:\project\tiku\tiku\.workbuddy\test-assets\{name}.pdf"
    r = pypdf.PdfReader(p)
    t = "\n".join((pg.extract_text() or "") for pg in r.pages)
    res[name] = {"chars": len(t), "head": t[:200], "has_cjk": any("\u4e00" <= ch <= "\u9fff" for ch in t)}

with open(r"D:\project\tiku\tiku\.workbuddy\pdfx_result.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
print("done")
