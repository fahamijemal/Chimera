FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy configuration
COPY pyproject.toml .

# Install Python deps
RUN pip install --no-cache-dir .[dev]

# Copy project files
COPY . .

# Default command
CMD ["make", "test"]
