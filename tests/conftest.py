import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.routes import projects as projects_routes
from app.storage import InMemoryStorage


@pytest.fixture
def fake_storage() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture
def unconfigured_settings() -> Settings:
    """Mirrors this environment: no real GMI or B2 credentials present."""
    return Settings(
        gmi_api_key=None,
        b2_key_id=None,
        b2_application_key=None,
        b2_bucket_name=None,
        b2_endpoint=None,
    )


@pytest.fixture
def client(fake_storage, unconfigured_settings):
    app.dependency_overrides[projects_routes.get_storage] = lambda: fake_storage
    app.dependency_overrides[projects_routes.get_settings] = lambda: unconfigured_settings
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def make_fake_mp4_bytes(size: int = 2048) -> bytes:
    """Minimal MP4-like byte header padded to a given size. Not a playable
    video -- sufficient for testing upload validation and persistence
    logic, which do not decode video content."""
    return b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00" + b"\x00" * size
