import asyncpg
from app.config import settings

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=1,
            max_size=10,
            statement_cache_size=0  # <-- Crucial: prevents DuplicatePreparedStatementError
        )
    return _pool
