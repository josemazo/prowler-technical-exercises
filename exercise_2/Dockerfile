ARG ENVIRONMENT=production
ARG PYTHON_IMAGE=python:3.13.5-alpine3.22
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.8.2-python3.13-alpine

FROM $PYTHON_IMAGE AS python-image
FROM $UV_IMAGE AS uv-image

FROM python-image AS builder

ARG PYTHONHASHSEED=42
ARG ENVIRONMENT

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=${PYTHONHASHSEED} \
    PYTHONUNBUFFERED=1 \
    PYDEVD_DISABLE_FILE_VALIDATION=1 \
    UV_CACHE_DIR=/root/.cache/uv \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

# Copy only the installation files because we want to cache the dependencies not the code
COPY uv.lock pyproject.toml /app/

RUN --mount=from=uv-image,source=/usr/local/bin/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    set -ex ; \
    UV_EXTRA="--compile-bytecode --no-group local --no-group test" ; \
    if [ $ENVIRONMENT = "local" ] ; then \
        UV_EXTRA="--group local --group test" ; \
    elif [ $ENVIRONMENT = "test" ] ; then \
        UV_EXTRA="--no-group local --group test" ; \
    fi ; \
    uv sync --locked --no-install-project $UV_EXTRA

COPY ./ /app/

FROM builder AS local
# Copy uv in local, so we can use it if we want to go full container while developing
COPY --from=uv-image /usr/local/bin/uv /usr/local/bin/uvx /bin/

FROM builder AS test
# NOOP

FROM builder AS production
# Precompile all Python files to bytecode for a faster startup
RUN set -ex ; \
    python -OO -m compileall -b -f /app/src ; \
    find . -name "*.py" -type f -delete

FROM $ENVIRONMENT AS final
ENTRYPOINT ["/app/entrypoint.sh"]
