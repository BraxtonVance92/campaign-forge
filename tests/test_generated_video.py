"""Tests for CF-03 generated-video persistence, versioning, serving, and
honest display: an animatic is never presented as a finished video, the
narration kind is always disclosed, saving a new version never loses a
prior one, and legacy single-record storage still loads."""

import hashlib
import json

import pytest
from fastapi.testclient import TestClient

from app import repository
from app.main import app, templates
from app.models import GeneratedVideoRecord, Project, SourceAsset
from app.routes import projects as projects_routes
from app.storage import InMemoryStorage


def _make_record(project_id="p1", source_id="s1", **overrides):
    video_bytes = overrides.pop("video_bytes", b"fake-mp4-bytes-for-testing")
    filename = overrides.pop("filename", "test_animatic.mp4")
    base = dict(
        project_id=project_id,
        source_id=source_id,
        kind="animatic",
        narration_kind="synthetic-generic-tts",
        likeness_used=False,
        filename=filename,
        size_bytes=len(video_bytes),
        checksum_sha256=hashlib.sha256(video_bytes).hexdigest(),
        duration_seconds=26.63,
        width=720,
        height=1280,
        storage_key=repository.generated_video_file_key(project_id, source_id, filename),
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


def test_saving_v2_preserves_v1():
    """Appending a second version must never overwrite or hide the first."""
    storage = InMemoryStorage()
    v1, v1_bytes = _make_record(filename="v1.mp4", video_bytes=b"v1-bytes")
    v2, v2_bytes = _make_record(filename="v2.mp4", video_bytes=b"v2-bytes-improved")
    repository.save_generated_video(storage, v1, v1_bytes)
    repository.save_generated_video(storage, v2, v2_bytes)

    records = repository.list_generated_video_records(storage, "p1", "s1")
    assert [r.id for r in records] == [v1.id, v2.id]  # oldest first, both present
    assert storage.get_object(v1.storage_key) == v1_bytes
    assert storage.get_object(v2.storage_key) == v2_bytes
    # Latest-by-default; by-id fetch works for both.
    assert repository.get_generated_video_record(storage, "p1", "s1").id == v2.id
    assert repository.get_generated_video_record(storage, "p1", "s1", v1.id).id == v1.id


def test_legacy_single_record_still_loads():
    """A record persisted under the pre-versioning single-record key (the
    real V1 animatic) must still appear in the list and survive a V2 save."""
    storage = InMemoryStorage()
    legacy, legacy_bytes = _make_record(filename="legacy.mp4", video_bytes=b"legacy-bytes")
    # Persist exactly as the old code did: bytes + single-record key.
    storage.put_object(legacy.storage_key, legacy_bytes, legacy.content_type)
    storage.put_object(
        f"projects/p1/sources/s1/generated_video.json",
        legacy.model_dump_json().encode("utf-8"),
        "application/json",
    )
    assert [r.id for r in repository.list_generated_video_records(storage, "p1", "s1")] == [legacy.id]

    v2, v2_bytes = _make_record(filename="v2.mp4", video_bytes=b"v2-bytes")
    repository.save_generated_video(storage, v2, v2_bytes)
    ids = [r.id for r in repository.list_generated_video_records(storage, "p1", "s1")]
    assert ids == [legacy.id, v2.id]


def test_generated_video_none_when_absent():
    storage = InMemoryStorage()
    assert repository.get_generated_video_record(storage, "p1", "s1") is None
    assert repository.list_generated_video_records(storage, "p1", "s1") == []


def test_generated_video_rejects_dishonest_kind():
    with pytest.raises(Exception):
        _make_record(kind="totally-real-final-video")


def test_generated_video_route_serves_latest_and_by_id():
    storage = InMemoryStorage()
    v1, v1_bytes = _make_record(filename="v1.mp4", video_bytes=b"v1-bytes")
    v2, v2_bytes = _make_record(filename="v2.mp4", video_bytes=b"v2-bytes-improved")
    repository.save_generated_video(storage, v1, v1_bytes)
    repository.save_generated_video(storage, v2, v2_bytes)

    app.dependency_overrides[projects_routes.get_storage] = lambda: storage
    try:
        with TestClient(app) as client:
            latest = client.get("/projects/p1/sources/s1/generated-video")
            assert latest.status_code == 200
            assert latest.content == v2_bytes
            by_id = client.get(f"/projects/p1/sources/s1/generated-video?video_id={v1.id}")
            assert by_id.status_code == 200
            assert by_id.content == v1_bytes
            missing = client.get("/projects/p1/sources/s1/generated-video?video_id=nope")
            assert missing.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_generated_video_route_honors_byte_ranges_for_seeking():
    """Browser <video> seeking sends Range requests; the route must answer
    206 with the exact slice, advertise Accept-Ranges, reject unsatisfiable
    starts with 416, and ignore malformed range headers (200 full body)."""
    storage = InMemoryStorage()
    record, video_bytes = _make_record(video_bytes=b"0123456789abcdef")
    repository.save_generated_video(storage, record, video_bytes)

    app.dependency_overrides[projects_routes.get_storage] = lambda: storage
    try:
        with TestClient(app) as client:
            url = "/projects/p1/sources/s1/generated-video"
            full = client.get(url)
            assert full.status_code == 200
            assert full.headers["accept-ranges"] == "bytes"

            part = client.get(url, headers={"Range": "bytes=4-7"})
            assert part.status_code == 206
            assert part.content == b"4567"
            assert part.headers["content-range"] == "bytes 4-7/16"

            open_ended = client.get(url, headers={"Range": "bytes=10-"})
            assert open_ended.status_code == 206
            assert open_ended.content == b"abcdef"

            suffix = client.get(url, headers={"Range": "bytes=-3"})
            assert suffix.status_code == 206
            assert suffix.content == b"def"

            past_end = client.get(url, headers={"Range": "bytes=99-"})
            assert past_end.status_code == 416
            assert past_end.headers["content-range"] == "bytes */16"

            malformed = client.get(url, headers={"Range": "bytes=zzz"})
            assert malformed.status_code == 200
            assert malformed.content == video_bytes
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


def _render_with_videos(generated_videos):
    project = Project(name="Video Test")
    source = SourceAsset(
        project_id=project.id, consent_id="c1", original_filename="clip.mp4",
        content_type="video/mp4", size_bytes=2048, checksum_sha256="deadbeef",
        storage_key="projects/x/sources/y/original/clip.mp4",
        storage_backend="local-disk-fallback",
    )
    return templates.get_template("project.html").render(
        project=project, source=source, result=None, extended_result=None,
        generated_videos=generated_videos, analysis_run=None,
        storage_backend="in-memory-fake",
    )


def test_template_displays_versions_side_by_side_with_honest_labels():
    v1, _ = _make_record(filename="v1.mp4")
    v2, _ = _make_record(filename="v2.mp4")
    html = _render_with_videos([v1, v2])
    assert "Generated video experiments" in html
    assert "2 VERSIONS" in html
    assert "V1" in html and "V2" in html
    assert "no real likeness is used" in html
    assert "generic synthetic text-to-speech voice" in html
    assert html.count("<video") == 2
    assert f"video_id={v1.id}" in html
    assert f"video_id={v2.id}" in html
    # Both records are animatics, so both carry the per-version animatic label.
    assert html.count("Animatic/storyboard — not a finished video.") == 2


def test_template_disclosure_is_conditioned_per_version_not_shared():
    """A preview-render version must NOT be labeled an animatic, and an
    animatic must NOT be labeled a finished-concept preview — the honest
    label is per-record, never a shared banner claiming all versions are
    storyboards."""
    v1, _ = _make_record(filename="v1.mp4")  # animatic
    v2, _ = _make_record(filename="v2.mp4")  # animatic
    v3, _ = _make_record(filename="v3.mp4", kind="preview-render",
                         render_method="pil-motion-graphics+ffmpeg-mix")
    html = _render_with_videos([v1, v2, v3])
    assert "3 VERSIONS" in html
    assert html.count("<video") == 3
    assert f"video_id={v3.id}" in html
    # Exactly two animatic labels (V1, V2) and exactly one preview label (V3).
    assert html.count("Animatic/storyboard — not a finished video.") == 2
    assert html.count("Finished-concept preview") == 1
    # The old blanket claim that every version is an unfinished animatic is gone.
    assert "These are animatics/storyboards, not finished videos" not in html
    # The always-true disclosures still apply to every version.
    assert "no real likeness is used in any of them" in html
    assert "generic synthetic text-to-speech voice" in html


def test_template_omits_video_section_when_absent():
    html = _render_with_videos([])
    assert "Generated video experiments" not in html
    assert "<video" not in html
