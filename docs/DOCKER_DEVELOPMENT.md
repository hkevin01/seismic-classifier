# Universal Docker Development Environment

This document describes the universal Docker-based development strategy for the Seismic Classifier project. This approach ensures consistent development environments across all team members and eliminates "works on my machine" issues.

## Overview

The universal Docker development environment provides:
- **Isolated Dependencies**: Each service runs in its own container with specific versions
- **Consistent Environment**: Same environment across all developer machines
- **Multi-Language Support**: Python, Node.js, and various tools in isolated containers
- **Database Integration**: PostgreSQL, Redis, MongoDB, and Elasticsearch for development
- **VS Code Integration**: DevContainer support for seamless IDE experience
- **Hot Reloading**: Live code updates without container restarts

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Development Network                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Backend Dev    │  Frontend Dev   │     Tools Container         │
│  ┌────────────┐ │  ┌────────────┐ │  ┌─────────────────────────┐│
│  │Python 3.11 │ │  │Node.js 18  │ │  │Code Quality & Security  ││
│  │FastAPI     │ │  │React       │ │  │- Black, Flake8, MyPy    ││
│  │Jupyter     │ │  │TypeScript  │ │  │- ESLint, Prettier       ││
│  │Pytest     │ │  │Jest        │ │  │- Bandit, Safety, Trivy  ││
│  │Celery      │ │  │Storybook   │ │  │- Docker, Terraform      ││
│  └────────────┘ │  └────────────┘ │  └─────────────────────────┘│
└─────────────────┴─────────────────┴─────────────────────────────┘
├─────────────────────────────────────────────────────────────────┤
│                     Data Layer                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐│
│  │PostgreSQL   │ │Redis        │ │MongoDB      │ │MinIO S3    ││
│  │Primary DB   │ │Cache/Queue  │ │Analytics    │ │Object Store││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker (20.10+)
- Docker Compose (2.0+)
- VS Code (optional, for devcontainer support)

### 1. Start Development Environment

```bash
# Start core services (backend, frontend, database)
make dev-up

# Or start all services including analytics and storage
make dev-up-full
```

### 2. Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Jupyter Notebook**: http://localhost:8888
- **Database**: postgresql://postgres:password@localhost:5432/seismic_dev
- **Redis**: redis://localhost:6379/0

### 3. Verify Environment

```bash
# Check service status
make dev-status

# Run health checks
make health-check

# Run tests
make test
```

## Development Containers

### Backend Development Container
- **Base**: Python 3.11 on Ubuntu 22.04
- **Tools**: FastAPI, Jupyter, Pytest, Celery, Alembic
- **Features**: 
  - Virtual environment with pip-tools
  - Jupyter Lab with extensions
  - Database migration tools
  - Hot reloading for development

### Frontend Development Container
- **Base**: Node.js 18 on Ubuntu 22.04
- **Tools**: React, TypeScript, Jest, Storybook, Vite
- **Features**:
  - Modern JavaScript toolchain
  - Component development with Storybook
  - Hot module replacement
  - Automated testing

### Tools Container
- **Purpose**: Code quality, security, and CI/CD tools
- **Languages**: Python, Node.js, Go
- **Tools**: 
  - Code Quality: Black, Flake8, MyPy, ESLint, Prettier
  - Security: Bandit, Safety, Snyk, Trivy
  - Infrastructure: Docker, Terraform, AWS CLI
  - Testing: Pytest, Jest, Go Test

## Database Services

### Core Databases
- **PostgreSQL 15**: Primary application database
- **Redis 7**: Caching and message queuing
- **MongoDB 6**: Analytics and document storage (optional)
- **Elasticsearch 8**: Search and logging (optional)
- **MinIO**: S3-compatible object storage (optional)

### Database Management
```bash
# Reset database
make db-reset

# Run migrations
make db-migrate

# Create new migration
make db-migration

# Backup database
make db-backup

# Access database shell
make db-shell
```

## VS Code DevContainer Integration

### Setup
1. Install the "Remote - Containers" extension
2. Open project in VS Code
3. Click "Reopen in Container" when prompted
4. VS Code will build and connect to the development container

### Features
- **Automatic Extensions**: Python, TypeScript, Docker extensions pre-installed
- **Integrated Terminal**: Direct access to container environment
- **Debugging**: Configured for Python and TypeScript
- **IntelliSense**: Full code completion and type checking
- **Port Forwarding**: Automatic forwarding of service ports

## Development Workflows

### New Developer Onboarding
```bash
# One-command setup for new developers
make quick-start
```

This command:
1. Starts all development services
2. Installs dependencies
3. Runs database migrations
4. Executes tests to verify setup
5. Displays service URLs

### Daily Development
```bash
# Start development environment
make dev-up

# Open backend shell for debugging
make dev-shell

# Open frontend shell for package management
make frontend-shell

# View logs from all services
make dev-logs

# Run tests continuously
make test-watch
```

### Code Quality Workflow
```bash
# Check code quality
make lint

# Fix formatting issues
make format

# Run security scans
make security-scan

# Run full CI pipeline locally
make ci-test
```

## Service Profiles

Docker Compose profiles allow selective service startup:

### Core Profile (Default)
```bash
make dev-up  # Starts: backend, frontend, postgres, redis
```

### Analytics Profile
```bash
make dev-up-full  # Includes: mongodb, elasticsearch
```

### Storage Profile
```bash
docker-compose -f docker-compose.dev.yml --profile storage up -d
# Includes: minio
```

### Tools Profile
```bash
docker-compose -f docker-compose.dev.yml --profile tools up -d
# Starts: development tools container
```

## Volume Management

### Persistent Volumes
- **backend-venv**: Python virtual environment cache
- **frontend-modules**: Node.js modules cache
- **dev-db-data**: PostgreSQL data persistence
- **dev-redis-data**: Redis data persistence

### Performance Benefits
- Faster startup times (cached dependencies)
- Persistent data across container restarts
- Shared cache across container rebuilds

## Environment Variables

### Backend Environment
```bash
PYTHONPATH=/workspace/src
DEVELOPMENT=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://postgres:password@dev-db:5432/seismic_dev
REDIS_URL=redis://dev-redis:6379/0
```

### Frontend Environment
```bash
NODE_ENV=development
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
CHOKIDAR_USEPOLLING=true
```

## Network Configuration

All services communicate through the `seismic-dev-network` Docker network:
- **Internal Communication**: Services use container names (e.g., `dev-db`, `dev-redis`)
- **External Access**: Services expose ports on localhost
- **Security**: Network isolation from other Docker projects

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using port 8000
sudo netstat -tulpn | grep :8000

# Stop conflicting services
make dev-down
```

#### Container Build Failures
```bash
# Rebuild containers from scratch
make dev-rebuild

# Clear Docker cache
docker system prune -a
```

#### Database Connection Issues
```bash
# Check database status
make logs-db

# Reset database
make db-reset
```

#### Volume Issues
```bash
# Clean all volumes and restart
make clean
make dev-up
```

### Performance Optimization

#### For macOS/Windows Users
```yaml
# In docker-compose.dev.yml, use cached volumes
volumes:
  - ./:/workspace:cached
  - backend-venv:/workspace/.venv:delegated
```

#### For Large Codebases
```bash
# Use dockerignore to exclude unnecessary files
echo "node_modules\n.git\n*.pyc\n__pycache__" >> .dockerignore
```

## Advanced Features

### Custom Entrypoints
Each container has a custom entrypoint script that:
- Sets up the development environment
- Installs dependencies if needed
- Configures development tools
- Provides helpful startup information

### Health Checks
All services include health checks for:
- Service availability monitoring
- Automatic restart on failure
- Dependency verification

### Multi-Database Support
The environment supports multiple database types:
- Relational data in PostgreSQL
- Caching and queues in Redis
- Document storage in MongoDB
- Search and analytics in Elasticsearch
- Object storage in MinIO

## Migration from Local Development

### For Python Developers
```bash
# Old way
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# New way
make dev-up
make dev-shell
```

### For Node.js Developers
```bash
# Old way
npm install
npm start

# New way
make dev-up  # Frontend starts automatically
```

### Benefits of Migration
- **Consistency**: Same environment for all team members
- **Isolation**: No conflicts with system packages
- **Completeness**: Includes all required services (database, cache, etc.)
- **Speed**: Pre-built containers start faster than local setup

## Best Practices

### Development Workflow
1. **Start Clean**: Begin each session with `make dev-up`
2. **Test Early**: Run `make test` after major changes
3. **Format Code**: Use `make format` before committing
4. **Check Quality**: Run `make lint` regularly
5. **Monitor Health**: Use `make health-check` to verify services

### Container Management
1. **Regular Cleanup**: Run `make clean` weekly
2. **Update Images**: Pull latest base images monthly
3. **Volume Management**: Monitor disk usage of Docker volumes
4. **Log Rotation**: Clear container logs periodically

### Team Collaboration
1. **Consistent Commands**: Always use Makefile commands
2. **Environment Documentation**: Keep this guide updated
3. **Issue Reporting**: Include container logs in bug reports
4. **Version Pinning**: Pin specific versions for stability

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [VS Code DevContainers](https://code.visualstudio.com/docs/remote/containers)
- [FastAPI Development](https://fastapi.tiangolo.com/)
- [React Development](https://reactjs.org/docs/getting-started.html)

## Support

For issues with the development environment:
1. Check the troubleshooting section above
2. Review Docker logs: `make dev-logs`
3. Reset environment: `make clean && make dev-up`
4. Contact the development team with error details
