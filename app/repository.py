"""Persistence functions over a StorageBackend, using the object layout
recommended in docs/canon/PRODUCT_CANON.md. No database is used for this
narrow slice -- project/source/analysis metadata are small JSON objects
stored alongside the binary source, which keeps the architecture simple
(a database can be introduced later without changing this interface).
"""

from __future__ import annotations

import json

from app.models import AnalysisBlockedRecord, ConsentRecord, CreatorProfile, Project, SourceAsset
from app.storage import StorageBackend


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


def get_source_original_url(source: SourceAsset, storage: StorageBackend) -> str:
    """Best-effort accessible reference to the original file.

    Only ever a real https:// URL for the real B2 backend; local-disk
    fallback has no public URL, which app/analysis.py's AnalysisBlockedError
    check depends on to correctly refuse a real analysis call in that mode.
    """
    if storage.name == "b2":
        # Presigned/public URL construction is deployment-specific; the bucket
        # endpoint plus key is the minimum honest reference for this slice.
        from app.config import load_settings

        settings = load_settings()
        return f"{settings.b2_endpoint}/{settings.b2_bucket_name}/" + _source_original_key(
            source.project_id, source.id, source.original_filename
        )
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
