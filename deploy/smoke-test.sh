#!/bin/sh
set -eu

base_url=${1:-${PUBLIC_BASE_URL:-}}
if [ -z "$base_url" ]; then
    echo "Uso: ./deploy/smoke-test.sh https://seu-dominio" >&2
    exit 1
fi

base_url=${base_url%/}

curl --fail --silent --show-error "$base_url/healthz/" >/dev/null
curl --fail --silent --show-error "$base_url/readyz/" >/dev/null
curl --fail --silent --show-error "$base_url/entrar/" >/dev/null

echo "Smoke test aprovado em $base_url"
