#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Available backups:"
    ls -la ./database/backups/
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "🔄 Restoring database from: $BACKUP_FILE"

# Stop services that use database
docker-compose stop backend bot

# Restore database
docker-compose exec postgres psql -U ${POSTGRES_USER:-myapp_user} -d ${POSTGRES_DB:-myapp} < $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully"
    
    # Restart services
    docker-compose start backend bot
    echo "🚀 Services restarted"
else
    echo "❌ Database restore failed"
    exit 1
fi
