"""Módulo de diagramas de acordes — resolução de notas, API v1 e metadados."""

from chord_diagram.service import chord_diagram_payload, list_instruments
from chord_diagram.api_service import (
    API_VERSION,
    build_chord_document,
    build_scale_document,
    build_arpeggio_document,
    catalog_payload,
    chord_document_for_modal,
    fetch_progression_for_modal,
)

__all__ = [
    'chord_diagram_payload',
    'list_instruments',
    'API_VERSION',
    'build_chord_document',
    'build_scale_document',
    'build_arpeggio_document',
    'catalog_payload',
    'chord_document_for_modal',
    'fetch_progression_for_modal',
]
