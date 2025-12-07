FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Ensure python output is sent straight to terminal (logs)
ENV PYTHONUNBUFFERED=1

# Default command (will be overridden by compose)
CMD ["python", "main.py"]