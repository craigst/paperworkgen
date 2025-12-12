FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends libreoffice \
    && rm -rf /var/lib/apt/lists/*

COPY . .

FROM base AS test
RUN pip install --no-cache-dir pytest
ENV PAPERWORK_DISABLE_PDF=true
RUN pytest

FROM base AS runtime
EXPOSE 8000
ENV HOST="::"
ENV PORT=8000
CMD ["sh", "-c", "uvicorn app.main:app --host ${HOST:-::} --port ${PORT:-8000}"]
