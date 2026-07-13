import pandas as pd
from app.services.phone_validation import validate_phone

REQUIRED_FIELDS = ["company_name", "phone", "address"]


def find_gaps(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=lambda c: c.strip().lower())
    missing_mask = df[REQUIRED_FIELDS].isna().any(axis=1)
    gaps = df[missing_mask].copy()
    gaps["missing_fields"] = gaps[REQUIRED_FIELDS].apply(
        lambda row: [f for f in REQUIRED_FIELDS if pd.isna(row[f])], axis=1
    )
    return gaps


def excel_row_to_entry(row: dict) -> dict:
    phone_raw = row.get("phone")
    phones = [validate_phone(str(phone_raw))] if pd.notna(phone_raw) else []
    return {
        "name": row.get("company_name") if pd.notna(row.get("company_name")) else None,
        "phones": phones,
        "address": row.get("address") if pd.notna(row.get("address")) else None,
        "confidence": "medium",
    }
