EXTRACTION_PROMPT = """You are extracting business directory entries from a scanned page of the
Egyptian Industrial Encyclopedia (الموسوعة الصناعية المصرية).

Return ONLY a JSON array. For each company entry visible on the page, extract:
- "name": company name (Arabic, as printed)
- "phones": array of {"number": string, "type": "mobile"|"landline"|"unspecified"}
- "address": full address text (Arabic, as printed)
- "confidence": "high"|"medium"|"low"

Rules:
- Do NOT extract fax numbers or email addresses.
- Do NOT invent or guess any value that is not visibly printed on the page.
- If a field is illegible, omit it rather than guessing.
- Preserve Arabic text exactly as printed.

Return valid JSON only — no prose, no markdown fences."""
