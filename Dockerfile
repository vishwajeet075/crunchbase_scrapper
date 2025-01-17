# Use a slim Python 3.9 base image
FROM python:3.9-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY *.py .

# Create data directory
RUN mkdir -p /app/data

# Download the 'en_core_web_sm' model
RUN python -m spacy validate && python -m spacy download en_core_web_sm

# Command to run the application
CMD ["python", "main.py"]
