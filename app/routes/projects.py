"""HTTP routes for the CF-RUN-001 slice: create project, upload one
authorized source video with consent, run (or honestly block) analysis,
and display the persisted result. Kept intentionally minimal -- one
project, one source, one analysis result, no unrelated UI.
"""

from __future__ import annotations

import hashlib
import re

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app import pipeline, repository
from app.analysis import AnalysisBlockedError, GMIAnalysisClient
from app.config import Settings, load_settings
from app.models import (
    MAX_UPLOAD_BYTES,
    ALLOWED_CONTENT_TYPES,
    AnalysisBlockedRecord,
    ConsentRecord,
    Project,
    SourceAsset,
    new_id,
)
from app.security import content_type_matches_signature, sanitize_filename
from app.storage import StorageBackend, build_storage_backend

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_storage() -> StorageBackend:
    return build_storage_backend(load_settings())


def get_settings() -> Settings:
    return load_settings()


@router.post("/projects")
def create_project(
    name: str = Form(...),
    storage: StorageBackend = Depends(get_storage),
):
    if not name.strip():
        raise HTTPException(status_code=422, detail="Project name must not be blank.")
    project = Project(name=name.strip())
    repository.save_project(storage, project)
    return RedirectResponse(url=f"/projects/{project.id}", status_code=303)


@router.post("/projects/{project_id}/sources")
async def upload_source(
    project_id: str,
    consent_statement: str = Form(...),
    permitted_uses: str = Form(...),
    file: UploadFile = File(...),
    storage: StorageBackend = Depends(get_storage),
):
    project = repository.get_project(storage, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    if _find_existing_source(storage, project_id) is not None:
        raise HTTPException(
            status_code=409,
            detail="This project already has an authorized source. CF-RUN-001's "
            "narrow scope supports exactly one source per project.",
        )

    if not consent_statement.strip():
        raise HTTPException(
            status_code=422, detail="Consent attestation is required before upload."
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported content type '{file.content_type}'. "
            f"Allowed: {sorted(ALLOWED_CONTENT_TYPES)}.",
        )

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"File exceeds the maximum allowed size of {MAX_UPLOAD_BYTES} bytes.",
        )

    if not content_type_matches_signature(file.content_type, data):
        raise HTTPException(
            status_code=422,
            detail=f"File content does not match a real {file.content_type} "
            "signature. The declared content type does not match the actual "
            "file format (checked via magic bytes, not the client-supplied "
            "header).",
        )

    uses = [u.strip() for u in permitted_uses.split(",") if u.strip()]
    if not uses:
        raise HTTPException(
            status_code=422,
            detail="At least one permitted use must be specified alongside consent.",
        )

    consent = ConsentRecord(
        project_id=project_id, statement=consent_statement, permitted_uses=uses
    )
    repository.save_consent(storage, consent)

    checksum = hashlib.sha256(data).hexdigest()
    filename = sanitize_filename(file.filename or "upload")
    source_id = new_id()
    source = SourceAsset(
        id=source_id,
        project_id=project_id,
        consent_id=consent.id,
        original_filename=filename,
        content_type=file.content_type,
        size_bytes=len(data),
        checksum_sha256=checksum,
        storage_key=repository.source_original_key(project_id, source_id, filename),
        storage_backend=storage.name if storage.name in ("b2", "local-disk-fallback") else "local-disk-fallback",
    )
    repository.save_source(storage, source, data)

    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.post("/projects/{project_id}/sources/{source_id}/analyze")
def analyze_source(
    project_id: str,
    source_id: str,
    storage: StorageBackend = Depends(get_storage),
    settings: Settings = Depends(get_settings),
):
    source = repository.get_source(storage, project_id, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")

    video_url = repository.get_source_original_url(source, storage)
    video_bytes = None
    if not video_url.startswith("https://"):
        # No hosted URL (B2 not configured) -- supply the raw bytes so
        # GMIAnalysisClient can attempt the base64 data-URI fallback
        # instead of blocking outright. See CF-01's research in
        # docs/ops/ACTIVE_WORK_PACKET.md.
        video_bytes = storage.get_object(source.storage_key)
    client = GMIAnalysisClient(settings)
    try:
        # CF-02 (2026-07-22, founder-directed): the richer, timestamped,
        # section-by-section analysis, not the narrower CreatorProfile
        # contract -- see app/analysis.py's analyze_extended() docstring.
        extended = client.analyze_extended(
            project_id=project_id,
            source_id=source_id,
            video_url=video_url,
            source_asset_hash=source.checksum_sha256,
            video_bytes=video_bytes,
            video_content_type=source.content_type,
        )
        repository.save_extended_analysis(storage, extended)
    except AnalysisBlockedError as exc:
        # GMIAnalysisClient guarantees every failure mode (missing
        # credential, unfetchable source, network error, HTTP error,
        # malformed response, contract validation failure) surfaces as this
        # one exception type with an already-sanitized message -- no raw
        # provider body or secret ever reaches this handler.
        blocked = AnalysisBlockedRecord(
            project_id=project_id, source_id=source_id, reason=str(exc)
        )
        repository.save_extended_blocked_record(storage, blocked)

    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.get("/projects/{project_id}/sources/{source_id}", response_class=JSONResponse)
def get_source_json(
    project_id: str,
    source_id: str,
    storage: StorageBackend = Depends(get_storage),
):
    source = repository.get_source(storage, project_id, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    result = repository.get_analysis_result(storage, project_id, source_id)
    extended_result = repository.get_extended_analysis(storage, project_id, source_id)
    return JSONResponse(
        {
            "source": source.model_dump(mode="json"),
            "analysis_result": result.model_dump(mode="json") if result else None,
            "extended_analysis_result": (
                extended_result.model_dump(mode="json") if extended_result else None
            ),
        }
    )


@router.post("/projects/{project_id}/sources/{source_id}/pipeline-analyze")
def start_pipeline_analysis(
    project_id: str,
    source_id: str,
    storage: StorageBackend = Depends(get_storage),
):
    """Run the CF-04 local analysis pipeline for this source. Synchronous
    (consistent with this app's other actions); per-stage state is
    persisted as it progresses, so an interrupted run leaves an honest
    partial state. Rejections (missing source/consent, duplicate run)
    surface as HTTP errors without persisting a run."""
    try:
        pipeline.run_analysis(storage, project_id, source_id)
    except pipeline.PipelineRejected as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)


@router.get("/projects/{project_id}/sources/{source_id}/analysis-frame/{index}")
def get_analysis_frame(
    project_id: str,
    source_id: str,
    index: int,
    storage: StorageBackend = Depends(get_storage),
):
    """Serve one sampled evidence frame. The frame is looked up from the
    persisted run's own frame list (never from a client-supplied path)."""
    run = repository.get_analysis_run(storage, project_id, source_id)
    if run is None or index < 0 or index >= len(run.frames):
        raise HTTPException(status_code=404, detail="No such analysis frame.")
    frame = run.frames[index]
    return Response(content=storage.get_object(frame.storage_key), media_type="image/jpeg")


@router.get("/projects/{project_id}/sources/{source_id}/generated-video")
def get_generated_video(
    request: Request,
    project_id: str,
    source_id: str,
    video_id: str | None = None,
    storage: StorageBackend = Depends(get_storage),
):
    """Serve a generated video version by ?video_id=...; latest when omitted.

    Honors single-range HTTP Range requests so browser <video> players can
    seek without re-downloading from the start; a malformed or unsatisfiable
    range falls back per RFC 7233 (ignore, or 416 for out-of-bounds starts).
    """
    record = repository.get_generated_video_record(storage, project_id, source_id, video_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No generated video for this source.")
    video_bytes = storage.get_object(record.storage_key)
    total = len(video_bytes)
    common_headers = {
        "Content-Disposition": f'inline; filename="{record.filename}"',
        "Accept-Ranges": "bytes",
    }

    range_header = request.headers.get("range", "")
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", range_header.strip())
    if match and (match.group(1) or match.group(2)):
        if match.group(1):
            start = int(match.group(1))
            end = min(int(match.group(2)), total - 1) if match.group(2) else total - 1
        else:  # suffix form: bytes=-N (final N bytes)
            start = max(total - int(match.group(2)), 0)
            end = total - 1
        if start >= total or start > end:
            return Response(
                status_code=416,
                headers={**common_headers, "Content-Range": f"bytes */{total}"},
            )
        return Response(
            content=video_bytes[start : end + 1],
            status_code=206,
            media_type=record.content_type,
            headers={
                **common_headers,
                "Content-Range": f"bytes {start}-{end}/{total}",
            },
        )

    return Response(
        content=video_bytes,
        media_type=record.content_type,
        headers=common_headers,
    )


@router.get("/projects/{project_id}", response_class=HTMLResponse)
def view_project(
    request: Request,
    project_id: str,
    storage: StorageBackend = Depends(get_storage),
):
    project = repository.get_project(storage, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Upload enforces exactly one source per project (see upload_source),
    # so there is at most one to find -- no "latest" ambiguity to resolve.
    source = None
    result = None
    extended_result = None
    generated_videos = []
    analysis_run = None
    if project.id:
        source = _find_existing_source(storage, project_id)
        if source is not None:
            result = repository.get_analysis_result(storage, project_id, source.id)
            extended_result = repository.get_extended_analysis(storage, project_id, source.id)
            generated_videos = repository.list_generated_video_records(storage, project_id, source.id)
            analysis_run = repository.get_analysis_run(storage, project_id, source.id)

    return templates.TemplateResponse(
        request,
        "project.html",
        {
            "project": project,
            "source": source,
            "result": result,
            "extended_result": extended_result,
            "generated_videos": generated_videos,
            "analysis_run": analysis_run,
            "storage_backend": storage.name,
        },
    )


def _find_existing_source(storage: StorageBackend, project_id: str) -> SourceAsset | None:
    # Uses the generic StorageBackend.list_keys(), so this works identically
    # across B2, local-disk-fallback, and the in-memory test backend -- not
    # a backend-specific hack. Upload enforces at most one source per
    # project, so there is never an ordering/"latest" question here.
    prefix = f"projects/{project_id}/sources/"
    metadata_keys = sorted(k for k in storage.list_keys(prefix) if k.endswith("/metadata.json"))
    if not metadata_keys:
        return None
    return SourceAsset.model_validate_json(storage.get_object(metadata_keys[0]))
