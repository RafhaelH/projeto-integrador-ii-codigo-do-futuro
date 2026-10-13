#!/bin/sh
set -eu

env_file=${1:-deploy/production.env}

if [ ! -f "$env_file" ]; then
    echo "Arquivo de ambiente não encontrado: $env_file" >&2
    exit 1
fi

if grep -Eq 'SUBSTITUA_|change-me|example-secret' "$env_file"; then
    echo "O arquivo $env_file ainda contém valores de exemplo." >&2
    exit 1
fi

for variable in \
    DJANGO_SECRET_KEY \
    DJANGO_ALLOWED_HOSTS \
    DJANGO_CSRF_TRUSTED_ORIGINS \
    POSTGRES_DB \
    POSTGRES_USER \
    POSTGRES_PASSWORD \
    DATABASE_URL
do
    if ! grep -Eq "^${variable}=.+" "$env_file"; then
        echo "Variável obrigatória ausente ou vazia: $variable" >&2
        exit 1
    fi
done

mode=$(stat -c '%a' "$env_file" 2>/dev/null || true)
if [ -n "$mode" ] && [ "$mode" != "600" ]; then
    echo "Aviso: use chmod 600 $env_file (permissão atual: $mode)." >&2
fi

echo "Arquivo de ambiente validado: $env_file"
