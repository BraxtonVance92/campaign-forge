"""Persistence functions over a StorageBackend, using the object layout
recommended in docs/canon/PRODUCT_CANON.md. No database is used for this
narrow slice -- project/source/analysis metadata are small JSON objects
stored alongside the binary source, which keeps the architecture simple
(a database can be introduced later without changing this interface).
"""

from __future__ import annotations

import json

from app.models import (
    AnalysisBlockedRecord,
    ConsentRecord,
    CreatorProfile,
    ExtendedCreatorAnalysis,
    GeneratedVideoRecord,
    Project,
    SourceAsset,
)
from app.storage import DEFAULT_PRESIGNED_URL_EXPIRES_SECONDS, StorageBackend


def _project_key(project_id: str) -> str:
    return f"projects/{project_id}/project.json"


def _consent_key(project_id: str, consent_id: str) -> str:
    return f"projects/{project_id}/consent/{consent_id}.json"


def _source_key(project_id: str, source_id: str) -> str:
    return f"projects/{project_id}/sources/{source_id}/metadata.json"


def source_original_key(project_id: str, source_id: str, filename: str) -> str:
    return f"projects/{project_id}/sources/{source_id}/original/{filename}"


def _profile_key(project_id: str, source_id: str) -> str:
    return f"projects/{project_id}/sources/{source_id}/profile.json"


def _extended_analysis_key(project_id: str, source_id: str) -> str:
    return f"projects/{project_id}/sources/{source_id}/extended_analysis.json"


def _generated_video_record_key(project_id: str, source_id: str) -> str:
    # Legacy single-record key (first CF-03 animatic); superseded by the
    # list key below but still read for migration so V1 is never lost.
    return f"projects/{project_id}/sources/{source_id}/generated_video.json"


def _generated_videos_list_key(project_id: str, source_id: str) -> str:
    return f"projects/{project_id}/sources/{source_id}/generated_videos.json"


def generated_video_file_key(project_id: str, source_id: str, filename: str) -> str:
    return f"projects/{project_id}/sources/{source_id}/generated/{filename}"


def save_project(storage: StorageBackend, project: Project) -> None:
    storage.put_object(
        _project_key(project.id),
        project.model_dump_json().encode("utf-8"),
        "application/json",
    )


def get_project(storage: StorageBackend, project_id: str) -> Project | None:
    key = _project_key(project_id)
    if not storage.exists(key):
        return None
    return Project.model_validate_json(storage.get_object(key))


def save_consent(storage: StorageBackend, consent: ConsentRecord) -> None:
    storage.put_object(
        _consent_key(consent.project_id, consent.id),
        consent.model_dump_json().encode("utf-8"),
        "application/json",
    )


def save_source(
    storage: StorageBackend, source: SourceAsset, original_bytes: bytes
) -> None:
    original_key = source_original_key(
        source.project_id, source.id, source.original_filename
    )
    storage.put_object(original_key, original_bytes, source.content_type)
    storage.put_object(
        _source_key(source.project_id, source.id),
        source.model_dump_json().encode("utf-8"),
        "application/json",
    )


def get_source(storage: StorageBackend, project_id: str, source_id: str) -> SourceAsset | None:
    key = _source_key(project_id, source_id)
    if not storage.exists(key):
        return None
    return SourceAsset.model_validate_json(storage.get_object(key))


def get_source_original_url(
    source: SourceAsset,
    storage: StorageBackend,
    expires_in: int = DEFAULT_PRESIGNED_URL_EXPIRES_SECONDS,
) -> str:
    """Accessible reference to the original file for a remote fetcher (GMI).

    Uploaded originals are private by default (docs/canon/FOUNDER_CANON.md).
    An earlier version of this function joined the bucket endpoint and key
    into a plain URL, which would 403 for a private B2 object -- GMI's
    servers cannot authenticate. This generates a real, time-limited
    presigned URL through the storage backend instead, so a private object
    is actually fetchable for the short window this analysis attempt needs.

    Only ever a real https:// presigned URL for the real B2 backend;
    local-disk fallback has no HTTP presence at all, which
    app/analysis.py's AnalysisBlockedError check depends on to correctly
    refuse a real analysis call in that mode.
    """
    if storage.name == "b2":
        key = source_original_key(
            source.project_id, source.id, source.original_filename
        )
        return storage.get_presigned_url(key, expires_in=expires_in)
    return f"local-disk-fallback://{source.storage_key}"


def save_profile(storage: StorageBackend, profile: CreatorProfile) -> None:
    storage.put_object(
        _profile_key(profile.project_id, profile.source_id),
        profile.model_dump_json().encode("utf-8"),
        "application/json",
    )


def save_blocked_record(storage: StorageBackend, record: AnalysisBlockedRecord) -> None:
    storage.put_object(
        _profile_key(record.project_id, record.source_id),
        record.model_dump_json().encode("utf-8"),
        "application/json",
    )


def save_extended_analysis(storage: StorageBackend, analysis: ExtendedCreatorAnalysis) -> None:
    storage.put_object(
        _extended_analysis_key(analysis.project_id, analysis.source_id),
        analysis.model_dump_json().encode("utf-8"),
        "application/json",
    )


def save_extended_blocked_record(storage: StorageBackend, record: AnalysisBlockedRecord) -> None:
    storage.put_object(
        _extended_analysis_key(record.project_id, record.source_id),
        record.model_dump_json().encode("utf-8"),
        "application/json",
    )


def get_extended_analysis(
    storage: StorageBackend, project_id: str, source_id: str
) -> ExtendedCreatorAnalysis | AnalysisBlockedRecord | None:
    key = _extended_analysis_key(project_id, source_id)
    if not storage.exists(key):
        return None
    raw = json.loads(storage.get_object(key))
    if raw.get("status") == "blocked":
        return AnalysisBlockedRecord.model_validate(raw)
    return ExtendedCreatorAnalysis.model_validate(raw)


def save_generated_video(
    storage: StorageBackend, record: GeneratedVideoRecord, video_bytes: bytes
) -> None:
    """Append a generated-video version. Prior versions are preserved --
    saving a V2 never overwrites or hides V1."""
    storage.put_object(record.storage_key, video_bytes, record.content_type)
    records = list_generated_video_records(storage, record.project_id, record.source_id)
    records = [r for r in records if r.id != record.id]
    records.append(record)
    storage.put_object(
        _generated_videos_list_key(record.project_id, record.source_id),
        json.dumps([json.loads(r.model_dump_json()) for r in records]).encode("utf-8"),
        "application/json",
    )


def list_generated_video_records(
    storage: StorageBackend, project_id: str, source_id: str
) -> list[GeneratedVideoRecord]:
    """All versions, oldest first. Falls back to (and migrates from) the
    legacy single-record key so the first animatic persisted before
    versioning existed is still listed."""
    list_key = _generated_videos_list_key(project_id, source_id)
    if storage.exists(list_key):
        raw = json.loads(storage.get_object(list_key))
        return [GeneratedVideoRecord.model_validate(item) for item in raw]
    legacy_key = _generated_video_record_key(project_id, source_id)
    if storage.exists(legacy_key):
        return [GeneratedVideoRecord.model_validate_json(storage.get_object(legacy_key))]
    return []


def get_generated_video_record(
    storage: StorageBackend, project_id: str, source_id: str, video_id: str | None = None
) -> GeneratedVideoRecord | None:
    """A specific version by id, or the latest when no id is given."""
    records = list_generated_video_records(storage, project_id, source_id)
    if not records:
        return None
    if video_id is None:
        return records[-1]
    for r in records:
        if r.id == video_id:
            return r
    return None


def get_analysis_result(
    storage: StorageBackend, project_id: str, source_id: str
) -> CreatorProfile | AnalysisBlockedRecord | None:
    key = _profile_key(project_id, source_id)
    if not storage.exists(key):
        return None
    raw = json.loads(storage.get_object(key))
    if raw.get("status") == "blocked":
        return AnalysisBlockedRecord.model_validate(raw)
    return CreatorProfile.model_validate(raw)
