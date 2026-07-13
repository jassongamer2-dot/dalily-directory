from fastapi import APIRouter, UploadFile, Depends
from app.deps import get_current_org_id, get_current_user
from app.database import get_pool
from app.services.storage import upload_to_storage
from app.config import settings

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    org_id: str = Depends(get_current_org_id),
    user: dict = Depends(get_current_user),
):
    contents = await file.read()
    filename = file.filename or "unnamed_upload"
    await upload_to_storage(org_id, filename, contents)

    pool = await get_pool()
    async with pool.acquire() as conn:
        job = await conn.fetchrow("""
            INSERT INTO ingestion_jobs (organization_id, file_name, file_type, extraction_tier, status, uploaded_by)
            VALUES ($1, $2, $3, $4, 'queued', $5)
            RETURNING id
        """, org_id, filename, _infer_file_type(filename), settings.EXTRACTION_TIER, user["sub"])
    return {"job_id": str(job["id"]), "status": "queued"}


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, org_id: str = Depends(get_current_org_id)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        job = await conn.fetchrow(
            "SELECT * FROM ingestion_jobs WHERE id = $1 AND organization_id = $2", job_id, org_id
        )
        return dict(job) if job else {"error": "not found"}


def _infer_file_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    return {"pdf": "pdf_scanned", "xlsx": "excel", "csv": "excel", "docx": "word"}.get(ext, "pdf_scanned")
