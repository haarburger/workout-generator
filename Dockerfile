FROM python:3.9-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make sure your app is listening on 0.0.0.0 to be accessible from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]