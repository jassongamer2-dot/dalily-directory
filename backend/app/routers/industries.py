import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.deps import get_current_user
from app.database import get_pool

router = APIRouter(prefix="/industries", tags=["industries"])


class IndustryCreate(BaseModel):
    name_en: str


@router.get("")
async def list_industries(user: dict = Depends(get_current_user)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT id, name_en, name_ar, slug FROM industries ORDER BY name_en")


@router.post("")
async def get_or_create_industry(payload: IndustryCreate, user: dict = Depends(get_current_user)):
    name = payload.name_en.strip()
    if not name:
        raise HTTPException(
            status_code=422, detail="Industry name cannot be empty")
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "industry"

    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("""
            INSERT INTO industries (name_en, slug)
            VALUES ($1, $2)
            ON CONFLICT (lower(name_en)) DO UPDATE SET name_en = industries.name_en
            RETURNING id, name_en, name_ar, slug
        """, name, slug)
