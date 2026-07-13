from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.85


async def find_possible_duplicate(conn, org_id: str, name: str, phones: list[str]):
    if phones:
        existing = await conn.fetchrow("""
            SELECT c.id, c.name FROM companies c
            JOIN phone_numbers p ON p.company_id = c.id
            WHERE c.organization_id = $1 AND p.number = ANY($2::text[])
            LIMIT 1
        """, org_id, phones)
        if existing:
            return existing

    candidates = await conn.fetch(
        "SELECT id, name FROM companies WHERE organization_id = $1 AND status = 'verified'",
        org_id,
    )
    for c in candidates:
        if SequenceMatcher(None, name, c["name"]).ratio() >= SIMILARITY_THRESHOLD:
            return c
    return None
