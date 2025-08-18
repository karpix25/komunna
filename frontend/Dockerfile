# frontend/Dockerfile для продакшена (ИСПРАВЛЕННЫЙ)
FROM node:18-alpine AS base

# Устанавливаем зависимости только когда нужно
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Копируем файлы пакетов
COPY package.json ./
# ИСПРАВЛЕНО: Генерируем package-lock.json если его нет
RUN if [ ! -f package-lock.json ]; then npm install --package-lock-only; fi
COPY package-lock.json* ./
RUN npm ci --omit=dev

# Стадия сборки
FROM base AS builder
WORKDIR /app

# Копируем зависимости
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# ИСПРАВЛЕНО: Устанавливаем все зависимости более надежно
RUN npm install --legacy-peer-deps
RUN npm run build

# Продакшн стадия
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Копируем собранное приложение
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Копируем public директорию если она существует
COPY --from=builder --chown=nextjs:nodejs /app/public ./public 2>/dev/null || true

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Добавляем healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
