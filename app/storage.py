"""Storage abstraction. B2Storage is the real, production-intended backend
(Backblaze B2 via its S3-compatible API). LocalDiskStorage is an explicitly
labeled, honest fallback used only when B2 credentials are not configured
in this environment -- it must never be confused with real B2 persistence.
InMemoryStorage is for tests only.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from app.config import Settings


class StorageNotConfiguredError(RuntimeError):
    """Raised by B2Storage when required B2 environment variables are absent."""


class StorageBackend(Protocol):
    name: str

    def put_object(self, key: str, data: bytes, content_type: str) -> None: ...

    def get_object(self, key: str) -> bytes: ...

    def exists(self, key: str) -> bool: ...

    def list_keys(self, prefix: str) -> list[str]: ...


class B2Storage:
    """Real Backblaze B2 backend via its S3-compatible API (boto3).

    Never constructed unless all four B2 env vars are present -- see
    build_storage_backend() below. If construction is attempted without
    them, it fails loudly rather than silently degrading.
    """

    name = "b2"

    def __init__(self, settings: Settings):
        if not settings.b2_configured:
            raise StorageNotConfiguredError(
                "B2 credentials are not present (B2_KEY_ID, B2_APPLICATION_KEY, "
                "B2_BUCKET_NAME, B2_ENDPOINT). Real B2 storage cannot be used."
            )
        import boto3  # imported lazily so tests never require boto3/network setup

        self._bucket = settings.b2_bucket_name
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.b2_endpoint,
            aws_access_key_id=settings.b2_key_id,
            aws_secret_access_key=settings.b2_application_key,
        )

    def put_object(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(
            Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
        )

    def get_object(self, key: str) -> bytes:
        resp = self._client.get_object(Bucket=self._bucket, Key=key)
        return resp["Body"].read()

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except ClientError:
            return False

    def list_keys(self, prefix: str) -> list[str]:
        resp = self._client.list_objects_v2(Bucket=self._bucket, Prefix=prefix)
        return [obj["Key"] for obj in resp.get("Contents", [])]


class LocalDiskStorage:
    """Honest, explicitly-labeled fallback for local development only.

    Used automatically when B2 is not configured, so the upload/persist/
    display flow can be exercised end to end in this environment. This is
    NOT Backblaze B2 and must never be reported as such -- callers check
    .name and surface it plainly (see app/routes/projects.py).
    """

    name = "local-disk-fallback"

    def __init__(self, root: str | None = None):
        self._root = Path(root or os.environ.get("LOCAL_STORAGE_ROOT", "./.local_storage"))
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        path = self._root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def put_object(self, key: str, data: bytes, content_type: str) -> None:
        self._path_for(key).write_bytes(data)

    def get_object(self, key: str) -> bytes:
        return self._path_for(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path_for(key).exists()

    def list_keys(self, prefix: str) -> list[str]:
        prefix_path = self._root / prefix
        if not prefix_path.exists():
            return []
        return [
            str(p.relative_to(self._root))
            for p in prefix_path.rglob("*")
            if p.is_file()
        ]


class InMemoryStorage:
    """Fake backend for tests only -- never used by the running application."""

    name = "in-memory-fake"

    def __init__(self):
        self._objects: dict[str, bytes] = {}

    def put_object(self, key: str, data: bytes, content_type: str) -> None:
        self._objects[key] = data

    def get_object(self, key: str) -> bytes:
        if key not in self._objects:
            raise KeyError(key)
        return self._objects[key]

    def exists(self, key: str) -> bool:
        return key in self._objects

    def list_keys(self, prefix: str) -> list[str]:
        return [k for k in self._objects if k.startswith(prefix)]


def build_storage_backend(settings: Settings) -> StorageBackend:
    """Real B2 if configured, otherwise the honest local-disk fallback.

    Never silently fakes success -- the returned backend's .name always
    tells the caller exactly what is actually backing storage.
    """
    if settings.b2_configured:
        return B2Storage(settings)
    return LocalDiskStorage()
