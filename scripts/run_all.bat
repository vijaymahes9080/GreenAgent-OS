@echo off
echo ======================================================================
echo   Starting GreenAgent OS Services (Backend + Frontend)
echo ======================================================================

echo [1/2] Launching GreenAgent OS FastAPI Backend on http://localhost:8000 ...
start "GreenAgent-Backend" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Launching GreenAgent OS Dashboard on http://localhost:5173 ...
start "GreenAgent-Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All services launched!
echo - API & Swagger Docs: http://localhost:8000/docs
echo - React Dashboard:   http://localhost:5173
echo ======================================================================
