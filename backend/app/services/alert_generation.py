"""Integration with the BAML SDK to generate alerts."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from baml_client.sync_client import b


BAML_PROJECT_ROOT = Path(__file__).resolve().parent.parent / "baml"


def _to_dict(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        return result
    if hasattr(result, 'model_dump'):
        return result.model_dump()  # Pydantic v2
    if hasattr(result, 'dict'):
        return result.dict()  # Pydantic v1
    raise TypeError("Unexpected BAML result type: {type(result)!r}")


def generate_alerts_from_text(text: str, clinic_policies: Optional[str] = None) -> Dict[str, Any]:
    """Run the BAML task against the provided text."""

    client = get_client(BAML_PROJECT_ROOT)
    result = client.tasks.ExtractMedicalAlertsTask.invoke(
        input_text=text,
        clinic_policies=clinic_policies or "",
    )
    return _to_dict(result)
