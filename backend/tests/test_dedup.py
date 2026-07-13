import pytest
from unittest.mock import AsyncMock
from app.services.dedup import find_possible_duplicate


@pytest.mark.asyncio
async def test_exact_phone_match_flags_duplicate():
    # Mocking asyncpg connection fetchrow response
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {...}

    match = await find_possible_duplicate(mock_conn, "org-uuid", "Test Company Name", ["01001234567"])
    assert match is not None
    assert match["id"] == "existing-uuid"
