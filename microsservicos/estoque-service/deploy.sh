#!/bin/bash
set -euo pipefail

echo "=== Building estoque-service ==="
rm -rf .aws-sam/
sam build --use-container

echo "=== Deploying estoque-service ==="
sam deploy --no-confirm-changeset

echo "=== Done ==="
sam list stack-outputs --stack-name tcc-estoque-service --output table
