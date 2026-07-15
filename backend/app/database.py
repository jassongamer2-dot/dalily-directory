# app/database.py — replace the whole file
import json
import asyncpg
from app.config import settings

_pool: asyncpg.Pool | None = None


async def _init_connection(conn):
    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog",
    )


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=2,
            max_size=10,
            statement_cache_size=0,
            init=_init_connection,
        )
    return _pool