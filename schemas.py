"""Pydantic schemas for validating TORO API payloads and query params."""

from __future__ import annotations

from typing import Annotated, Literal
import re

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationError,
    field_validator,
)

Priority = Literal["low", "medium", "high"]
Status = Literal["created", "in_progress", "completed"]
PhoneStr = Annotated[str, Field(min_length=17, max_length=17)]

PHONE_PATTERN = re.compile(r"^\+7-\d{3}-\d{3}-\d{2}-\d{2}$")
EQUIPMENT_ID_PATTERN = re.compile(r"^[A-Z0-9-]{3,40}$")


class _BaseSchema(BaseModel):
    """Shared configuration for API schemas."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OrderCreateSchema(_BaseSchema):
    """Schema for validating incoming order creation payloads."""

    equipment_type: Annotated[str, Field(min_length=1, max_length=120)]
    equipment_id: Annotated[str, Field(min_length=1, max_length=120)]
    issue_description: Annotated[str, Field(min_length=1)]
    priority: Priority = "medium"
    requester_name: Annotated[str, Field(min_length=1, max_length=120)]
    department: Annotated[str, Field(min_length=1, max_length=120)]
    contact_phone: PhoneStr
    contact_email: EmailStr

    @field_validator("issue_description")
    @classmethod
    def limit_issue_description(cls, value: str) -> str:
        if len(value) > 2000:
            msg = "Issue description must not exceed 2000 characters"
            raise ValueError(msg)
        return value

    @field_validator("contact_phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value:
            raise ValueError("Phone is required")
        if not PHONE_PATTERN.match(value):
            raise ValueError("Phone must match +7-XXX-XXX-XX-XX")
        return value

    @field_validator("equipment_id")
    @classmethod
    def validate_equipment_id(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not EQUIPMENT_ID_PATTERN.match(normalized):
            msg = "Equipment ID must be 3-40 chars: A-Z, 0-9 or '-' (Opus 4.5)"
            raise ValueError(msg)
        return normalized

    @field_validator("department")
    @classmethod
    def normalize_department(cls, value: str) -> str:
        collapsed = " ".join(value.split())
        if not collapsed:
            raise ValueError("Department is required")
        return collapsed


class OrderFiltersSchema(_BaseSchema):
    """Schema for validating query parameters of the list endpoint."""

    priority: Priority | None = None
    status: Status | None = None
    department: Annotated[str, Field(min_length=1, max_length=120)] | None = None


class OrderStatusUpdateSchema(_BaseSchema):
    """Schema for validating status updates (Opus 4.5)."""

    status: Status


__all__ = [
    "OrderCreateSchema",
    "OrderFiltersSchema",
    "OrderStatusUpdateSchema",
    "Priority",
    "Status",
]
