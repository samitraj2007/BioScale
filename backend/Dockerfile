FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Copy trained models
COPY models/ ./models/

# Set Python path
ENV PYTHONPATH=/app/src

# Expose API port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "bioscale.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
