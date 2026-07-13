import anthropic
import base64
import json
from worker.extraction.prompts import EXTRACTION_PROMPT

client = anthropic.Anthropic()


def _get_text(response) -> str:
    """Safely extracts text from blocks, bypassing Pylance attribute issues."""
    for block in response.content:
        # Use getattr to safely check for 'text' attribute across different Block types
        if hasattr(block, 'text'):
            return getattr(block, 'text')
    return ""


def extract_page_tier_b(image_bytes: bytes) -> list[dict]:
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64",
                                             "media_type": "image/png", "data": b64}},
                {"type": "text", "text": EXTRACTION_PROMPT},
            ],
        }],
    )
    return json.loads(_get_text(response))


def extract_text_tier_b(text: str) -> list[dict]:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": f"{EXTRACTION_PROMPT}\n\nText to extract from:\n{text}"}],
    )
    return json.loads(_get_text(response))
