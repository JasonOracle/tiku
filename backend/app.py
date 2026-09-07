import os
import uvicorn
from app.main import app

# Hugging Face Spaces 原生支持以 app 为 ASGI 入口
# 同时也提供标准 uvicorn 兼容
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
