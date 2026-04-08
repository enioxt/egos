FROM oven/bun:1-alpine

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install --frozen-lockfile 2>/dev/null || bun install

COPY . .

ENV PORT=3071
EXPOSE 3071

CMD ["bun", "run", "src/server.ts"]
