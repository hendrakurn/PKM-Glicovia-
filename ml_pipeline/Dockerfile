FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run from /app/src so local imports and bundled model paths resolve cleanly.
WORKDIR /app/src

CMD ["sh", "-c", "uvicorn api_connector:app --host 0.0.0.0 --port ${PORT}"]
