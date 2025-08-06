#!/bin/bash

# Simple deployment script for ping-pong helm chart
# Usage: ./deploy.sh [OPTIONS]
#
# Options:
#   --build-type=<release|development>  Build type (default: development)
#   --image-tag=<tag>                   Image tag to deploy (default: latest)
#   --namespace=<name>                  Kubernetes namespace (default: auto-generated)
#   --release-name=<name>               Helm release name (default: auto-generated)
#   --branch-name=<name>                Branch name for development builds
#   --pr-number=<number>                PR number for development builds
#   --ghcr-username=<username>          GHCR username (default: current user)
#   --ghcr-token=<token>                GHCR PAT token (required)
#   --help                              Show this help message


set -ex

# Print help and exit if no arguments are provided
if [[ $# -eq 0 ]]; then
  exec "$0" --help
fi

# Default values
BUILD_TYPE="development"
IMAGE_TAG="latest"
NAMESPACE=""
RELEASE_NAME=""
BRANCH_NAME=""
PR_NUMBER=""
GHCR_USERNAME="${USER}"
GHCR_TOKEN=""
IMAGE_NAME="ghcr.io/bruj0/cicd-for-eks/ping-pong"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --build-type=*)
      BUILD_TYPE="${1#*=}"
      shift
      ;;
    --image-tag=*)
      IMAGE_TAG="${1#*=}"
      shift
      ;;
    --namespace=*)
      NAMESPACE="${1#*=}"
      shift
      ;;
    --release-name=*)
      RELEASE_NAME="${1#*=}"
      shift
      ;;
    --branch-name=*)
      BRANCH_NAME="${1#*=}"
      shift
      ;;
    --pr-number=*)
      PR_NUMBER="${1#*=}"
      shift
      ;;
    --ghcr-username=*)
      GHCR_USERNAME="${1#*=}"
      shift
      ;;
    --ghcr-token=*)
      GHCR_TOKEN="${1#*=}"
      shift
      ;;
    --help)
      echo "Simple deployment script for ping-pong helm chart"
      echo ""
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --build-type=<release|development>  Build type (default: development)"
      echo "  --image-tag=<tag>                   Image tag to deploy (default: latest)"
      echo "  --namespace=<name>                  Kubernetes namespace (default: auto-generated)"
      echo "  --release-name=<name>               Helm release name (default: auto-generated)"
      echo "  --branch-name=<name>                Branch name for development builds"
      echo "  --pr-number=<number>                PR number for development builds"
      echo "  --ghcr-username=<username>          GHCR username (default: current user)"
      echo "  --ghcr-token=<token>                GHCR PAT token (required)"
      echo "  --help                              Show this help message"
      echo ""
      echo "Examples:"
      echo "  # Production deployment"
      echo "  $0 --build-type=release --image-tag=1.0.0 --ghcr-token=ghp_xxx"
      echo ""
      echo "  # Development deployment"
      echo "  $0 --build-type=development --branch-name=feature-branch --pr-number=123 --ghcr-token=ghp_xxx"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Validate required parameters
if [[ -z "$GHCR_TOKEN" ]]; then
  echo "Error: GHCR token is required. Use --ghcr-token=<token>"
  exit 1
fi

# Check if required tools are available
for cmd in kubectl helm; do
  if ! command -v $cmd &> /dev/null; then
    echo "Error: $cmd is not installed or not in PATH"
    exit 1
  fi
done

# Determine deployment parameters based on build type
if [[ "$BUILD_TYPE" == "release" ]]; then
  if [[ -z "$NAMESPACE" ]]; then
    NAMESPACE="default"
  fi
  if [[ -z "$RELEASE_NAME" ]]; then
    RELEASE_NAME="ping-pong"
  fi
  VALUES_FILE="values.yaml"
  echo "Deploying release to production namespace: $NAMESPACE"
else
  # For development builds
  if [[ -z "$NAMESPACE" ]]; then
    if [[ -n "$BRANCH_NAME" ]]; then
      BRANCH_CLEAN=$(echo "$BRANCH_NAME" | sed 's/[^a-zA-Z0-9-]/-/g' | tr '[:upper:]' '[:lower:]')
      NAMESPACE="$BRANCH_CLEAN"
    else
      NAMESPACE="development"
    fi
  fi

  if [[ -z "$RELEASE_NAME" ]]; then
    if [[ -n "$PR_NUMBER" ]]; then
      RELEASE_NAME="ping-pong-pr-$PR_NUMBER"
    elif [[ -n "$BRANCH_NAME" ]]; then
      BRANCH_CLEAN=$(echo "$BRANCH_NAME" | sed 's/[^a-zA-Z0-9-]/-/g' | tr '[:upper:]' '[:lower:]')
      RELEASE_NAME="ping-pong-$BRANCH_CLEAN"
    else
      RELEASE_NAME="ping-pong-dev"
    fi
  fi
  VALUES_FILE="values-dev.yaml"
  echo "Deploying to development namespace: $NAMESPACE"
fi

echo "Deployment parameters:"
echo "  Namespace: $NAMESPACE"
echo "  Release Name: $RELEASE_NAME"
echo "  Values File: $VALUES_FILE"
echo "  Image: $IMAGE_NAME:$IMAGE_TAG"
echo "  Build Type: $BUILD_TYPE"

# Change to the ping-pong chart directory
cd "$(dirname "$0")/ping-pong"

# Create namespace if it doesn't exist
echo "Creating namespace if it doesn't exist..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Deploy with Helm
echo "Deploying with Helm..."
helm upgrade --install "$RELEASE_NAME" . \
  --namespace "$NAMESPACE" \
  --values "$VALUES_FILE" \
  --set image.repository="$IMAGE_NAME" \
  --set image.tag="$IMAGE_TAG" \
  --set ghcr.enabled=true \
  --set ghcr.username="$GHCR_USERNAME" \
  --set ghcr.token="$GHCR_TOKEN" \
  --wait \
  --timeout=10m

# Verify deployment
echo "Verifying deployment..."
kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=ping-pong
kubectl get services -n "$NAMESPACE" -l app.kubernetes.io/name=ping-pong

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=ping-pong -n "$NAMESPACE" --timeout=300s

# Get deployment info
echo "Getting deployment information..."
INGRESS_HOST=$(kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "Not available")
SERVICE_IP=$(kubectl get service -n "$NAMESPACE" -l app.kubernetes.io/name=ping-pong -o jsonpath='{.items[0].spec.clusterIP}' 2>/dev/null || echo "Not available")

echo ""
echo "Deployment Summary:"
echo "  Image: $IMAGE_NAME:$IMAGE_TAG"
echo "  Namespace: $NAMESPACE"
echo "  Release: $RELEASE_NAME"
echo "  Build Type: $BUILD_TYPE"
echo "  Service IP: $SERVICE_IP"
echo "  Ingress Host: $INGRESS_HOST"
echo ""
echo "Verification Commands:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=ping-pong"
echo ""
echo "Deployment completed successfully!"
