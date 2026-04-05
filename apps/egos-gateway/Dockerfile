FROM oven/bun:1.3
WORKDIR /app
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile 2>/dev/null || bun install
COPY . .
ENV GATEWAY_PORT=3050
EXPOSE 3050
CMD ["bun", "run", "src/server.ts"]
