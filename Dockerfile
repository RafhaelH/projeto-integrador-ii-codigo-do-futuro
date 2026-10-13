# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12
ARG UV_VERSION=0.12.23

FROM python:${PYTHON_VERSION}-slim AS builder

ARG UV_VERSION
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


FROM python:${PYTHON_VERSION}-slim AS runtime

ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system codigo \
    && useradd --system --gid codigo --home-dir /app --shell /usr/sbin/nologin codigo

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src /app/src
COPY deploy/entrypoint.sh deploy/gunicorn.conf.py /app/deploy/

RUN chmod 0755 /app/deploy/entrypoint.sh \
    && mkdir -p /app/src/media /app/src/staticfiles \
    && chown -R codigo:codigo /app

USER codigo

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import socket; s=socket.create_connection(('127.0.0.1', 8000), 3); s.close()"

ENTRYPOINT ["/app/deploy/entrypoint.sh"]
CMD ["gunicorn", "--config", "/app/deploy/gunicorn.conf.py", "config.wsgi:application"]
