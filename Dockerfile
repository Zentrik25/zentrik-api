# Multi-stage Dockerfile for FastAPI application
# This creates a lightweight, production-ready image

# Stage 1: Builder stage
# Purpose: Install dependencies and prepare the application
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies needed for building Python packages
# - gcc: C compiler for some Python packages
# - postgresql-dev: PostgreSQL client libraries
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker caching
# If requirements.txt hasn't changed, this layer will be cached
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't cache pip packages (saves space)
# --user: Install to user directory (for next stage)
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
# Purpose: Create minimal final image with only what's needed to run
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Make sure Python can find the packages
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY ./app ./app

# Create non-root user for security
# Running as root in containers is a security risk
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Health check - Docker will periodically check if app is healthy
# If health checks fail, Docker can restart the container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Command to run the application
# --host 0.0.0.0: Listen on all network interfaces (required in Docker)
# --port 8000: Port to listen on
# --workers: Number of worker processes (adjust based on CPU cores)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]