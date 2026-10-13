#!/bin/sh
set -eu

project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
env_file=${1:-"$project_root/deploy/production.env"}
compose_file="$project_root/compose.production.yaml"

cd "$project_root"
./deploy/check-env.sh "$env_file"

compose() {
    docker compose --env-file "$env_file" -f "$compose_file" "$@"
}

compose config --quiet
compose build --pull app
compose up -d database
compose up -d app

attempt=1
while [ "$attempt" -le 30 ]; do
    if compose exec -T app python -c \
        "import os, urllib.request; host=os.environ['DJANGO_ALLOWED_HOSTS'].split(',')[0].strip(); urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/readyz/', headers={'Host': host, 'X-Forwarded-Proto': 'https'}), timeout=3).read()" \
        >/dev/null 2>&1; then
        compose exec -T app python src/manage.py check --deploy
        echo "Aplicação pronta após $attempt tentativa(s)."
        compose ps
        exit 0
    fi
    sleep 2
    attempt=$((attempt + 1))
done

echo "A aplicação não ficou pronta no tempo esperado." >&2
compose logs --tail=100 app >&2
exit 1
