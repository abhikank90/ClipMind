#!/bin/bash
# Run all pending Alembic migrations

cd backend
poetry run alembic upgrade head
echo "Migrations completed successfully!"
