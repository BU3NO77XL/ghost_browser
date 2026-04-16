"""
Ghost Browser MCP — Hacker-style test runner.
Usage: uv run python run_tests.py [--unit-only] [--browser-only] [--security-only] [--demo] [--no-open] [--help]
"""

import argparse
import json
import os
import subprocess
import sys
import time

# ── ensure src is on path for banner import ───────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from cli.banner import DIVIDER, THIN_DIV, print_banner  # noqa: E402

# ── ANSI helpers ──────────────────────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

GREEN = "\033[38;5;82m"
RED = "\033[38;5;196m"
YELLOW = "\033[38;5;226m"
CYAN = "\033[38;5;51m"
GRAY = "\033[38;5;240m"


def c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


def tag(label: str, color: str) -> str:
    return f"{color}[{label}]{RESET}"


def _project_src_dir() -> str:
    """Return this repository's src directory."""
    return os.path.join(os.path.dirname(__file__), "src")


def _should_wait_for_enter(no_wait: bool) -> bool:
    """Return whether the runner should pause before exiting."""
    return not no_wait and os.environ.get("CI", "").lower() != "true"


def _render_progress(
    done: int, total: int, passed: int, failed: int, label: str, spin: str, elapsed: float
) -> str:
    """Build a single-line progress display."""
    BAR_WIDTH = 40
    if total > 0:
        pct = done / total
        filled = int(BAR_WIDTH * pct)
        bar = f"{GREEN}{'█' * filled}{RESET}{GRAY}{'░' * (BAR_WIDTH - filled)}{RESET}"
        pct_str = f"{int(pct * 100):3d}%"
    else:
        pos = (done % BAR_WIDTH) if done > 0 else 0
        bar_chars = list("░" * BAR_WIDTH)
        for i in range(min(3, BAR_WIDTH)):
            bar_chars[(pos + i) % BAR_WIDTH] = "█"
        bar = f"{GREEN}{''.join(bar_chars)}{RESET}"
        pct_str = f" {done:3d}"

    t_str = f"{GRAY}{elapsed:.1f}s{RESET}"

    return f"\r  {spin} [{bar}] {pct_str}  " f"{GRAY}{label}{RESET}  {t_str}   "


def _read_progress(path: str) -> dict:
    """Safely read the progress JSON file written by the pytest plugin."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def spinner_run(label: str, cmd: list[str]) -> tuple[int, float, list[str]]:
    """
    Run a subprocess with a live progress bar.
    For pytest commands, injects a progress plugin that writes live stats to a
    temp JSON file, which this function reads every 100ms to update the bar.
    Returns (returncode, elapsed_seconds, output_lines).
    """
    import tempfile
    import threading
    import queue as q_mod

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start = time.time()
    is_pytest = "pytest" in " ".join(cmd)

    # ── inject progress plugin for pytest runs ────────────────────────────────
    progress_file = None
    run_cmd = list(cmd)
    if is_pytest:
        fd, progress_file = tempfile.mkstemp(suffix=".json", prefix="ghost_progress_")
        os.close(fd)
        os.unlink(progress_file)  # plugin will create it
        # insert plugin and progress-file arg right after "pytest"
        pi = next((i for i, t in enumerate(run_cmd) if "pytest" in t), -1)
        if pi >= 0:
            # Insert in reverse order to maintain correct positions
            run_cmd.insert(pi + 1, f"--progress-file={progress_file}")
            run_cmd.insert(pi + 1, "cli.pytest_progress_plugin")
            run_cmd.insert(pi + 1, "-p")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    # ensure src/ is on PYTHONPATH so the plugin can be found
    src_dir = _project_src_dir()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_dir + (os.pathsep + existing if existing else "")

    proc = subprocess.Popen(
        run_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    # ── reader thread ─────────────────────────────────────────────────────────
    line_queue: q_mod.Queue = q_mod.Queue()

    def _reader():
        try:
            for line in proc.stdout:
                line_queue.put(line)
        finally:
            line_queue.put(None)

    threading.Thread(target=_reader, daemon=True).start()

    frame_idx = 0
    output_lines: list[str] = []
    done = passed = failed = total = 0
    finished = False

    while not finished:
        # drain output lines
        while True:
            try:
                item = line_queue.get_nowait()
            except q_mod.Empty:
                break
            if item is None:
                finished = True
                break
            output_lines.append(item.rstrip())

        # read progress from plugin file
        if progress_file:
            data = _read_progress(progress_file)
            if data:
                total = data.get("total", total)
                done = data.get("done", done)
                passed = data.get("passed", passed)
                failed = data.get("failed", failed)

        elapsed = time.time() - start
        spin = frames[frame_idx % len(frames)]
        print(
            _render_progress(done, total, passed, failed, label, spin, elapsed), end="", flush=True
        )
        frame_idx += 1
        time.sleep(0.1)

    proc.wait()

    elapsed = time.time() - start
    spin_color = GREEN if proc.returncode == 0 else RED
    spin_char = "✔" if proc.returncode == 0 else "✖"
    final = max(total, done)
    print(
        _render_progress(
            final, final, passed, failed, label, f"{spin_color}{spin_char}{RESET}", elapsed
        ),
        end="",
        flush=True,
    )
    time.sleep(0.4)
    print("\r" + " " * 90 + "\r", end="", flush=True)

    # cleanup
    if progress_file and os.path.exists(progress_file):
        try:
            os.unlink(progress_file)
        except Exception:
            pass

    return proc.returncode, elapsed, output_lines


def print_section_header(title: str, index: str = ""):
    print()
    prefix = f"{index} " if index else ""
    print(f"  {prefix}{BOLD}{title}{RESET}")
    print(f"  {THIN_DIV}")


def print_result(label: str, rc: int, elapsed: float, output_lines: list[str]):
    status = c(GREEN, "✔  PASSED") if rc == 0 else c(RED, "✖  FAILED")
    time_str = c(GRAY, f"{elapsed:.1f}s")
    print(f"  {status}  {c(GRAY, label)}  {time_str}")

    if rc != 0:
        # Show last 30 lines of output on failure
        print()
        print(f"  {YELLOW}┌─ Output (last 30 lines) {'─' * 30}{RESET}")
        tail = output_lines[-30:] if len(output_lines) > 30 else output_lines
        for line in tail:
            print(f"  {GRAY}│{RESET}  {DIM}{line}{RESET}")
        print(f"  {YELLOW}└{'─' * 46}{RESET}")
        print()


def print_summary(results: dict[str, int]):
    print()
    print(DIVIDER)
    print(f"  {BOLD}SUMMARY{RESET}")
    print(f"  {THIN_DIV}")

    all_passed = True
    for name, rc in results.items():
        if rc == -1:
            continue  # skipped
        icon = c(GREEN, "✔") if rc == 0 else c(RED, "✖")
        label_color = GREEN if rc == 0 else RED
        print(f"  {icon}  {label_color}{name}{RESET}")
        if rc != 0:
            all_passed = False

    print()
    if all_passed:
        print(f"  {GREEN}{BOLD}All suites passed.{RESET}  {c(GRAY, 'Ghost is clean.')}")
    else:
        print(f"  {RED}{BOLD}Some suites failed.{RESET}  {c(GRAY, 'Check output above.')}")
    print()
    print(DIVIDER)
    print()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ghost Browser MCP — Test Runner",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--browser-only", action="store_true", help="Run only browser/integration tests"
    )
    parser.add_argument("--security-only", action="store_true", help="Run only security scan")
    parser.add_argument("--demo", action="store_true", help="Run visual demo")
    parser.add_argument("--no-open", action="store_true", help="Do not open HTML reports")
    parser.add_argument(
        "--no-wait", action="store_true", help="Do not wait for Enter before exiting"
    )
    return parser.parse_args()


def main():
    # ── enable ANSI on Windows ────────────────────────────────────────────────
    if sys.platform == "win32":
        os.system("chcp 65001 >nul 2>&1")
        os.system("")  # trigger ANSI mode

    args = parse_args()

    run_unit = True
    run_browser = True
    run_security = True
    run_demo = False

    if args.unit_only:
        run_browser = run_security = False
    elif args.browser_only:
        run_unit = run_security = False
    elif args.security_only:
        run_unit = run_browser = False
    elif args.demo:
        run_unit = run_browser = run_security = False
        run_demo = True

    # ── banner ────────────────────────────────────────────────────────────────
    print_banner()

    os.makedirs("tests/reports", exist_ok=True)

    results: dict[str, int] = {
        "Security Scan": -1,
        "Unit Tests": -1,
        "Browser Tests": -1,
        "Demo": -1,
    }

    # ── security scan ─────────────────────────────────────────────────────────
    if run_security:
        print_section_header("Security Scan", "SEC")
        cmd = [
            "uv",
            "run",
            "bandit",
            "-r",
            "src/",
            "--severity-level",
            "medium",
            "--confidence-level",
            "medium",
            "-x",
            "src/.storage",
            "-f",
            "html",
            "-o",
            "tests/reports/security-bandit.html",
        ]
        rc, elapsed, lines = spinner_run("bandit", cmd)
        print_result("bandit static analysis", rc, elapsed, lines)
        results["Security Scan"] = rc

    # ── unit tests ────────────────────────────────────────────────────────────
    if run_unit:
        print_section_header("Unit Tests", "1/2")
        cmd = [
            "uv",
            "run",
            "python",
            "-m",
            "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            "--html=tests/reports/unit-tests.html",
            "--self-contained-html",
            "--cov=src",
            "--cov-report=html:tests/reports/coverage-html",
            "--cov-report=term-missing",
            "-p",
            "no:warnings",
        ]
        rc, elapsed, lines = spinner_run("pytest tests/unit/", cmd)
        print_result("unit tests", rc, elapsed, lines)
        results["Unit Tests"] = rc

    # ── browser / integration tests ───────────────────────────────────────────
    if run_browser:
        print_section_header("Browser & Integration Tests", "2/2")
        cmd = [
            "uv",
            "run",
            "python",
            "-m",
            "pytest",
            "tests/e2e/test_final_smoke.py",
            "tests/e2e/test_mcp_interface.py",
            "tests/e2e/test_integration_full.py",
            "tests/integration/test_browser_tools.py",
            "tests/integration/test_element_tools.py",
            "tests/integration/test_network_tools.py",
            "tests/integration/test_navigation_flow.py",
            "tests/integration/test_login_flow.py",
            "-v",
            "--tb=short",
            "--html=tests/reports/browser-tests.html",
            "--self-contained-html",
            "-p",
            "no:warnings",
        ]
        rc, elapsed, lines = spinner_run("pytest tests/integration/ + e2e/", cmd)
        print_result("browser & integration tests", rc, elapsed, lines)
        results["Browser Tests"] = rc

    # ── demo ──────────────────────────────────────────────────────────────────
    if run_demo:
        print_section_header("Visual Demo", "DEMO")
        cmd = ["uv", "run", "python", "examples/demo_visual.py"]
        rc, elapsed, lines = spinner_run("demo_visual.py", cmd)
        print_result("visual demo", rc, elapsed, lines)
        results["Demo"] = rc

    # ── summary ───────────────────────────────────────────────────────────────
    print_summary(results)

    # ── open reports ─────────────────────────────────────────────────────────
    if not args.no_open and sys.platform == "win32":
        base = os.path.dirname(os.path.abspath(__file__))
        unit_report = os.path.join(base, "tests", "reports", "unit-tests.html")
        browser_report = os.path.join(base, "tests", "reports", "browser-tests.html")
        try:
            if results["Unit Tests"] != -1 and os.path.isfile(unit_report):
                os.startfile(unit_report)
        except Exception:
            pass
        try:
            if results["Browser Tests"] != -1 and os.path.isfile(browser_report):
                os.startfile(browser_report)
        except Exception:
            pass

    # ── exit code ─────────────────────────────────────────────────────────────
    failed = any(rc not in (-1, 0) for rc in results.values())

    if _should_wait_for_enter(args.no_wait):
        print()
        print(f"  {GRAY}Testes finalizados. Pressione Enter para fechar...{RESET}")
        input()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
