#!/bin/sh
set -eu

is_enabled() {
    value=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
    [ "$value" = "1" ] || [ "$value" = "true" ] || [ "$value" = "yes" ]
}

if is_enabled "${WAIT_FOR_DATABASE:-true}"; then
    python - <<'PY'
import time

from django.db import connection
from django.db.utils import OperationalError

attempts = 30
for attempt in range(1, attempts + 1):
    try:
        connection.ensure_connection()
        print("Banco de dados disponível.", flush=True)
        break
    except OperationalError:
        if attempt == attempts:
            raise
        print(f"Aguardando banco de dados ({attempt}/{attempts})...", flush=True)
        time.sleep(2)
PY
fi

if is_enabled "${RUN_MIGRATIONS:-true}"; then
    python src/manage.py migrate --noinput
fi

if is_enabled "${COLLECT_STATIC:-true}"; then
    python src/manage.py collectstatic --noinput --clear
fi

exec "$@"
