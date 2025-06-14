FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY src/web_interface/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/web_interface/ ./

# Create non-root user
RUN addgroup -g 1000 testpilot && adduser -D -s /bin/sh -u 1000 -G testpilot testpilot
RUN chown -R testpilot:testpilot /app
USER testpilot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

EXPOSE 3000
CMD ["npm", "start"]