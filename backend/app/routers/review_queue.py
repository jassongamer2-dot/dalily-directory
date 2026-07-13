from fastapi import APIRouter, Depends
from app.deps import get_current_org_id, get_current_user
from app.database import get_pool

router = APIRouter(prefix="/review-queue", tags=["review-queue"])


@router.get("")
async def list_review_queue(org_id: str = Depends(get_current_org_id)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM companies WHERE organization_id = $1 AND status = 'pending_review' ORDER BY created_at",
            org_id,
        )


@router.post("/{company_id}/approve")
async def approve_entry(company_id: str, org_id: str = Depends(get_current_org_id), user: dict = Depends(get_current_user)):
    pool = await get_pool()
    async with pool.acquire() as conn, conn.transaction():
        await conn.execute(
            "UPDATE companies SET status='verified', updated_at=now() WHERE id=$1 AND organization_id=$2",
            company_id, org_id,
        )
        await conn.execute("""
            INSERT INTO audit_log (organization_id, actor_id, action, target_table, target_id)
            VALUES ($1, $2, 'company.approved', 'companies', $3)
        """, org_id, user["sub"], company_id)
    return {"status": "verified"}


@router.post("/{company_id}/reject")
async def reject_entry(company_id: str, org_id: str = Depends(get_current_org_id), user: dict = Depends(get_current_user)):
    pool = await get_pool()
    async with pool.acquire() as conn, conn.transaction():
        await conn.execute(
            "UPDATE companies SET status='rejected', updated_at=now() WHERE id=$1 AND organization_id=$2",
            company_id, org_id,
        )
        await conn.execute("""
            INSERT INTO audit_log (organization_id, actor_id, action, target_table, target_id)
            VALUES ($1, $2, 'company.rejected', 'companies', $3)
        """, org_id, user["sub"], company_id)
    return {"status": "rejected"}
