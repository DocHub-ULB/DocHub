# Auto-deploy

Pushing a tag triggers an automatic deploy. Tests must pass first.

## Flow

```
Tag push
  → python-tests.yml runs
    → deploy.yml triggers (on workflow_run success)
      → POSTs HMAC-signed payload to https://dochub.be/webhook/dochub-deploy
        → server validates signature, runs deploy.sh
          → output returned to GitHub Action logs
```

## How to deploy

Push a tag matching the `YYYY.M.N` format:

```bash
git tag 2026.4.0 && git push origin 2026.4.0
```

Check the **Actions** tab for deploy output, or on the server:

```bash
journalctl -fu dochub-webhook
```

## What `deploy.sh` does

1. Validates the tag format
2. Acquires a file lock (prevents concurrent deploys)
3. `git fetch --tags --prune origin && git checkout $TAG`
4. `uv run --frozen manage.py migrate --noinput`
5. `uv run --frozen manage.py collectstatic --noinput`
6. `sudo systemctl restart dochub-gunicorn dochub-celery`

If any step fails, `set -e` stops the script before restarting services, so the old code keeps running.

`--frozen` is mandatory: without it, `uv run` rewrites `uv.lock`'s dynamic `exclude-newer` timestamp on every invocation, leaving a dirty working tree that breaks the next
deploy's `git checkout`. The `dochub-gunicorn` and `dochub-celery` systemd units pass `--frozen` for the same reason.

## GitHub secret

`DEPLOY_WEBHOOK_SECRET` (repo Settings > Secrets and variables > Actions) must match the secret in `/etc/webhook/hooks.json` on the server.

## Server-side components

These files live on the server only (not in git):

| File | Purpose |
|------|---------|
| `/srv/dochub/deploy.sh` | Thin wrapper that `exec`s the repo's `deploy.sh` |
| `/etc/webhook/hooks.json` | Webhook config: HMAC validation, ref check, runs as `dochub` |
| `/etc/systemd/system/dochub-webhook.service` | Runs `webhook` on `127.0.0.1:9000` |
| `/etc/caddy/Caddyfile` | Proxies `/webhook/*` to the webhook service |
| `/etc/sudoers.d/dochub-deploy` | Allows `dochub` to restart services without password |

## Appendix: server-side file contents

### `/srv/dochub/deploy.sh`

```bash
#!/bin/bash
# Thin wrapper — real logic lives in /srv/dochub/source/deploy.sh (versioned in git)
exec /srv/dochub/source/deploy.sh "$@"
```

### `/etc/webhook/hooks.json`

```json
[
  {
    "id": "dochub-deploy",
    "execute-command": "/srv/dochub/deploy.sh",
    "command-working-directory": "/srv/dochub",
    "include-command-output-in-response": true,
    "trigger-rule": {
      "and": [
        {
          "match": {
            "type": "payload-hmac-sha256",
            "secret": "<DEPLOY_WEBHOOK_SECRET>",
            "parameter": {
              "source": "header",
              "name": "X-Hub-Signature-256"
            }
          }
        },
        {
          "match": {
            "type": "regex",
            "regex": "^refs/tags/",
            "parameter": {
              "source": "payload",
              "name": "ref"
            }
          }
        }
      ]
    },
    "pass-arguments-to-command": [
      {
        "source": "payload",
        "name": "ref"
      }
    ]
  }
]
```

### `/etc/systemd/system/dochub-webhook.service`

```ini
[Unit]
Description=DocHub deploy webhook
After=network.target

[Service]
ExecStart=/usr/bin/webhook -hooks /etc/webhook/hooks.json -ip 127.0.0.1 -port 9000
User=dochub
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### `/etc/caddy/Caddyfile` (relevant block)

```
handle_path /webhook/* {
    rewrite * /hooks{uri}
    reverse_proxy localhost:9000
}
```

### `/etc/sudoers.d/dochub-deploy`

```
dochub ALL=(root) NOPASSWD: /bin/systemctl restart dochub-gunicorn dochub-celery
```
