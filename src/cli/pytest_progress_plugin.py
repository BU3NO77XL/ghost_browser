"""
Pytest plugin that writes live progress to a JSON file.
Used by run_tests.py to display a real-time progress bar.

Usage (injected automatically by run_tests.py):
    pytest ... -p cli.pytest_progress_plugin --progress-file=/tmp/progress.json

How it works:
- pytest_collection_finish: Sets the total number of tests
- pytest_runtest_logreport: Called for each phase (setup, call, teardown)
  - Tracks outcomes across all phases to handle setup/teardown failures
  - Updates counters (passed, failed, skipped) in real-time
  - Marks test as done after teardown phase completes
  - Handles edge cases like setup failures and teardown failures after passed calls
"""

import json
import os
import time


def pytest_addoption(parser):
    parser.addoption(
        "--progress-file",
        default=None,
        help="Path to write live progress JSON for the test runner UI",
    )


class ProgressPlugin:
    def __init__(self, path: str):
        self.path = path
        self.total = 0
        self.done = 0
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.current = ""
        self._test_outcomes = {}  # track outcome per test nodeid
        self._write()

    def _write(self):
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "total": self.total,
                        "done": self.done,
                        "passed": self.passed,
                        "failed": self.failed,
                        "skipped": self.skipped,
                        "current": self.current,
                        "ts": time.time(),
                    },
                    f,
                )
            os.replace(tmp, self.path)
        except Exception:
            pass

    def pytest_collection_finish(self, session):
        self.total = len(session.items)
        self._write()

    def pytest_runtest_logreport(self, report):
        """
        Called for each phase of test execution: setup, call, teardown.
        We track the outcome and only count the test as done after teardown.
        """
        nodeid = report.nodeid

        # Track the worst outcome for this test across all phases
        if nodeid not in self._test_outcomes:
            self._test_outcomes[nodeid] = {"setup": None, "call": None, "teardown": None}

        self._test_outcomes[nodeid][report.when] = report.outcome
        self.current = nodeid

        # Update counters based on the phase
        if report.when == "setup":
            if report.failed:
                # Setup failure means test failed and won't run
                self.failed += 1
                self.done += 1
                self._write()
            elif report.skipped:
                # Setup skipped means test is skipped
                self.skipped += 1
                self.done += 1
                self._write()

        elif report.when == "call":
            # Only update if setup didn't fail or skip
            if self._test_outcomes[nodeid]["setup"] not in ("failed", "skipped"):
                if report.passed:
                    self.passed += 1
                elif report.failed:
                    self.failed += 1
                elif report.skipped:
                    self.skipped += 1
                self._write()

        elif report.when == "teardown":
            # Teardown is the final phase - count test as done if not already counted
            if self._test_outcomes[nodeid]["setup"] not in ("failed", "skipped"):
                # Test was counted in call phase, just mark as done
                self.done += 1

                # If teardown failed but call passed, update to failed
                if report.failed and self._test_outcomes[nodeid]["call"] == "passed":
                    self.passed -= 1
                    self.failed += 1

                self._write()


def pytest_configure(config):
    path = config.getoption("--progress-file", default=None)
    if path:
        config.pluginmanager.register(ProgressPlugin(path), "ghost_progress")
