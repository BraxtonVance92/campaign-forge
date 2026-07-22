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
