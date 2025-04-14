FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY backend/ .

# Install aimakerspace package in development mode
RUN pip install -e .

# Expose port
EXPOSE 7860

# Start the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"] 