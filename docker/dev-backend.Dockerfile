# Multi-purpose backend development environment
# Supports Python, Node.js, and common development tools
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.6.1 \
    NODE_VERSION=18.17.0 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    vim \
    nano \
    wget \
    unzip \
    jq \
    htop \
    postgresql-client \
    redis-tools \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install Poetry for Python dependency management
RUN pip install poetry==$POETRY_VERSION

# Install common Python development tools
RUN pip install \
    black \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    jupyter \
    ipython \
    debugpy

# Install common Node.js development tools
RUN npm install -g \
    typescript \
    ts-node \
    nodemon \
    prettier \
    eslint \
    @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin

# Create development user
RUN useradd -m -s /bin/bash developer && \
    usermod -aG sudo developer

# Set up working directory
WORKDIR /workspace

# Copy development scripts
COPY scripts/dev-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/dev-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Switch to development user
USER developer

# Set up shell environment
RUN echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -A"' >> ~/.bashrc && \
    echo 'alias l="ls -CF"' >> ~/.bashrc

ENTRYPOINT ["/usr/local/bin/dev-entrypoint.sh"]
CMD ["bash"]
