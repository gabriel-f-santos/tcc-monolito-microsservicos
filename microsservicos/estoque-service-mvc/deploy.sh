#!/bin/bash
set -euo pipefail
echo "=== Building estoque-service-mvc ==="
rm -rf .aws-sam/
sam build --use-container
echo "=== Deploying estoque-service-mvc ==="
sam deploy --no-confirm-changeset
echo "=== Done ==="
sam list stack-outputs --stack-name tcc-estoque-service-mvc --output table
