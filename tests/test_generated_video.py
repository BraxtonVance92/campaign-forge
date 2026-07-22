"""Tests for the CF-03 generated-video persistence, serving route, and
honest display: an animatic is never presented as a finished render, the
narration kind is always disclosed, and the artifact survives storage
round-trips exactly."""

import hashlib

import pytest
from fastapi.testclient import TestClient

from app import repository
from app.main import app, templates
from app.models import GeneratedVideoRecord, Project, SourceAsset
from app.routes import projects as projects_routes
from app.storage import InMemoryStorage


def _make_record(project_id="p1", source_id="s1", **overrides):
    video_bytes = overrides.pop("video_bytes", b"fake-mp4-bytes-for-testing")
    base = dict(
        project_id=project_id,
        source_id=source_id,
        kind="animatic",
        narration_kind="synthetic-generic-tts",
        likeness_used=False,
        filename="test_animatic.mp4",
        size_bytes=len(video_bytes),
        checksum_sha256=hashlib.sha256(video_bytes).hexdigest(),
        duration_seconds=26.63,
        width=720,
        height=1280,
        storage_key=repository.generated_video_file_key(project_id, source_id, "test_animatic.mp4"),
        spec={"topic": "test", "shots": [{"line": 1}]},
        render_method="ffmpeg-storyboard-assembly",
    )
    base.update(overrides)
    return GeneratedVideoRecord(**base), video_bytes


def test_generated_video_round_trip():
    storage = InMemoryStorage()
    record, video_bytes = _make_record()
    repository.save_generated_video(storage, record, video_bytes)

    loaded = repository.get_generated_video_record(storage, "p1", "s1")
    assert loaded is not None
    assert loaded.kind == "animatic"
    assert loaded.narration_kind == "synthetic-generic-tts"
    assert loaded.likeness_used is False
    assert storage.get_object(loaded.storage_key) == video_bytes


def test_generated_video_none_when_absent():
    storage = InMemoryStorage()
    assert repository.get_generated_video_record(storage, "p1", "s1") is None


def test_generated_video_rejects_dishonest_kind():
    with pytest.raises(Exception):
        _make_record(kind="totally-real-final-video")


def test_generated_video_route_serves_bytes():
    storage = InMemoryStorage()
    record, video_bytes = _make_record()
    repository.save_generated_video(storage, record, video_bytes)

    app.dependency_overrides[projects_routes.get_storage] = lambda: storage
    try:
        with TestClient(app) as client:
            resp = client.get("/projects/p1/sources/s1/generated-video")
            assert resp.status_code == 200
            assert resp.content == video_bytes
            assert resp.headers["content-type"].startswith("video/mp4")
    finally:
        app.dependency_overrides.clear()


def test_generated_video_route_404_when_absent():
    storage = InMemoryStorage()
    app.dependency_overrides[projects_routes.get_storage] = lambda: storage
    try:
        with TestClient(app) as client:
            resp = client.get("/projects/p1/sources/s1/generated-video")
            assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()


def _render_with_video(generated_video):
    project = Project(name="Video Test")
    source = SourceAsset(
        project_id=project.id, consent_id="c1", original_filename="clip.mp4",
        content_type="video/mp4", size_bytes=2048, checksum_sha256="deadbeef",
        storage_key="projects/x/sources/y/original/clip.mp4",
        storage_backend="local-disk-fallback",
    )
    return templates.get_template("project.html").render(
        project=project, source=source, result=None, extended_result=None,
        generated_video=generated_video, storage_backend="in-memory-fake",
    )


def test_template_displays_animatic_with_honest_labels():
    record, _ = _make_record()
    html = _render_with_video(record)
    assert "Generated animatic" in html
    assert "not a finished video" in html
    assert "no real likeness is used" in html
    assert "generic synthetic text-to-speech voice" in html
    assert "<video" in html
    assert f"/sources/{record.source_id}/generated-video" in html


def test_template_omits_video_section_when_absent():
    html = _render_with_video(None)
    assert "Generated animatic" not in html
    assert "<video" not in html
