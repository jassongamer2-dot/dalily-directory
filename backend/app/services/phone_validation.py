import re

EGYPT_MOBILE_RE = re.compile(r"01[0125]\d{8}$")
EGYPT_LANDLINE_RE = re.compile(r"0\d{1,2}\d{6,8}$")


def validate_phone(raw: str) -> dict:
    digits = re.sub(r"\D", "", raw)
    if EGYPT_MOBILE_RE.fullmatch(digits):
        return {"number": digits, "type": "mobile", "valid": True}
    if EGYPT_LANDLINE_RE.fullmatch(digits):
        return {"number": digits, "type": "landline", "valid": True}
    return {"number": digits, "type": "unspecified", "valid": False}
