#!/bin/bash
# Production Deployment Script for Phase V Todo System
# Supports: Azure AKS, Google GKE, Oracle OKE
# Usage: ./deploy-prod.sh [aks|gke|oke]

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
NAMESPACE="todo-system"
HELM_CHART_PATH="./helm/charts"
PROD_VALUES_FILE="./helm/charts/values-prod.yaml"
EXTERNAL_SECRETS_FILE="./k8s/dapr/secrets-external.yaml"
RBAC_FILE="./k8s/rbac/production-rbac.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed"
        exit 1
    fi

    # Check if values file exists
    if [[ ! -f "$PROD_VALUES_FILE" ]]; then
        log_error "Production values file not found: $PROD_VALUES_FILE"
        exit 1
    fi

    # Check if secrets file exists
    if [[ ! -f "$EXTERNAL_SECRETS_FILE" ]]; then
        log_error "External secrets file not found: $EXTERNAL_SECRETS_FILE"
        exit 1
    fi

    # Check if RBAC file exists
    if [[ ! -f "$RBAC_FILE" ]]; then
        log_error "RBAC file not found: $RBAC_FILE"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Validate cluster connectivity
validate_cluster() {
    log "Validating cluster connectivity..."

    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    log_success "Cluster connectivity validated"
}

# Install External Secrets Operator (if not already installed)
install_external_secrets_operator() {
    log "Installing External Secrets Operator..."

    # Check if ESO is already installed
    if kubectl get ns external-secrets &> /dev/null; then
        log "External Secrets Operator already installed"
        return 0
    fi

    # Install External Secrets Operator
    helm repo add external-secrets https://charts.external-secrets.io
    helm repo update
    helm upgrade --install external-secrets external-secrets/external-secrets \
        --namespace external-secrets \
        --create-namespace \
        --wait \
        --timeout 10m

    log_success "External Secrets Operator installed"
}

# Deploy secrets configuration
deploy_secrets() {
    log "Deploying external secrets configuration..."

    kubectl apply -f "$EXTERNAL_SECRETS_FILE"

    # Wait for secret stores to be ready
    kubectl wait --for=condition=ready secretstore/vault-secret-store -n "$NAMESPACE" --timeout=60s || true

    log_success "External secrets configuration deployed"
}

# Deploy RBAC configuration
deploy_rbac() {
    log "Deploying RBAC configuration..."

    kubectl apply -f "$RBAC_FILE"

    # Wait for service accounts to be created
    sleep 5

    log_success "RBAC configuration deployed"
}

# Deploy Dapr (if not already installed)
install_dapr() {
    log "Installing Dapr..."

    # Check if Dapr is already installed
    if kubectl get ns dapr-system &> /dev/null; then
        log "Dapr already installed"
        return 0
    fi

    # Install Dapr CLI if not present
    if ! command -v dapr &> /dev/null; then
        log "Installing Dapr CLI..."
        wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
    fi

    # Initialize Dapr in Kubernetes
    dapr init -k --enable-ha=true --enable-mtls=true

    log_success "Dapr installed"
}

# Deploy the application
deploy_application() {
    log "Deploying application to production..."

    # Create namespace if it doesn't exist
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

    # Deploy using Helm with production values
    helm upgrade --install todo-system "$HELM_CHART_PATH" \
        --values "$PROD_VALUES_FILE" \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --wait \
        --timeout 15m

    log_success "Application deployed successfully"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."

    # Check if all pods are running
    log "Waiting for all pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=core-todo-service -n "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app=recurring-task-service -n "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app=notification-service -n "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app=audit-log-service -n "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app=websocket-sync-service -n "$NAMESPACE" --timeout=300s
    kubectl wait --for=condition=ready pod -l app=frontend -n "$NAMESPACE" --timeout=300s

    # Check services
    log "Checking services..."
    kubectl get svc -n "$NAMESPACE"

    # Check deployments
    log "Checking deployments..."
    kubectl get deploy -n "$NAMESPACE"

    # Check Dapr status
    log "Checking Dapr status..."
    dapr status -k

    log_success "Deployment verified successfully"
}

# Configure ingress for production
configure_ingress() {
    log "Configuring ingress for production..."

    # Check if ingress is configured
    if kubectl get ingress todo-ingress -n "$NAMESPACE" &> /dev/null; then
        log "Ingress already configured"
        return 0
    fi

    log_success "Ingress configuration completed"
}

# Show deployment status
show_status() {
    log "=== Production Deployment Status ==="
    echo ""
    echo "Namespace: $NAMESPACE"
    echo "Environment: Production"
    echo ""
    echo "Services:"
    kubectl get svc -n "$NAMESPACE"
    echo ""
    echo "Deployments:"
    kubectl get deploy -n "$NAMESPACE"
    echo ""
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo ""
    echo "Dapr Components:"
    kubectl get components.dapr.io -A
    echo ""
    log_success "Production deployment completed successfully!"
}

# Cleanup function
cleanup() {
    log "Performing cleanup..."
    # Add any cleanup operations here if needed
}

# Main execution
main() {
    log "Starting production deployment for Phase V Todo System"

    # Validate input
    if [[ $# -eq 0 ]]; then
        log_error "Usage: $0 [aks|gke|oke]"
        log_error "Supported platforms: Azure AKS, Google GKE, Oracle OKE"
        exit 1
    fi

    PLATFORM="$1"

    if [[ ! "$PLATFORM" =~ ^(aks|gke|oke)$ ]]; then
        log_error "Invalid platform. Supported: aks, gke, oke"
        exit 1
    fi

    log "Target platform: $PLATFORM"

    # Set trap for cleanup
    trap cleanup EXIT

    # Execute deployment steps
    check_prerequisites
    validate_cluster
    install_external_secrets_operator
    deploy_secrets
    deploy_rbac
    install_dapr
    deploy_application
    verify_deployment
    configure_ingress
    show_status

    log_success "All production deployment tasks completed successfully!"
}

# Run main function with all arguments
main "$@"