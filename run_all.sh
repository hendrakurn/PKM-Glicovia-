#!/bin/bash

# Tangkap signal exit (Ctrl+C) dan matikan semua background jobs
trap 'kill $(jobs -p) 2>/dev/null' EXIT

echo "[0/4] Starting Database (Docker Postgres)..."
cd app/backend
docker compose up -d
cd ../..

echo "[1/4] Starting Backend (app/backend)..."
cd app/backend
npm run dev &
cd ../..

echo "[2/4] Starting Web Frontend (app/web)..."
cd app/web
npm run dev &
cd ../..

echo "[3/4] Starting ML API Connector (ml_pipeline)..."
cd ml_pipeline
venv/bin/uvicorn src.api_connector:app --host 0.0.0.0 --port 8001 &
cd ..

echo "✅ Semua service beserta Database berjalan."
echo "Tekan Ctrl+C untuk menghentikan service backend, web, dan ml_pipeline."

# Tunggu semua proses selesai (atau sampai di-kill)
wait
