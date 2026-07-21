from app.config import Settings
from app.storage import B2Storage


def _b2_storage_with_fake_client(fake_client):
    settings = Settings(
        gmi_api_key=None,
        b2_key_id="fake-key-id",
        b2_application_key="fake-app-key",
        b2_bucket_name="fake-bucket",
        b2_endpoint="https://s3.example-region.backblazeb2.com",
    )
    storage = B2Storage(settings)
    storage._client = fake_client  # swap in the fake after real (safe) construction
    return storage


def test_b2_list_keys_paginates_across_multiple_pages():
    """list_objects_v2 caps a single page at 1000 keys; this proves
    B2Storage.list_keys aggregates every page rather than silently
    truncating results."""

    class FakePaginator:
        def paginate(self, Bucket, Prefix):
            assert Bucket == "fake-bucket"
            assert Prefix == "projects/p1/"
            yield {"Contents": [{"Key": f"projects/p1/key{i}"} for i in range(1000)]}
            yield {"Contents": [{"Key": f"projects/p1/key{i}"} for i in range(1000, 1500)]}
            yield {"Contents": []}  # a trailing empty page must not break anything

    class FakeClient:
        def get_paginator(self, operation_name):
            assert operation_name == "list_objects_v2"
            return FakePaginator()

    storage = _b2_storage_with_fake_client(FakeClient())
    keys = storage.list_keys("projects/p1/")

    assert len(keys) == 1500
    assert "projects/p1/key0" in keys
    assert "projects/p1/key999" in keys
    assert "projects/p1/key1499" in keys


def test_b2_list_keys_handles_single_page_with_no_contents():
    class FakePaginator:
        def paginate(self, Bucket, Prefix):
            yield {}  # no "Contents" key at all -- e.g. an empty prefix

    class FakeClient:
        def get_paginator(self, operation_name):
            return FakePaginator()

    storage = _b2_storage_with_fake_client(FakeClient())
    assert storage.list_keys("projects/nonexistent/") == []
