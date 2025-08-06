# Frontend development environment with modern tooling
FROM node:18-slim

# Set environment variables
ENV NODE_ENV=development \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    vim \
    nano \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install global npm packages for development
RUN npm install -g \
    @vitejs/create-vite \
    create-react-app \
    @vue/cli \
    @angular/cli \
    typescript \
    ts-node \
    tsx \
    nodemon \
    prettier \
    eslint \
    @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin \
    sass \
    less \
    stylus \
    postcss \
    autoprefixer \
    tailwindcss \
    webpack \
    webpack-cli \
    webpack-dev-server \
    parcel \
    @playwright/test \
    cypress \
    jest \
    vitest

# Install additional package managers
RUN npm install -g yarn pnpm

# Create development user
RUN useradd -m -s /bin/bash frontend && \
    chown -R frontend:frontend /usr/local/lib/node_modules && \
    chown -R frontend:frontend /usr/local/bin

# Set up working directory
WORKDIR /app

# Copy development scripts
COPY scripts/frontend-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/frontend-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node --version || exit 1

# Switch to development user
USER frontend

# Set up shell environment
RUN echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -A"' >> ~/.bashrc && \
    echo 'alias npm-check="npm outdated"' >> ~/.bashrc && \
    echo 'alias yarn-check="yarn outdated"' >> ~/.bashrc

# Expose common development ports
EXPOSE 3000 3001 4200 5173 8080 8000

ENTRYPOINT ["/usr/local/bin/frontend-entrypoint.sh"]
CMD ["bash"]
