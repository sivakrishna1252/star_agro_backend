#!/bin/sh
set -eu

APP_PORT="${APP_PORT:-6021}"
GUNICORN_WORKERS="${GUNICORN_WORKERS:-3}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"

echo "Waiting for PostgreSQL at ${DB_HOST:-db}:${DB_PORT:-5432}..."

python <<'PY'
import os
import sys
import time

import psycopg2

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "5432"))
name = os.environ.get("DB_NAME", "star_agro")
user = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "")

for attempt in range(1, 31):
    try:
        conn = psycopg2.connect(
            dbname=name,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=3,
        )
        conn.close()
        print("PostgreSQL is ready.")
        sys.exit(0)
    except psycopg2.OperationalError as exc:
        print(f"Attempt {attempt}/30: database not ready ({exc})")
        time.sleep(2)

print("PostgreSQL did not become ready in time.")
sys.exit(1)
PY

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then
    echo "Ensuring Django superuser exists..."
    python manage.py shell <<'PY'
import os

from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get("ADMIN_USERNAME", "admin")
email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
password = os.environ.get("ADMIN_PASSWORD")

if not password:
    raise SystemExit("CREATE_SUPERUSER=true requires ADMIN_PASSWORD.")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created superuser: {username}")
else:
    print(f"Superuser already exists: {username}")
PY
fi

if [ "${SEED_DATA:-false}" = "true" ]; then
    echo "Loading seed data..."
    python manage.py seed_data
fi

echo "Starting Gunicorn on port ${APP_PORT}..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${APP_PORT}" \
    --workers "${GUNICORN_WORKERS}" \
    --timeout "${GUNICORN_TIMEOUT}" \
    --access-logfile - \
    --error-logfile -
