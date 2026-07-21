"""Real creator-video analysis via GMI Cloud, gated behind GMI_API_KEY.

parse_creator_profile() is the tested, real unit: it validates a raw
analysis response against docs/canon/PRODUCT_CANON.md's exact contract.
GMIAnalysisClient.analyze() is implemented for production use but its
live HTTP call is not exercised in this environment -- see
AnalysisBlockedError conditions below. No fixture or canned response is
ever substituted for a real result; if analysis cannot really run, the
caller persists an AnalysisBlockedRecord, never a fake CreatorProfile.
"""

from __future__ import annotations

from typing import Any

from app.config import Settings
from app.models import CreatorProfile, EvidenceItem

GMI_CHAT_ENDPOINT = "https://api.gmi-serving.com/v1/chat/completions"
ANALYSIS_MODEL = "gemini-omni-flash-preview"  # per GMI's video-capable quickstart list
PROMPT_SCHEMA_VERSION = "cf-run-001-v1"


class AnalysisBlockedError(RuntimeError):
    """Raised when a real analysis call cannot be made, with the exact reason."""


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

        prompt = _build_analysis_prompt(video_url)
        headers = {
            "Authorization": f"Bearer {self._settings.gmi_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": ANALYSIS_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        resp = httpx.post(GMI_CHAT_ENDPOINT, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        import json as _json

        data = _json.loads(raw)
        return parse_creator_profile(
            data,
            project_id=project_id,
            source_id=source_id,
            source_asset_hash=source_asset_hash,
        )


def _build_analysis_prompt(video_url: str) -> str:
    return (
        "Analyze the authorized creator video at the following URL and return "
        "ONLY a JSON object with these exact keys: audience (string), "
        "content_pillars (array of strings), voice_traits (array of strings), "
        "hook_patterns (array of strings), structure_patterns (array of "
        "strings), visual_patterns (array of strings), cta_patterns (array of "
        "strings), avoid (array of strings), evidence (array of objects with "
        "source_reference and observation string fields), confidence (0-1 "
        "float), limitations (array of strings). Video: " + video_url
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
