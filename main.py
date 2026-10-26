import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


app = FastAPI(
    title="Silage FQI Prediction API",
    description="Research prototype for predicting Fermentation Quality Index (FQI).",
    version="1.0.0",
)

# Configure CORS with trusted origins for browser requests
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:3000,http://localhost:3000"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount frontend directory for static assets
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def root():
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return {
        "message": "Silage FQI Prediction API is running",
        "docs": "/docs"
    }


@app.get("/index.html")
def serve_index():
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    return root()


@app.get("/sample.html")
def serve_sample():
    sample_file = FRONTEND_DIR / "sample.html"
    if sample_file.exists():
        return FileResponse(sample_file)
    return FileResponse(FRONTEND_INDEX)


@app.get("/login.html")
def serve_login():
    return FileResponse(FRONTEND_DIR / "login.html")


@app.get("/register.html")
def serve_register():
    return FileResponse(FRONTEND_DIR / "register.html")


@app.get("/dashboard.html")
def serve_dashboard():
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@app.get("/history.html")
def serve_history():
    return FileResponse(FRONTEND_DIR / "history.html")


@app.get("/admin.html")
def serve_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")


@app.get("/result.html")
def serve_result():
    return FileResponse(FRONTEND_DIR / "result.html")


# Mount uploads directory for photos if present
UPLOAD_DIR = BASE_DIR / "backend" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


# Connect backend routers for auth, dashboard, samples, assessments, and FQI prediction
try:
    from backend.database import engine, Base
    from backend.routers.auth import router as auth_router
    from backend.routers.samples import router as samples_router
    from backend.routers.assessment import router as assessment_router
    from backend.routers.dashboard import router as dashboard_router
    from backend.routers.admin import router as admin_router
    from backend.routers.predict import router as predict_router

    Base.metadata.create_all(bind=engine)

    app.include_router(auth_router)
    app.include_router(samples_router)
    app.include_router(assessment_router)
    app.include_router(dashboard_router)
    app.include_router(admin_router)
    app.include_router(predict_router)
except Exception as e:
    print(f"[SmartSilageAI Info] Backend routers initialization note: {e}")