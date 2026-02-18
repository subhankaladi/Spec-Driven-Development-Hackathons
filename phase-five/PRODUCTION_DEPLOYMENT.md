# Production Deployment Guide for Phase V Todo System

This document describes the production deployment process for the Phase V Todo System on Kubernetes, supporting Azure AKS, Google GKE, and Oracle OKE.

## Overview

The production deployment includes:

- **Microservices Architecture**: Core Todo, Recurring Tasks, Notifications, Audit Logs, WebSocket Sync
- **Dapr Integration**: For service-to-service communication, state management, and pub/sub
- **Managed Services**: PostgreSQL (Neon), Kafka (managed), External Secrets
- **Security**: RBAC, Network Policies, Pod Security Policies
- **High Availability**: Multi-replica deployments, HA Dapr, Load Balancers

## Prerequisites

Before deploying to production, ensure you have:

1. **Kubernetes Cluster**: AKS, GKE, or OKE with sufficient resources
2. **kubectl**: Configured to connect to your cluster
3. **Helm 3**: Installed and configured
4. **Dapr CLI**: Installed locally
5. **External Services**:
   - Managed PostgreSQL (e.g., Neon, Azure Database for PostgreSQL)
   - Managed Kafka (e.g., Confluent Cloud, Azure Event Hubs, Google Cloud Pub/Sub)
   - External Secrets Store (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, Google Secret Manager)

## Configuration Files

### 1. Production Values (`helm/charts/values-prod.yaml`)

Contains production-specific configurations including:

- Resource limits and requests
- Replica counts for high availability
- External service endpoints
- Security settings
- Monitoring and logging configurations

### 2. External Secrets (`k8s/dapr/secrets-external.yaml`)

Defines how to connect to external secrets stores and what secrets to fetch.

### 3. RBAC Configuration (`k8s/rbac/production-rbac.yaml`)

Sets up role-based access control with principle of least privilege for each service.

## Deployment Steps

### 1. Prepare Your Environment

```bash
# Clone the repository
git clone <repository-url>
cd phase-five

# Configure kubectl to point to your production cluster
# (This step varies by cloud provider)
```

### 2. Update Configuration

Update the following files with your production values:

- `helm/charts/values-prod.yaml`: Update database connection strings, Kafka endpoints, image repositories
- `k8s/dapr/secrets-external.yaml`: Update Vault/Azure Key Vault/other secrets store configuration

### 3. Run the Deployment Script

```bash
# For Azure AKS
./deploy-prod.sh aks

# For Google GKE
./deploy-prod.sh gke

# For Oracle OKE
./deploy-prod.sh oke
```

## Platform-Specific Configuration

### Azure AKS

When deploying to AKS, you may need to:

1. Enable Azure Workload Identity for secrets access
2. Configure Azure Container Registry for image pulling
3. Set up Azure Application Gateway for ingress

### Google GKE

When deploying to GKE, you may need to:

1. Enable Workload Identity for secrets access
2. Configure Google Container Registry or Artifact Registry
3. Set up Google Cloud Load Balancer for ingress

### Oracle OKE

When deploying to OKE, you may need to:

1. Configure OCI Vault for secrets access
2. Set up OCI Registry for image pulling
3. Configure OCI Load Balancer for ingress

## Security Considerations

### RBAC

Each service runs with minimal required permissions:

- Core Todo Service: Can read database secrets, access logs
- Recurring Task Service: Read-only access to state store secrets
- Notification Service: Minimal permissions, mostly logs access
- Audit Log Service: Read database secrets, write logs
- WebSocket Sync Service: In-memory only, minimal permissions

### Network Policies

Network policies restrict traffic between services and external access:

- Only ingress controller can access services
- Services can communicate via Dapr sidecars
- Egress allowed only to required external services (Kafka, PostgreSQL, DNS, HTTPS)

### Pod Security

All pods run with:

- Non-root user
- ReadOnlyRootFilesystem where possible
- Privilege escalation disabled
- Required capabilities dropped

## Monitoring and Observability

The production deployment includes:

- **Metrics**: Prometheus scraping configured
- **Logging**: Structured JSON logging enabled
- **Tracing**: Distributed tracing with OpenTelemetry
- **Health Checks**: Comprehensive liveness/readiness probes

## Scaling Configuration

Default production scaling:

- Core Todo Service: 2 replicas (can autoscale up to 10)
- Recurring Task Service: 2 replicas (fixed)
- Notification Service: 3 replicas (higher scale for notifications)
- Audit Log Service: 1 replica (single for ordering guarantees)
- WebSocket Sync Service: 2 replicas (sticky sessions enabled)

## Backup and Recovery

The system includes:

- Daily automated backups scheduled at 2 AM UTC
- 30-day retention for backup data
- Database-level backup configuration
- State store backup procedures

## Rollback Procedure

To rollback to a previous version:

```bash
# Find the previous release
helm list -n todo-system

# Rollback to a specific revision
helm rollback todo-system <revision-number> -n todo-system
```

## Troubleshooting

### Common Issues

1. **Pods not starting**: Check resource quotas and node capacity
2. **Secrets not loading**: Verify external secrets operator and configuration
3. **Dapr sidecars not injected**: Check Dapr installation and annotations
4. **Database connectivity**: Verify connection strings and network policies

### Useful Commands

```bash
# Check all pods status
kubectl get pods -n todo-system

# Check logs for a specific service
kubectl logs -n todo-system deployment/core-todo-service

# Check Dapr status
dapr status -k

# Check services
kubectl get svc -n todo-system

# Describe a pod for detailed information
kubectl describe pod <pod-name> -n todo-system
```

## Maintenance

### Updating Images

To update service images:

1. Update the image tags in `values-prod.yaml`
2. Run `helm upgrade` with the updated values file

### Rotating Secrets

External secrets operator handles automatic rotation based on the refresh interval configured in the ExternalSecret resources.

## Architecture Diagram

The production architecture includes:

```
Internet -> Ingress Controller -> Load Balancer -> Services
                                    |
                                    v
                              Dapr Sidecars (Service Mesh)
                                    |
                                    v
                    Managed Kafka <- -> Managed PostgreSQL
                         |
                         v
                 External Secrets Store
```

## Performance Tuning

For optimal performance in production:

- Monitor resource utilization and adjust limits/requests
- Tune Kafka partition counts based on load
- Optimize database connection pools
- Configure appropriate caching strategies
- Monitor and tune Dapr components for performance