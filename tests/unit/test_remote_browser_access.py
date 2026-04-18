"""Tests for remote browser access metadata."""


def test_remote_browser_access_disabled_by_default():
    from core.remote_browser_access import build_remote_login_access

    # Always returns None in local development mode
    assert build_remote_login_access("instance-1") is None


def test_remote_browser_access_always_returns_none():
    from core.remote_browser_access import build_remote_login_access

    # Remote viewer is not available in local development mode
    assert build_remote_login_access("any-instance") is None
