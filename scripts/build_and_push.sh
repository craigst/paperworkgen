#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAG="${1:-paperworkgen/api:latest}"

docker build -t "$TAG" "$PROJECT_ROOT"

if [ "${SKIP_PUSH:-}" != "true" ]; then
  docker push "$TAG"
fi
