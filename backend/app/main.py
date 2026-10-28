from contextlib import asynccontextmanager
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401
from app.routers import auth, cases, images, results, patients, dashboard, notifications, models as model_registry, audit_logs, reports, preprocessing, admin_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.report_path.mkdir(parents=True, exist_ok=True)
    # Creates missing tables only. Existing installations must run the SQL migration first.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ArteryVision Backend API",
    description="Authentication, case and patient metadata, secure image storage, exports, notifications, and model registry metadata. AI inference is intentionally not included in this upgrade.",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

for router in (auth.router, cases.router, images.router, results.router, patients.router, dashboard.router, notifications.router, model_registry.router, audit_logs.router, reports.router, preprocessing.router, admin_users.router):
    app.include_router(router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "ArteryVision Backend API", "version": "1.1.0", "ai_inference": "not_implemented"}
