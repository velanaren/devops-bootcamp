FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create data directory for database
RUN mkdir -p /data

# Expose port
EXPOSE 5000

# Set environment variable for database path
ENV DB_PATH=/data/blog.db

# Run application
CMD ["python", "app.py"]

