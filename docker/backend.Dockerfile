#Dockerfile para criação da imagem do backend (FastAPI/ uvicorn)

# ----------------------------------------------------------------------
# BUILD STAGE
# ----------------------------------------------------------------------

FROM python:3.11-alpine AS build

WORKDIR /app

RUN apk add --no-cache build-base

COPY src/backEnd/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/backEnd/ . 

# ----------------------------------------------------------------------
# PRODUCTION STAGE
# ----------------------------------------------------------------------


FROM python:3.11-alpine AS production

WORKDIR /app

#instala utilitarios
RUN apk add --no-cache ca-certificates curl

#copia o necessario do build
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /app /app

#cria usuario com permissoes especificas
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

#troca pro usuario nao root
USER appuser

#exposicao do back para o front
ARG SERVICE_PORT=3000
EXPOSE ${SERVICE_PORT}

# HEALTHCHECK: Verifica a disponibilidade da aplicação
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${SERVICE_PORT}/health || exit 1

CMD ["uvicorn", "controller:app", "--host", "0.0.0.0", "--port", "3000"]