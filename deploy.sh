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
git fetch --tags --prune origin
git checkout "$TAG"
/srv/dochub/.local/bin/uv run manage.py migrate --noinput
/srv/dochub/.local/bin/uv run manage.py collectstatic --noinput
sudo /bin/systemctl restart dochub-gunicorn dochub-celery
echo "Deployed $TAG"
