"""LeadSheet — substitui a grade harmônica legada no SetSync."""

from .converter import (
    grade_flat_to_leadsheet,
    is_leadsheet_document,
    leadsheet_to_grade_flat,
    resolve_leadsheet_document,
    resolve_to_grade_flat,
)
from .build import build_payload

__all__ = [
    "build_payload",
    "grade_flat_to_leadsheet",
    "is_leadsheet_document",
    "leadsheet_to_grade_flat",
    "resolve_leadsheet_document",
    "resolve_to_grade_flat",
]
