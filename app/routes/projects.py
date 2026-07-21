"""HTTP routes for the CF-RUN-001 slice: create project, upload one
authorized source video with consent, run (or honestly block) analysis,
and display the persisted result. Kept intentionally minimal -- one
project, one source, one analysis result, no unrelated UI.
"""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app import repository
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
    filename = file.filename or "upload"
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
    client = GMIAnalysisClient(settings)
    try:
        profile = client.analyze(
            project_id=project_id,
            source_id=source_id,
            video_url=video_url,
            source_asset_hash=source.checksum_sha256,
        )
        repository.save_profile(storage, profile)
    except AnalysisBlockedError as exc:
        blocked = AnalysisBlockedRecord(
            project_id=project_id, source_id=source_id, reason=str(exc)
        )
        repository.save_blocked_record(storage, blocked)
    except ValidationError as exc:
        blocked = AnalysisBlockedRecord(
            project_id=project_id,
            source_id=source_id,
            reason=f"Analysis response failed contract validation: {exc}",
        )
        repository.save_blocked_record(storage, blocked)

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
    return JSONResponse(
        {
            "source": source.model_dump(mode="json"),
            "analysis_result": result.model_dump(mode="json") if result else None,
        }
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

    # This narrow slice supports exactly one source per project; look it up
    # by scanning the one expected metadata key pattern via a source_id the
    # upload step would have produced. For simplicity we store the most
    # recent source id on the project object itself.
    source = None
    result = None
    if project.id:
        source = _find_latest_source(storage, project_id)
        if source is not None:
            result = repository.get_analysis_result(storage, project_id, source.id)

    return templates.TemplateResponse(
        request,
        "project.html",
        {
            "project": project,
            "source": source,
            "result": result,
            "storage_backend": storage.name,
        },
    )


def _find_latest_source(storage: StorageBackend, project_id: str) -> SourceAsset | None:
    # Uses the generic StorageBackend.list_keys(), so this works identically
    # across B2, local-disk-fallback, and the in-memory test backend -- not
    # a backend-specific hack. Kept to "find the one source" since this
    # narrow slice supports exactly one source per project.
    prefix = f"projects/{project_id}/sources/"
    metadata_keys = sorted(k for k in storage.list_keys(prefix) if k.endswith("/metadata.json"))
    if not metadata_keys:
        return None
    return SourceAsset.model_validate_json(storage.get_object(metadata_keys[0]))
