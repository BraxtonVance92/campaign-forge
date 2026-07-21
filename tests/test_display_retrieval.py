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
    assert "Not yet analyzed" in resp.text


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
    assert body["analysis_result"]["status"] == "blocked"
    assert "GMI_API_KEY is not configured" in body["analysis_result"]["reason"]

    html_resp = client.get(f"/projects/{project_id}")
    assert "blocked" in html_resp.text
    assert "GMI_API_KEY is not configured" in html_resp.text
    # The honest-blocked-state disclosure must be present -- never a fake result.
    assert "not a placeholder result" in html_resp.text


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
    assert "not real Backblaze B2" in resp.text
