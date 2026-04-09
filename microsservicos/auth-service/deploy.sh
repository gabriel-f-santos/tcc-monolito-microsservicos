#!/bin/bash
set -euo pipefail
echo "=== Building auth-service ==="
rm -rf .aws-sam/
sam build --use-container
echo "=== Deploying auth-service ==="
sam deploy --no-confirm-changeset
echo "=== Done ==="
sam list stack-outputs --stack-name tcc-auth-service --output table
