from tests.conftest import make_fake_mp4_bytes


def create_project(client, name: str = "Test Project") -> str:
    resp = client.post("/projects", data={"name": name}, follow_redirects=False)
    assert resp.status_code == 303
    location = resp.headers["location"]
    return location.rsplit("/", 1)[-1]


def test_valid_upload_succeeds(client):
    project_id = create_project(client)
    resp = client.post(
        f"/projects/{project_id}/sources",
        data={
            "consent_statement": "I authorize analysis of this footage.",
            "permitted_uses": "analysis, public demo",
        },
        files={"file": ("clip.mp4", make_fake_mp4_bytes(), "video/mp4")},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == f"/projects/{project_id}"


def test_upload_rejects_unsupported_content_type(client):
    project_id = create_project(client)
    resp = client.post(
        f"/projects/{project_id}/sources",
        data={
            "consent_statement": "I authorize analysis of this footage.",
            "permitted_uses": "analysis",
        },
        files={"file": ("clip.txt", b"not a video", "text/plain")},
    )
    assert resp.status_code == 422
    assert "Unsupported content type" in resp.json()["detail"]


def test_upload_rejects_oversized_file(client, monkeypatch):
    import app.models as models

    monkeypatch.setattr(models, "MAX_UPLOAD_BYTES", 100)
    # routes/projects.py imported MAX_UPLOAD_BYTES by value at import time,
    # so patch it there too to exercise the real check the route uses.
    import app.routes.projects as projects_routes

    monkeypatch.setattr(projects_routes, "MAX_UPLOAD_BYTES", 100)

    project_id = create_project(client)
    resp = client.post(
        f"/projects/{project_id}/sources",
        data={
            "consent_statement": "I authorize analysis of this footage.",
            "permitted_uses": "analysis",
        },
        files={"file": ("clip.mp4", make_fake_mp4_bytes(size=1000), "video/mp4")},
    )
    assert resp.status_code == 422
    assert "exceeds the maximum allowed size" in resp.json()["detail"]


def test_upload_rejects_missing_consent(client):
    project_id = create_project(client)
    resp = client.post(
        f"/projects/{project_id}/sources",
        data={"consent_statement": "   ", "permitted_uses": "analysis"},
        files={"file": ("clip.mp4", make_fake_mp4_bytes(), "video/mp4")},
    )
    assert resp.status_code == 422
    assert "Consent attestation is required" in resp.json()["detail"]


def test_upload_rejects_missing_permitted_uses(client):
    project_id = create_project(client)
    resp = client.post(
        f"/projects/{project_id}/sources",
        data={
            "consent_statement": "I authorize analysis of this footage.",
            "permitted_uses": "   ",
        },
        files={"file": ("clip.mp4", make_fake_mp4_bytes(), "video/mp4")},
    )
    assert resp.status_code == 422
    assert "permitted use must be specified" in resp.json()["detail"]


def test_upload_rejects_empty_file(client):
    project_id = create_project(client)
    resp = client.post(
        f"/projects/{project_id}/sources",
        data={
            "consent_statement": "I authorize analysis of this footage.",
            "permitted_uses": "analysis",
        },
        files={"file": ("clip.mp4", b"", "video/mp4")},
    )
    assert resp.status_code == 422
    assert "empty" in resp.json()["detail"]


def test_upload_to_nonexistent_project_returns_404(client):
    resp = client.post(
        "/projects/does-not-exist/sources",
        data={
            "consent_statement": "I authorize analysis of this footage.",
            "permitted_uses": "analysis",
        },
        files={"file": ("clip.mp4", make_fake_mp4_bytes(), "video/mp4")},
    )
    assert resp.status_code == 404
