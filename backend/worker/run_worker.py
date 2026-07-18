from worker.parsers.docx_extract import extract_docx_text
from worker.parsers.excel_gaps import find_gaps, excel_row_to_entry
from worker.extraction.structure_entries import structure_page, structure_text_blocks
from worker.extraction.tier_b_claude import extract_page_tier_b, extract_text_tier_b
from worker.extraction.tier_a_paddle import extract_page_tier_a
from worker.extraction.preprocess import preprocess_for_ocr
from worker.extraction.pdf_to_images import pdf_page_to_array, array_to_png_bytes
from app.services.dedup import find_possible_duplicate
from app.services.storage import download_from_storage
from app.config import settings
import pandas as pd
import fitz
import asyncpg
import asyncio
import sys
import os
# Force Python to recognize the backend root folder before importing the app
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


POLL_INTERVAL_SECONDS = 5


async def claim_next_job(conn: asyncpg.Connection):
    return await conn.fetchrow("""
        UPDATE ingestion_jobs
        SET status = 'processing'
        WHERE id = (
            SELECT id FROM ingestion_jobs
            WHERE status = 'queued'
            ORDER BY uploaded_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        RETURNING *
    """)


async def process_job(pool: asyncpg.Pool, job: asyncpg.Record):
    try:
        local_path = await download_from_storage(job["organization_id"], job["file_name"])

        if job["file_type"] in ("pdf_scanned", "pdf_text"):
            stats = await _process_pdf(pool, job, local_path)
        elif job["file_type"] == "excel":
            stats = await _process_excel(pool, job, local_path)
        elif job["file_type"] == "word":
            stats = await _process_word(pool, job, local_path)
        else:
            raise ValueError(f"Unknown file_type: {job['file_type']}")

        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE ingestion_jobs SET status='completed', entries_extracted=$2, entries_needing_review=$3
                WHERE id=$1
            """, job["id"], stats["extracted"], stats["needing_review"])

    except Exception:
        async with pool.acquire() as conn:
            await conn.execute("UPDATE ingestion_jobs SET status='failed' WHERE id=$1", job["id"])
        raise


async def _process_pdf(pool, job, local_path) -> dict:
    doc = fitz.open(local_path)
    total_pages = len(doc)
    async with pool.acquire() as conn:
        await conn.execute("UPDATE ingestion_jobs SET total_pages=$2 WHERE id=$1", job["id"], total_pages)

    extracted = needing_review = 0
    for page_num in range(total_pages):
        try:
            text_layer = doc[page_num].get_text().strip()  # pyright: ignore[reportAttributeAccessIssue]
            if text_layer:
                entries = structure_text_blocks(text_layer)
            else:
                page_array = pdf_page_to_array(local_path, page_num)
                if settings.EXTRACTION_TIER == "tier_b":
                    entries = extract_page_tier_b(array_to_png_bytes(page_array))
                else:
                    entries = structure_page(extract_page_tier_a(preprocess_for_ocr(page_array)))
            e, r = await _persist_entries(pool, job, entries, source_page=page_num)
            extracted += e
            needing_review += r
        except Exception as page_error:
            print(f"Page {page_num} failed, skipping: {page_error}")
            continue

    return {"extracted": extracted, "needing_review": needing_review}


async def _process_excel(pool, job, local_path) -> dict:
    df = pd.read_excel(local_path).rename(columns=lambda c: c.strip().lower())
    find_gaps(df)
    entries = [excel_row_to_entry(row) for row in df.to_dict("records")]
    e, r = await _persist_entries(pool, job, entries, source_page=None, force_review=True)
    return {"extracted": e, "needing_review": r}


async def _process_word(pool, job, local_path) -> dict:
    text = extract_docx_text(local_path)
    entries = extract_text_tier_b(
        text) if settings.EXTRACTION_TIER == "tier_b" else structure_text_blocks(text)
    e, r = await _persist_entries(pool, job, entries, source_page=None)
    return {"extracted": e, "needing_review": r}


async def _persist_entries(pool, job, entries, source_page, force_review=False) -> tuple[int, int]:
    extracted = needing_review = 0
    async with pool.acquire() as conn:
        for entry in entries:
            dup = await find_possible_duplicate(
                conn, job["organization_id"], entry.get("name") or "",
                [p["number"] for p in entry.get("phones", [])],
            )
            status = "pending_review" if (force_review or dup or entry.get(
                "confidence") != "high") else "verified"
            company = await conn.fetchrow("""
                INSERT INTO companies (organization_id, name, source_document, source_page,
                                        status, confidence_score, duplicate_of)
                VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING id
            """, job["organization_id"], entry.get("name"), job["file_name"], source_page,
                status, _confidence_to_score(entry.get("confidence")), dup["id"] if dup else None)

            for phone in entry.get("phones", []):
                await conn.execute(
                    "INSERT INTO phone_numbers (company_id, number, number_type) VALUES ($1, $2, $3)",
                    company["id"], phone["number"], phone["type"],
                )
            if entry.get("address"):
                await conn.execute(
                    "INSERT INTO addresses (company_id, address_text) VALUES ($1, $2)",
                    company["id"], entry["address"],
                )
            extracted += 1
            needing_review += status == "pending_review"
    return extracted, needing_review


def _confidence_to_score(label: str | None) -> float:
    return {"high": 0.95, "medium": 0.7, "low": 0.4}.get(label or "", 0.5)

# worker/run_worker.py — main_loop(), one-line fix


async def main_loop():
    pool = await asyncpg.create_pool(settings.DATABASE_URL, min_size=1, max_size=3, statement_cache_size=0)
    while True:
        async with pool.acquire() as conn, conn.transaction():
            job = await claim_next_job(conn)
        if job:
            await process_job(pool, job)
        else:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main_loop())
