# ----------------------------------------------------------------------
# BUILD STAGE
# ----------------------------------------------------------------------
FROM python:3.11-alpine AS build

WORKDIR /app

RUN apk add --no-cache build-base

# copia requirements
COPY src/backEnd/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# copia a pasta inteira "src" para manter o path correto
COPY src /app/src


# ----------------------------------------------------------------------
# PRODUCTION STAGE
# ----------------------------------------------------------------------
FROM python:3.11-alpine AS production

WORKDIR /app

RUN apk add --no-cache ca-certificates curl

# copia libs e arquivos do build stage
COPY --from=build /usr/local/lib /usr/local/lib
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app /app

# cria usuario-
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

USER appuser

ARG SERVICE_PORT=3000
EXPOSE ${SERVICE_PORT}

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${SERVICE_PORT}/health || exit 1

# IMPORTANTE: usar o caminho correto com src.backEnd
CMD ["uvicorn", "src.backEnd.controller:app", "--host", "0.0.0.0", "--port", "3000"]

