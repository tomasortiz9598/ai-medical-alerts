import uuid

from api.dependencies import get_medical_records_repository
from api.error_handlers import InvalidRequest
from api.repositories.medical_records_repository import \
    MedicalRecordsRepository
from api.schemas import EventsResponse, MedicalRecordResponse
from fastapi import APIRouter, Depends, File, UploadFile

router = APIRouter(prefix="/medical-records", tags=["medical_records"])


@router.post("", response_model=EventsResponse)
async def upload_medical_record(
    file: UploadFile = File(...),
    medical_records_repository: MedicalRecordsRepository = Depends(
        get_medical_records_repository
    ),
) -> EventsResponse:
    if not file.filename or not file.filename.endswith(".pdf"):
        raise InvalidRequest("Invalid filename")
    events = medical_records_repository.process_medical_record(
        await file.read(), filename=file.filename
    )
    return EventsResponse(events=events)


@router.delete("/{medical_record_id}", status_code=204)
async def delete_medical_record(
    medical_record_id: uuid.UUID,
    medical_records_repository: MedicalRecordsRepository = Depends(
        get_medical_records_repository
    ),
) -> None:
    medical_records_repository.delete_medical_record(
        medical_record_id=medical_record_id
    )


@router.get("", response_model=MedicalRecordResponse)
async def get_medical_record(
    medical_records_repository: MedicalRecordsRepository = Depends(
        get_medical_records_repository
    ),
) -> MedicalRecordResponse:
    medical_records = medical_records_repository.get_medical_records()
    return MedicalRecordResponse(medical_records=medical_records)
