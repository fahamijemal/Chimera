FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy configuration
COPY pyproject.toml .

# Install dependencies
# --system installs into the system python, avoiding permission issues in docker
RUN uv pip install --system --no-cache .[dev]

# Copy project files
COPY . .

# Default command
CMD ["make", "test"]
