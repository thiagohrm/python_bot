FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Copy dependency specification first for docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (includes src/, tests/, examples/)
# The modular structure is in src/ folder with clear separation of concerns
COPY . /app

# Install system dependencies for QR code detection
RUN apt-get update && apt-get install -y --no-install-recommends libzbar0 && rm -rf /var/lib/apt/lists/*

# Default command (runs main.py which delegates to src/main.py)
CMD ["python", "main.py"]
