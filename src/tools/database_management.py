"""Database management MCP tools for WebSQL operations.

WARNING: WebSQL is deprecated. SQL queries are forwarded directly to the
browser's WebSQL engine. Always sanitize inputs to prevent SQL injection.
"""

from typing import Any, Dict, List, Optional

from core.database_handler import DatabaseHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("database-management")
    async def list_websql_databases(instance_id: str) -> List[Dict[str, Any]]:
        """
        List all WebSQL databases on the current page.

        Note: WebSQL is deprecated and only available in Chromium-based browsers.
        Most modern web apps use IndexedDB instead.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List[Dict[str, Any]]: List of database objects with id, domain, name, version.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DatabaseHandler.list_databases(tab)

    @section_tool("database-management")
    async def get_websql_table_names(
        instance_id: str, database_id: str
    ) -> List[str]:
        """
        Get all table names in a WebSQL database.

        Args:
            instance_id (str): Browser instance ID.
            database_id (str): The CDP database ID (from list_websql_databases).

        Returns:
            List[str]: List of table names.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DatabaseHandler.get_table_names(tab, database_id)

    @section_tool("database-management")
    async def execute_websql_query(
        instance_id: str,
        database_id: str,
        query: str,
        query_args: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a SQL query against a WebSQL database.

        WARNING: SQL injection risk — never pass unsanitized user input as the
        query string. Use query_args for parameterized queries.

        Example:
            execute_websql_query("abc123", "db1", "SELECT * FROM users WHERE id = ?", [42])

        Args:
            instance_id (str): Browser instance ID.
            database_id (str): The CDP database ID.
            query (str): The SQL query to execute.
            query_args (Optional[List[Any]]): Optional list of query parameters.

        Returns:
            Dict[str, Any]: Query results with columns, rows, and any SQL error.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await DatabaseHandler.execute_sql(tab, database_id, query, query_args)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
