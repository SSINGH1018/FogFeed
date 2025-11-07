# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHROME_BIN=/usr/bin/google-chrome \
    CHROME_PATH=/usr/bin/google-chrome \
    DISPLAY=:99

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for the project
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    curl \
    xvfb \
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y \
    google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright dependencies
RUN playwright install chromium \
    && playwright install-deps chromium

# Copy the project files into the container
COPY . .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Create a wrapper script to start Xvfb before running the scrapers
USER root
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &\nexec python run_all_scrapers.py' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh
USER appuser

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]