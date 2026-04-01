# Stage 1: Build Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Final Image
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uvicorn aiofiles

# Copy Backend
COPY backend/ ./backend/

# Copy Build Frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Environment variables
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start Backend (which serves the static frontend)
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
