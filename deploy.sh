#!/bin/bash
set -euo pipefail

TAG="${1#refs/tags/}"

# Validate tag name to prevent injection
if [[ ! "$TAG" =~ ^v?[0-9]+\.[0-9]+(\.[0-9]+)?(-[a-zA-Z0-9.]+)?$ ]]; then
  echo "Invalid tag format: $TAG" >&2
  exit 1
fi

# Prevent concurrent deploys
exec 200>/tmp/dochub-deploy.lock
flock -n 200 || { echo "Deploy already running, skipping" >&2; exit 1; }

cd /srv/dochub/source

PREV=$(git describe --tags HEAD 2>/dev/null || git rev-parse --short HEAD)
echo "Deploying $PREV -> $TAG"
echo

echo "[1/4] Fetching and checking out $TAG..."
git fetch --tags --prune origin
git checkout "$TAG"

echo "[2/4] Running migrations..."
/srv/dochub/.local/bin/uv run manage.py migrate --noinput

echo "[3/4] Collecting static files..."
/srv/dochub/.local/bin/uv run manage.py collectstatic --noinput

echo "[4/4] Restarting services..."
sudo /bin/systemctl restart dochub-gunicorn dochub-celery

echo
echo "Done. Deployed $TAG."
