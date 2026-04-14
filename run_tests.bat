@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  STEALTH BROWSER MCP - TEST SUITE + DEVSECOPS
echo ============================================================
echo.

:: Create reports directory
if not exist "reports" mkdir reports

:: Check uv is available
where uv >nul 2>&1
if errorlevel 1 (
    echo [ERRO] uv nao encontrado. Instale em: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

:: Parse arguments
set RUN_UNIT=1
set RUN_BROWSER=1
set RUN_SECURITY=1
set OPEN_REPORT=1

if "%1"=="--unit-only"    set RUN_BROWSER=0  & set RUN_SECURITY=0
if "%1"=="--browser-only" set RUN_UNIT=0     & set RUN_SECURITY=0
if "%1"=="--security-only" set RUN_UNIT=0    & set RUN_BROWSER=0
if "%1"=="--no-open"      set OPEN_REPORT=0
if "%2"=="--no-open"      set OPEN_REPORT=0

echo.

:: ── SECURITY SCAN ────────────────────────────────────────────
if "%RUN_SECURITY%"=="1" (
    echo [SEC] Executando scan de seguranca ^(Bandit^)...
    echo --------------------------------------------------------

    uv run bandit -r src/ ^
        --severity-level medium ^
        --confidence-level medium ^
        -x src/.storage ^
        -f html -o reports/security-bandit.html ^
        2>&1

    if errorlevel 1 (
        echo [AVISO] Bandit encontrou issues de seguranca. Veja reports\security-bandit.html
        set SECURITY_FAILED=1
    ) else (
        echo [OK] Nenhum issue de seguranca Medium/High encontrado.
        set SECURITY_FAILED=0
    )
    echo.
)

:: ── UNIT TESTS (no browser) ──────────────────────────────────
if "%RUN_UNIT%"=="1" (
    echo [1/2] Executando testes unitarios ^(sem browser^)...
    echo --------------------------------------------------------

    uv run python -m pytest ^
        tests/test_core_modules.py ^
        tests/test_race_conditions.py ^
        tests/test_persistence.py ^
        tests/test_login_guard.py ^
        -v --tb=short ^
        --html=reports/unit-tests.html ^
        --self-contained-html ^
        --cov=src ^
        --cov-report=html:reports/coverage-html ^
        --cov-report=term-missing ^
        -p no:warnings ^
        2>&1

    if errorlevel 1 (
        echo.
        echo [FALHA] Testes unitarios falharam.
        set UNIT_FAILED=1
    ) else (
        echo.
        echo [OK] Testes unitarios passaram.
        set UNIT_FAILED=0
    )
    echo.
)

:: ── BROWSER TESTS ────────────────────────────────────────────
if "%RUN_BROWSER%"=="1" (
    echo [2/2] Executando testes com browser ^(Chrome necessario^)...
    echo --------------------------------------------------------

    uv run python -m pytest ^
        tests/test_final_smoke.py ^
        tests/test_mcp_tools.py ^
        tests/test_integration_full.py ^
        tests/test_browser_management.py ^
        tests/test_navigation.py ^
        tests/test_javascript.py ^
        tests/test_cookies.py ^
        tests/test_login_flow.py ^
        tests/test_instance_recovery.py ^
        tests/test_element_cloners.py ^
        -v --tb=short ^
        --html=reports/browser-tests.html ^
        --self-contained-html ^
        -p no:warnings ^
        2>&1

    if errorlevel 1 (
        echo.
        echo [FALHA] Testes com browser falharam.
        set BROWSER_FAILED=1
    ) else (
        echo.
        echo [OK] Testes com browser passaram.
        set BROWSER_FAILED=0
    )
    echo.
)

:: ── SUMMARY ──────────────────────────────────────────────────
echo ============================================================
echo  RESULTADO FINAL
echo ============================================================

if "%RUN_SECURITY%"=="1" (
    if "%SECURITY_FAILED%"=="1" (
        echo  [AVISO] Seguranca ^(issues encontrados^)
    ) else (
        echo  [OK]    Seguranca
    )
)
if "%RUN_UNIT%"=="1" (
    if "%UNIT_FAILED%"=="1" (
        echo  [FALHA] Testes unitarios
    ) else (
        echo  [OK]    Testes unitarios
    )
)
if "%RUN_BROWSER%"=="1" (
    if "%BROWSER_FAILED%"=="1" (
        echo  [FALHA] Testes com browser
    ) else (
        echo  [OK]    Testes com browser
    )
)

echo.
echo  Relatorios salvos em: reports\
if "%RUN_SECURITY%"=="1" echo    - reports\security-bandit.html
if "%RUN_UNIT%"=="1" (
    echo    - reports\unit-tests.html
    echo    - reports\coverage-html\index.html
)
if "%RUN_BROWSER%"=="1" echo    - reports\browser-tests.html
echo ============================================================
echo.

:: ── OPEN REPORTS ─────────────────────────────────────────────
if "%OPEN_REPORT%"=="1" (
    echo Abrindo relatorios no navegador...
    if "%RUN_SECURITY%"=="1" if exist "reports\security-bandit.html"    start "" "reports\security-bandit.html"
    if "%RUN_UNIT%"=="1"     if exist "reports\unit-tests.html"         start "" "reports\unit-tests.html"
    if "%RUN_UNIT%"=="1"     if exist "reports\coverage-html\index.html" start "" "reports\coverage-html\index.html"
    if "%RUN_BROWSER%"=="1"  if exist "reports\browser-tests.html"      start "" "reports\browser-tests.html"
)

:: Exit with error if tests failed (security is warning only)
if "%UNIT_FAILED%"=="1" exit /b 1
if "%BROWSER_FAILED%"=="1" exit /b 1
exit /b 0
