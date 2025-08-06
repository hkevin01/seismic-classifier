# Development tooling environment for code quality and CI/CD
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHON_VERSION=3.11 \
    NODE_VERSION=18 \
    GO_VERSION=1.21.0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    unzip \
    zip \
    jq \
    tree \
    htop \
    build-essential \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Install Python
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-pip python${PYTHON_VERSION}-venv && \
    ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 && \
    ln -s /usr/bin/python3 /usr/bin/python

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get install -y nodejs

# Install Go
RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz

# Set Go environment
ENV PATH=/usr/local/go/bin:$PATH

# Install Python development tools
RUN python -m pip install --upgrade pip && \
    pip install \
    black \
    flake8 \
    mypy \
    pylint \
    isort \
    bandit \
    safety \
    pre-commit \
    pytest \
    pytest-cov \
    coverage \
    sphinx \
    twine

# Install Node.js development tools
RUN npm install -g \
    eslint \
    prettier \
    typescript \
    @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin \
    jsdoc \
    typedoc \
    semantic-release \
    commitizen \
    conventional-changelog-cli \
    snyk \
    audit-ci

# Install Go development tools
RUN go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest && \
    go install golang.org/x/tools/cmd/goimports@latest && \
    go install github.com/securecodewarrior/gosec/v2/cmd/gosec@latest

# Install Docker and docker-compose
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh && \
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Install additional security tools
RUN wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_$(dpkg --print-architecture).deb && \
    dpkg -i trivy_$(dpkg --print-architecture).deb && \
    rm trivy_$(dpkg --print-architecture).deb

# Create development user
RUN useradd -m -s /bin/bash devtools && \
    usermod -aG docker devtools

# Set up working directory
WORKDIR /workspace

# Copy development scripts
COPY scripts/tools-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/tools-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python --version && node --version && go version || exit 1

# Switch to development user
USER devtools

# Set up shell environment
RUN echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc && \
    echo 'alias ll="ls -la"' >> ~/.bashrc && \
    echo 'alias la="ls -A"' >> ~/.bashrc && \
    echo 'alias lint-all="black . && flake8 . && mypy . && eslint . && prettier --check ."' >> ~/.bashrc

ENTRYPOINT ["/usr/local/bin/tools-entrypoint.sh"]
CMD ["bash"]
