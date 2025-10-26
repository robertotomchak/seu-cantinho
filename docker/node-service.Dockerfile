#Dockerfile para criação da imagem do backend + servicos
#Usa express (cors + helmet + morgan) para o back
#Usa fastify para os servicos

# ----------------------------------------------------------------------
# BUILD STAGE
# ----------------------------------------------------------------------

FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json tsconfig.json ./

RUN npm ci

COPY src/ ./src/ 

RUN npm run build

# ----------------------------------------------------------------------
# PRODUCTION STAGE
# ----------------------------------------------------------------------


FROM node:20-alpine AS production

WORKDIR /app

#cria usuario com permissoes especificas
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

ARG SERVICE_PORT=3000

#copia o necessario do build
COPY --from=build --chown=nextjs:nodejs /app/package*.json ./
COPY --from=build --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=build --chown=nextjs:nodejs /app/dist ./dist

#troca pro usuario nao root
USER nextjs

EXPOSE ${SERVICE_PORT}

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${SERVICE_PORT}/health || exit 1

CMD ["npm", "start"]