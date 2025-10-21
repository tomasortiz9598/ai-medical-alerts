# ai-medical-alerts

AI-powered medical record ingestion pipeline. The backend (FastAPI + PostgreSQL + MinIO) parses uploaded PDFs into structured events, while the frontend (React + Vite + MUI) surfaces extracted alerts.

## Project layout
- `backend/` – FastAPI application, database models/migrations, evaluation scripts.
- `frontend/` – React SPA served by Vite.
- `backend/data/` – Sample PDFs and labelled ground truth for evaluation.

## Prerequisites
- Python 3.11 and [Pipenv](https://pipenv.pypa.io/en/latest/).
- Node.js 18+ and npm.
- [Poppler](https://poppler.freedesktop.org/) (provides `pdftoppm` for PDF rendering).
- [Tesseract OCR](https://tesseract-ocr.github.io/) (needed by `pytesseract`).
- Docker & Docker Compose (optional, for running Postgres/MinIO/API together).

macOS install:
```bash
brew install poppler tesseract
```

## Environment configuration
1. Copy the example file and adjust values as needed:
   ```bash
   cd backend
   cp .env.example .env
   ```
2. Update secrets such as `OPENAI_API_KEY`. When running everything locally set:
   - PostgreSQL: `PGHOST=localhost`, `PGPORT=5432`, `PGUSER`, `PGPASSWORD`, `PGDATABASE=ai_medical_alerts`.
   - MinIO: `MINIO_ENDPOINT=localhost:9000`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_BUCKET`.
3. Alembic also respects `DATABASE_URL`; you may set `DATABASE_URL=postgresql://user:pass@localhost:5432/ai_medical_alerts` instead of the discrete vars if preferred.

## Backend (FastAPI)
Install dependencies:
```bash
cd backend
pipenv install --dev
```

### Start infrastructure
- **Docker (recommended for local dev)**:
  ```bash
  cd backend
  docker compose up db minio
  ```
  This runs PostgreSQL on `localhost:5432` and MinIO on `localhost:9000` (console `:9001`).
- **Manual DB setup**: create the `ai_medical_alerts` database yourself and ensure credentials match `.env`.

### Apply database migrations
```bash
cd backend
pipenv run alembic upgrade head
```
Alembic seeds the four default event types during the first migration.

### Run the API
```bash
cd backend
docker compose up api
```
The server listens on `http://localhost:8000`. Update the frontend’s base URL in `frontend/src/api/client.ts` if you change the port.

### Run with Docker Compose (API + dependencies)
```bash
cd backend
docker compose up --build
```
The API becomes available at `http://localhost:8000`, PostgreSQL at `localhost:5432`, and MinIO at `http://localhost:9000`.

## Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
The dev server runs on `http://localhost:5173` and proxies API calls to `http://localhost:8000`. Build for production with `npm run build` and preview the static output using `npm run preview`.

## Tests
- **Backend**: in-memory SQLite + stubbed external services allow the suite to run without Postgres or MinIO.
  ```bash
  cd backend
  pipenv run pytest api/tests
  ```
- **Frontend**: no automated tests are defined today.



## Evaluation pipeline
Sample evaluation PDFs aligned with the supported alert taxonomy (`VACCINE_EXPIRATIONS`, `UPCOMING_DENTAL_PROCEDURES`, `ROUTINE_EXAMS`, `FOLLOW_UP_APPOINTMENTS`) live in `backend/data` with annotations in `backend/data/ground_truth/alerts.json`.

Run the end-to-end evaluation (requires the API to be running and reachable at `http://localhost:8000`):
```bash
pipenv run python backend/evaluation/run_evaluation.py
```
The script uploads each evaluation PDF, compares predictions to ground truth, and reports accuracy, type matching, and average date deltas.
