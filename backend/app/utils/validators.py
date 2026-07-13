from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status


def validate_uuid(value: str, field_name: str = "id") -> str:
    try:
        uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{field_name}' must be a valid UUID, got '{value}'.",
        ) from exc
    return value


def validate_date_range(
    date_from: Optional[datetime], date_to: Optional[datetime]
) -> None:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"'date_from' ({date_from.isoformat()}) must not be after "
                f"'date_to' ({date_to.isoformat()})."
            ),
        )


def validate_pagination(
    page: int, page_size: int, max_page_size: int = 100
) -> None:
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="page must be >= 1",
        )

    if not (1 <= page_size <= max_page_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"page_size must be between 1 and {max_page_size}",
        )


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def is_blank(value: Optional[str]) -> bool:
    return value is None or value.strip() == ""