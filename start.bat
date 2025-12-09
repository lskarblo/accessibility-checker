@echo off
echo ============================================================
echo PowerPoint ^& PDF Accessibility Checker
echo ============================================================
echo.
echo Starting server...
echo.

cd /d "%~dp0"
uv run python start_server.py

pause
