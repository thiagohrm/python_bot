FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Copy dependency specification first for docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Default command
CMD ["python", "main.py"]
