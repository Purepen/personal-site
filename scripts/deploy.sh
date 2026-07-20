#!/usr/bin/env bash
# Build and deploy the personal site to fly.io: create the app on first run,
# then deploy. No secrets to stage - it's a static site with no env vars.
set -euo pipefail

APP="micheal"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

command -v flyctl >/dev/null || { echo "flyctl not found - install it first"; exit 1; }
flyctl auth whoami >/dev/null || { echo "Not logged in - run 'fly auth login'"; exit 1; }

# 1. Create the app on first run (name must be globally unique).
flyctl status -a "$APP" >/dev/null 2>&1 || { echo "Creating $APP..."; flyctl apps create "$APP"; }

# 2. Deploy (build context = this folder).
flyctl deploy --config scripts/fly.toml --dockerfile Dockerfile -a "$APP" --ha=false

echo "Deployed: https://${APP}.fly.dev"
