#Dockerfile para criacao da imagem do frontend
#Usa React + Next.js 

# ----------------------------------------------------------------------
# BUILD STAGE
# ----------------------------------------------------------------------

#usa a versão do node com SSR mais lisa
FROM node:20-alpine AS builder

#APP como diretorio padrão para comandos do dockerfile
WORKDIR /app

#copia arquivos de dependencia, evita intall desnecessario
COPY src/frontEnd/package.json src/frontEnd/package-lock.json ./

#dependencias necessarias
RUN npm ci

#copia codigo pro container
COPY src/frontEnd .

RUN npm run build

# ----------------------------------------------------------------------
# RUNTIME STAGE
# ----------------------------------------------------------------------

#nova imagem, pequena e boa para a execucao
FROM node:20-alpine AS production

WORKDIR /app

RUN addgroup -g 1001 -S nodejs && \
    adduser -S -u 1001 -G nodejs nextjs

ENV NODE_ENV=production
ENV PORT=8000

#copia modulos do estagio de dependencias
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

#porta do container aberta pro host
EXPOSE 8000

#comando de inicializacao
CMD ["npm", "start"]
