FROM python:3.12-slim

# Set workdir
WORKDIR /app

# System dependency required by pyzbar for QR decoding
RUN apt-get update \
	&& apt-get install -y --no-install-recommends libzbar0 \
	&& rm -rf /var/lib/apt/lists/*

# Copy dependency specification first for docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Default command
CMD ["python", "src/main.py"]
