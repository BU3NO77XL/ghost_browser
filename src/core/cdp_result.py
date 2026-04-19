"""Compatibility helpers for nodriver CDP return values."""

from typing import Any, Dict, List, Tuple


def runtime_parts(result: Any) -> Tuple[Any, Any]:
    """Return (RemoteObject, ExceptionDetails) from Runtime/Debugger evaluation results."""
    if isinstance(result, (tuple, list)):
        value = result[0] if len(result) > 0 else None
        exception = result[1] if len(result) > 1 else None
        return value, exception
    return getattr(result, "result", None), getattr(result, "exception_details", None)


def runtime_value(result: Any) -> Any:
    remote_object, _ = runtime_parts(result)
    return getattr(remote_object, "value", None) if remote_object else None


def remote_object_to_dict(remote_object: Any) -> Dict[str, Any]:
    if not remote_object:
        return {}
    type_value = getattr(remote_object, "type_", None)
    return {
        "type": getattr(type_value, "value", type_value),
        "value": getattr(remote_object, "value", None),
        "description": getattr(remote_object, "description", None),
        "object_id": (
            str(getattr(remote_object, "object_id", None))
            if getattr(remote_object, "object_id", None)
            else None
        ),
    }


def exception_details_to_dict(exception_details: Any) -> Dict[str, Any]:
    if not exception_details:
        return {}
    return {
        "text": getattr(exception_details, "text", None),
        "line_number": getattr(exception_details, "line_number", None),
        "column_number": getattr(exception_details, "column_number", None),
    }


def to_json(value: Any) -> Any:
    if hasattr(value, "to_json"):
        return value.to_json()
    if isinstance(value, list):
        return [to_json(item) for item in value]
    if isinstance(value, tuple):
        return [to_json(item) for item in value]
    if isinstance(value, dict):
        return {key: to_json(item) for key, item in value.items()}
    return value


def dom_storage_items_to_dict(items: Any) -> Dict[str, str]:
    output: Dict[str, str] = {}
    entries = items.get("entries", []) if isinstance(items, dict) else items or []
    for entry in entries:
        if len(entry) >= 2:
            output[str(entry[0])] = str(entry[1])
    return output


def indexeddb_request_data_to_dict(result: Any) -> Dict[str, Any]:
    if isinstance(result, (tuple, list)):
        entries = result[0] if len(result) > 0 else []
        has_more = bool(result[1]) if len(result) > 1 else False
        return {"object_store_data_entries": to_json(entries or []), "has_more": has_more}
    return to_json(result or {})


def coverage_parts(result: Any) -> Tuple[List[Any], float]:
    if isinstance(result, (tuple, list)):
        return (result[0] if len(result) > 0 else []) or [], float(result[1] or 0) if len(result) > 1 else 0
    return getattr(result, "result", None) or [], getattr(result, "timestamp", 0) or 0
