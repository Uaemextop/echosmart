"""Reusable pagination primitives.

Provides ``PaginationParams`` for capturing page/sort query parameters and
``PaginatedResponse[T]`` as a generic envelope that carries page metadata
alongside the result items.

Usage in a router::

    from src.shared.pagination import PaginatedResponse
    from src.shared.dependencies import get_pagination

    @router.get("/sensors", response_model=PaginatedResponse[SensorOut])
    async def list_sensors(pagination: PaginationParams = Depends(get_pagination)):
        ...
"""

from __future__ import annotations

import math
from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query-parameter bag for paginated list endpoints.

    Attributes:
        page: 1-based page number.
        per_page: Items per page (clamped to 1–100).
        sort_by: Optional column name to sort on.
        sort_order: ``"asc"`` or ``"desc"``.
    """

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    per_page: int = Field(default=50, ge=1, le=100, description="Items per page")
    sort_by: str | None = Field(default=None, description="Column to sort by")
    sort_order: str = Field(default="desc", description="Sort direction: asc or desc")

    model_config = {"extra": "forbid"}

    @field_validator("sort_order")
    @classmethod
    def _validate_sort_order(cls, value: str) -> str:
        normalised = value.strip().lower()
        if normalised not in ("asc", "desc"):
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return normalised

    @property
    def offset(self) -> int:
        """Calculate the SQL OFFSET from page and per_page."""
        return (self.page - 1) * self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response envelope.

    Attributes:
        items: The page of results.
        total: Total number of matching records.
        page: Current page number.
        per_page: Requested page size.
        pages: Total number of pages.
    """

    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    per_page: int = Field(ge=1)
    pages: int = Field(ge=0)

    model_config = {"extra": "forbid"}

    @classmethod
    def build(cls, *, items: list[T], total: int, page: int, per_page: int) -> PaginatedResponse[T]:
        """Factory that calculates ``pages`` automatically.

        Args:
            items: The slice of results for the current page.
            total: Total count of matching records.
            page: Current page number.
            per_page: Requested page size.

        Returns:
            A fully populated ``PaginatedResponse``.
        """
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=math.ceil(total / per_page) if per_page > 0 else 0,
        )
