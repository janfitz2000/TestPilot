FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY src/web_interface/package*.json ./

# Install dependencies
RUN npm install

# Copy source code (excluding node_modules)
COPY src/web_interface/src ./src
COPY src/web_interface/public ./public
COPY src/web_interface/tsconfig.json ./
COPY src/web_interface/tailwind.config.js ./
COPY src/web_interface/postcss.config.js ./

# Create non-root user (handle existing group gracefully)
RUN addgroup -g 1001 testpilot || addgroup testpilot
RUN adduser -D -s /bin/sh -u 1001 -G testpilot testpilot
RUN chown -R testpilot:testpilot /app
USER testpilot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

EXPOSE 3000
CMD ["npm", "start"]