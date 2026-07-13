from pydantic import BaseModel
from typing import Literal
from uuid import UUID


class PhoneOut(BaseModel):
    number: str
    type: Literal["mobile", "landline", "unspecified"]


class CompanyOut(BaseModel):
    id: UUID
    name: str
    industry_id: UUID | None
    industry_name: str | None
    address: str | None
    phones: list[PhoneOut]


class CompanySearchResponse(BaseModel):
    results: list[CompanyOut]
    next_cursor: int | None


class CompanyCreate(BaseModel):
    name: str
    industry_id: UUID | None = None
    phones: list[PhoneOut] = []
    address: str | None = None
