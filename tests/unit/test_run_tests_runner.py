"""Tests for the local test runner helpers."""

from pathlib import Path

import run_tests


def test_project_src_dir_points_to_repo_src():
    expected = Path(run_tests.__file__).resolve().parent / "src"

    assert Path(run_tests._project_src_dir()).resolve() == expected


def test_should_wait_for_enter_defaults_to_interactive(monkeypatch):
    monkeypatch.delenv("CI", raising=False)

    assert run_tests._should_wait_for_enter(no_wait=False) is True


def test_should_wait_for_enter_skips_in_ci(monkeypatch):
    monkeypatch.setenv("CI", "true")

    assert run_tests._should_wait_for_enter(no_wait=False) is False
    assert run_tests._should_wait_for_enter(no_wait=True) is False
