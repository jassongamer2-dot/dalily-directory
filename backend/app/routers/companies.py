from fastapi import APIRouter, Depends, Query
from app.deps import get_current_org_id, get_current_user
from app.database import get_pool
from app.models.schemas import CompanySearchResponse, CompanyOut, CompanyCreate, PhoneOut
from app.services.phone_validation import validate_phone

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/search", response_model=CompanySearchResponse)
async def search_companies(
    q: str = Query(..., min_length=1),
    industry: str | None = None,
    cursor: int = 0,
    limit: int = Query(30, le=100),
    org_id: str = Depends(get_current_org_id),
):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT c.id, c.name, c.industry_id, i.name_en AS industry_name, a.address_text AS address,
                   coalesce(
                     jsonb_agg(jsonb_build_object('number', p.number, 'type', p.number_type))
                       FILTER (WHERE p.id IS NOT NULL),
                     '[]'
                   ) AS phones
            FROM companies c
            LEFT JOIN industries i ON i.id = c.industry_id
            LEFT JOIN phone_numbers p ON p.company_id = c.id
            LEFT JOIN addresses a ON a.company_id = c.id
            WHERE c.organization_id = $1
              AND c.status = 'verified'
              AND c.name % $2
              AND ($3::uuid IS NULL OR c.industry_id = $3)
            GROUP BY c.id, i.name_en, a.address_text
            ORDER BY similarity(c.name, $2) DESC
            OFFSET $4 LIMIT $5
        """, org_id, q, industry, cursor, limit)

    results = [CompanyOut(**dict(r)) for r in rows]
    next_cursor = cursor + limit if len(results) == limit else None
    return CompanySearchResponse(results=results, next_cursor=next_cursor)


@router.post("", response_model=CompanyOut)
async def create_company_manually(
    payload: CompanyCreate,
    org_id: str = Depends(get_current_org_id),
    user: dict = Depends(get_current_user),
):
    pool = await get_pool()
    validated_phones = [validate_phone(p.number) for p in payload.phones]
    async with pool.acquire() as conn, conn.transaction():
        company = await conn.fetchrow("""
            INSERT INTO companies (organization_id, name, industry_id, status, confidence_score, created_by)
            VALUES ($1, $2, $3, 'verified', 1.0, $4) RETURNING id
        """, org_id, payload.name, payload.industry_id, user["sub"])

        for phone in validated_phones:
            await conn.execute(
                "INSERT INTO phone_numbers (company_id, number, number_type) VALUES ($1, $2, $3)",
                company["id"], phone["number"], phone["type"],
            )
        if payload.address:
            await conn.execute(
                "INSERT INTO addresses (company_id, address_text) VALUES ($1, $2)",
                company["id"], payload.address,
            )
        await conn.execute("""
            INSERT INTO audit_log (organization_id, actor_id, action, target_table, target_id)
            VALUES ($1, $2, 'company.manual_create', 'companies', $3)
        """, org_id, user["sub"], company["id"])

    return CompanyOut(
        id=company["id"], name=payload.name, industry_id=payload.industry_id, industry_name=None,
        address=payload.address,
        phones=[PhoneOut(number=p["number"], type=p["type"])
                for p in validated_phones],
    )
