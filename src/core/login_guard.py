"""Login guard — blocks tool execution when instance is pending manual login."""

from typing import Any, Dict, Optional

from core.manual_login_handler import manual_login_handler


async def check_pending_login_guard(instance_id: str) -> Optional[Dict[str, Any]]:
    """
    Guard function: blocks tool execution if instance is pending manual login.

    Call this at the start of every tool that takes instance_id (except
    confirm_manual_login and check_login_status which must work during pending login).

    Returns None if the instance is NOT pending (tool can proceed).
    Returns a blocking response dict if the instance IS pending.
    """
    if not await manual_login_handler.is_pending_login(instance_id):
        return None
    pending = await manual_login_handler.get_pending_info(instance_id)
    return {
        "blocked": True,
        "action_required": "STOP_AND_WAIT_FOR_USER",
        "reason": "INSTANCE_PENDING_MANUAL_LOGIN",
        "instance_id": instance_id,
        "pending_since": pending.get("registered_at") if pending else None,
        "next_step": f"Ask user to log in manually, WAIT for their reply, then call confirm_manual_login(instance_id='{instance_id}')",
        "message": (
            "STOP — This browser instance is waiting for the user to log in manually. "
            "You CANNOT use any tools on this instance until the user finishes logging in. "
            "Send a message to the user asking them to log in on the open browser window. "
            "WAIT for the user to reply confirming they are done. "
            f"Then call confirm_manual_login(instance_id='{instance_id}'). "
            "DO NOT try other tools, DO NOT close the browser, DO NOT give up."
        ),
    }
