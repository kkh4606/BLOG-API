#!/bin/sh
set -e  # Exit immediately if a command fails

echo "Waiting for database to be ready..."

# Optional: wait for Postgres to be ready
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT"; do
  echo "Database not ready yet, retrying..."
  sleep 2
done

echo "Running migrations..."
alembic upgrade head

echo "Starting the FastAPI app..."
exec "$@"  # Run the CMD from Dockerfile
