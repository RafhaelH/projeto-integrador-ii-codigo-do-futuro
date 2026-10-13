# Evidências de verificação automatizada

## Release candidata anterior

A `develop` no commit `d883272` foi validada pela CI com PostgreSQL 17 após a integração da carga
determinística. O histórico registrou 188 testes considerados, incluindo o cenário concorrente
executado somente no PostgreSQL, e cobertura de 88,21%.

## Branch de preparação para a VPS

Validação local da branch `feat/finalization-pre-vps` antes da revisão remota:

| Verificação | Resultado |
|---|---|
| Pytest | 190 coletados; 189 aprovados; 1 reservado ao PostgreSQL |
| Cobertura | 88,26% |
| Ruff lint | aprovado |
| Ruff format | aprovado |
| `manage.py check` | nenhuma ocorrência |
| `makemigrations --check --dry-run` | nenhuma mudança detectada |
| `manage.py check --deploy` | nenhuma ocorrência |
| Scripts POSIX com `sh -n` | aprovados |
| Parse do `compose.production.yaml` | aprovado |
| Migrações em banco vazio | aprovadas em SQLite com configuração de produção |
| Gunicorn e endpoints | `/healthz/`, `/readyz/` e `/entrar/` aprovados em configuração de produção |
| Build da imagem Docker | pendente da CI/VPS, pois o executor local não fornece Docker |
| Teste concorrente no PostgreSQL 17 | pendente da CI desta branch |

Data da execução local: 13/10/2026.

## Comandos reproduzíveis

```bash
uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python src/manage.py check
uv run python src/manage.py makemigrations --check --dry-run
sh -n deploy/*.sh
```

Verificação de produção sem usar segredos reais:

```bash
DJANGO_SETTINGS_MODULE=config.settings.production \
DJANGO_SECRET_KEY='chave-temporaria-com-mais-de-cinquenta-caracteres' \
DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1' \
DJANGO_CSRF_TRUSTED_ORIGINS='https://localhost' \
DATABASE_URL='sqlite:////tmp/codigo-futuro-production-check.sqlite3' \
uv run python src/manage.py check --deploy
```

## Evidência definitiva

Após a CI da branch e depois das correções dos cinco avaliadores, substituir esta seção pelo link
da execução da tag final e registrar contagem, cobertura, SHA, migração em banco vazio, build
Docker, smoke test público e teste de restauração. A evidência final não pode apontar somente para
uma versão anterior.
