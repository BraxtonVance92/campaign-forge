"""Tests for the presigned-URL fix: get_source_original_url() previously
joined the B2 endpoint and key into a plain URL, which would 403 for a
private object -- GMI's servers cannot authenticate against it. These
tests prove the real presigned-URL path, its expiration bounds, and the
private-object fetch design (fail loudly rather than silently returning
an unusable or unbounded-lifetime URL).
"""

import pytest

from app import repository
from app.config import Settings
from app.models import SourceAsset
from app.storage import (
    B2Storage,
    InMemoryStorage,
    LocalDiskStorage,
    MAX_PRESIGNED_URL_EXPIRES_SECONDS,
    MIN_PRESIGNED_URL_EXPIRES_SECONDS,
    PresignedUrlUnsupportedError,
)


def _b2_storage_with_fake_client(fake_client):
    settings = Settings(
        gmi_api_key=None,
        b2_key_id="fake-key-id",
        b2_application_key="fake-app-key",
        b2_bucket_name="fake-bucket",
        b2_endpoint="https://s3.example-region.backblazeb2.com",
    )
    storage = B2Storage(settings)
    storage._client = fake_client
    return storage


class _FakeBotoClient:
    def __init__(self):
        self.calls = []

    def generate_presigned_url(self, operation_name, Params, ExpiresIn):
        self.calls.append((operation_name, Params, ExpiresIn))
        return (
            f"https://s3.example-region.backblazeb2.com/{Params['Bucket']}/"
            f"{Params['Key']}?X-Amz-Expires={ExpiresIn}&X-Amz-Signature=fake"
        )


def test_b2_get_presigned_url_calls_boto3_with_correct_params():
    fake_client = _FakeBotoClient()
    storage = _b2_storage_with_fake_client(fake_client)

    url = storage.get_presigned_url("projects/p1/sources/s1/original/clip.mp4", expires_in=300)

    assert len(fake_client.calls) == 1
    operation, params, expires = fake_client.calls[0]
    assert operation == "get_object"
    assert params == {"Bucket": "fake-bucket", "Key": "projects/p1/sources/s1/original/clip.mp4"}
    assert expires == 300
    assert url.startswith("https://")
    assert "X-Amz-Expires=300" in url


def test_b2_get_presigned_url_uses_sane_default_expiration():
    fake_client = _FakeBotoClient()
    storage = _b2_storage_with_fake_client(fake_client)

    storage.get_presigned_url("some/key")

    _, _, expires = fake_client.calls[0]
    assert expires == 900  # DEFAULT_PRESIGNED_URL_EXPIRES_SECONDS
    assert 0 < expires <= MAX_PRESIGNED_URL_EXPIRES_SECONDS


@pytest.mark.parametrize("bad_expires", [0, -1, -3600, MAX_PRESIGNED_URL_EXPIRES_SECONDS + 1, 10**9])
def test_b2_get_presigned_url_rejects_out_of_bounds_expiration(bad_expires):
    storage = _b2_storage_with_fake_client(_FakeBotoClient())
    with pytest.raises(ValueError, match="expires_in must be between"):
        storage.get_presigned_url("some/key", expires_in=bad_expires)


@pytest.mark.parametrize(
    "good_expires", [MIN_PRESIGNED_URL_EXPIRES_SECONDS, 1, 900, 3600, MAX_PRESIGNED_URL_EXPIRES_SECONDS]
)
def test_b2_get_presigned_url_accepts_in_bounds_expiration(good_expires):
    fake_client = _FakeBotoClient()
    storage = _b2_storage_with_fake_client(fake_client)
    storage.get_presigned_url("some/key", expires_in=good_expires)
    assert fake_client.calls[0][2] == good_expires


def test_local_disk_storage_refuses_presigned_url(tmp_path):
    storage = LocalDiskStorage(root=str(tmp_path / "store"))
    with pytest.raises(PresignedUrlUnsupportedError, match="no HTTP presence"):
        storage.get_presigned_url("some/key")


def test_in_memory_storage_refuses_presigned_url():
    storage = InMemoryStorage()
    with pytest.raises(PresignedUrlUnsupportedError):
        storage.get_presigned_url("some/key")


def test_get_source_original_url_uses_presigned_url_for_b2_not_plain_join():
    """The core regression test for the fix: a b2-backed source must
    produce a real presigned URL through the storage backend, never a
    plain bucket/key string concatenation that would 403 against a
    private object."""
    fake_client = _FakeBotoClient()
    storage = _b2_storage_with_fake_client(fake_client)

    source = SourceAsset(
        project_id="p1",
        consent_id="c1",
        original_filename="clip.mp4",
        content_type="video/mp4",
        size_bytes=100,
        checksum_sha256="deadbeef",
        storage_key=repository.source_original_key("p1", "s1", "clip.mp4"),
        storage_backend="b2",
    )
    # Force a known source_id so the expected key is deterministic.
    source = source.model_copy(update={"id": "s1"})

    url = repository.get_source_original_url(source, storage)

    assert url.startswith("https://")
    assert "X-Amz-Signature=fake" in url
    operation, params, expires = fake_client.calls[0]
    assert params["Key"] == "projects/p1/sources/s1/original/clip.mp4"
    assert expires == 900  # sane default, not an unbounded/absent lifetime


def test_get_source_original_url_unaffected_for_local_disk_fallback():
    """Regression guard: the local-disk-fallback sentinel path must not
    change as a side effect of the presigned-URL fix."""
    storage = InMemoryStorage()  # storage.name != "b2" branch is what's under test
    storage.name = "local-disk-fallback"
    source = SourceAsset(
        project_id="p1",
        consent_id="c1",
        original_filename="clip.mp4",
        content_type="video/mp4",
        size_bytes=100,
        checksum_sha256="deadbeef",
        storage_key="projects/p1/sources/s1/original/clip.mp4",
        storage_backend="local-disk-fallback",
    )
    url = repository.get_source_original_url(source, storage)
    assert url == "local-disk-fallback://projects/p1/sources/s1/original/clip.mp4"
