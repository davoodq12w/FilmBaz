#!/bin/sh
set -e

echo "Waiting for database (Python retry)..."
python - <<'PY'
import os, time
import psycopg2

db = os.getenv("POSTGRES_DB", "postgres")
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "")
host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5432"))

while True:
    try:
        conn = psycopg2.connect(
            dbname=db, user=user, password=password,
            host=host, port=port
        )
        conn.close()
        print("Database is ready.")
        break
    except Exception as e:
        print("DB not ready yet:", e)
        time.sleep(1)
PY

echo "Applying migrations..."
python manage.py migrate

echo "Creating genres..."
python manage.py load_genres

echo "Creating casts..."
python manage.py load_casts

echo "Creating crews..."
python manage.py load_crews

echo "Creating movies..."
python manage.py load_movies

echo "Creating relations..."
python manage.py load_relations

echo "Enabling pg_trgm extension..."
python manage.py shell -c "from django.db import connection; connection.cursor().execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')"

echo "Collect static..."
python manage.py collectstatic --noinput

exec gunicorn FilmBaz.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --error-logfile - --log-level info
