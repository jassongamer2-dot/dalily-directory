from fastapi import APIRouter, Depends, Query
from app.deps import get_current_org_id, get_current_user
from app.database import get_pool
from app.models.schemas import CompanySearchResponse, CompanyOut, CompanyCreate, PhoneOut
from app.services.phone_validation import validate_phone

router = APIRouter(prefix="/companies", tags=["companies"])


# app/routers/companies.py — search_companies, full replacement
@router.get("/search", response_model=CompanySearchResponse)
async def search_companies(
    q: str = Query(""),
    industry: str | None = None,
    cursor: int = 0,
    limit: int = Query(30, le=100),
    org_id: str = Depends(get_current_org_id),
):
    pool = await get_pool()
    q = q.strip()
    async with pool.acquire() as conn:
        if q:
            rows = await conn.fetch("""
                SELECT c.id, c.name, c.industry_id, i.name_en AS industry_name, a.address_text AS address,
                       coalesce(jsonb_agg(jsonb_build_object('number', p.number, 'type', p.number_type))
                         FILTER (WHERE p.id IS NOT NULL), '[]') AS phones
                FROM companies c
                LEFT JOIN industries i ON i.id = c.industry_id
                LEFT JOIN phone_numbers p ON p.company_id = c.id
                LEFT JOIN addresses a ON a.company_id = c.id
                WHERE c.organization_id = $1 AND c.status = 'verified'
                  AND (c.name ILIKE '%' || $2 || '%' OR c.name % $2)
                  AND ($3::uuid IS NULL OR c.industry_id = $3)
                GROUP BY c.id, i.name_en, a.address_text
                ORDER BY similarity(c.name, $2) DESC
                OFFSET $4 LIMIT $5
            """, org_id, q, industry, cursor, limit)
        else:
            rows = await conn.fetch("""
                SELECT c.id, c.name, c.industry_id, i.name_en AS industry_name, a.address_text AS address,
                       coalesce(jsonb_agg(jsonb_build_object('number', p.number, 'type', p.number_type))
                         FILTER (WHERE p.id IS NOT NULL), '[]') AS phones
                FROM companies c
                LEFT JOIN industries i ON i.id = c.industry_id
                LEFT JOIN phone_numbers p ON p.company_id = c.id
                LEFT JOIN addresses a ON a.company_id = c.id
                WHERE c.organization_id = $1 AND c.status = 'verified'
                  AND ($2::uuid IS NULL OR c.industry_id = $2)
                GROUP BY c.id, i.name_en, a.address_text
                ORDER BY c.name ASC
                OFFSET $3 LIMIT $4
            """, org_id, industry, cursor, limit)

    results = [CompanyOut(**dict(r)) for r in rows]
    next_cursor = cursor + limit if len(results) == limit else None
    return CompanySearchResponse(results=results, next_cursor=next_cursor)
