FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock first for better docker caching
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv
RUN pipenv install  --system --deploy

ENV PYTHONPATH=/app:$PYTHONPATH

COPY . /app

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
