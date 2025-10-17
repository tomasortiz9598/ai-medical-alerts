"""FastAPI application exposing the medical alert extraction workflow."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .models import AlertResponse
from .services.alert_generation import generate_alerts_from_text
from .services.pdf_processing import PDFExtractionError, extract_text_from_pdf

app = FastAPI(title="Medical Record Alert Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/alerts", response_model=AlertResponse)
async def create_alerts(
    file: UploadFile = File(..., description="Medical record PDF"),
    clinic_policies: str | None = Form(None),
) -> AlertResponse:
    """Accept a PDF upload, extract alerts using the BAML pipeline, and return structured data."""

    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    pdf_bytes = await file.read()

    try:
        extracted_text = extract_text_from_pdf(pdf_bytes)
    except PDFExtractionError as exc:  # pragma: no cover - depends on optional deps
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result: Dict[str, Any] = generate_alerts_from_text(extracted_text, clinic_policies)
    return AlertResponse(**result)


@app.get("/health")
async def healthcheck() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/alerts/from-text", response_model=AlertResponse)
async def create_alerts_from_text(payload: Dict[str, Any]) -> AlertResponse:
    """Development helper that bypasses PDF parsing and accepts raw text."""

    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' field in payload")
    clinic_policies = payload.get("clinic_policies")
    result: Dict[str, Any] = generate_alerts_from_text(text, clinic_policies)
    return AlertResponse(**result)
