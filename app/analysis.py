"""Real creator-video analysis via GMI Cloud, gated behind GMI_API_KEY.

parse_creator_profile() is the tested, real unit: it validates a raw
analysis response against docs/canon/PRODUCT_CANON.md's exact contract.

GMIAnalysisClient.analyze() is implemented for production use, but is
NOT claimed to be production-ready -- see the verification notes below.
No fixture or canned response is ever substituted for a real result; if
analysis cannot really run or the provider's response is unusable for
any reason, the caller persists an AnalysisBlockedRecord, never a fake
CreatorProfile, and this module guarantees that every failure mode
(auth, network, malformed response, contract mismatch) surfaces as
AnalysisBlockedError -- never an unhandled exception -- and never
includes the raw provider response body or any secret in its message.

VERIFICATION STATUS (accessed 2026-07-21, re-checked after review):
- Endpoint https://api.gmi-serving.com/v1/chat/completions -- VERIFIED,
  directly quoted from
  https://docs.gmicloud.ai/model-quickstarts/text/nvidia-nvidia-nemotron-3-nano-omni.md
- Model id "nvidia/nemotron-3-nano-omni" -- VERIFIED, directly quoted
  from the same page.
- An EARLIER version of this file used "gemini-omni-flash-preview" and
  implied it was a GMI chat/vision model. That was WRONG: it is a video
  GENERATION model (prompt + optional reference image -> new video)
  invoked through GMI's separate request-queue endpoint
  (console.gmicloud.ai), not a video-understanding model at all. This
  was caught in review, not by this module's own tests, and is recorded
  here so it is not repeated.
- The exact JSON shape for passing VIDEO (as opposed to image) input to
  nemotron-3-nano-omni is NOT documented on the page fetched -- only a
  text-chat example and an image_url multimodal example are shown, with
  video support described only in prose ("understanding ... across
  text, images, video, and audio"). The `video_url` content-block type
  used below follows the documented `image_url` pattern as the closest
  verified analogue, but this specific shape is UNVERIFIED and has not
  been exercised against a live response. Do not describe this client
  as production-ready until a live call has actually been made and its
  real response shape confirmed.
"""

from __future__ import annotations

import json as _json
from typing import Any

from pydantic import ValidationError

from app.config import Settings
from app.models import CreatorProfile, EvidenceItem

GMI_CHAT_ENDPOINT = "https://api.gmi-serving.com/v1/chat/completions"
ANALYSIS_MODEL = "nvidia/nemotron-3-nano-omni"
PROMPT_SCHEMA_VERSION = "cf-run-001-v2"


class AnalysisBlockedError(RuntimeError):
    """Raised for any condition that prevents a real analysis result --
    missing credential, unfetchable source, network failure, HTTP error,
    malformed response shape, or contract validation failure. Callers
    (app/routes/projects.py) need only handle this one exception type;
    no other exception should ever escape GMIAnalysisClient.analyze()."""


class GMIAnalysisClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def analyze(
        self, *, project_id: str, source_id: str, video_url: str, source_asset_hash: str
    ) -> CreatorProfile:
        if not self._settings.gmi_configured:
            raise AnalysisBlockedError(
                "GMI_API_KEY is not configured in this environment. The real "
                "analysis call was not made."
            )
        if not video_url.startswith("https://"):
            raise AnalysisBlockedError(
                "The source video is not stored behind a real, publicly "
                "fetchable HTTPS URL (local-disk-fallback storage cannot "
                "provide one). GMI's servers cannot fetch it, so the real "
                "analysis call was not made even though GMI_API_KEY is present."
            )

        import httpx  # imported lazily; never required when analysis is blocked

        payload = {
            "model": ANALYSIS_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _ANALYSIS_INSTRUCTIONS},
                        # UNVERIFIED shape -- see module docstring.
                        {"type": "video_url", "video_url": {"url": video_url}},
                    ],
                }
            ],
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self._settings.gmi_api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = httpx.post(GMI_CHAT_ENDPOINT, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AnalysisBlockedError(
                f"GMI returned HTTP {exc.response.status_code}. The real analysis "
                "call did not produce a usable result. Raw response body is not "
                "persisted or displayed."
            ) from exc
        except httpx.RequestError as exc:
            raise AnalysisBlockedError(
                f"Network error contacting GMI ({type(exc).__name__}). The real "
                "analysis call did not complete."
            ) from exc

        try:
            body = resp.json()
            raw_content = body["choices"][0]["message"]["content"]
            data = _json.loads(raw_content)
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            # ValueError also covers json.JSONDecodeError (a subclass).
            raise AnalysisBlockedError(
                f"GMI's response was not in the expected shape ({type(exc).__name__}). "
                "Raw provider content is not persisted or displayed."
            ) from exc

        try:
            return parse_creator_profile(
                data,
                project_id=project_id,
                source_id=source_id,
                source_asset_hash=source_asset_hash,
            )
        except ValidationError as exc:
            raise AnalysisBlockedError(
                f"GMI's analysis response failed contract validation "
                f"({len(exc.errors())} field error(s)). Raw provider content is "
                "not persisted or displayed."
            ) from exc
        except (KeyError, TypeError) as exc:
            # parse_creator_profile accesses some required fields via direct
            # dict indexing (data["audience"], etc.), which raises KeyError
            # -- not pydantic.ValidationError -- when they're absent. Both
            # must block honestly rather than escape as an unhandled 500.
            raise AnalysisBlockedError(
                f"GMI's analysis response is missing a required field "
                f"({type(exc).__name__}: {exc}). Raw provider content is not "
                "persisted or displayed."
            ) from exc


_ANALYSIS_INSTRUCTIONS = (
    "Analyze the authorized creator video provided and return ONLY a JSON "
    "object with these exact keys: audience (string), content_pillars "
    "(array of strings), voice_traits (array of strings), hook_patterns "
    "(array of strings), structure_patterns (array of strings), "
    "visual_patterns (array of strings), cta_patterns (array of strings), "
    "avoid (array of strings), evidence (array of objects with "
    "source_reference and observation string fields), confidence (0-1 "
    "float), limitations (array of strings)."
)


def parse_creator_profile(
    data: dict[str, Any],
    *,
    project_id: str,
    source_id: str,
    source_asset_hash: str,
) -> CreatorProfile:
    """Validate a raw analysis response against the exact contract required by
    docs/canon/PRODUCT_CANON.md. Raises pydantic.ValidationError on any
    missing/malformed required field -- callers must not catch this to
    fabricate a partial or fake result.
    """
    evidence = [
        item if isinstance(item, EvidenceItem) else EvidenceItem(**item)
        for item in data.get("evidence", [])
    ]
    return CreatorProfile(
        project_id=project_id,
        source_id=source_id,
        audience=data["audience"],
        content_pillars=data["content_pillars"],
        voice_traits=data.get("voice_traits", []),
        hook_patterns=data.get("hook_patterns", []),
        structure_patterns=data.get("structure_patterns", []),
        visual_patterns=data.get("visual_patterns", []),
        cta_patterns=data.get("cta_patterns", []),
        avoid=data.get("avoid", []),
        evidence=evidence,
        confidence=data["confidence"],
        limitations=data["limitations"],
        analysis_provider="gmi-cloud",
        analysis_model=ANALYSIS_MODEL,
        prompt_schema_version=PROMPT_SCHEMA_VERSION,
        source_asset_hash=source_asset_hash,
    )
