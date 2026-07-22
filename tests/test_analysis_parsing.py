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


def test_parse_creator_profile_marks_result_shape_unverified():
    """The experimental marker (app.analysis.REQUEST_SHAPE_VERIFIED) must be
    threaded onto every produced CreatorProfile, not just left as a code
    comment, so the display layer can warn on it. See also
    app/templates/project.html's EXPERIMENTAL badge."""
    import app.analysis as analysis_module

    profile = parse_creator_profile(
        VALID_FIXTURE, project_id="p1", source_id="s1", source_asset_hash="x"
    )
    assert profile.request_shape_verified == analysis_module.REQUEST_SHAPE_VERIFIED
    assert profile.request_shape_verified is False, (
        "must stay False until an authorized live test actually confirms the "
        "video_url request shape -- never set speculatively"
    )


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


def _client_with_key():
    settings = Settings(
        gmi_api_key="test-key-not-real", b2_key_id=None, b2_application_key=None,
        b2_bucket_name=None, b2_endpoint=None,
    )
    return GMIAnalysisClient(settings)


def test_analyze_blocked_on_http_error_status(monkeypatch):
    """A GMI 5xx/4xx must become an honest AnalysisBlockedError, never an
    unhandled exception -- and must never include the raw response body."""
    import httpx

    class FakeErrorResponse:
        status_code = 503

        def raise_for_status(self):
            raise httpx.HTTPStatusError(
                "Service Unavailable", request=None, response=self
            )

        def json(self):
            raise AssertionError("json() should not be called after raise_for_status fails")

    def fake_post(url, headers=None, json=None, timeout=None):
        return FakeErrorResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(AnalysisBlockedError, match="HTTP 503") as exc_info:
        _client_with_key().analyze(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )
    assert "secret_super_sensitive_body_content" not in str(exc_info.value)


def test_analyze_blocked_on_network_error(monkeypatch):
    """A connection failure must become an honest AnalysisBlockedError, not
    an unhandled httpx.RequestError propagating as a 500."""
    import httpx

    def fake_post(url, headers=None, json=None, timeout=None):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(AnalysisBlockedError, match="Network error contacting GMI"):
        _client_with_key().analyze(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


def test_analyze_blocked_on_malformed_json_content(monkeypatch):
    """If GMI's message content isn't valid JSON, block honestly instead of
    letting json.JSONDecodeError propagate unhandled."""
    import httpx

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "not valid json {{{"}}]}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse())

    with pytest.raises(AnalysisBlockedError, match="not in the expected shape"):
        _client_with_key().analyze(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


def test_analyze_blocked_on_missing_choices_key(monkeypatch):
    """A response shape without the expected 'choices' key must block
    honestly instead of raising an unhandled KeyError."""
    import httpx

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"unexpected": "shape"}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse())

    with pytest.raises(AnalysisBlockedError, match="not in the expected shape"):
        _client_with_key().analyze(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


def test_analyze_blocked_on_contract_validation_failure(monkeypatch):
    """A syntactically valid JSON response that fails a real pydantic
    constraint (confidence out of the documented 0-1 range) must block
    honestly instead of raising an unhandled ValidationError. This is
    distinct from a missing directly-indexed key, which raises KeyError
    -- see test_analyze_blocked_on_missing_required_field below."""
    import httpx

    broken_fixture = dict(VALID_FIXTURE, confidence=5.0)

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": __import__("json").dumps(broken_fixture)}}]}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse())

    with pytest.raises(AnalysisBlockedError, match="failed contract validation"):
        _client_with_key().analyze(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


def test_analyze_attempts_base64_fallback_when_bytes_supplied(monkeypatch):
    """When no hosted HTTPS URL is available but the caller supplies raw
    bytes (e.g. local-disk-fallback storage), analyze() must attempt a
    base64 data-URI request instead of blocking outright -- see CF-01's
    research in docs/ops/ACTIVE_WORK_PACKET.md. This proves the request
    is actually built with the data: URI, not that GMI accepts it (that
    remains unverified until a real live call is made)."""
    import base64 as _base64
    import httpx

    sent = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": __import__("json").dumps(VALID_FIXTURE)}}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        sent["payload"] = json
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    video_bytes = b"fake-small-video-bytes"
    profile = _client_with_key().analyze(
        project_id="p1", source_id="s1",
        video_url="local-disk-fallback://projects/p1/sources/s1/original/clip.mp4",
        source_asset_hash="x",
        video_bytes=video_bytes,
        video_content_type="video/mp4",
    )
    assert profile.audience == VALID_FIXTURE["audience"]
    sent_url = sent["payload"]["messages"][0]["content"][1]["video_url"]["url"]
    assert sent_url.startswith("data:video/mp4;base64,")
    assert _base64.b64encode(video_bytes).decode("ascii") in sent_url


def test_analyze_blocked_when_bytes_exceed_data_uri_cap():
    """A video too large for the conservative base64 fallback cap must
    block honestly rather than send an oversized, unverified request."""
    import app.analysis as analysis_module

    oversized = b"x" * (analysis_module.MAX_DATA_URI_BYTES + 1)
    with pytest.raises(AnalysisBlockedError, match="exceeds the"):
        _client_with_key().analyze(
            project_id="p1", source_id="s1",
            video_url="local-disk-fallback://projects/p1/sources/s1/original/clip.mp4",
            source_asset_hash="x",
            video_bytes=oversized,
            video_content_type="video/mp4",
        )


def test_analyze_blocked_on_network_timeout(monkeypatch):
    """httpx.TimeoutException is a subclass of httpx.RequestError -- must
    surface as the same honest AnalysisBlockedError, not an unhandled
    exception or a hang."""
    import httpx

    def fake_post(url, headers=None, json=None, timeout=None):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(AnalysisBlockedError, match="Network error contacting GMI"):
        _client_with_key().analyze(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


# --- analyze_extended(): the CF-02 founder-directed rich analysis path ---


def _extended_client_with_key():
    settings = Settings(
        gmi_api_key="test-key-not-real", b2_key_id=None, b2_application_key=None,
        b2_bucket_name=None, b2_endpoint=None,
    )
    return GMIAnalysisClient(settings)


EXTENDED_FIXTURE = {
    "transcript": [{"start_seconds": 0.0, "end_seconds": 2.0, "text": "hey what's up"}],
    "voice_and_delivery": {"speaking_speed": "fast"},
}


def test_analyze_extended_blocked_when_gmi_key_absent():
    settings = Settings(
        gmi_api_key=None, b2_key_id=None, b2_application_key=None,
        b2_bucket_name=None, b2_endpoint=None,
    )
    with pytest.raises(AnalysisBlockedError, match="GMI_API_KEY is not configured"):
        GMIAnalysisClient(settings).analyze_extended(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


def test_analyze_extended_blocked_when_no_url_and_no_bytes():
    with pytest.raises(AnalysisBlockedError, match="no local bytes were supplied"):
        _extended_client_with_key().analyze_extended(
            project_id="p1", source_id="s1",
            video_url="local-disk-fallback://projects/p1/sources/s1/original/clip.mp4",
            source_asset_hash="x",
        )


def test_analyze_extended_blocked_when_bytes_exceed_data_uri_cap():
    import app.analysis as analysis_module

    oversized = b"x" * (analysis_module.MAX_DATA_URI_BYTES + 1)
    with pytest.raises(AnalysisBlockedError, match="exceeds the"):
        _extended_client_with_key().analyze_extended(
            project_id="p1", source_id="s1",
            video_url="local-disk-fallback://projects/p1/sources/s1/original/clip.mp4",
            source_asset_hash="x",
            video_bytes=oversized,
            video_content_type="video/mp4",
        )


def test_analyze_extended_success_path_with_mocked_gmi_response(monkeypatch):
    """Proves the extended client -> ExtendedCreatorAnalysis path end to
    end using a mocked HTTP layer. NOT a live call -- see
    docs/verification/CF-02-experiment-receipt.md for the real, live
    result (blocked: model not deployed on this account)."""
    import base64 as _base64
    import httpx

    sent = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": __import__("json").dumps(EXTENDED_FIXTURE)}}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        sent["payload"] = json
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    video_bytes = b"fake-small-video-bytes"
    result = _extended_client_with_key().analyze_extended(
        project_id="p1", source_id="s1",
        video_url="local-disk-fallback://projects/p1/sources/s1/original/clip.mp4",
        source_asset_hash="deadbeef",
        video_bytes=video_bytes,
        video_content_type="video/mp4",
    )
    assert result.sections == EXTENDED_FIXTURE
    assert result.source_asset_hash == "deadbeef"
    assert result.request_shape_verified is False
    sent_url = sent["payload"]["messages"][0]["content"][1]["video_url"]["url"]
    assert sent_url.startswith("data:video/mp4;base64,")
    assert _base64.b64encode(video_bytes).decode("ascii") in sent_url


def test_analyze_extended_blocked_on_http_error_status(monkeypatch):
    import httpx

    class FakeErrorResponse:
        status_code = 404

        def raise_for_status(self):
            raise httpx.HTTPStatusError("Not Found", request=None, response=self)

        def json(self):
            raise AssertionError("json() should not be called after raise_for_status fails")

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeErrorResponse())

    with pytest.raises(AnalysisBlockedError, match="HTTP 404") as exc_info:
        _extended_client_with_key().analyze_extended(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )
    assert "target server" not in str(exc_info.value)  # raw provider body never surfaces


def test_analyze_extended_blocked_on_network_error(monkeypatch):
    import httpx

    monkeypatch.setattr(httpx, "post", lambda *a, **k: (_ for _ in ()).throw(httpx.ConnectError("refused")))

    with pytest.raises(AnalysisBlockedError, match="Network error contacting GMI"):
        _extended_client_with_key().analyze_extended(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


def test_analyze_extended_blocked_on_malformed_json_content(monkeypatch):
    import httpx

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "not valid json {{{"}}]}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse())

    with pytest.raises(AnalysisBlockedError, match="not in the expected shape"):
        _extended_client_with_key().analyze_extended(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )


def test_analyze_extended_blocked_on_non_dict_response():
    """A response that parses as valid JSON but isn't an object (e.g. a
    bare list or string) must block honestly, not be persisted as if it
    were real structured sections."""
    import httpx

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "[1, 2, 3]"}}]}

    def fake_post(url, headers=None, json=None, timeout=None):
        return FakeResponse()

    import unittest.mock
    with unittest.mock.patch.object(httpx, "post", fake_post):
        with pytest.raises(AnalysisBlockedError, match="not a non-empty object"):
            _extended_client_with_key().analyze_extended(
                project_id="p1", source_id="s1",
                video_url="https://example-bucket.example.com/video.mp4",
                source_asset_hash="x",
            )


def test_analyze_extended_blocked_on_empty_dict_response():
    import httpx

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "{}"}}]}

    import unittest.mock
    with unittest.mock.patch.object(httpx, "post", lambda *a, **k: FakeResponse()):
        with pytest.raises(AnalysisBlockedError, match="not a non-empty object"):
            _extended_client_with_key().analyze_extended(
                project_id="p1", source_id="s1",
                video_url="https://example-bucket.example.com/video.mp4",
                source_asset_hash="x",
            )


def test_analyze_blocked_on_missing_required_field(monkeypatch):
    """A response missing a directly-indexed required field (e.g.
    'audience') raises KeyError inside parse_creator_profile, not
    pydantic.ValidationError -- analyze() must catch this too, not just
    ValidationError, or it escapes as an unhandled 500. Found by this
    test during review; app/analysis.py's except clause was widened to
    (ValidationError, KeyError, TypeError) as a result."""
    import httpx

    broken_fixture = {k: v for k, v in VALID_FIXTURE.items() if k != "audience"}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": __import__("json").dumps(broken_fixture)}}]}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResponse())

    with pytest.raises(AnalysisBlockedError, match="missing a required field"):
        _client_with_key().analyze(
            project_id="p1", source_id="s1",
            video_url="https://example-bucket.example.com/video.mp4",
            source_asset_hash="x",
        )
