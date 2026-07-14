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


async def require_org_admin(user: dict = Depends(get_current_user)) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT role FROM user_profiles WHERE id = $1", user["sub"])
    if not row or row["role"] not in ("org_admin", "super_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


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


@router.patch("/{industry_id}")
async def rename_industry(industry_id: str, payload: IndustryCreate, admin: dict = Depends(require_org_admin)):
    name = payload.name_en.strip()
    if not name:
        raise HTTPException(
            status_code=422, detail="Industry name cannot be empty")
    pool = await get_pool()
    async with pool.acquire() as conn:
        clash = await conn.fetchrow(
            "SELECT id FROM industries WHERE lower(name_en) = lower($1) AND id != $2", name, industry_id
        )
        if clash:
            raise HTTPException(
                status_code=409, detail="An industry with this name already exists")
        row = await conn.fetchrow(
            "UPDATE industries SET name_en = $1 WHERE id = $2 RETURNING id, name_en, name_ar, slug",
            name, industry_id,
        )
    if not row:
        raise HTTPException(status_code=404, detail="Industry not found")
    return row


@router.delete("/{industry_id}")
async def delete_industry(industry_id: str, admin: dict = Depends(require_org_admin)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM industries WHERE id = $1", industry_id)
    return {"deleted": result.endswith("1")}
