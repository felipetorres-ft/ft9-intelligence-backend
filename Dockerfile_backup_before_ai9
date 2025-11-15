# FT9 Intelligence Platform - Production Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data uploads

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Run the application with dynamic port
CMD uvicorn main_multitenant:app --host 0.0.0.0 --port ${PORT:-8000}
