# Исправление поврежденного package-lock.json

## 📝 Commit сообщение:
```
fix: remove corrupted package-lock.json and update Dockerfile

- Delete package-lock.json with fake integrity checksums
- Update Dockerfile to work without lock file
- Use npm install to generate fresh lock file
```

## 🔧 Проблема:
package-lock.json содержит поддельные integrity checksums (`sha512-example`), что вызывает ошибки.

## ⚡ Решение:

### Шаг 1: Удалить package-lock.json
В GitHub:
1. Перейдите в `frontend/`
2. Нажмите на `package-lock.json`
3. Нажмите иконку корзины (Delete this file)
4. Коммит: `remove corrupted package-lock.json`

### Шаг 2: Обновить Dockerfile
Замените `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy only package.json (no lock file)
COPY package.json ./

# Install production dependencies and generate new lock file
RUN npm install --production --legacy-peer-deps

# Build stage
FROM base AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Install all dependencies (will generate package-lock.json)
RUN npm install --legacy-peer-deps

# Build the application
RUN npm run build

# Production stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy public assets
COPY --from=builder /app/public ./public

# Create .next directory and set permissions
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```
