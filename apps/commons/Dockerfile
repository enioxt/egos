# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json bun.lockb* ./

# Install dependencies
RUN npm install

# Copy source code
COPY tsconfig.json tsconfig.app.json tsconfig.node.json eslint.config.js vite.config.ts index.html ./
COPY src ./src
COPY public ./public

# Build
RUN npm run build

# Production stage - serve with simple HTTP server
FROM node:22-alpine

WORKDIR /app

# Install simple http server
RUN npm install -g http-server

# Copy built files from builder
COPY --from=builder /app/dist ./dist

# Copy public files (for products.json access)
COPY --from=builder /app/public ./public

EXPOSE 80

CMD ["http-server", "dist", "-p", "80", "--gzip", "-c-1"]
