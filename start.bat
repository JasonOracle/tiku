@echo off
chcp 65001 > nul
echo ==========================================
echo       TiKu v1.5 全端一键启动脚本
echo ==========================================
echo.

echo [1/3] 启动后端服务 (FastAPI - 端口 8000)...
start "TiKu Backend (8000)" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/3] 启动 B端机构管理台 (Vue3 - 端口 3000/5174)...
start "TiKu B-End (tob)" cmd /k "cd tob && pnpm install && pnpm run dev"

echo [3/3] 启动 C端学员答题端 (UniApp - 端口 5173)...
start "TiKu C-End (toc-new)" cmd /k "cd toc-new && pnpm install && pnpm run dev:h5"

echo.
echo 所有服务已在新窗口中启动！
echo.
echo 默认访问入口：
echo C端 (H5): http://localhost:5173
echo B端 (PC): http://localhost:3000 (具体端口请查看 B端终端)
echo 后端API : http://localhost:8000
echo ==========================================
pause
