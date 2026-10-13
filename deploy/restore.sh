#!/bin/sh
set -eu

if [ "${CONFIRM_RESTORE:-}" != "SUBSTITUIR_BANCO_DA_HOMOLOGACAO" ]; then
    echo "Restauração bloqueada. Defina CONFIRM_RESTORE=SUBSTITUIR_BANCO_DA_HOMOLOGACAO." >&2
    exit 1
fi

if [ "$#" -lt 1 ]; then
    echo "Uso: CONFIRM_RESTORE=SUBSTITUIR_BANCO_DA_HOMOLOGACAO ./deploy/restore.sh ARQUIVO.dump [ENV]" >&2
    exit 1
fi

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
backup_file=$1
env_file=${2:-"$project_root/deploy/production.env"}
compose_file="$project_root/compose.production.yaml"

case "$backup_file" in
    /*) ;;
    *) backup_file="$project_root/$backup_file" ;;
esac

if [ ! -f "$backup_file" ]; then
    echo "Backup não encontrado: $backup_file" >&2
    exit 1
fi

cd "$project_root"
./deploy/check-env.sh "$env_file"

compose() {
    docker compose --env-file "$env_file" -f "$compose_file" "$@"
}

./deploy/backup.sh "$env_file"
compose stop app
trap 'compose up -d app >/dev/null' EXIT

compose exec -T database sh -eu -c \
    'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges' \
    <"$backup_file"

compose up -d app
trap - EXIT
echo "Restauração concluída a partir de: $backup_file"
