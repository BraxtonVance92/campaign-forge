"""CampaignForge CF-RUN-001: smallest real product flow.

Upload one authorized creator video -> real analysis (or an honest
blocked state) -> persist -> display. See docs/ops/ACTIVE_WORK_PACKET.md.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import load_settings
from app.routes.projects import router as projects_router

app = FastAPI(title="CampaignForge (CF-RUN-001)")
templates = Jinja2Templates(directory="app/templates")

app.include_router(projects_router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html")


@app.get("/health")
def health():
    settings = load_settings()
    return {
        "status": "ok",
        "gmi_configured": settings.gmi_configured,
        "b2_configured": settings.b2_configured,
    }
