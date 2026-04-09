#!/bin/bash
set -euo pipefail
echo "=== Building auth-service-mvc ==="
rm -rf .aws-sam/
sam build --use-container
echo "=== Deploying auth-service-mvc ==="
sam deploy --no-confirm-changeset
echo "=== Done ==="
sam list stack-outputs --stack-name tcc-auth-service-mvc --output table
