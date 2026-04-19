"""Animation domain handler for CSS and Web Animations API control via CDP."""

import asyncio
from typing import Any, Dict, List, Optional

from nodriver import Tab, cdp

from core.cdp_result import runtime_value
from core.debug_logger import debug_logger


class AnimationHandler:
    """Handles animation operations via CDP Animation domain."""

    @staticmethod
    async def enable_animation_domain(tab: Tab) -> None:
        """
        Enable the Animation domain for the given tab.

        Args:
            tab (Tab): The browser tab object.
        """
        try:
            await tab.send(cdp.animation.enable())
        except Exception as e:
            error_msg = str(e).lower()
            if "already enabled" in error_msg:
                return
            raise

    @staticmethod
    async def list_animations(tab: Tab) -> List[Dict[str, Any]]:
        """
        List all active animations on the current page.

        Supports both CSS animations (@keyframes) and Web Animations API.

        Args:
            tab (Tab): The browser tab object.

        Returns:
            List[Dict[str, Any]]: List of animation objects with id, name, type, and timing.
        """
        debug_logger.log_info("AnimationHandler", "list_animations", "Listing active animations")
        try:
            await AnimationHandler.enable_animation_domain(tab)
            # Use JS to enumerate animations since CDP Animation domain uses events
            result = await tab.send(
                cdp.runtime.evaluate(
                    expression="""
                    (function() {
                        const animations = document.getAnimations();
                        return JSON.stringify(animations.map((a, i) => ({
                            id: a.id || String(i),
                            name: a.animationName || a.id || 'animation-' + i,
                            type: a.constructor.name,
                            play_state: a.playState,
                            current_time: a.currentTime,
                            duration: a.effect && a.effect.getTiming ? a.effect.getTiming().duration : null,
                            iterations: a.effect && a.effect.getTiming ? a.effect.getTiming().iterations : null
                        })));
                    })()
                    """,
                    return_by_value=True,
                )
            )
            import json

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
            debug_logger.log_error("AnimationHandler", "list_animations", e, {})
            raise

    @staticmethod
    async def pause_animation(tab: Tab, animation_id: str) -> bool:
        """
        Pause an animation by its ID.

        Args:
            tab (Tab): The browser tab object.
            animation_id (str): The animation ID.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "AnimationHandler", "pause_animation", f"Pausing animation: {animation_id}"
        )
        try:
            await AnimationHandler.enable_animation_domain(tab)
            await tab.send(cdp.animation.set_paused(animations=[animation_id], paused=True))
            return True
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
                "AnimationHandler", "pause_animation", e, {"animation_id": animation_id}
            )
            raise

    @staticmethod
    async def play_animation(tab: Tab, animation_id: str) -> bool:
        """
        Resume (play) a paused animation by its ID.

        Args:
            tab (Tab): The browser tab object.
            animation_id (str): The animation ID.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "AnimationHandler", "play_animation", f"Playing animation: {animation_id}"
        )
        try:
            await AnimationHandler.enable_animation_domain(tab)
            await tab.send(cdp.animation.set_paused(animations=[animation_id], paused=False))
            return True
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
                "AnimationHandler", "play_animation", e, {"animation_id": animation_id}
            )
            raise

    @staticmethod
    async def set_playback_rate(tab: Tab, playback_rate: float) -> bool:
        """
        Set the global playback rate for all animations on the page.

        Args:
            tab (Tab): The browser tab object.
            playback_rate (float): The playback rate (1.0 = normal, 2.0 = double speed,
                                   0.5 = half speed, 0.0 = paused).

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "AnimationHandler",
            "set_playback_rate",
            f"Setting playback rate: {playback_rate}",
        )
        try:
            await AnimationHandler.enable_animation_domain(tab)
            await tab.send(cdp.animation.set_playback_rate(playback_rate=playback_rate))
            return True
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
                "AnimationHandler",
                "set_playback_rate",
                e,
                {"playback_rate": playback_rate},
            )
            raise

    @staticmethod
    async def seek_animation(tab: Tab, animation_ids: List[str], current_time: float) -> bool:
        """
        Seek one or more animations to a specific time position.

        Args:
            tab (Tab): The browser tab object.
            animation_ids (List[str]): List of animation IDs to seek.
            current_time (float): The time position in milliseconds to seek to.

        Returns:
            bool: True if successful.
        """
        debug_logger.log_info(
            "AnimationHandler",
            "seek_animation",
            f"Seeking animations to {current_time}ms: {animation_ids}",
        )
        try:
            await AnimationHandler.enable_animation_domain(tab)
            await tab.send(
                cdp.animation.seek_animations(animations=animation_ids, current_time=current_time)
            )
            return True
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
                "AnimationHandler",
                "seek_animation",
                e,
                {"animation_ids": animation_ids, "current_time": current_time},
            )
            raise

    @staticmethod
    async def get_animation_timing(tab: Tab, animation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current timing information for an animation.

        Args:
            tab (Tab): The browser tab object.
            animation_id (str): The animation ID.

        Returns:
            Optional[Dict[str, Any]]: Timing info with current_time, duration, etc.
        """
        debug_logger.log_info(
            "AnimationHandler",
            "get_animation_timing",
            f"Getting timing for animation: {animation_id}",
        )
        try:
            await AnimationHandler.enable_animation_domain(tab)
            result = await tab.send(cdp.animation.get_current_time(id_=animation_id))
            return {
                "animation_id": animation_id,
                "current_time": result.current_time if result else None,
            }
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
                "AnimationHandler",
                "get_animation_timing",
                e,
                {"animation_id": animation_id},
            )
            raise
