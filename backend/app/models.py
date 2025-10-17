"""Pydantic models for the FastAPI backend."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """Possible alert categories."""

    VACCINE_EXPIRATION = "VACCINE_EXPIRATION"
    DENTAL_PROCEDURE = "DENTAL_PROCEDURE"
    ROUTINE_EXAM = "ROUTINE_EXAM"
    FOLLOW_UP = "FOLLOW_UP"
    OTHER = "OTHER"


class Alert(BaseModel):
    title: str = Field(..., description="Human-readable title for the alert")
    alert_type: AlertType = Field(..., description="Classification of the alert")
    due_date: Optional[date] = Field(None, description="Due date for the task")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    source_excerpt: str = Field(..., description="Snippet supporting the alert")
    notes: Optional[str] = Field(None, description="Additional context or instructions")


class AlertResponse(BaseModel):
    patient_name: Optional[str] = Field(None, description="Name of the patient if available")
    patient_species: Optional[str] = Field(None, description="Species of the patient")
    alerts: List[Alert] = Field(default_factory=list, description="Generated alerts")


class AlertEvaluationRequest(BaseModel):
    expected_alerts_path: str
    generated_alerts_path: str
