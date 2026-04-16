"""Dynamic network hook system tools."""

from typing import Any, Dict, List, Optional


def register(mcp, section_tool, deps):
    dynamic_hook_ai = deps["dynamic_hook_ai"]

    @section_tool("dynamic-hooks")
    async def create_dynamic_hook(
        name: str,
        requirements: Dict[str, Any],
        function_code: str,
        instance_ids: Optional[List[str]] = None,
        priority: int = 100,
    ) -> Dict[str, Any]:
        """
        Create a new dynamic hook with AI-generated Python function.

        Args:
            name (str): Human-readable hook name.
            requirements (Dict[str, Any]): Matching criteria (url_pattern, method, resource_type, custom_condition).
            function_code (str): Python function code that processes requests (must define process_request(request)).
            instance_ids (Optional[List[str]]): Browser instances to apply hook to (all if None).
            priority (int): Hook priority (lower = higher priority).

        Returns:
            Dict[str, Any]: Hook creation result with hook_id.
        """
        return await dynamic_hook_ai.create_dynamic_hook(
            name=name,
            requirements=requirements,
            function_code=function_code,
            instance_ids=instance_ids,
            priority=priority,
        )

    @section_tool("dynamic-hooks")
    async def create_simple_dynamic_hook(
        name: str,
        url_pattern: str,
        action: str,
        target_url: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        instance_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a simple dynamic hook using predefined templates (easier for AI).

        Args:
            name (str): Hook name.
            url_pattern (str): URL pattern to match.
            action (str): Action type - 'block', 'redirect', 'add_headers', or 'log'.
            target_url (Optional[str]): Target URL for redirect action.
            custom_headers (Optional[Dict[str, str]]): Headers to add for add_headers action.
            instance_ids (Optional[List[str]]): Browser instances to apply hook to.

        Returns:
            Dict[str, Any]: Hook creation result.
        """
        return await dynamic_hook_ai.create_simple_hook(
            name=name,
            url_pattern=url_pattern,
            action=action,
            target_url=target_url,
            custom_headers=custom_headers,
            instance_ids=instance_ids,
        )

    @section_tool("dynamic-hooks")
    async def list_dynamic_hooks(instance_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List all dynamic hooks.

        Args:
            instance_id (Optional[str]): Optional filter by browser instance.

        Returns:
            Dict[str, Any]: List of hooks with details and statistics.
        """
        return await dynamic_hook_ai.list_dynamic_hooks(instance_id=instance_id)

    @section_tool("dynamic-hooks")
    async def get_dynamic_hook_details(hook_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific dynamic hook.

        Args:
            hook_id (str): Hook identifier.

        Returns:
            Dict[str, Any]: Detailed hook information including function code.
        """
        return await dynamic_hook_ai.get_hook_details(hook_id=hook_id)

    @section_tool("dynamic-hooks")
    async def remove_dynamic_hook(hook_id: str) -> Dict[str, Any]:
        """
        Remove a dynamic hook.

        Args:
            hook_id (str): Hook identifier to remove.

        Returns:
            Dict[str, Any]: Removal status.
        """
        return await dynamic_hook_ai.remove_dynamic_hook(hook_id=hook_id)

    @section_tool("dynamic-hooks")
    def get_hook_documentation() -> Dict[str, Any]:
        """
        Get comprehensive documentation for creating hook functions (AI learning).

        Returns:
            Dict[str, Any]: Documentation of request object structure and HookAction types.
        """
        return dynamic_hook_ai.get_request_documentation()

    @section_tool("dynamic-hooks")
    def get_hook_examples() -> Dict[str, Any]:
        """
        Get example hook functions for AI learning.

        Returns:
            Dict[str, Any]: Collection of example hook functions with explanations.
        """
        return dynamic_hook_ai.get_hook_examples()

    @section_tool("dynamic-hooks")
    def get_hook_requirements_documentation() -> Dict[str, Any]:
        """
        Get documentation on hook requirements and matching criteria.

        Returns:
            Dict[str, Any]: Requirements documentation and best practices.
        """
        return dynamic_hook_ai.get_requirements_documentation()

    @section_tool("dynamic-hooks")
    def get_hook_common_patterns() -> Dict[str, Any]:
        """
        Get common hook patterns and use cases.

        Returns:
            Dict[str, Any]: Common patterns like ad blocking, API proxying, etc.
        """
        return dynamic_hook_ai.get_common_patterns()

    @section_tool("dynamic-hooks")
    def validate_hook_function(function_code: str) -> Dict[str, Any]:
        """
        Validate hook function code for common issues before creating.

        Args:
            function_code (str): Python function code to validate.

        Returns:
            Dict[str, Any]: Validation results with issues and warnings.
        """
        return dynamic_hook_ai.validate_hook_function(function_code=function_code)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
