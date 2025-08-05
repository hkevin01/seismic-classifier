# Deployment Guide

## Local Development with Docker

1. Build and run the application locally:

```bash
docker-compose up --build
```

2. Access the services:
   - API: [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Prometheus: [http://localhost:9090](http://localhost:9090)
   - Grafana: [http://localhost:3000](http://localhost:3000)

### Cloud Deployment (AWS)

1. Set up AWS credentials:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

2. Initialize Terraform:
```bash
cd infrastructure/aws
terraform init
```

3. Plan and apply infrastructure:
```bash
terraform plan
terraform apply
```

4. Build and push Docker image:
```bash
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-west-2.amazonaws.com
docker build -t seismic-classifier .
docker tag seismic-classifier:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-west-2.amazonaws.com/seismic-classifier:latest
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-west-2.amazonaws.com/seismic-classifier:latest
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Configuration
JWT_SECRET_KEY=your-secret-key
ENVIRONMENT=production
LOG_LEVEL=INFO

# AWS Configuration (if using AWS deployment)
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Monitoring and Logging

1. Access Grafana dashboards:
   - Local: http://localhost:3000
   - AWS: https://grafana.your-domain.com

2. Default credentials:
   - Username: admin
   - Password: admin

3. Available metrics:
   - HTTP request counters
   - Request latency histograms
   - System resource utilization
   - Custom seismic analysis metrics

### API Documentation

The API documentation is available at `/docs` when running the application. Key endpoints:

- POST `/analyze`: Submit seismic data for analysis
- GET `/status`: Check system status
- GET `/health`: Health check endpoint
- GET `/metrics`: Prometheus metrics

### Security

1. Authentication:
   - JWT-based authentication
   - Secure token generation and validation
   - Role-based access control

2. API Security:
   - Rate limiting
   - CORS configuration
   - Input validation

3. Infrastructure Security:
   - VPC configuration
   - Security groups
   - IAM roles and policies

### Scalability

The application is designed to scale horizontally:

1. Load Balancing:
   - Application Load Balancer for API requests
   - Multiple container instances

2. Auto Scaling:
   - ECS service auto scaling
   - Target tracking policies

3. Database (if added):
   - Connection pooling
   - Read replicas

### Troubleshooting

1. Container Issues:
```bash
# Check container logs
docker-compose logs -f api

# Restart services
docker-compose restart
```

2. AWS Deployment:
```bash
# Check ECS service logs
aws ecs describe-services --cluster seismic-classifier-cluster --services seismic-classifier

# Check CloudWatch logs
aws logs get-log-events --log-group-name /ecs/seismic-classifier
```

3. Common Issues:
   - Container health check failures
   - Memory/CPU constraints
   - Network connectivity
   - Authentication issues
