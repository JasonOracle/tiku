"""
生成静态 Swagger API 文档与 OpenAPI 规范文件至 tob/public/
供国内网络直连访问 (Cloudflare Pages 托管)，避免 *.vercel.app 域名受阻断。
"""
import json
import os
import sys

# 将 backend 路径加入 sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from app.main import app
    schema = app.openapi()
except Exception as e:
    print(f"[-] 导入 app.main 失败: {e}，尝试从线上 Vercel 获取最新 schema...")
    import urllib.request
    req = urllib.request.Request("https://tiku-api.vercel.app/openapi.json", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        schema = json.loads(resp.read().decode("utf-8"))

tob_public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tob", "public"))
os.makedirs(tob_public_dir, exist_ok=True)

# 1. 写入 openapi.json
openapi_file = os.path.join(tob_public_dir, "openapi.json")
with open(openapi_file, "w", encoding="utf-8") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)
print(f"[+] 成功生成: {openapi_file}")

# 2. 写入 docs.html
docs_file = os.path.join(tob_public_dir, "docs.html")
html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>智题库 (TiKu) 接口文档 - Swagger UI</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui.min.css">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <style>
    body {
      margin: 0;
      background: #fafafa;
    }
    .top-banner {
      background: #1890ff;
      color: #fff;
      padding: 10px 20px;
      font-size: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .top-banner a {
      color: #fff;
      text-decoration: underline;
      margin-left: 12px;
    }
  </style>
</head>
<body>
  <div class="top-banner">
    <span>💡 提示：本页面由 Cloudflare Pages 全球 CDN 加速直连托管，国内网络秒开。</span>
    <div>
      <a href="/dashboard">进入 B 端管理台</a>
      <a href="https://tiku-toc-new.pages.dev" target="_blank">进入 C 端考场</a>
    </div>
  </div>
  <div id="swagger-ui"></div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui-bundle.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui-standalone-preset.min.js"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: './openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout"
      });
    };
  </script>
</body>
</html>
"""
with open(docs_file, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"[+] 成功生成: {docs_file}")
print("[+] 静态 Swagger API 文档生成完毕！")
