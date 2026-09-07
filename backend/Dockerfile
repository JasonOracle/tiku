FROM python:3.12-slim

WORKDIR /app

# 安装 ca-certificates 确保访问 TiDB Cloud 等外部 SSL 安全连接
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary bcrypt -r requirements.txt

COPY . .

ENV PORT=7860
EXPOSE 7860

# 启动命令使用 shell 形式读取 PORT 环境变量，默认兼容 HuggingFace(7860) 与常见云容器
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860} --workers 2"]

