.PHONY: help lint template template-dev template-prod install install-dev install-prod uninstall get-alb-url get-alb-url-dev get-alb-url-prod
# Variables
APP_NAME := ping-pong
DOCKER_TAG := latest
PORT := 5000
NAMESPACE := default

help: ## Show this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Kubernetes/Helm targets
lint: ## Lint the Helm chart
	helm lint ping-pong

template: ## Generate Kubernetes manifests from Helm chart
	helm template ping-pong ping-pong --namespace $(NAMESPACE) --set image.tag=$(DOCKER_TAG)

template-dev: ## Generate Kubernetes manifests for dev environment
	helm template ping-pong ping-pong -f ping-pong/values-dev.yaml --namespace $(NAMESPACE) --set image.tag=$(DOCKER_TAG)

template-prod: ## Generate Kubernetes manifests for prod environment
	helm template ping-pong ping-pong -f ping-pong/values-prod.yaml --namespace $(NAMESPACE) --set image.tag=$(DOCKER_TAG)

install: ## Install the Helm chart (requires kubectl context)
	helm upgrade --install ping-pong ping-pong --namespace $(NAMESPACE) --create-namespace --set image.tag=$(DOCKER_TAG)

install-dev: ## Install the Helm chart for dev environment
	helm upgrade --install ping-pong-dev ping-pong -f ping-pong/values-dev.yaml --namespace $(NAMESPACE) --create-namespace --set image.tag=$(DOCKER_TAG)

install-prod: ## Install the Helm chart for prod environment
	helm upgrade --install ping-pong-prod ping-pong -f ping-pong/values-prod.yaml --namespace $(NAMESPACE) --create-namespace --set image.tag=$(DOCKER_TAG)

uninstall: ## Uninstall the Helm chart
	helm uninstall ping-pong --namespace $(NAMESPACE)

get-alb-url: ## Get the ALB URL after deployment
	@echo "Fetching ALB hostname..."
	@kubectl get ingress ping-pong -n $(NAMESPACE) -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "Ingress not found or ALB not ready yet"

get-alb-url-dev: ## Get the ALB URL for dev environment
	@echo "Fetching ALB hostname for dev..."
	@kubectl get ingress ping-pong-dev -n $(NAMESPACE) -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "Dev ingress not found or ALB not ready yet"

get-alb-url-prod: ## Get the ALB URL for prod environment
	@echo "Fetching ALB hostname for prod..."
	@kubectl get ingress ping-pong-prod -n $(NAMESPACE) -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "Prod ingress not found or ALB not ready yet"
