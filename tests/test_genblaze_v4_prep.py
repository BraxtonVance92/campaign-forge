"""Zero-cost CF-V4 preparation tests for the Genblaze/GMI path.

These prove, entirely offline, that the pinned Genblaze SDK + GMI adapter
can express the planned V4 voice step (MiniMax voice clone with reference
audio) and the B2 sink — adapter construction and request validation only.
A guard transport makes any accidental network call fail the test, so this
can never incur provider spend or upload any material.
"""

import httpx
import pytest

from genblaze_core import Modality, Pipeline
from genblaze_gmicloud import GMICloudAudioProvider
from genblaze_gmicloud.models.audio import build_audio_registry

CLONE_MODEL = "minimax-audio-voice-clone-speech-2.6-hd"


class _NetworkGuard(httpx.BaseTransport):
    """Transport that records and refuses any real request."""

    def __init__(self):
        self.attempts = 0

    def handle_request(self, request):  # pragma: no cover - must not run
        self.attempts += 1
        raise AssertionError(
            f"zero-cost test attempted a network call: {request.method} {request.url}"
        )


def test_gmi_adapter_registry_supports_minimax_voice_clone():
    """The planned V4 voice step must be a first-class registered model,
    not an inferred capability: audio modality, with reference_audio,
    voice_id and prompt accepted parameters."""
    reg = build_audio_registry()
    spec = reg.get(CLONE_MODEL)
    assert spec is not None, f"{CLONE_MODEL} not registered in genblaze-gmicloud"
    assert spec.modality == Modality.AUDIO
    for param in ("reference_audio", "voice_id", "prompt"):
        assert param in spec.param_allowlist
    # 'voice' is documented as an alias for voice_id.
    assert spec.param_aliases.get("voice") == "voice_id"


def test_gmi_audio_provider_constructs_offline_with_guarded_client():
    """Adapter construction with an injected client must not require a real
    key value or any network traffic."""
    guard = _NetworkGuard()
    client = httpx.Client(transport=guard)
    provider = GMICloudAudioProvider(api_key="offline-test-placeholder", http_client=client)
    assert provider is not None
    assert guard.attempts == 0


def test_v4_voice_pipeline_step_builds_without_network():
    """The exact planned V4 voice step must be constructible (request
    validation happens at build time for model/params) without submitting
    anything: building a Pipeline with the clone step is free; only .run()
    would submit, and it is deliberately never called here."""
    guard = _NetworkGuard()
    client = httpx.Client(transport=guard)
    provider = GMICloudAudioProvider(api_key="offline-test-placeholder", http_client=client)
    pipeline = Pipeline("cf-v4-voice-prep-offline").step(
        provider,
        model=CLONE_MODEL,
        modality=Modality.AUDIO,
        prompt="Offline request-shape validation only. Never submitted.",
        reference_audio="placeholder://not-a-real-upload",
        voice_id="cf-v4-authorized-voice",
    )
    assert pipeline is not None
    assert guard.attempts == 0, "building a pipeline must not touch the network"


def test_b2_sink_backend_constructs_offline():
    """The B2 storage backend must construct from explicit arguments with
    preflight disabled (no bucket probe) — proving the persistence path is
    wired without needing real credentials in CI."""
    from genblaze_s3 import S3StorageBackend

    backend = S3StorageBackend.for_backblaze(
        "cf-v4-placeholder-bucket",
        key_id="offline-test-placeholder",
        app_key="offline-test-placeholder",
        preflight=False,
    )
    assert backend is not None
