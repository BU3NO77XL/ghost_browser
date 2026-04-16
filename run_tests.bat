@echo off
chcp 65001 >nul
uv run python run_tests.py %*
if errorlevel 1 (
    echo.
    echo   Testes finalizados com falhas. Pressione qualquer tecla para fechar...
    pause >nul
)
