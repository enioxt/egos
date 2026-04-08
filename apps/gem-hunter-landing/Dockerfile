FROM oven/bun:1.3-slim AS builder
WORKDIR /app
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile 2>/dev/null || bun install
COPY . .

FROM oven/bun:1.3-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3070

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src ./src
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./

EXPOSE 3070
CMD ["bun", "run", "src/server.ts"]
