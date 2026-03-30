FROM oven/bun:1.1-alpine
WORKDIR /app

# Copy package files
COPY packages/guard-brasil/package.json packages/guard-brasil/package.json
COPY packages/guard-brasil/src/ packages/guard-brasil/src/
COPY apps/api/src/ apps/api/src/

EXPOSE 3099

ENV GUARD_API_PORT=3099
ENV GUARD_RATE_LIMIT=100

CMD ["bun", "run", "apps/api/src/server.ts"]
