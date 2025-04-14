FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend source and install dependencies
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Copy backend source
WORKDIR /app
COPY backend/ .

# Install serve to run the frontend
RUN npm install -g serve

# Expose the port (Hugging Face requires 7860)
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV REACT_APP_API_URL=https://shipmaster1-pythonicragreact.hf.space

# Start both services
CMD ["sh", "-c", "serve -s frontend/build -l 3000 & uvicorn main:app --host 0.0.0.0 --port 7860"]