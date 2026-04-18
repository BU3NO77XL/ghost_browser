"""
Tests for core modules that don't require a browser:
- models.py
- platform_utils.py
- process_cleanup.py
- response_handler.py
- hook_learning_system.py
- dynamic_hook_ai_interface.py (sync parts)
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ─────────────────────────────────────────────────────────────────────────────
# models.py
# ─────────────────────────────────────────────────────────────────────────────
class TestModels:

    def test_browser_instance_defaults(self):
        from core.models import BrowserInstance, BrowserState

        inst = BrowserInstance(instance_id="test-123")
        assert inst.instance_id == "test-123"
        assert inst.state == BrowserState.STARTING
        assert inst.headless is False
        assert inst.viewport == {"width": 1920, "height": 1080}
        assert inst.current_url is None

    def test_browser_instance_update_activity(self):
        from core.models import BrowserInstance

        inst = BrowserInstance(instance_id="test-456")
        before = inst.last_activity
        time.sleep(0.01)
        inst.update_activity()
        assert inst.last_activity >= before

    def test_browser_state_enum_values(self):
        from core.models import BrowserState

        assert BrowserState.STARTING == "starting"
        assert BrowserState.READY == "ready"
        assert BrowserState.CLOSED == "closed"
        assert BrowserState.ERROR == "error"

    def test_browser_options_defaults(self):
        from core.models import BrowserOptions

        opts = BrowserOptions()
        assert opts.headless is False
        assert opts.viewport_width == 1920
        assert opts.viewport_height == 1080
        assert opts.sandbox is True
        assert opts.block_resources == []
        assert opts.extra_headers == {}

    def test_browser_options_custom(self):
        from core.models import BrowserOptions

        opts = BrowserOptions(
            headless=True,
            viewport_width=1280,
            viewport_height=720,
            user_agent="TestAgent/1.0",
            sandbox=False,
        )
        assert opts.headless is True
        assert opts.viewport_width == 1280
        assert opts.user_agent == "TestAgent/1.0"
        assert opts.sandbox is False

    def test_page_state_model(self):
        from core.models import PageState

        state = PageState(
            instance_id="test-id",
            url="https://example.com",
            title="Test Page",
            ready_state="complete",
            viewport={"width": 1280, "height": 720},
        )
        assert state.url == "https://example.com"
        assert state.cookies == []
        assert state.local_storage == {}
        assert isinstance(state.timestamp, datetime)

    def test_page_state_model_dump(self):
        """model_dump() must work (not deprecated dict())."""
        from core.models import PageState

        state = PageState(
            instance_id="test-id",
            url="https://example.com",
            title="Test",
            ready_state="complete",
            viewport={"width": 1280, "height": 720},
        )
        d = state.model_dump(mode="json")
        assert isinstance(d, dict)
        assert d["url"] == "https://example.com"
        assert "timestamp" in d

    def test_network_request_model(self):
        from core.models import NetworkRequest

        req = NetworkRequest(
            request_id="req-1", instance_id="inst-1", url="https://example.com/api", method="GET"
        )
        assert req.method == "GET"
        assert req.headers == {}
        assert req.cookies == {}
        assert req.post_data is None

    def test_network_response_model(self):
        from core.models import NetworkResponse

        resp = NetworkResponse(request_id="req-1", status=200)
        assert resp.status == 200
        assert resp.headers == {}

    def test_element_info_model(self):
        from core.models import ElementInfo

        el = ElementInfo(selector="body", tag_name="BODY")
        assert el.is_visible is True
        assert el.is_clickable is False
        assert el.children_count == 0
        assert el.bounding_box is None

    def test_hook_enums(self):
        from core.models import HookAction, HookStage, HookStatus

        assert HookAction.BLOCK == "block"
        assert HookStage.REQUEST == "request"
        assert HookStatus.ACTIVE == "active"

    def test_network_hook_model(self):
        from core.models import HookAction, HookStage, NetworkHook

        hook = NetworkHook(
            hook_id="h-1",
            name="Test Hook",
            url_pattern="*example.com*",
            stage=HookStage.REQUEST,
            action=HookAction.BLOCK,
        )
        assert hook.priority == 100
        assert hook.trigger_count == 0
        assert hook.last_triggered is None

    def test_script_result_model(self):
        from core.models import ScriptResult

        r = ScriptResult(success=True, result=42, execution_time=1.5)
        assert r.success is True
        assert r.result == 42
        assert r.error is None


# ─────────────────────────────────────────────────────────────────────────────
# platform_utils.py
# ─────────────────────────────────────────────────────────────────────────────
class TestPlatformUtils:

    def test_is_running_as_root_returns_bool(self):
        from core.platform_utils import is_running_as_root

        result = is_running_as_root()
        assert isinstance(result, bool)

    def test_is_running_in_container_returns_bool(self):
        from core.platform_utils import is_running_in_container

        result = is_running_in_container()
        assert isinstance(result, bool)

    def test_get_platform_info_has_required_keys(self):
        from core.platform_utils import get_platform_info

        info = get_platform_info()
        required = [
            "system",
            "release",
            "machine",
            "python_version",
            "is_root",
            "is_container",
            "is_ci",
            "should_disable_sandbox",
            "should_force_headless",
            "required_sandbox_args",
        ]
        for key in required:
            assert key in info, f"Missing key: {key}"

    def test_get_platform_info_types(self):
        from core.platform_utils import get_platform_info

        info = get_platform_info()
        assert isinstance(info["system"], str)
        assert isinstance(info["is_root"], bool)
        assert isinstance(info["is_container"], bool)
        assert isinstance(info["is_ci"], bool)
        assert isinstance(info["should_disable_sandbox"], bool)
        assert isinstance(info["should_force_headless"], bool)
        assert isinstance(info["required_sandbox_args"], list)

    def test_check_browser_executable_finds_browser(self):
        from core.platform_utils import check_browser_executable

        path = check_browser_executable()
        # On CI might be None, but on dev machine should find Chrome/Edge
        assert path is None or isinstance(path, str)
        if path:
            assert Path(path).exists()

    def test_merge_browser_args_no_duplicates(self):
        from core.platform_utils import merge_browser_args

        args = merge_browser_args(["--headless", "--no-sandbox"])
        # No duplicates
        assert len(args) == len(set(args))

    def test_merge_browser_args_preserves_user_args(self):
        from core.platform_utils import merge_browser_args

        user_args = ["--custom-flag", "--another-flag"]
        result = merge_browser_args(user_args)
        for arg in user_args:
            assert arg in result

    def test_merge_browser_args_empty(self):
        from core.platform_utils import merge_browser_args

        result = merge_browser_args()
        assert isinstance(result, list)

    def test_validate_browser_environment_structure(self):
        from core.platform_utils import validate_browser_environment

        result = validate_browser_environment()
        assert "is_ready" in result
        assert "issues" in result
        assert "warnings" in result
        assert "platform_info" in result
        assert isinstance(result["is_ready"], bool)
        assert isinstance(result["issues"], list)

    def test_get_required_sandbox_args_returns_list(self):
        from core.platform_utils import get_required_sandbox_args

        args = get_required_sandbox_args()
        assert isinstance(args, list)
        # All args should be strings starting with --
        for arg in args:
            assert isinstance(arg, str)

    def test_linux_ci_disables_browser_sandbox(self, monkeypatch):
        from core import platform_utils

        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        monkeypatch.setattr(platform_utils.platform, "system", lambda: "Linux")
        monkeypatch.setattr(platform_utils, "is_running_as_root", lambda: False)
        monkeypatch.setattr(platform_utils, "is_running_in_container", lambda: False)

        assert platform_utils.is_running_in_ci() is True
        assert platform_utils.should_disable_browser_sandbox() is True
        assert "--no-sandbox" in platform_utils.get_required_sandbox_args()
        assert "--single-process" not in platform_utils.get_required_sandbox_args()

    def test_linux_ci_without_display_forces_headless(self, monkeypatch):
        from core import platform_utils

        monkeypatch.setenv("CI", "true")
        monkeypatch.delenv("DISPLAY", raising=False)
        monkeypatch.setattr(platform_utils.platform, "system", lambda: "Linux")

        assert platform_utils.should_force_browser_headless() is True


# ─────────────────────────────────────────────────────────────────────────────
# browser_management.py
# ─────────────────────────────────────────────────────────────────────────────
class TestBrowserManagementTools:

    @pytest.mark.parametrize(
        ("raw_value", "expected"),
        [
            ({"no_sandbox": True}, False),
            ({"no_sandbox": False}, True),
            ({"enabled": False}, False),
            ({"sandbox": True}, True),
            ("no_sandbox", False),
            ("false", False),
            ("true", True),
            (0, False),
            (1, True),
            (False, False),
            (True, True),
        ],
    )
    def test_normalize_sandbox_option(self, raw_value, expected):
        from tools.browser_management import normalize_sandbox_option

        assert normalize_sandbox_option(raw_value) is expected


class TestOutputPaths:

    def test_container_app_path_maps_to_workspace(self, monkeypatch):
        from core import output_paths

        monkeypatch.setattr(output_paths, "is_running_in_container", lambda: True)
        monkeypatch.setenv("GHOST_CLIENT_WORKSPACE", "/workspace")

        result = output_paths.resolve_output_path("/app/govbr/index.html")

        assert result.as_posix() == "/workspace/govbr/index.html"

    def test_container_relative_path_maps_to_workspace(self, monkeypatch):
        from core import output_paths

        monkeypatch.setattr(output_paths, "is_running_in_container", lambda: True)
        monkeypatch.setenv("GHOST_CLIENT_WORKSPACE", "/workspace")

        result = output_paths.resolve_output_path("govbr/index.html")

        assert result.as_posix() == "/workspace/govbr/index.html"

    def test_local_path_is_preserved(self, monkeypatch):
        from core import output_paths

        monkeypatch.setattr(output_paths, "is_running_in_container", lambda: False)

        result = output_paths.resolve_output_path("govbr/index.html")

        assert result.as_posix() == "govbr/index.html"


# ─────────────────────────────────────────────────────────────────────────────
# process_cleanup.py
# ─────────────────────────────────────────────────────────────────────────────
class TestProcessCleanup:

    def test_singleton_exists(self):
        from core.process_cleanup import ProcessCleanup, process_cleanup

        assert isinstance(process_cleanup, ProcessCleanup)

    def test_get_tracked_processes_returns_dict(self):
        from core.process_cleanup import process_cleanup

        result = process_cleanup.get_tracked_processes()
        assert isinstance(result, dict)

    def test_is_process_alive_nonexistent(self):
        from core.process_cleanup import process_cleanup

        result = process_cleanup.is_process_alive("nonexistent-instance")
        assert result is False

    def test_untrack_nonexistent_is_safe(self):
        from core.process_cleanup import process_cleanup

        result = process_cleanup.untrack_browser_process("nonexistent-xyz")
        assert result is False

    def test_kill_nonexistent_is_safe(self):
        from core.process_cleanup import process_cleanup

        result = process_cleanup.kill_browser_process("nonexistent-xyz")
        assert result is False

    def test_track_and_untrack_mock_process(self):
        import os

        from core.process_cleanup import process_cleanup

        class MockProcess:
            pid = os.getpid()  # Use current process PID (safe, won't kill it)

        instance_id = "test-track-mock"
        # Track
        result = process_cleanup.track_browser_process(instance_id, MockProcess())
        assert result is True
        assert instance_id in process_cleanup.get_tracked_processes()

        # Untrack
        result = process_cleanup.untrack_browser_process(instance_id)
        assert result is True
        assert instance_id not in process_cleanup.get_tracked_processes()

    def test_track_process_without_pid(self):
        from core.process_cleanup import process_cleanup

        class MockProcessNoPid:
            pid = None

        result = process_cleanup.track_browser_process("no-pid-instance", MockProcessNoPid())
        assert result is False

    def test_is_process_alive_current_process(self):
        """Current process should be alive."""
        import os

        from core.process_cleanup import process_cleanup

        class MockProcess:
            pid = os.getpid()

        instance_id = "alive-test"
        process_cleanup.track_browser_process(instance_id, MockProcess())
        assert process_cleanup.is_process_alive(instance_id) is True
        process_cleanup.untrack_browser_process(instance_id)


# ─────────────────────────────────────────────────────────────────────────────
# response_handler.py
# ─────────────────────────────────────────────────────────────────────────────
class TestResponseHandler:

    def test_singleton_exists(self):
        from core.response_handler import ResponseHandler, response_handler

        assert isinstance(response_handler, ResponseHandler)

    def test_estimate_tokens_dict(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler()
        data = {"key": "value", "number": 42}
        tokens = rh.estimate_tokens(data)
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_estimate_tokens_string(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler()
        tokens = rh.estimate_tokens("hello world")
        assert tokens > 0

    def test_estimate_tokens_list(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler()
        tokens = rh.estimate_tokens([1, 2, 3, "test"])
        assert tokens > 0

    def test_small_response_returned_as_is(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler(max_tokens=10000)
        small_data = {"key": "value"}
        result = rh.handle_response(small_data, "test")
        # Small data should be returned as-is (same object)
        assert result == small_data

    def test_large_response_returns_remediation_error(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler(max_tokens=10)
        # Create data that exceeds 10 tokens
        large_data = {"data": "x" * 1000}
        result = rh.handle_response(large_data, "test_large")
        assert isinstance(result, dict)
        assert result["error"] == "response_too_large"
        assert result["estimated_tokens"] > rh.max_tokens
        assert result["max_tokens"] == rh.max_tokens
        assert result["remediation"]["for_structured_data"]["args"]["output_path"].endswith(
            "/test_large.json"
        )

    def test_large_response_does_not_persist_data_to_disk(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler(max_tokens=10)
        large_data = {"content": "y" * 500}
        result = rh.handle_response(large_data, "test_content")
        assert result["error"] == "response_too_large"
        assert "file_path" not in result
        assert "filename" not in result
        assert "data" not in result

    def test_handle_response_with_metadata(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler(max_tokens=10)
        large_data = {"x": "z" * 500}
        meta = {"instance_id": "test-123", "selector": "body"}
        result = rh.handle_response(large_data, "meta_test", metadata=meta)
        assert result["remediation"]["for_html"]["args"]["instance_id"] == "test-123"

    def test_clone_dir_is_noop_compatibility_attribute(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler()
        assert rh.clone_dir is None

    def test_estimate_tokens_large_vs_small(self):
        from core.response_handler import ResponseHandler

        rh = ResponseHandler()
        small = rh.estimate_tokens("hi")
        large = rh.estimate_tokens("x" * 10000)
        assert large > small


# ─────────────────────────────────────────────────────────────────────────────
# hook_learning_system.py
# ─────────────────────────────────────────────────────────────────────────────
class TestHookLearningSystem:

    def test_singleton_exists(self):
        from core.hook_learning_system import HookLearningSystem, hook_learning_system

        assert isinstance(hook_learning_system, HookLearningSystem)

    def test_get_request_object_documentation(self):
        from core.hook_learning_system import hook_learning_system

        doc = hook_learning_system.get_request_object_documentation()
        assert "request_object" in doc
        assert "hook_action" in doc
        fields = doc["request_object"]["fields"]
        for key in ["url", "method", "headers", "stage"]:
            assert key in fields

    def test_get_hook_examples_returns_list(self):
        from core.hook_learning_system import hook_learning_system

        examples = hook_learning_system.get_hook_examples()
        assert isinstance(examples, list)
        assert len(examples) > 0
        for ex in examples:
            assert "name" in ex
            assert "function" in ex
            assert "requirements" in ex

    def test_get_requirements_documentation(self):
        from core.hook_learning_system import hook_learning_system

        doc = hook_learning_system.get_requirements_documentation()
        assert "requirements" in doc
        assert "best_practices" in doc
        fields = doc["requirements"]["fields"]
        assert "url_pattern" in fields
        assert "method" in fields

    def test_get_common_patterns(self):
        from core.hook_learning_system import hook_learning_system

        patterns = hook_learning_system.get_common_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0
        for p in patterns:
            assert "pattern" in p
            assert "action" in p

    def test_validate_valid_hook(self):
        from core.hook_learning_system import hook_learning_system

        code = """
def process_request(request):
    return HookAction(action="continue")
"""
        result = hook_learning_system.validate_hook_function(code)
        assert result["valid"] is True
        assert result["issues"] == []

    def test_validate_missing_function(self):
        from core.hook_learning_system import hook_learning_system

        code = """
def wrong_name(request):
    return HookAction(action="continue")
"""
        result = hook_learning_system.validate_hook_function(code)
        assert result["valid"] is False
        assert any("process_request" in i for i in result["issues"])

    def test_validate_syntax_error(self):
        from core.hook_learning_system import hook_learning_system

        code = "def process_request(request: INVALID SYNTAX"
        result = hook_learning_system.validate_hook_function(code)
        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_validate_banned_import(self):
        from core.hook_learning_system import hook_learning_system

        code = """
import os
def process_request(request):
    return HookAction(action="continue")
"""
        result = hook_learning_system.validate_hook_function(code)
        assert result["valid"] is False
        assert any("Import" in i for i in result["issues"])

    def test_validate_banned_eval(self):
        from core.hook_learning_system import hook_learning_system

        code = """
def process_request(request):
    eval("dangerous")
    return HookAction(action="continue")
"""
        result = hook_learning_system.validate_hook_function(code)
        assert result["valid"] is False
        assert any("eval" in i for i in result["issues"])

    def test_validate_wrong_param_count(self):
        from core.hook_learning_system import hook_learning_system

        code = """
def process_request(request, extra):
    return HookAction(action="continue")
"""
        result = hook_learning_system.validate_hook_function(code)
        assert result["valid"] is False

    def test_validate_block_hook(self):
        from core.hook_learning_system import hook_learning_system

        code = """
def process_request(request):
    return HookAction(action="block")
"""
        result = hook_learning_system.validate_hook_function(code)
        assert result["valid"] is True

    def test_validate_complex_valid_hook(self):
        from core.hook_learning_system import hook_learning_system

        code = """
def process_request(request):
    if "api" in request["url"]:
        new_headers = request["headers"].copy()
        new_headers["X-Custom"] = "value"
        return HookAction(action="modify", headers=new_headers)
    return HookAction(action="continue")
"""
        result = hook_learning_system.validate_hook_function(code)
        assert result["valid"] is True


# ─────────────────────────────────────────────────────────────────────────────
# dynamic_hook_ai_interface.py — sync methods
# ─────────────────────────────────────────────────────────────────────────────
class TestDynamicHookAIInterface:

    def test_singleton_exists(self):
        from core.dynamic_hook_ai_interface import DynamicHookAIInterface, dynamic_hook_ai

        assert isinstance(dynamic_hook_ai, DynamicHookAIInterface)

    def test_get_request_documentation(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = dynamic_hook_ai.get_request_documentation()
        assert result["success"] is True
        assert "documentation" in result

    def test_get_hook_examples(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = dynamic_hook_ai.get_hook_examples()
        assert result["success"] is True
        assert "examples" in result
        assert len(result["examples"]) > 0

    def test_get_requirements_documentation(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = dynamic_hook_ai.get_requirements_documentation()
        assert result["success"] is True
        assert "documentation" in result

    def test_get_common_patterns(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = dynamic_hook_ai.get_common_patterns()
        assert result["success"] is True
        assert "patterns" in result

    def test_validate_valid_hook(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        code = """
def process_request(request):
    return HookAction(action="continue")
"""
        result = dynamic_hook_ai.validate_hook_function(code)
        assert result["success"] is True
        assert result["validation"]["valid"] is True

    def test_validate_invalid_hook(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        code = """
import os
def process_request(request):
    return HookAction(action="continue")
"""
        result = dynamic_hook_ai.validate_hook_function(code)
        assert result["success"] is True
        assert result["validation"]["valid"] is False

    @pytest.mark.asyncio
    async def test_list_hooks_empty(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = await dynamic_hook_ai.list_dynamic_hooks()
        assert result["success"] is True
        assert "hooks" in result
        assert isinstance(result["hooks"], list)

    @pytest.mark.asyncio
    async def test_create_and_remove_hook(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        code = """
def process_request(request):
    return HookAction(action="block")
"""
        create_result = await dynamic_hook_ai.create_dynamic_hook(
            name="Test Block Hook", requirements={"url_pattern": "*test-block*"}, function_code=code
        )
        assert create_result["success"] is True
        hook_id = create_result["hook_id"]

        # Verify it appears in list
        list_result = await dynamic_hook_ai.list_dynamic_hooks()
        hook_ids = [h["hook_id"] for h in list_result["hooks"]]
        assert hook_id in hook_ids

        # Get details
        details = await dynamic_hook_ai.get_hook_details(hook_id)
        assert details["success"] is True
        assert details["hook"]["name"] == "Test Block Hook"

        # Remove
        remove_result = await dynamic_hook_ai.remove_dynamic_hook(hook_id)
        assert remove_result["success"] is True

        # Verify gone
        details_after = await dynamic_hook_ai.get_hook_details(hook_id)
        assert details_after["success"] is False

    @pytest.mark.asyncio
    async def test_create_simple_block_hook(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = await dynamic_hook_ai.create_simple_hook(
            name="Simple Block", url_pattern="*ads*", action="block"
        )
        assert result["success"] is True
        hook_id = result["hook_id"]
        await dynamic_hook_ai.remove_dynamic_hook(hook_id)

    @pytest.mark.asyncio
    async def test_create_simple_redirect_hook(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = await dynamic_hook_ai.create_simple_hook(
            name="Simple Redirect",
            url_pattern="*old-site*",
            action="redirect",
            target_url="https://new-site.com",
        )
        assert result["success"] is True
        hook_id = result["hook_id"]
        await dynamic_hook_ai.remove_dynamic_hook(hook_id)

    @pytest.mark.asyncio
    async def test_create_simple_redirect_without_url_fails(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = await dynamic_hook_ai.create_simple_hook(
            name="Bad Redirect",
            url_pattern="*test*",
            action="redirect",
            # missing target_url
        )
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_create_hook_with_invalid_code_fails(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        code = """
import os
def process_request(request):
    return HookAction(action="continue")
"""
        result = await dynamic_hook_ai.create_dynamic_hook(
            name="Bad Hook", requirements={"url_pattern": "*"}, function_code=code
        )
        assert result["success"] is False
        assert "issues" in result

    @pytest.mark.asyncio
    async def test_get_hook_details_nonexistent(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = await dynamic_hook_ai.get_hook_details("nonexistent-hook-id")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_remove_nonexistent_hook(self):
        from core.dynamic_hook_ai_interface import dynamic_hook_ai

        result = await dynamic_hook_ai.remove_dynamic_hook("nonexistent-hook-id")
        assert result["success"] is False


# ─────────────────────────────────────────────────────────────────────────────
# progressive_element_cloner.py — no-browser methods
# ─────────────────────────────────────────────────────────────────────────────
class TestProgressiveElementCloner:

    def test_singleton_exists(self):
        from core.progressive_element_cloner import (
            ProgressiveElementCloner,
            progressive_element_cloner,
        )

        assert isinstance(progressive_element_cloner, ProgressiveElementCloner)

    def test_list_stored_elements_empty(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.list_stored_elements()
        # Key is 'stored_elements' or 'elements' depending on implementation
        assert "stored_elements" in result or "elements" in result
        key = "stored_elements" if "stored_elements" in result else "elements"
        assert isinstance(result[key], list)

    def test_clear_nonexistent_element(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.clear_stored_element("nonexistent-id")
        assert "error" in result or "message" in result

    def test_clear_all_elements(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.clear_all_elements()
        assert "message" in result or "cleared" in str(result).lower()

    def test_expand_styles_nonexistent(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.expand_styles("nonexistent-element-id")
        assert "error" in result

    def test_expand_events_nonexistent(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.expand_events("nonexistent-element-id")
        assert "error" in result

    def test_expand_children_nonexistent(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.expand_children("nonexistent-element-id")
        assert "error" in result

    def test_expand_css_rules_nonexistent(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.expand_css_rules("nonexistent-element-id")
        assert "error" in result

    def test_expand_pseudo_elements_nonexistent(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.expand_pseudo_elements("nonexistent-element-id")
        assert "error" in result

    def test_expand_animations_nonexistent(self):
        from core.progressive_element_cloner import progressive_element_cloner

        result = progressive_element_cloner.expand_animations("nonexistent-element-id")
        assert "error" in result
