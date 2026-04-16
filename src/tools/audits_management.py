"""Audits management MCP tools for encoded response inspection and contrast checking via CDP."""

from typing import Optional

from core.audits_handler import AuditsHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("audits-management")
    async def audits_enable(instance_id: str) -> bool:
        """Enable the Audits domain for a browser instance."""
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AuditsHandler.enable_audits(tab)

    @section_tool("audits-management")
    async def audits_disable(instance_id: str) -> bool:
        """Disable the Audits domain for a browser instance."""
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AuditsHandler.disable_audits(tab)

    @section_tool("audits-management")
    async def audits_get_encoded_response(
        instance_id: str,
        request_id: str,
        encoding: str,
        quality: Optional[int] = None,
    ) -> dict:
        """
        Get an encoded version of a network response.

        Args:
            instance_id: Browser instance ID.
            request_id: Network request ID.
            encoding: Target encoding — must be one of 'webp', 'jpeg', 'png'.
            quality: Optional compression quality (0-100, for jpeg/webp).

        Returns:
            Dict with 'body' (str), 'original_size' (int), 'encoded_size' (int).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AuditsHandler.get_encoded_response(tab, request_id, encoding, quality)

    @section_tool("audits-management")
    async def audits_check_contrast(
        instance_id: str,
        report_aaa: bool = False,
    ) -> bool:
        """
        Trigger a contrast check on the current page.

        Args:
            instance_id: Browser instance ID.
            report_aaa: Whether to report AAA-level contrast issues. Defaults to False.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AuditsHandler.check_contrast(tab, report_aaa=report_aaa)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
