import pytest
from pydantic import ValidationError

from app.analysis import AnalysisBlockedError, GMIAnalysisClient, parse_creator_profile
from app.config import Settings

VALID_FIXTURE = {
    "audience": "solo creators building a personal brand",
    "content_pillars": ["productivity tips", "behind the scenes"],
    "voice_traits": ["direct", "encouraging"],
    "hook_patterns": ["opens with a question"],
    "structure_patterns": ["problem -> insight -> call to action"],
    "visual_patterns": ["handheld camera", "natural light"],
    "cta_patterns": ["ask viewers to comment"],
    "avoid": ["overly corporate tone"],
    "evidence": [
        {"source_reference": "00:00:03", "observation": "opens with a direct question to camera"}
    ],
    "confidence": 0.4,
    "limitations": ["based on a single example; confidence is low"],
}


def test_parse_creator_profile_accepts_valid_contract_fixture():
    profile = parse_creator_profile(
        VALID_FIXTURE,
        project_id="p1",
        source_id="s1",
        source_asset_hash="deadbeef",
    )
    assert profile.audience == VALID_FIXTURE["audience"]
    assert profile.content_pillars == VALID_FIXTURE["content_pillars"]
    assert profile.evidence[0].source_reference == "00:00:03"
    assert profile.confidence == 0.4
    assert profile.analysis_provider == "gmi-cloud"
    assert profile.project_id == "p1"
    assert profile.source_id == "s1"
    assert profile.source_asset_hash == "deadbeef"


@pytest.mark.parametrize(
    "missing_key", ["audience", "content_pillars", "confidence", "limitations"]
)
def test_parse_creator_profile_rejects_missing_required_field(missing_key):
    broken = {k: v for k, v in VALID_FIXTURE.items() if k != missing_key}
    with pytest.raises((ValidationError, KeyError)):
        parse_creator_profile(broken, project_id="p1", source_id="s1", source_asset_hash="x")


def test_parse_creator_profile_rejects_empty_evidence():
    broken = dict(VALID_FIXTURE, evidence=[])
    with pytest.raises(ValidationError):
        parse_creator_profile(broken, project_id="p1", source_id="s1", source_asset_hash="x")


def test_parse_creator_profile_rejects_confidence_out_of_range():
    broken = dict(VALID_FIXTURE, confidence=1.5)
    with pytest.raises(ValidationError):
        parse_creator_profile(broken, project_id="p1", source_id="s1", source_asset_hash="x")


def test_analyze_blocked_when_gmi_key_absent():
    settings = Settings(
        gmi_api_key=None, b2_key_id=None, b2_application_key=None,
        b2_bucket_name=None, b2_endpoint=None,
    )
    client = GMIAnalysisClient(settings)
    with pytest.raises(AnalysisBlockedError, match="GMI_API_KEY is not configured"):
        client.analyze(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


def test_analyze_blocked_when_video_not_publicly_fetchable():
    """Even with a (fake) key present, a local-disk-fallback reference isn't
    a real HTTPS URL GMI's servers could fetch -- this must block too."""
    settings = Settings(
        gmi_api_key="test-key-not-real", b2_key_id=None, b2_application_key=None,
        b2_bucket_name=None, b2_endpoint=None,
    )
    client = GMIAnalysisClient(settings)
    with pytest.raises(AnalysisBlockedError, match="publicly fetchable"):
        client.analyze(
            project_id="p1", source_id="s1",
            video_url="local-disk-fallback://projects/p1/sources/s1/original/clip.mp4",
            source_asset_hash="x",
        )


def test_analyze_success_path_with_mocked_gmi_response(monkeypatch):
    """Proves the client -> parse -> CreatorProfile path end to end using a
    mocked HTTP layer, since no real GMI_API_KEY exists in this environment.
    This is a unit test of our own code's response handling, NOT a live
    call, and must never be cited as evidence that real analysis works --
    see docs/verification/CF-VERIFY-001.md and the CF-RUN-001 receipt for
    that distinction.
    """
    import httpx

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": __import__("json").dumps(VALID_FIXTURE)}}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        assert url == "https://api.gmi-serving.com/v1/chat/completions"
        assert headers["Authorization"] == "Bearer test-key-not-real"
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    settings = Settings(
        gmi_api_key="test-key-not-real", b2_key_id=None, b2_application_key=None,
        b2_bucket_name=None, b2_endpoint=None,
    )
    client = GMIAnalysisClient(settings)
    profile = client.analyze(
        project_id="p1", source_id="s1",
        video_url="https://example-bucket.example.com/video.mp4",
        source_asset_hash="deadbeef",
    )
    assert profile.audience == VALID_FIXTURE["audience"]
    assert profile.source_asset_hash == "deadbeef"
