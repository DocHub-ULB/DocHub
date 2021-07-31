import os
from typing import Optional


def get_env(secret_name: str, default: Optional[str] = None):
    """Gathers secrets and envvars from secret provider and environment"""
    if secret_name.startswith("SDC_"):
        # Get secret from a secret provider (portainer ?)
        return ""

    result = os.environ.get(secret_name)
    if result is None:
        return default
    return result
