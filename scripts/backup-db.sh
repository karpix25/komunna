#!/bin/bash

BACKUP_DIR="./database/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

echo "🗄️ Creating database backup..."

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
docker-compose exec postgres pg_dump -U ${POSTGRES_USER:-myapp_user} ${POSTGRES_DB:-myapp} > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"
    
    # Keep only last 10 backups
    ls -t $BACKUP_DIR/backup_*.sql | tail -n +11 | xargs -r rm
    echo "🧹 Old backups cleaned up"
else
    echo "❌ Backup failed"
    exit 1
fi
