FROM python:3.12-slim

WORKDIR /app

# bcrypt 官方发布了 manylinux 预编译 wheel，无需 gcc。
# pymysql 是纯 Python，也无需 C 编译器。
# 直接用 pip --only-binary :all: 强制使用预编译 wheel。
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary bcrypt -r requirements.txt

COPY . .

EXPOSE 8000

# 生产模式：4 worker 进程，关闭 reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
