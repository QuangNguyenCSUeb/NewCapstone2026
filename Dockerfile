FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000 \
    FLASK_DEBUG=0 \
    DATABASE_PATH=/app/data/compliance.db

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt \
    && groupadd --system app \
    && useradd --system --gid app --create-home app \
    && mkdir -p /app/data \
    && chown app:app /app/data

COPY --chown=app:app backend ./backend
COPY --chown=app:app frontend ./frontend

USER app

EXPOSE 5000
VOLUME ["/app/data"]

CMD ["sh", "-c", "python -c 'from backend.app import initialize; initialize()' && exec gunicorn --bind 0.0.0.0:${FLASK_PORT} --workers 2 backend.app:app"]
