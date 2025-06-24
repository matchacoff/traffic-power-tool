# Use official Python 3.13 slim image as base
FROM python:3.13.4-slim

# Set working directory inside the container
WORKDIR /app

# Install essential build tools required for compiling some dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list into the container
COPY requirements.txt .

# Install Python dependencies without caching to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright along with necessary browser dependencies
RUN playwright install chromium

# Copy all project files into the container
COPY . .

# Create required output and preset directories
RUN mkdir -p /app/output/profiles \
    /app/output/errors \
    /app/output/history \
    /app/output/logs \
    /app/output/reports \
    /app/output/screenshots \
    /app/presets

# Expose Streamlit default port
EXPOSE 8501

# Add a basic healthcheck to verify the container is healthy
HEALTHCHECK CMD streamlit hello --server.port 8501 || exit 1

# Default command to run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=${PORT}", "--server.address=0.0.0.0"]

