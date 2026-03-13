FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (libpq for asyncpg, build-essential for Rust compilation)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version (helps with wheel caching)
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies (prefer wheels, avoid unnecessary compilation)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --prefer-binary \
    --only-binary :all: \
    -r requirements.txt || pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p app/uploads/textbooks /data

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
