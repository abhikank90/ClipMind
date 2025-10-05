#!/bin/bash
# Create a new Alembic migration
# Usage: ./scripts/create_migration.sh "migration message"

if [ -z "$1" ]; then
    echo "Error: Please provide a migration message"
    echo "Usage: ./scripts/create_migration.sh 'your migration message'"
    exit 1
fi

cd backend
poetry run alembic revision --autogenerate -m "$1"
echo "Migration created successfully!"
