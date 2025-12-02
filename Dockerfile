FROM python:3.11-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY backend /app

# Expose port
EXPOSE 8000

# Run uvicorn (sin --reload en producción)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]