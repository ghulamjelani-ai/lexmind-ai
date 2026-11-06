"""Pluggable object storage.

LocalStorage (filesystem) backs dev and tests. An S3-compatible backend (MinIO
in dev, S3 in prod) is a drop-in replacement implementing the same interface;
downloads there would use presigned URLs instead of streaming through the API.
Bytes never live in the database.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from app.core.config import get_settings


class Storage(Protocol):
    def put(self, key: str, data: bytes) -> None: ...
    def get(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...


class LocalStorage:
    def __init__(self, base_dir: str) -> None:
        self.base = Path(base_dir).resolve()
        self.base.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # Prevent path traversal: resolve and ensure it stays under base.
        p = (self.base / key).resolve()
        if not str(p).startswith(str(self.base)):
            raise ValueError("Invalid storage key")
        return p

    def put(self, key: str, data: bytes) -> None:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        p = self._path(key)
        if p.exists():
            os.remove(p)


_storage: Storage | None = None


def get_storage() -> Storage:
    global _storage
    if _storage is None:
        settings = get_settings()
        # Only "local" is implemented; S3/MinIO backend is a future swap-in.
        _storage = LocalStorage(settings.storage_local_dir)
    return _storage
