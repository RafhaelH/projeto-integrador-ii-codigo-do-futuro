#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
env_file=${1:-"$project_root/deploy/production.env"}
backup_dir=${BACKUP_DIR:-"$project_root/backups"}
retention_days=${BACKUP_RETENTION_DAYS:-14}
compose_file="$project_root/compose.production.yaml"
timestamp=$(date -u '+%Y%m%dT%H%M%SZ')
target="$backup_dir/codigo-futuro-$timestamp.dump"

cd "$project_root"
./deploy/check-env.sh "$env_file"
mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
umask 077

docker compose --env-file "$env_file" -f "$compose_file" exec -T database \
    sh -eu -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-privileges' \
    >"$target"

sha256sum "$target" >"$target.sha256"
find "$backup_dir" -maxdepth 1 -type f -name 'codigo-futuro-*.dump' -mtime "+$retention_days" -delete
find "$backup_dir" -maxdepth 1 -type f -name 'codigo-futuro-*.dump.sha256' -mtime "+$retention_days" -delete

echo "Backup criado: $target"
