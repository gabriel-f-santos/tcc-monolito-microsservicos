#!/bin/bash
set -euo pipefail
echo "=== Building catalogo-service ==="
rm -rf .aws-sam/
sam build --use-container
echo "=== Deploying catalogo-service ==="
sam deploy --no-confirm-changeset
echo "=== Done ==="
sam list stack-outputs --stack-name tcc-catalogo-service --output table
