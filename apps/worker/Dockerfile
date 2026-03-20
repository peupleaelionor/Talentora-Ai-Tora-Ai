FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for lxml, spaCy, asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY apps/worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy multilingual models (French + English)
RUN python -m spacy download fr_core_news_md && \
    python -m spacy download en_core_web_md

# Copy application source
COPY apps/worker/worker /app/worker
COPY packages /app/packages

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check: verify Celery can import correctly
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "from worker.celery_app import app; print('OK')" || exit 1

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--concurrency=4"]
