from app.services.phone_validation import validate_phone, EGYPT_MOBILE_RE, EGYPT_LANDLINE_RE

VERTICAL_GAP_THRESHOLD = 15


def group_lines_into_blocks(lines: list[dict]) -> list[list[dict]]:
    sorted_lines = sorted(
        lines, key=lambda l: l["bbox"][0][1] if l["bbox"] else 0)
    blocks, current, prev_bottom = [], [], None
    for line in sorted_lines:
        top = line["bbox"][0][1] if line["bbox"] else (prev_bottom or 0)
        if prev_bottom is not None and (top - prev_bottom) > VERTICAL_GAP_THRESHOLD:
            blocks.append(current)
            current = []
        current.append(line)
        prev_bottom = line["bbox"][2][1] if line["bbox"] else top
    if current:
        blocks.append(current)
    return blocks


def classify_block(block: list[dict]) -> dict:
    phones, address_lines, name_lines = [], [], []
    for line in block:
        digits_only = "".join(c for c in line["text"] if c.isdigit())
        if EGYPT_MOBILE_RE.fullmatch(digits_only) or EGYPT_LANDLINE_RE.fullmatch(digits_only):
            phones.append(validate_phone(line["text"]))
        elif not name_lines and not any(c.isdigit() for c in line["text"]):
            name_lines.append(line["text"])
        else:
            address_lines.append(line["text"])
    return {
        "name": " ".join(name_lines) or None,
        "phones": phones,
        "address": " ".join(address_lines) or None,
        "confidence": "medium" if phones and name_lines else "low",
    }


def structure_page(lines: list[dict]) -> list[dict]:
    return [classify_block(b) for b in group_lines_into_blocks(lines) if b]


def structure_text_blocks(text: str) -> list[dict]:
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    return [classify_block([{"text": line, "bbox": None} for line in block.split("\n")]) for block in blocks]
