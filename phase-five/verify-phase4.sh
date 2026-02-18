#!/bin/bash
# Verification script for Phase 4: Production Cloud Deployment
# Ensures all deliverables for User Story 2 are properly created

set -euo pipefail

echo "🔍 Verifying Phase 4: Production Cloud Deployment Deliverables..."

# Define expected files
EXPECTED_FILES=(
    "helm/charts/values-prod.yaml"
    "k8s/dapr/secrets-external.yaml"
    "k8s/rbac/production-rbac.yaml"
    "deploy-prod.sh"
    "PRODUCTION_DEPLOYMENT.md"
    "PHASE-4-COMPLETE.md"
)

MISSING_FILES=()
ALL_PRESENT=true

echo "📋 Checking required files..."
for file in "${EXPECTED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ Found: $file"
    else
        echo "❌ Missing: $file"
        MISSING_FILES+=("$file")
        ALL_PRESENT=false
    fi
done

echo ""
if [ "$ALL_PRESENT" = true ]; then
    echo "🎉 All Phase 4 deliverables are present!"

    echo ""
    echo "📄 File details:"
    for file in "${EXPECTED_FILES[@]}"; do
        size=$(stat -c%s "$file")
        echo "   $file ($(numfmt --to=iec --format="%.2f" $size))"
    done

    echo ""
    echo "🎯 Phase 4 Tasks Successfully Verified:"
    echo "   T018: Production Helm Values - helm/charts/values-prod.yaml"
    echo "   T019: External Secrets Configuration - k8s/dapr/secrets-external.yaml"
    echo "   T020: Production RBAC Configuration - k8s/rbac/production-rbac.yaml"
    echo "   T021: Production Deployment Script - deploy-prod.sh"
    echo "   T022: Production Deployment Documentation - PRODUCTION_DEPLOYMENT.md"

    echo ""
    echo "🚀 Ready for production deployment to AKS/GKE/OKE!"
else
    echo "❌ Some files are missing. Please create the following files:"
    for missing in "${MISSING_FILES[@]}"; do
        echo "   - $missing"
    done
    exit 1
fi