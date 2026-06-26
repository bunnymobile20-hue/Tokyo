# Stage 1: Build stage
FROM python:3.12-slim-bookworm AS builder

# Install build dependencies, Rust, and Maturin
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    git \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain matching rust-toolchain.toml (or latest)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install maturin for compiling Rust wheel
RUN pip install --no-cache-dir maturin

WORKDIR /build
# Copy Rust source code
COPY rust /build/rust

# Compile openjarvis_rust as a python wheel using maturin
WORKDIR /build/rust
RUN maturin build --release --strip --out /build/wheels

# Stage 2: Final runtime stage
FROM python:3.12-slim-bookworm

LABEL title="TokyoOS"
LABEL developer="GrupsBunny"
LABEL author="GrupsBunny"
LABEL category="Utilities"
LABEL description="Tokyo IA - GrupsBunny AI Hub with voice, dashboard, and ERP integration"
LABEL version="1.0.0-fusion"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TOKYO_ENV=zimaos
ENV TOKYO_HOST=0.0.0.0
ENV TOKYO_HTTP_PORT=8788
ENV TOKYO_DATA_PATH=/DATA/AppData/tokyoos
ENV TOKYO_DATA_DIR=/data/tokyo
ENV TOKYO_LOG_DIR=/data/tokyo/logs
ENV TOKYO_SAFE_MODE=true
ENV TOKYO_TOKEN_EXPOSED=false

# Setup folders
RUN mkdir -p /data/tokyo /data/tokyo/logs /data/tokyo/memory/local /data/tokyo/intelligence /data/tokyo/workspace

WORKDIR /app

# Copy python requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy compiled wheel from builder and install it
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

# Copy script and entrypoint
COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy full application codebase
COPY . .

VOLUME ["/data/tokyo"]

EXPOSE 8788

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8788/tokyo/system/health')" || exit 1

CMD ["/app/entrypoint.sh"]
