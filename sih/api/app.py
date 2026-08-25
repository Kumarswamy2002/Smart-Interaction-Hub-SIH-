from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from sih.core.config import settings
from sih.core.database import init_db
from sih.api.v1.auth import router as auth_router
from sih.api.v1.conversations import router as conv_router
from sih.api.v1.tasks import router as task_router
from sih.api.v1.approvals import router as approval_router
from sih.api.v1.workflows import router as workflow_router
from sih.api.v1.knowledge import router as knowledge_router
from sih.api.v1.integrations import router as integration_router
from sih.api.v1.audit import router as audit_router
from sih.api.v1.system import router as system_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Smart Interaction Hub (SIH) - Production-grade Interaction & Automation Platform API Gateway",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
api_v1_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(conv_router, prefix=api_v1_prefix)
app.include_router(task_router, prefix=api_v1_prefix)
app.include_router(approval_router, prefix=api_v1_prefix)
app.include_router(workflow_router, prefix=api_v1_prefix)
app.include_router(knowledge_router, prefix=api_v1_prefix)
app.include_router(integration_router, prefix=api_v1_prefix)
app.include_router(audit_router, prefix=api_v1_prefix)
app.include_router(system_router, prefix=api_v1_prefix)

# Static file serving for Web Dashboard
web_dir = Path(__file__).resolve().parent.parent / "web"
static_dir = web_dir / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    index_file = web_dir / "static" / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Welcome to Smart Interaction Hub API Gateway. Visit /docs for OpenAPI specifications."}
