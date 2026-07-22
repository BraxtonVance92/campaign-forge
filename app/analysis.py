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
- Base64 data-URI fallback (when no hosted HTTPS URL is available, e.g.
  B2 not configured): documented for a *different* GMI model family
  (video generation, e.g. Veo3), NOT for nemotron-3-nano-omni specifically
  -- also UNVERIFIED until exercised live. Capped at MAX_DATA_URI_BYTES
  as a conservative first-test size, never used to justify claiming this
  is a documented capability of this endpoint.
"""

from __future__ import annotations

import base64
import json as _json
from typing import Any

from pydantic import ValidationError

from app.config import Settings
from app.models import CreatorProfile, EvidenceItem, ExtendedCreatorAnalysis

GMI_CHAT_ENDPOINT = "https://api.gmi-serving.com/v1/chat/completions"
ANALYSIS_MODEL = "nvidia/nemotron-3-nano-omni"
PROMPT_SCHEMA_VERSION = "cf-run-001-v2"
EXTENDED_PROMPT_SCHEMA_VERSION = "cf-02-extended-v1"

# Conservative cap for the unverified base64-data-URI fallback path (see
# GMIAnalysisClient.analyze() below) -- GMI's own docs warn that large
# inline payloads may slow requests for a *different* model family, and
# this endpoint's request-size limit is undocumented for video input at
# all. Keep the very first real test small rather than guess a larger safe
# size.
MAX_DATA_URI_BYTES = 8 * 1024 * 1024  # 8 MB

# EXPERIMENTAL: this client is not claimed to be production-ready. Flip to
# True only after an authorized live test actually confirms the video_url
# request shape against a real GMI response -- never speculatively. This
# flag is threaded into every CreatorProfile this client produces (see
# parse_creator_profile()) so the experimental status is visible all the
# way to the display page, not just in this module's comments.
REQUEST_SHAPE_VERIFIED = False


class AnalysisBlockedError(RuntimeError):
    """Raised for any condition that prevents a real analysis result --
    missing credential, unfetchable source, network failure, HTTP error,
    malformed response shape, or contract validation failure. Callers
    (app/routes/projects.py) need only handle this one exception type;
    no other exception should ever escape GMIAnalysisClient.analyze()."""


class GMIAnalysisClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def _resolve_video_url(
        self,
        video_url: str,
        video_bytes: bytes | None,
        video_content_type: str | None,
    ) -> str:
        if video_url.startswith("https://"):
            return video_url
        # No hosted URL (B2 not configured). Per CF-01's research
        # (docs/ops/ACTIVE_WORK_PACKET.md), it is unverified but not ruled
        # out that this model's endpoint accepts a small video directly as
        # a base64 data URI -- attempt that instead of blocking outright,
        # when the caller can supply the raw bytes.
        if video_bytes is None:
            raise AnalysisBlockedError(
                "The source video is not stored behind a real, publicly "
                "fetchable HTTPS URL (local-disk-fallback storage cannot "
                "provide one), and no local bytes were supplied to attempt "
                "a direct base64 request instead. The real analysis call "
                "was not made even though GMI_API_KEY is present."
            )
        if len(video_bytes) > MAX_DATA_URI_BYTES:
            raise AnalysisBlockedError(
                f"The source video ({len(video_bytes)} bytes) exceeds the "
                f"{MAX_DATA_URI_BYTES}-byte cap for a direct base64 "
                "request, and no hosted HTTPS URL is available (B2 is not "
                "configured). The real analysis call was not made."
            )
        content_type = video_content_type or "video/mp4"
        encoded = base64.b64encode(video_bytes).decode("ascii")
        return f"data:{content_type};base64,{encoded}"

    def _post_chat_completion(self, instructions: str, resolved_video_url: str) -> dict:
        import httpx  # imported lazily; never required when analysis is blocked

        payload = {
            "model": ANALYSIS_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instructions},
                        # UNVERIFIED shape -- see module docstring.
                        {"type": "video_url", "video_url": {"url": resolved_video_url}},
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
            resp = httpx.post(GMI_CHAT_ENDPOINT, headers=headers, json=payload, timeout=180)
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
            return _json.loads(raw_content)
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            # ValueError also covers json.JSONDecodeError (a subclass).
            raise AnalysisBlockedError(
                f"GMI's response was not in the expected shape ({type(exc).__name__}). "
                "Raw provider content is not persisted or displayed."
            ) from exc

    def analyze(
        self,
        *,
        project_id: str,
        source_id: str,
        video_url: str,
        source_asset_hash: str,
        video_bytes: bytes | None = None,
        video_content_type: str | None = None,
    ) -> CreatorProfile:
        if not self._settings.gmi_configured:
            raise AnalysisBlockedError(
                "GMI_API_KEY is not configured in this environment. The real "
                "analysis call was not made."
            )
        resolved_video_url = self._resolve_video_url(video_url, video_bytes, video_content_type)
        data = self._post_chat_completion(_ANALYSIS_INSTRUCTIONS, resolved_video_url)

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

    def analyze_extended(
        self,
        *,
        project_id: str,
        source_id: str,
        video_url: str,
        source_asset_hash: str,
        video_bytes: bytes | None = None,
        video_content_type: str | None = None,
    ) -> ExtendedCreatorAnalysis:
        """Founder-directed CF-02 experiment (2026-07-22): requests the
        richer, timestamped, section-by-section analysis described in that
        instruction, rather than the narrower CreatorProfile contract.
        Persists whatever real JSON object GMI actually returns -- never a
        fabricated or partially-invented structure. Every honest failure
        mode funnels into AnalysisBlockedError exactly like analyze()."""
        if not self._settings.gmi_configured:
            raise AnalysisBlockedError(
                "GMI_API_KEY is not configured in this environment. The real "
                "analysis call was not made."
            )
        resolved_video_url = self._resolve_video_url(video_url, video_bytes, video_content_type)
        data = self._post_chat_completion(_EXTENDED_ANALYSIS_INSTRUCTIONS, resolved_video_url)

        if not isinstance(data, dict) or not data:
            raise AnalysisBlockedError(
                "GMI's response parsed as JSON but was not a non-empty object. "
                "Raw provider content is not persisted or displayed."
            )

        return ExtendedCreatorAnalysis(
            project_id=project_id,
            source_id=source_id,
            sections=data,
            analysis_provider="gmi-cloud",
            analysis_model=ANALYSIS_MODEL,
            prompt_schema_version=EXTENDED_PROMPT_SCHEMA_VERSION,
            source_asset_hash=source_asset_hash,
            request_shape_verified=REQUEST_SHAPE_VERIFIED,
        )


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

_EXTENDED_ANALYSIS_INSTRUCTIONS = (
    "Analyze this authorized creator video in depth. This is a real person's "
    "actual content -- never invent a phrase, gesture, object, emotion, or "
    "studio detail you did not actually observe. Return ONLY a JSON object "
    "with these exact top-level keys:\n\n"
    "transcript: array of {start_seconds, end_seconds, text} -- his actual "
    "wording verbatim, including filler words, contractions, and sentence "
    "fragments. Do not clean it up into polished writing.\n\n"
    "word_choice_patterns: object with favored_words_or_phrases (array of "
    "strings), sentence_openers (array of strings), transitions (array of "
    "strings), emphasis_techniques (array of strings) -- each an array of "
    "{text, timestamp_seconds, confidence: high|medium|low}.\n\n"
    "voice_and_delivery: object with speaking_speed (string description), "
    "pacing_changes (array of {timestamp_seconds, description}), tone_shifts "
    "(array of {timestamp_seconds, tone, description}), overall_delivery_style "
    "(string). Do not claim identity-level voice characteristics the audio "
    "cannot establish.\n\n"
    "body_movement: object with posture (string), gestures (array of "
    "{timestamp_seconds, gesture, paired_with_words}), eye_contact_and_gaze "
    "(string), resting_position (string). Separate clearly visible movement "
    "from uncertain interpretation using the classification field below.\n\n"
    "content_structure: object with opening_hook ({start_seconds, "
    "end_seconds, text}), main_topic (string), promise_to_viewer (string), "
    "idea_sequence (array of {timestamp_seconds, description}), "
    "call_to_action ({timestamp_seconds, text}), ending_style (string), "
    "what_makes_it_specific_to_him (string).\n\n"
    "studio_and_atmosphere: object with background_description (string), "
    "lighting (string), camera_angle_and_framing (string), wardrobe "
    "(string), audio_atmosphere (string), editing_style (string), "
    "unknown_or_undeterminable (array of strings -- list anything you "
    "cannot actually determine from this video).\n\n"
    "reproduction_specification: object with camera_placement (string), "
    "lighting_arrangement (string), studio_requirements (string), wardrobe "
    "characteristics (string), delivery_instructions (string), "
    "gesture_instructions (string), editing_rhythm (string), "
    "script_writing_rules (array of strings, based only on observed "
    "evidence), must_remain_consistent (array of strings), may_vary (array "
    "of strings).\n\n"
    "accuracy_notes: object with missed_or_uncertain (array of strings -- "
    "explicitly list anything you could not confidently observe or hear), "
    "observed_in_this_video_only (array of strings -- patterns that must "
    "not be treated as permanent traits until multiple videos confirm "
    "them).\n\n"
    "Every major finding elsewhere in the object should include a "
    "confidence value (high, medium, or low) and a classification "
    "(directly_observed, reasonable_inference, or unknown) where the "
    "schema above allows for one."
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
        request_shape_verified=REQUEST_SHAPE_VERIFIED,
    )
