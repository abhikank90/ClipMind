#!/bin/bash
# Reset database (WARNING: This will delete all data!)

echo "WARNING: This will delete all data in the database!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    cd backend
    poetry run python app/db/init_db.py
    echo "Database reset complete!"
else
    echo "Operation cancelled"
fi
