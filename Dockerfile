# Multi-stage Dockerfile for VeriPack
# Stage 1: Build the React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend & OCR Runtime
FROM python:3.11-slim

# Install system dependencies: Tesseract OCR, English & Hindi language packs, OpenCV dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend assets from Stage 1 into the frontend dist location
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set environment variables
ENV TESSERACT_CMD=tesseract
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Working directory set to backend
WORKDIR /app/backend

# Prime database and pre-seed demo packaging records
RUN python -c "from app.seed import seed_database; seed_database()"

EXPOSE 8000

# Start server using Uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
