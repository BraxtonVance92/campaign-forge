"""Data contracts for the CF-RUN-001 slice.

CreatorProfile mirrors the exact contract required by
docs/canon/PRODUCT_CANON.md's "Creator profile contract" section.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_UPLOAD_BYTES = 500 * 1024 * 1024  # 500 MB
ALLOWED_CONTENT_TYPES = {"video/mp4", "video/quicktime", "video/webm"}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid.uuid4())


class ConsentRecord(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    statement: str = Field(min_length=1)
    permitted_uses: list[str] = Field(min_length=1)
    created_at: datetime = Field(default_factory=utcnow)

    @field_validator("statement")
    @classmethod
    def statement_must_be_meaningful(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("consent statement must not be blank")
        return v.strip()


class SourceAsset(BaseModel):
    id: str = Field(default_factory=new_id)
    project_id: str
    consent_id: str
    original_filename: str
    content_type: str
    size_bytes: int
    checksum_sha256: str
    storage_key: str
    storage_backend: Literal["b2", "local-disk-fallback"]
    uploaded_at: datetime = Field(default_factory=utcnow)


class EvidenceItem(BaseModel):
    source_reference: str
    observation: str


class CreatorProfile(BaseModel):
    """Mirrors docs/canon/PRODUCT_CANON.md's creator-profile contract exactly."""

    project_id: str
    source_id: str
    version: int = 1

    audience: str
    content_pillars: list[str] = Field(min_length=1)
    voice_traits: list[str] = Field(default_factory=list)
    hook_patterns: list[str] = Field(default_factory=list)
    structure_patterns: list[str] = Field(default_factory=list)
    visual_patterns: list[str] = Field(default_factory=list)
    cta_patterns: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    limitations: list[str] = Field(min_length=1)

    analysis_provider: str
    analysis_model: str
    prompt_schema_version: str
    source_asset_hash: str
    created_at: datetime = Field(default_factory=utcnow)

    # Explicit, code-level (not just comment/docstring) experimental marker.
    # False means the exact request shape used to produce this profile has
    # not been confirmed against a live provider response -- see
    # app/analysis.py's module docstring. Must be set true only by a future
    # change made *after* a live call actually confirms the request/response
    # shape; never set true speculatively.
    request_shape_verified: bool = False


class ExtendedCreatorAnalysis(BaseModel):
    """A founder-directed CF-02 experiment (2026-07-22), alongside (not
    replacing) CreatorProfile/docs/canon/PRODUCT_CANON.md's narrower
    contract. The founder asked for far more resolution than that contract
    captures -- timestamped transcript/word-choice, voice/delivery, body
    movement, content structure, studio/atmosphere, a reproduction
    specification, and per-finding confidence/classification.

    `sections` is intentionally a flexible dict rather than dozens of
    hand-typed fields: this is the FIRST real test of whether the provider
    can produce this level of detail at all, and over-constraining the
    shape before seeing a real response would risk silently dropping
    real content that didn't fit a guessed schema. Persisted and
    displayed as real data only when a real call actually parses as a
    JSON object -- never fabricated or filled with placeholder content.
    """

    project_id: str
    source_id: str
    sections: dict = Field(min_length=1)

    analysis_provider: str
    analysis_model: str
    prompt_schema_version: str
    source_asset_hash: str
    created_at: datetime = Field(default_factory=utcnow)
    request_shape_verified: bool = False


AnalysisRunState = Literal[
    "queued",
    "probing",
    "transcribing",
    "sampling_frames",
    "analyzing",
    "completed",
    "partially_completed",
    "failed",
]


class TranscriptSegment(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str


class FrameEvidence(BaseModel):
    timestamp_seconds: float
    storage_key: str
    checksum_sha256: str


class PipelineObservation(BaseModel):
    """One evidence-linked observation. `classification` distinguishes what
    the pipeline directly measured from what it inferred and from what it
    genuinely cannot determine; `evidence_type`/`evidence_ref` tie every
    claim back to a transcript segment, probe field, or extracted frame."""

    topic: str
    statement: str
    evidence_type: Literal[
        "transcript_segment", "media_probe", "frame_available_for_human_review", "derived_metric"
    ]
    evidence_ref: str
    confidence: Literal["high", "medium", "low"]
    classification: Literal["directly_observed", "inferred", "unknown"]
    limitation: str | None = None


class AnalysisRun(BaseModel):
    """A reusable in-app pipeline run (CF-04). Stored separately from the
    CF-02 ExtendedCreatorAnalysis so historical results are never
    overwritten. State is persisted after every stage transition, so a
    crash or restart leaves an honest partial state rather than a false
    'completed' or a silent loss."""

    id: str = Field(default_factory=new_id)
    project_id: str
    source_id: str
    consent_id: str
    input_checksum_sha256: str
    state: AnalysisRunState = "queued"
    stage_timestamps: dict[str, str] = Field(default_factory=dict)
    engine_info: dict[str, str] = Field(default_factory=dict)

    media_probe: dict | None = None
    transcript: list[TranscriptSegment] = Field(default_factory=list)
    frames: list[FrameEvidence] = Field(default_factory=list)
    observations: list[PipelineObservation] = Field(default_factory=list)

    errors: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class GeneratedVideoRecord(BaseModel):
    """A generated video artifact tied to a project/source. `kind` is an
    honest classification, never inflated: an animatic is not a final
    render, and `narration_kind` records whether the voice is the real
    creator, an authorized synthetic clone, or (as in CF-03's first
    experiment) a clearly generic synthetic TTS voice with no relation to
    the creator's identity."""

    id: str = Field(default_factory=new_id)
    project_id: str
    source_id: str
    kind: Literal["storyboard", "animatic", "preview-render", "final-render"]
    narration_kind: Literal[
        "none", "synthetic-generic-tts", "authorized-voice-clone", "original-recording"
    ]
    likeness_used: bool
    filename: str
    content_type: str = "video/mp4"
    size_bytes: int
    checksum_sha256: str
    duration_seconds: float
    width: int
    height: int
    storage_key: str
    spec: dict = Field(min_length=1)
    render_method: str
    created_at: datetime = Field(default_factory=utcnow)


class AnalysisBlockedRecord(BaseModel):
    """Persisted in place of a CreatorProfile when the real call could not run."""

    project_id: str
    source_id: str
    status: Literal["blocked"] = "blocked"
    reason: str
    created_at: datetime = Field(default_factory=utcnow)


class Project(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=utcnow)
