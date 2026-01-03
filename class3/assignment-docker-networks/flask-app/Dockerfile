FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for networking tools
RUN apt-get update && apt-get install -y \
    iputils-ping \
    dnsutils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Expose Flask port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]

