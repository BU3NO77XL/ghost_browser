"""Unit tests for StorageHandler."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.storage_handler import StorageHandler


@pytest.mark.asyncio
async def test_get_local_storage():
    """Test getting localStorage items."""
    handler = StorageHandler()
    tab = AsyncMock()

    # Mock the CDP response
    tab.send = AsyncMock(return_value={"entries": [["key1", "value1"], ["key2", "value2"]]})

    result = await handler.get_local_storage(tab, "https://example.com")

    assert result == {"key1": "value1", "key2": "value2"}
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_set_local_storage_item():
    """Test setting a localStorage item."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)

    result = await handler.set_local_storage_item(
        tab, "https://example.com", "test_key", "test_value"
    )

    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_remove_local_storage_item():
    """Test removing a localStorage item."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)

    result = await handler.remove_local_storage_item(tab, "https://example.com", "test_key")

    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_clear_local_storage():
    """Test clearing all localStorage items."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)

    result = await handler.clear_local_storage(tab, "https://example.com")

    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_get_local_storage_empty():
    """Test getting localStorage when empty."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value={"entries": []})

    result = await handler.get_local_storage(tab, "https://example.com")

    assert result == {}
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_get_local_storage_websocket_error():
    """Test handling WebSocket connection errors."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await handler.get_local_storage(tab, "https://example.com")

    assert "WebSocket connection lost" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_local_storage_item_timeout():
    """Test handling timeout errors."""
    import asyncio

    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await handler.set_local_storage_item(tab, "https://example.com", "key", "value")

    assert "timed out" in str(exc_info.value).lower()


# SessionStorage Tests


@pytest.mark.asyncio
async def test_get_session_storage():
    """Test getting sessionStorage items."""
    handler = StorageHandler()
    tab = AsyncMock()

    # Mock the CDP response
    tab.send = AsyncMock(
        return_value={
            "entries": [["session_key1", "session_value1"], ["session_key2", "session_value2"]]
        }
    )

    result = await handler.get_session_storage(tab, "https://example.com")

    assert result == {"session_key1": "session_value1", "session_key2": "session_value2"}
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_set_session_storage_item():
    """Test setting a sessionStorage item."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)

    result = await handler.set_session_storage_item(
        tab, "https://example.com", "session_key", "session_value"
    )

    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_remove_session_storage_item():
    """Test removing a sessionStorage item."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)

    result = await handler.remove_session_storage_item(tab, "https://example.com", "session_key")

    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_clear_session_storage():
    """Test clearing all sessionStorage items."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)

    result = await handler.clear_session_storage(tab, "https://example.com")

    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_storage_empty():
    """Test getting sessionStorage when empty."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value={"entries": []})

    result = await handler.get_session_storage(tab, "https://example.com")

    assert result == {}
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_storage_websocket_error():
    """Test handling WebSocket connection errors for sessionStorage."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await handler.get_session_storage(tab, "https://example.com")

    assert "WebSocket connection lost" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_session_storage_item_timeout():
    """Test handling timeout errors for sessionStorage."""
    import asyncio

    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await handler.set_session_storage_item(tab, "https://example.com", "key", "value")

    assert "timed out" in str(exc_info.value).lower()


# IndexedDB Tests


@pytest.mark.asyncio
async def test_list_indexed_databases():
    """Test listing IndexedDB databases."""
    from unittest.mock import MagicMock

    handler = StorageHandler()
    tab = AsyncMock()

    mock_result = MagicMock()
    mock_result.database_names = ["db1", "db2"]
    tab.send = AsyncMock(return_value=mock_result)

    result = await handler.list_indexed_databases(tab, "https://example.com")
    assert isinstance(result, list)
    tab.send.assert_called()


@pytest.mark.asyncio
async def test_list_indexed_databases_empty():
    """Test listing IndexedDB databases when none exist."""
    from unittest.mock import MagicMock

    handler = StorageHandler()
    tab = AsyncMock()

    mock_result = MagicMock()
    mock_result.database_names = []
    tab.send = AsyncMock(return_value=mock_result)

    result = await handler.list_indexed_databases(tab, "https://example.com")
    assert result == []


@pytest.mark.asyncio
async def test_delete_indexed_database():
    """Test deleting an IndexedDB database."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)

    result = await handler.delete_indexed_database(tab, "https://example.com", "myDB")
    assert result is True
    tab.send.assert_called()


@pytest.mark.asyncio
async def test_list_indexed_databases_websocket_error():
    """Test handling WebSocket error in list_indexed_databases."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await handler.list_indexed_databases(tab, "https://example.com")
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_indexed_database_timeout():
    """Test handling timeout in delete_indexed_database."""
    import asyncio

    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await handler.delete_indexed_database(tab, "https://example.com", "myDB")
    assert "timed out" in str(exc_info.value).lower()


# Cache Storage Tests


@pytest.mark.asyncio
async def test_list_cache_storage():
    """Test listing Cache Storage caches."""
    from unittest.mock import MagicMock

    handler = StorageHandler()
    tab = AsyncMock()

    mock_cache1 = MagicMock()
    mock_cache1.cache_name = "workbox-precache"
    mock_cache2 = MagicMock()
    mock_cache2.cache_name = "api-cache"
    tab.send = AsyncMock(return_value=[mock_cache1, mock_cache2])

    result = await handler.list_cache_storage(tab, "https://example.com")
    assert isinstance(result, list)
    assert "workbox-precache" in result
    assert "api-cache" in result


@pytest.mark.asyncio
async def test_list_cache_storage_empty():
    """Test listing Cache Storage when no caches exist."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=[])

    result = await handler.list_cache_storage(tab, "https://example.com")
    assert result == []


@pytest.mark.asyncio
async def test_delete_cache():
    """Test deleting a Cache Storage cache."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(return_value=None)

    result = await handler.delete_cache(tab, "https://example.com", "api-cache")
    assert result is True
    tab.send.assert_called_once()


@pytest.mark.asyncio
async def test_list_cache_storage_websocket_error():
    """Test handling WebSocket error in list_cache_storage."""
    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=Exception("WebSocket connection lost"))

    with pytest.raises(Exception) as exc_info:
        await handler.list_cache_storage(tab, "https://example.com")
    assert "WebSocket" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_cache_timeout():
    """Test handling timeout in delete_cache."""
    import asyncio

    handler = StorageHandler()
    tab = AsyncMock()
    tab.send = AsyncMock(side_effect=asyncio.TimeoutError())

    with pytest.raises(Exception) as exc_info:
        await handler.delete_cache(tab, "https://example.com", "api-cache")
    assert "timed out" in str(exc_info.value).lower()
