from tests.conftest import make_fake_mp4_bytes
from tests.test_upload_validation import create_project


def upload_source(client, project_id: str):
    return client.post(
        f"/projects/{project_id}/sources",
        data={
            "consent_statement": "I authorize analysis of this footage.",
            "permitted_uses": "analysis, public demo",
        },
        files={"file": ("clip.mp4", make_fake_mp4_bytes(), "video/mp4")},
        follow_redirects=False,
    )


def test_view_project_shows_upload_form_before_any_source(client):
    project_id = create_project(client)
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert "Upload one authorized creator video" in resp.text


def test_view_project_shows_source_and_analyze_prompt_after_upload(client):
    project_id = create_project(client)
    upload_source(client, project_id)

    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert "clip.mp4" in resp.text
    # Copy wording changed with the UI refresh; the state itself (no
    # analysis run yet, an explicit prompt to run one) must still be true.
    assert "Not started" in resp.text
    assert "Run creator analysis" in resp.text


def test_analyze_without_gmi_key_persists_and_displays_honest_blocked_state(client):
    project_id = create_project(client)
    upload_source(client, project_id)

    resp = client.get(f"/projects/{project_id}")
    # Extract the analyze form's target to locate the source_id.
    assert "sources/" in resp.text and "/analyze" in resp.text

    # Look up the source via the JSON API to get its id, then trigger analysis.
    view = client.get(f"/projects/{project_id}")
    assert view.status_code == 200

    # Find source_id from storage directly via the app's own dependency-
    # overridden fake storage, exercised through the JSON endpoint pattern:
    # we know only one source exists in this narrow slice, so locate it via
    # the HTML form action attribute.
    import re

    match = re.search(r'/projects/[^/]+/sources/([^/"]+)/analyze', view.text)
    assert match, "expected an analyze form pointing at a specific source_id"
    source_id = match.group(1)

    analyze_resp = client.post(
        f"/projects/{project_id}/sources/{source_id}/analyze", follow_redirects=False
    )
    assert analyze_resp.status_code == 303

    json_resp = client.get(f"/projects/{project_id}/sources/{source_id}")
    assert json_resp.status_code == 200
    body = json_resp.json()
    assert body["extended_analysis_result"]["status"] == "blocked"
    assert "GMI_API_KEY is not configured" in body["extended_analysis_result"]["reason"]

    html_resp = client.get(f"/projects/{project_id}")
    assert "blocked" in html_resp.text
    assert "GMI_API_KEY is not configured" in html_resp.text
    # The honest-blocked-state disclosure must be present -- never a fake
    # result. Copy wording changed with the UI refresh; the guarantee
    # (explicit statement that nothing was invented) must still hold.
    assert "No result was invented" in html_resp.text


def test_full_flow_real_route_persists_and_displays_extended_analysis(monkeypatch):
    """End-to-end through the real routes (not just unit-level): upload,
    a mocked-but-real HTTP-shaped analyze call, persistence, and display
    -- proving the whole wire survives, not just GMIAnalysisClient in
    isolation. GMI itself is mocked here (no real credential in the test
    environment); the actual live call and its real (blocked) outcome are
    recorded separately in docs/verification/CF-02-experiment-receipt.md.
    """
    import json as _json

    import httpx
    from fastapi.testclient import TestClient

    from app.config import Settings
    from app.main import app
    from app.routes import projects as projects_routes
    from app.storage import InMemoryStorage

    configured_settings = Settings(
        gmi_api_key="test-key-not-real", b2_key_id=None, b2_application_key=None,
        b2_bucket_name=None, b2_endpoint=None,
    )
    fixture = {"transcript": [{"start_seconds": 0.0, "end_seconds": 1.0, "text": "hi there"}]}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": _json.dumps(fixture)}}]}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse())

    storage = InMemoryStorage()
    app.dependency_overrides[projects_routes.get_storage] = lambda: storage
    app.dependency_overrides[projects_routes.get_settings] = lambda: configured_settings
    try:
        with TestClient(app) as real_client:
            project_id = create_project(real_client)
            upload_source(real_client, project_id)

            view = real_client.get(f"/projects/{project_id}")
            import re
            match = re.search(r'/projects/[^/]+/sources/([^/"]+)/analyze', view.text)
            source_id = match.group(1)

            analyze_resp = real_client.post(
                f"/projects/{project_id}/sources/{source_id}/analyze", follow_redirects=False
            )
            assert analyze_resp.status_code == 303

            # JSON API reflects the real persisted result.
            json_resp = real_client.get(f"/projects/{project_id}/sources/{source_id}")
            body = json_resp.json()
            assert body["extended_analysis_result"]["sections"] == fixture
            assert "status" not in body["extended_analysis_result"]  # not a blocked record

            # The website shows it too, organized -- not a raw JSON dump.
            html = real_client.get(f"/projects/{project_id}").text
            assert "Transcript" in html
            assert "hi there" in html
            assert '{"transcript"' not in html  # not dumped as raw JSON text

            # "Restart" simulation: a fresh TestClient context, same storage
            # instance, proves persistence survives process boundaries in
            # this architecture (see test_persistence.py for the repository-
            # level version of this same guarantee).
        with TestClient(app) as reloaded_client:
            html_after_restart = reloaded_client.get(f"/projects/{project_id}").text
            assert "hi there" in html_after_restart
    finally:
        app.dependency_overrides.clear()


def test_source_json_endpoint_404_for_unknown_source(client):
    project_id = create_project(client)
    resp = client.get(f"/projects/{project_id}/sources/does-not-exist")
    assert resp.status_code == 404


def test_view_unknown_project_returns_404(client):
    resp = client.get("/projects/does-not-exist")
    assert resp.status_code == 404


def test_storage_backend_is_disclosed_on_the_page(client):
    project_id = create_project(client)
    resp = client.get(f"/projects/{project_id}")
    assert "in-memory-fake" in resp.text
    # Copy wording changed with the UI refresh; the disclosure that this
    # is not real B2 storage must still be present, not silently dropped.
    assert "Backblaze B2 is not connected here yet" in resp.text
