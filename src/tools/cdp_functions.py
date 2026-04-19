"""CDP function execution tools."""

from typing import Any, Dict, List, Optional

from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]
    cdp_function_executor = deps["cdp_function_executor"]
    response_handler = deps["response_handler"]

    @section_tool("cdp-functions")
    async def list_cdp_commands() -> List[str]:
        """
        List all available CDP Runtime commands for function execution.

        Returns:
            List[str]: List of available CDP command names.
        """
        return await cdp_function_executor.list_cdp_commands()

    @section_tool("cdp-functions")
    async def execute_cdp_command(
        instance_id: str, command: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a CDP command with given parameters.

        Args:
            instance_id (str): Browser instance ID.
            command (str): Runtime command name (e.g., 'evaluate') or fully-qualified
                CDP method (e.g., 'Input.dispatchMouseEvent').
            params (Dict[str, Any], optional): Command parameters. Runtime helpers use
                snake_case; fully-qualified raw methods use CDP wire names.

        Returns:
            Dict[str, Any]: Command execution result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return {"success": False, "error": f"Instance not found: {instance_id}"}
        return await cdp_function_executor.execute_cdp_command(tab, command, params or {})

    @section_tool("cdp-functions")
    async def get_execution_contexts(instance_id: str) -> List[Dict[str, Any]]:
        """
        Get all available JavaScript execution contexts.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List[Dict[str, Any]]: List of execution contexts with their details.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return []
        contexts = await cdp_function_executor.get_execution_contexts(tab)
        return [
            {
                "id": ctx.id,
                "name": ctx.name,
                "origin": ctx.origin,
                "unique_id": ctx.unique_id,
                "aux_data": ctx.aux_data,
            }
            for ctx in contexts
        ]

    @section_tool("cdp-functions")
    async def discover_global_functions(
        instance_id: str, context_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Discover all global JavaScript functions available in the page.

        Args:
            instance_id (str): Browser instance ID.
            context_id (str, optional): Optional execution context ID.

        Returns:
            List[Dict[str, Any]]: List of discovered functions with their details.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return []
        functions = await cdp_function_executor.discover_global_functions(tab, context_id)
        result = [
            {
                "name": func.name,
                "path": func.path,
                "signature": func.signature,
                "description": func.description,
            }
            for func in functions
        ]

        file_response = response_handler.handle_response(
            result,
            fallback_filename_prefix="global_functions",
            metadata={
                "context_id": context_id,
                "function_count": len(result),
                "url": getattr(tab, "url", "unknown"),
            },
        )

        if isinstance(file_response, dict) and "file_path" in file_response:
            return [
                {
                    "name": "LARGE_RESPONSE_SAVED_TO_FILE",
                    "path": "file_storage",
                    "signature": "automatic_file_fallback",
                    "description": f"Response too large ({file_response['estimated_tokens']} tokens), saved to: {file_response['filename']}",
                }
            ]

        return file_response

    @section_tool("cdp-functions")
    async def discover_object_methods(instance_id: str, object_path: str) -> List[Dict[str, Any]]:
        """
        Discover methods of a specific JavaScript object.

        Args:
            instance_id (str): Browser instance ID.
            object_path (str): Path to the object (e.g., 'document', 'window.localStorage').

        Returns:
            List[Dict[str, Any]]: List of discovered methods.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return []
        methods = await cdp_function_executor.discover_object_methods(tab, object_path)
        methods_data = [
            {
                "name": method.name,
                "path": method.path,
                "signature": method.signature,
                "description": method.description,
            }
            for method in methods
        ]
        return response_handler.handle_response(
            methods_data, f"object_methods_{object_path.replace('.', '_')}"
        )

    @section_tool("cdp-functions")
    async def call_javascript_function(
        instance_id: str, function_path: str, args: List[Any] = None
    ) -> Dict[str, Any]:
        """
        Call a JavaScript function with arguments.

        Args:
            instance_id (str): Browser instance ID.
            function_path (str): Full path to the function (e.g., 'document.getElementById').
            args (List[Any], optional): List of arguments to pass to the function.

        Returns:
            Dict[str, Any]: Function call result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return {"success": False, "error": f"Instance not found: {instance_id}"}
        return await cdp_function_executor.call_discovered_function(tab, function_path, args or [])

    @section_tool("cdp-functions")
    async def inspect_function_signature(instance_id: str, function_path: str) -> Dict[str, Any]:
        """
        Inspect a JavaScript function's signature and details.

        Args:
            instance_id (str): Browser instance ID.
            function_path (str): Full path to the function.

        Returns:
            Dict[str, Any]: Function signature and details.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return {"success": False, "error": f"Instance not found: {instance_id}"}
        return await cdp_function_executor.inspect_function_signature(tab, function_path)

    @section_tool("cdp-functions")
    async def inject_and_execute_script(
        instance_id: str, script_code: str, context_id: str = None
    ) -> Dict[str, Any]:
        """
        Inject and execute custom JavaScript code.

        Args:
            instance_id (str): Browser instance ID.
            script_code (str): JavaScript code to execute.
            context_id (str, optional): Optional execution context ID.

        Returns:
            Dict[str, Any]: Script execution result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return {"success": False, "error": f"Instance not found: {instance_id}"}
        return await cdp_function_executor.inject_and_execute_script(tab, script_code, context_id)

    @section_tool("cdp-functions")
    async def create_persistent_function(
        instance_id: str, function_name: str, function_code: str
    ) -> Dict[str, Any]:
        """
        Create a persistent JavaScript function that survives page reloads.

        Args:
            instance_id (str): Browser instance ID.
            function_name (str): Name for the function.
            function_code (str): JavaScript function code.

        Returns:
            Dict[str, Any]: Function creation result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return {"success": False, "error": f"Instance not found: {instance_id}"}
        return await cdp_function_executor.create_persistent_function(
            tab, function_name, function_code, instance_id
        )

    @section_tool("cdp-functions")
    async def execute_function_sequence(
        instance_id: str, function_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute a sequence of JavaScript function calls.

        Args:
            instance_id (str): Browser instance ID.
            function_calls (List[Dict[str, Any]]): List of function calls with 'function_path', 'args', and optional 'context_id'.

        Returns:
            List[Dict[str, Any]]: List of function call results.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        from core.cdp_function_executor import FunctionCall

        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return [{"success": False, "error": f"Instance not found: {instance_id}"}]
        calls = [
            FunctionCall(
                function_path=call_data["function_path"],
                args=call_data.get("args", []),
                context_id=call_data.get("context_id"),
            )
            for call_data in function_calls
        ]
        return await cdp_function_executor.execute_function_sequence(tab, calls)

    @section_tool("cdp-functions")
    async def create_python_binding(
        instance_id: str, binding_name: str, python_code: str
    ) -> Dict[str, Any]:
        """
        Create a binding that allows JavaScript to call Python functions.

        Args:
            instance_id (str): Browser instance ID.
            binding_name (str): Name for the binding.
            python_code (str): Python function code (as string).

        Returns:
            Dict[str, Any]: Binding creation result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return {"success": False, "error": f"Instance not found: {instance_id}"}
        try:
            exec_globals = {}
            # User-controlled feature; keep disabled at the tool-section level when untrusted.
            exec(python_code, exec_globals)  # nosec B102
            python_function = None
            for name, obj in exec_globals.items():
                if callable(obj) and not name.startswith("_"):
                    python_function = obj
                    break
            if not python_function:
                return {"success": False, "error": "No function found in Python code"}
            return await cdp_function_executor.create_python_binding(
                tab, binding_name, python_function
            )
        except Exception as e:
            return {"success": False, "error": f"Failed to create Python function: {str(e)}"}

    @section_tool("cdp-functions")
    async def execute_python_in_browser(instance_id: str, python_code: str) -> Dict[str, Any]:
        """
        Execute Python code by translating it to JavaScript.

        Args:
            instance_id (str): Browser instance ID.
            python_code (str): Python code to translate and execute.

        Returns:
            Dict[str, Any]: Execution result.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            return {"success": False, "error": f"Instance not found: {instance_id}"}
        return await cdp_function_executor.execute_python_in_browser(tab, python_code)

    @section_tool("cdp-functions")
    async def get_function_executor_info(instance_id: str = None) -> Dict[str, Any]:
        """
        Get information about the CDP function executor state.

        Args:
            instance_id (str, optional): Optional browser instance ID for specific info.

        Returns:
            Dict[str, Any]: Function executor state and capabilities.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        return await cdp_function_executor.get_function_executor_info(instance_id)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
