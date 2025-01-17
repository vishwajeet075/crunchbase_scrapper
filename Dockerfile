# Use Python 3.9 slim image
FROM python:3.9-slim

# Install Chrome and required dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    curl \
    unzip \
    xvfb \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9]{3}") \
    && wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION.0/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && rm -rf /usr/local/bin/chromedriver-linux64 \
    && chmod +x /usr/local/bin/chromedriver

# Create app directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directory for data
RUN mkdir -p /app/data

# Set display port to avoid crash
ENV DISPLAY=:99

# Run the scraper
CMD ["python", "main.py"]