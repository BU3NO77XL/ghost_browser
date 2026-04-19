"""Database domain handler for WebSQL database operations via CDP.

WARNING: WebSQL is deprecated. SQL queries passed to execute_sql are forwarded
directly to the browser's WebSQL engine. Always validate and sanitize inputs
to prevent SQL injection when building queries from user-supplied data.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.cdp_result import runtime_value
from core.debug_logger import debug_logger


class DatabaseHandler:
    """Handles WebSQL database operations via CDP Database domain."""

    @staticmethod
    async def enable_database_domain(tab: Tab) -> None:
        """
        Enable the Database domain for the given tab.

        Note: nodriver does not expose cdp.database directly.
        WebSQL operations are performed via JavaScript evaluation.

        Args:
            tab (Tab): The browser tab object.
        """
        # WebSQL is accessed via JS — no CDP enable needed
        pass

    @staticmethod
    async def list_databases(tab: Tab) -> List[Dict[str, Any]]:
        """
        List all WebSQL databases on the current page.

        Note: WebSQL is deprecated and only supported in Chromium-based browsers.
        Uses JavaScript evaluation since nodriver does not expose cdp.database.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            List[Dict[str, Any]]: List of database objects with id, domain, name, version.
        """
        debug_logger.log_info("DatabaseHandler", "list_databases", "Listing WebSQL databases")
        try:
            result = await tab.send(
                cdp.runtime.evaluate(
                    expression="""
                    (function() {
                        if (!window.openDatabase) return JSON.stringify([]);
                        return JSON.stringify(window.__cdp_databases__ || []);
                    })()
                    """,
                    return_by_value=True,
                )
            )
            value = runtime_value(result)
            if value:
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except Exception:
                    pass
            return []
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error("DatabaseHandler", "list_databases", e, {})
            raise

    @staticmethod
    async def get_table_names(tab: Tab, database_id: str) -> List[str]:
        """
        Get all table names in a WebSQL database via JavaScript.

        Args:
            tab (Tab): The browser tab object.
            database_id (str): The database name (used as identifier).

        Returns:
            List[str]: List of table names.
        """
        debug_logger.log_info(
            "DatabaseHandler",
            "get_table_names",
            f"Getting table names for database: {database_id}",
        )
        try:
            database_id_json = json.dumps(database_id)
            table_names_query_json = json.dumps("SELECT name FROM sqlite_master WHERE type='table'")
            result = await tab.send(
                cdp.runtime.evaluate(
                    expression=f"""
                    (function() {{
                        return new Promise((resolve, reject) => {{
                            try {{
                                var db = openDatabase({database_id_json}, '', '', 0);
                                db.transaction(function(tx) {{
                                    tx.executeSql(
                                        {table_names_query_json},
                                        [],
                                        function(tx, results) {{
                                            var tables = [];
                                            for (var i = 0; i < results.rows.length; i++) {{
                                                tables.push(results.rows.item(i).name);
                                            }}
                                            resolve(JSON.stringify(tables));
                                        }},
                                        function(tx, err) {{ reject(err.message); }}
                                    );
                                }});
                            }} catch(e) {{ resolve('[]'); }}
                        }});
                    }})()
                    """,
                    await_promise=True,
                    return_by_value=True,
                )
            )
            value = runtime_value(result)
            if value:
                try:
                    return json.loads(value) if isinstance(value, str) else value
                except Exception:
                    pass
            return []
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            debug_logger.log_error(
                "DatabaseHandler", "get_table_names", e, {"database_id": database_id}
            )
            raise

    @staticmethod
    async def execute_sql(
        tab: Tab,
        database_id: str,
        query: str,
        query_args: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a SQL query against a WebSQL database via JavaScript.

        WARNING: SQL injection risk — never pass unsanitized user input as the
        query string. Use parameterized queries via query_args where possible.

        Args:
            tab (Tab): The browser tab object.
            database_id (str): The database name.
            query (str): The SQL query to execute.
            query_args (Optional[List[Any]]): Optional list of query parameters.

        Returns:
            Dict[str, Any]: Query results with column names and row data.
        """
        debug_logger.log_info(
            "DatabaseHandler",
            "execute_sql",
            f"Executing SQL on database {database_id}: {query[:80]}",
        )
        try:
            args_json = json.dumps(query_args or [])
            database_id_json = json.dumps(database_id)
            result = await tab.send(
                cdp.runtime.evaluate(
                    expression=f"""
                    (function() {{
                        return new Promise((resolve, reject) => {{
                            try {{
                                var db = openDatabase({database_id_json}, '', '', 0);
                                db.transaction(function(tx) {{
                                    tx.executeSql(
                                        {json.dumps(query)},
                                        {args_json},
                                        function(tx, results) {{
                                            var cols = [];
                                            var rows = [];
                                            if (results.rows.length > 0) {{
                                                var item = results.rows.item(0);
                                                cols = Object.keys(item);
                                            }}
                                            for (var i = 0; i < results.rows.length; i++) {{
                                                rows.push(Object.values(results.rows.item(i)));
                                            }}
                                            resolve(JSON.stringify({{columns: cols, rows: rows, sql_error: null}}));
                                        }},
                                        function(tx, err) {{
                                            resolve(JSON.stringify({{columns: [], rows: [], sql_error: {{code: err.code, message: err.message}}}}));
                                        }}
                                    );
                                }});
                            }} catch(e) {{
                                resolve(JSON.stringify({{columns: [], rows: [], sql_error: {{code: 0, message: e.message}}}}));
                            }}
                        }});
                    }})()
                    """,
                    await_promise=True,
                    return_by_value=True,
                )
            )
            value = runtime_value(result)
            if value:
                try:
                    data = json.loads(value) if isinstance(value, str) else value
                    column_names = data.get("columns", [])
                    raw_rows = data.get("rows", [])
                    rows = []
                    for row in raw_rows:
                        row_dict = {}
                        for i, col in enumerate(column_names):
                            row_dict[col] = row[i] if i < len(row) else None
                        rows.append(row_dict)
                    return {
                        "columns": column_names,
                        "rows": rows,
                        "sql_error": data.get("sql_error"),
                    }
                except Exception:
                    pass
            return {"columns": [], "rows": [], "sql_error": None}
        except asyncio.TimeoutError:
            raise Exception("Operation timed out")
        except Exception as e:
            error_msg = str(e).lower()
            if "websocket" in error_msg or "http 500" in error_msg:
                raise Exception(
                    "WebSocket connection lost. Check instance health with "
                    "check_instance_health and recreate if needed."
                )
            if "syntax error" in error_msg or "sql" in error_msg:
                raise Exception(f"SQL error: {e}")
            debug_logger.log_error(
                "DatabaseHandler",
                "execute_sql",
                e,
                {"database_id": database_id, "query": query},
            )
            raise
