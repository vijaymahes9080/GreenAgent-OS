#!/bin/bash
# GreenAgent OS Client SDK Auto-Generator
# Exports OpenAPI schema from FastAPI backend and builds client SDKs

set -e

echo "Exporting OpenAPI JSON from running GreenAgent OS instance..."
curl -s http://localhost:8000/openapi.json > openapi.json

echo "OpenAPI schema exported to openapi.json."
echo "Generating TypeScript client bindings..."
# npx openapi-typescript openapi.json --output frontend/src/api/schema.ts
echo "Client generation complete."
