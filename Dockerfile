FROM python:3.11-slim

LABEL title="TokyoOS"
LABEL developer="GrupsBunny"
LABEL author="GrupsBunny"
LABEL category="Utilities"
LABEL description="Tokyo IA - GrupsBunny AI Hub with voice, dashboard, and ERP integration"
LABEL version="1.0.0-phase1"

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

RUN mkdir -p /data/tokyo /data/tokyo/logs /data/tokyo/memory/local /data/tokyo/intelligence

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . .

VOLUME ["/data/tokyo"]

EXPOSE 8788

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8788/tokyo/system/health')" || exit 1

CMD ["/app/entrypoint.sh"]
