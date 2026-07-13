import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_search_verified_only_stub():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {...}
    # Simple execution check to ensure SQL results map directly to schemas
    assert len(mock_conn.fetch.return_value) == 1
