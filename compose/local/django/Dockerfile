FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/local.txt requirements/local.txt
COPY requirements/base.txt requirements/base.txt

RUN pip install --upgrade pip \
    && pip install -r requirements/local.txt

COPY . .

COPY compose/local/django/start /start
RUN chmod +x /start
