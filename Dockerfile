FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and certificates
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ca-certificates \
    wget \
    && update-ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for requests
ENV PYTHONWARNINGS="ignore:Unverified HTTPS request"
ENV REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"] 