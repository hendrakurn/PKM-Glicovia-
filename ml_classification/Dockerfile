FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    # Model dipilih eksplisit: tanpa ini api.py memakai .pkl dengan mtime terbaru, dan mtime hasil
    # git checkout / COPY tidak bisa diandalkan. Ganti saat model baru dilatih.
    GLICO_CLS_MODEL=/app/models/model_cls_kal_20261029.pkl

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY cls/ cls/
COPY models/ models/

CMD ["sh", "-c", "uvicorn cls.api:app --host 0.0.0.0 --port ${PORT}"]
