"""Animation management MCP tools for CSS and Web Animations API control."""

from typing import Any, Dict, List, Optional

from core.animation_handler import AnimationHandler
from core.login_guard import check_pending_login_guard


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("animation-management")
    async def list_animations(instance_id: str) -> List[Dict[str, Any]]:
        """
        List all active animations on the current page.

        Returns both CSS animations (@keyframes) and Web Animations API animations.
        Useful for debugging animation issues or verifying animation states.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List[Dict[str, Any]]: List of animations with id, name, type, play_state,
                                   current_time, duration, and iterations.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AnimationHandler.list_animations(tab)

    @section_tool("animation-management")
    async def pause_animation(instance_id: str, animation_id: str) -> bool:
        """
        Pause a specific animation by its ID.

        Example:
            pause_animation("abc123", "my-animation")
            # Pauses the animation named "my-animation"

        Args:
            instance_id (str): Browser instance ID.
            animation_id (str): The animation ID (from list_animations).

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AnimationHandler.pause_animation(tab, animation_id)

    @section_tool("animation-management")
    async def play_animation(instance_id: str, animation_id: str) -> bool:
        """
        Resume (play) a paused animation by its ID.

        Example:
            play_animation("abc123", "my-animation")
            # Resumes the paused animation

        Args:
            instance_id (str): Browser instance ID.
            animation_id (str): The animation ID (from list_animations).

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AnimationHandler.play_animation(tab, animation_id)

    @section_tool("animation-management")
    async def set_animation_playback_rate(
        instance_id: str, playback_rate: float
    ) -> bool:
        """
        Set the global playback rate for all animations on the page.

        Useful for slowing down animations to debug timing issues or speeding
        them up to skip through long animations during testing.

        Example:
            set_animation_playback_rate("abc123", 0.1)  # 10% speed for debugging
            set_animation_playback_rate("abc123", 5.0)  # 5x speed to skip animations

        Args:
            instance_id (str): Browser instance ID.
            playback_rate (float): The playback rate (1.0 = normal, 0.0 = paused,
                                   2.0 = double speed, 0.5 = half speed).

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AnimationHandler.set_playback_rate(tab, playback_rate)

    @section_tool("animation-management")
    async def seek_animations(
        instance_id: str, animation_ids: List[str], current_time: float
    ) -> bool:
        """
        Seek one or more animations to a specific time position.

        Useful for jumping to a specific frame in an animation for visual testing
        or debugging.

        Example:
            seek_animations("abc123", ["anim1", "anim2"], 500.0)
            # Seeks both animations to 500ms

        Args:
            instance_id (str): Browser instance ID.
            animation_ids (List[str]): List of animation IDs to seek.
            current_time (float): The time position in milliseconds to seek to.

        Returns:
            bool: True if successful.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AnimationHandler.seek_animation(tab, animation_ids, current_time)

    @section_tool("animation-management")
    async def get_animation_timing(
        instance_id: str, animation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the current timing information for a specific animation.

        Args:
            instance_id (str): Browser instance ID.
            animation_id (str): The animation ID (from list_animations).

        Returns:
            Optional[Dict[str, Any]]: Timing info with animation_id and current_time (ms).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await AnimationHandler.get_animation_timing(tab, animation_id)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
