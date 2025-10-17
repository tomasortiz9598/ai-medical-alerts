"""Thin wrapper around the BAML Python SDK."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from baml import Client


_client_cache = {}


def get_client(project_root: Path) -> Client:
    """Return a cached BAML client for the provided project root."""

    key = project_root.resolve()
    if key not in _client_cache:
        _client_cache[key] = Client(project_root=str(key))
    return _client_cache[key]
