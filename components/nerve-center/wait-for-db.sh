#!/bin/bash
# Wait for database to be ready
echo "Waiting for database to be ready..."

until pg_isready -h database -p 5432 -U dio_user -d dio_platform; do
  echo "Database is unavailable - sleeping for 2 seconds"
  sleep 2
done

echo "Database is ready - starting Nerve Center"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000