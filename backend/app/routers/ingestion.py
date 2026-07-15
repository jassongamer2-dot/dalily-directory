# app/routers/ingestion.py — full file
from fastapi import APIRouter, UploadFile, Depends, BackgroundTasks
from app.config import settings
from app.deps import get_current_org_id, get_current_user
from app.database import get_pool
from app.services.storage import upload_to_storage

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/upload")
async def upload_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    org_id: str = Depends(get_current_org_id),
    user: dict = Depends(get_current_user),
):
    filename = file.filename or "unnamed_upload"
    contents = await file.read()

    pool = await get_pool()
    async with pool.acquire() as conn:
        job = await conn.fetchrow("""
            INSERT INTO ingestion_jobs (organization_id, file_name, file_type, extraction_tier, status, uploaded_by)
            VALUES ($1, $2, $3, $4, 'uploading', $5) RETURNING id
        """, org_id, filename, _infer_file_type(filename), settings.EXTRACTION_TIER, user["sub"])

    background_tasks.add_task(_finish_upload, str(job["id"]), org_id, filename, contents)
    return {"job_id": str(job["id"]), "status": "uploading"}


async def _finish_upload(job_id: str, org_id: str, filename: str, contents: bytes):
    pool = await get_pool()
    try:
        await upload_to_storage(org_id, filename, contents)
        async with pool.acquire() as conn:
            await conn.execute("UPDATE ingestion_jobs SET status = 'queued' WHERE id = $1", job_id)
    except Exception:
        async with pool.acquire() as conn:
            await conn.execute("UPDATE ingestion_jobs SET status = 'failed' WHERE id = $1", job_id)


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str, org_id: str = Depends(get_current_org_id)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        job = await conn.fetchrow(
            "SELECT * FROM ingestion_jobs WHERE id = $1 AND organization_id = $2", job_id, org_id
        )
    return dict(job) if job else {"error": "not found"}


def _infer_file_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return {"pdf": "pdf_scanned", "xlsx": "excel", "csv": "excel", "docx": "word"}.get(ext, "pdf_scanned")