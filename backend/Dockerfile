FROM python:3.11-slim

WORKDIR /app

# Configure Cargo for better caching and writable temp space
ENV CARGO_HOME=/tmp/cargo \
    RUSTFLAGS="-C target-dir=/tmp/rust-target" \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1

# Install system dependencies (libpq for asyncpg)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip/setuptools/wheel first
RUN pip install --upgrade pip setuptools wheel

# Create temp directories with proper permissions
RUN mkdir -p /tmp/cargo /tmp/rust-target && chmod 777 /tmp/cargo /tmp/rust-target

# Install Python dependencies - pre-install wheels separately to avoid compilation failures
COPY requirements.txt .
RUN pip install --upgrade --prefer-binary \
    pydantic==2.6.4 \
    pydantic-core==2.16.3 \
    && pip install --prefer-binary -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p app/uploads/textbooks /data

# Expose port
EXPOSE 8000

# Run with uvicorn (Render provides PORT at runtime)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
