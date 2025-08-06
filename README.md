# Ping-Pong Flask Application

This application is created in Python and is meant to test the CICD pipeline to EKS.
It's a simple Flask application that responds to HTTP requests.

## Features

- **GET /ping** - Health check endpoint that responds with "pong"
- **POST /hello** - Receives JSON `{"name":"<name>"}` and responds with `{"message": "Hello <name>, current time is <timestamp>"}`
- **GET /** - Serves an interactive HTML page with API testing capabilities
- **GET /health** - Health check endpoint for Kubernetes probes

### Interactive Web Interface

The home page (`/`) includes an interactive web interface that allows users to:

- **Test all API endpoints** directly from the browser
- **Customize the /hello message** by entering any name
- **See real-time responses** with success/error indicators
- **View formatted JSON responses** for health checks

## Project Structure

```
/
├── .github/workflows/           # GitHub Actions workflows
│   ├── docker-build.yml        # Docker build and push
│   ├── validate.yml            # Code validation and testing
│   └── semantic-release.yml    # Automated versioning
├── src/                        # Application source code
│   ├── main.py                 # Main Flask application
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Container image definition
│   ├── .dockerignore          # Docker ignore file
│   ├── Makefile               # Development commands
│   ├── pyproject.toml         # Project configuration
│   ├── wsgi.py                # WSGI entry point
│   ├── gunicorn.conf.py       # Gunicorn configuration
│   ├── entrypoint.sh          # Container entrypoint
│   └── html/
│       └── index.html         # Interactive web interface template
├── helm-charts/               # Kubernetes deployment charts
│   ├── Makefile              # Helm deployment commands
│   └── ping-pong/           # Main application chart
│       ├── Chart.yaml        # Helm chart metadata
│       ├── values.yaml       # Default configuration values
│       └── templates/        # Kubernetes resource templates
├── GitVersion.yml            # Semantic versioning configuration
├── .releaserc.json          # Semantic release configuration
├── CI-CD-README.md          # CI/CD pipeline documentation
└── README.md                # This file
```

## Local Development

### Prerequisites
- Python 3.11+
- Docker
- Kubernetes cluster with Helm (for deployment)

### Docker

1. **Build Docker image:**
   ```bash
   cd src && make docker-build
   ```

2. **Run Docker container:**
   ```bash
   cd src && make docker-run
   ```

3. **Test with Docker:**
   ```bash
   cd src && make docker-test
   ```

### Manual Docker Commands

1. **Build image:**
   ```bash
   docker build -t ping-pong:latest ./src
   ```

2. **Run container:**
   ```bash
   docker run -p 5000:5000 ping-pong:latest
   ```

### Helm Deployment

1. **Deploy to development:**
   ```bash
   cd helm-charts && make install-dev
   ```

2. **Deploy to production:**
   ```bash
   cd helm-charts && make install-prod
   ```

## API Endpoints

### GET /ping
Returns a simple "pong" response for health checks.

**Response:**
```
pong
```

### POST /hello
Accepts JSON with a name and returns a personalized greeting with timestamp.

**Request:**
```json
{
  "name": "World"
}
```

**Response:**
```json
{
  "message": "Hello World, current time is 2025-08-06 10:30:45 UTC"
}
```

### GET /
Returns an interactive HTML page that includes:
- EKS cluster status display
- Interactive API testing interface

Users can test all endpoints directly from the web interface:
- **Ping Test**: One-click ping endpoint testing
- **Custom Greetings**: Enter any name to test the /hello endpoint
- **Health Check**: View detailed application health information

### GET /health
Returns application health status for Kubernetes probes.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-06 10:30:45 UTC",
  "app": "ping-pong"
}
```

## Kubernetes Deployment

The application includes a complete Helm chart for deployment to Kubernetes with AWS Load Balancer Controller support.

### ALB Integration

The Helm chart is configured to use AWS Application Load Balancer (ALB) with automatic hostname assignment:

- **No static hostname required** - The ALB controller automatically assigns a hostname
- **Environment-specific configurations** - Separate values files for dev and prod
- **Health checks** - Configured for ALB health check integration
- **SSL/TLS ready** - Production values include SSL redirect configuration

### Environment-Specific Deployments

The chart includes environment-specific value files:

- **`values-dev.yaml`** - Development environment with debug enabled, lower resources
- **`values-prod.yaml`** - Production environment with SSL, high availability, anti-affinity

### Configuration

The Helm chart supports configuration through `values.yaml`:

- **Replicas:** Number of pod replicas (default: 2)
- **Resources:** CPU and memory limits/requests
- **Ingress:** ALB ingress controller configuration
- **Autoscaling:** Horizontal Pod Autoscaler settings
- **Security:** Pod security context and non-root user

## Environment Variables

- `APP_NAME`: Application name (default: "ping-pong")
- `PORT`: Server port (default: 5000)
- `HOST`: Server host (default: "0.0.0.0")
- `DEBUG`: Debug mode (default: false)

## Production Considerations

- Application runs with gunicorn in production
- Uses non-root user (UID 1001) for security
- Includes health checks and probes
- Supports horizontal pod autoscaling
- Configured for AWS ALB ingress controller
- Includes resource limits and requests
