#!/bin/bash
set -euo pipefail
echo "=== Building catalogo-service-mvc ==="
rm -rf .aws-sam/
sam build --use-container
echo "=== Deploying catalogo-service-mvc ==="
sam deploy --no-confirm-changeset
echo "=== Done ==="
sam list stack-outputs --stack-name tcc-catalogo-service-mvc --output table
