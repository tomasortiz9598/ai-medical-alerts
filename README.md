# Medical Record PDF Alert System

This project demonstrates an end-to-end system that extracts actionable, date-driven alerts from medical
record PDFs. It covers prompt design using [BAML](https://docs.boundaryml.com/), a FastAPI backend, an
evaluation harness, and a React frontend for manual testing.

## Project structure

```
.
├── backend/                # FastAPI service and BAML integration
│   ├── app/
│   │   ├── baml/           # BAML prompt + task definition
│   │   ├── services/       # PDF parsing and alert generation helpers
│   │   ├── baml_client.py
│   │   ├── main.py
│   │   └── models.py
│   └── requirements.txt
├── data/                   # Sample documents and reference outputs
├── evaluation/             # Accuracy evaluation utilities
└── frontend/               # React dashboard for alert visualization
```

## Section 1 – Prompt design and BAML task setup

The BAML task lives at [`backend/app/baml/alerts.baml`](backend/app/baml/alerts.baml). It defines:

- `Alert`, `AlertType`, and `AlertExtractionResponse` schemas
- `AlertExtractionPrompt` prompt template including system and user guidance
- `ExtractMedicalAlertsTask` task configuration
- A worked sample input and output pair referencing the sample medical record

### Sample prompt I/O

Input text example (`data/sample_record_text.txt`):

```
Patient: Luna (Canine)
Vaccines: Rabies booster due on 2024-08-17. Bordetella administered 2023-08-01; recommend annual booster.
Dental cleaning scheduled for 2024-09-02. Routine senior wellness exam every six months, last completed 2024-02-10.
Recheck skin lesion in 3 weeks from 2024-05-01.
```

Expected task output (`data/sample_alerts_model_output.json`):

```json
{
  "patient_name": "Luna",
  "patient_species": "Canine",
  "alerts": [
    {
      "title": "Rabies booster due",
      "alert_type": "VACCINE_EXPIRATION",
      "due_date": "2024-08-17",
      "confidence": 0.98,
      "source_excerpt": "Rabies booster due on 2024-08-17",
      "notes": "Notify owner 30 days ahead per SOP."
    },
    {
      "title": "Bordetella booster reminder",
      "alert_type": "VACCINE_EXPIRATION",
      "due_date": "2024-07-01",
      "confidence": 0.76,
      "source_excerpt": "Bordetella administered 2023-08-01",
      "notes": "Due 11 months after last dose per SOP."
    },
    {
      "title": "Dental cleaning appointment",
      "alert_type": "DENTAL_PROCEDURE",
      "due_date": "2024-09-02",
      "confidence": 0.95,
      "source_excerpt": "Dental cleaning scheduled for 2024-09-02",
      "notes": null
    },
    {
      "title": "Senior wellness exam",
      "alert_type": "ROUTINE_EXAM",
      "due_date": "2024-08-10",
      "confidence": 0.88,
      "source_excerpt": "Routine senior wellness exam every six months, last completed 2024-02-10",
      "notes": "Due six months after the last exam per SOP."
    },
    {
      "title": "Skin lesion recheck",
      "alert_type": "FOLLOW_UP",
      "due_date": "2024-05-22",
      "confidence": 0.82,
      "source_excerpt": "Recheck skin lesion in 3 weeks from 2024-05-01",
      "notes": null
    }
  ]
}
```

## Section 2 – System integration

### FastAPI service

Install dependencies and run the API server:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Endpoints:

- `POST /alerts`: Upload a PDF (field name `file`) and optional `clinic_policies` string. Returns
  structured alerts.
- `POST /alerts/from-text`: Development helper for posting raw text payloads.
- `GET /health`: Simple healthcheck.

### PDF ingestion

- Primary extraction uses `pdfminer.six`.
- Optional OCR support via `pdf2image` + `pytesseract` when text extraction fails.

### BAML integration

`backend/app/services/alert_generation.py` invokes `ExtractMedicalAlertsTask` defined in the BAML file.
The `baml_client` module caches a BAML client per project root to avoid re-initialization overhead.

### Example request

Use `curl` to exercise the endpoint with the included sample PDF:

```bash
curl -X POST \
  -F "file=@../data/sample_record.pdf" \
  -F "clinic_policies=Clinic SOP: Schedule routine exam reminders one month before due date." \
  http://localhost:8000/alerts
```

## Section 3 – Evaluation and iteration

Ground-truth alerts for the sample PDF are stored in
[`data/sample_alerts_ground_truth.json`](data/sample_alerts_ground_truth.json).

Run the evaluation script against a model output file:

```bash
python evaluation/evaluate_alerts.py \
  data/sample_alerts_ground_truth.json \
  data/sample_alerts_model_output.json
```

Reported metrics include precision, recall, alert type mismatches, and the mean absolute difference between
expected and generated due dates.

## Section 4 – React UI for end-to-end testing

Install dependencies and start the Vite dev server:

```bash
cd frontend
npm install
npm run dev
```

The UI supports:

- Uploading medical record PDFs
- Optional entry of clinic SOPs to tailor alert generation
- Displaying alerts sorted by urgency (High, Medium, Low) with color-coded badges
- Showing confidence, due dates, supporting excerpts, and notes

Configure the proxy in [`frontend/vite.config.ts`](frontend/vite.config.ts) to match your backend origin if
needed.

## Stretch ideas

- Extend `alerts.baml` with additional SOP-driven logic or new alert categories.
- Enrich the frontend with filters by alert type, species, or date range.
- Persist alerts and evaluation metrics in a database for longitudinal tracking.
