"""
Main FastAPI Application for SmartSilageAI (SIH26111)
SIH Problem Statement: Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers
Ministry of Fisheries, Animal Husbandry & Dairying
"""
import os
from contextlib import asynccontextmanager
from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database import engine, Base, SessionLocal
from backend.models.farmer import Farmer
from backend.models.sample import Sample
from backend.models.assessment import Assessment
from backend.services.auth_service import hash_password
from backend.services.assessment_service import run_and_save_assessment

from backend.routers.auth import router as auth_router
from backend.routers.samples import router as samples_router
from backend.routers.assessment import router as assessment_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.admin import router as admin_router
from backend.routers.predict import router as predict_router


def seed_initial_demo_data():
    """Seeds realistic demo data if database is empty."""
    db = SessionLocal()
    try:
        farmer_count = db.query(Farmer).count()
        if farmer_count == 0:
            print("[SmartSilageAI] Seeding initial dairy farmer profile and realistic samples...")
            demo_farmer = Farmer(
                name="Ramesh Patel",
                mobile="9876543210",
                email="ramesh.farmer@example.com",
                location="Anand, Gujarat",
                password_hash=hash_password("farmer123")
            )
            db.add(demo_farmer)
            db.commit()
            db.refresh(demo_farmer)

            # Sample 1: Good quality corn silage
            sample1 = Sample(
                sample_id="SMP-2026-001",
                farmer_id=demo_farmer.id,
                sample_type="Corn Silage",
                sample_date=date(2026, 9, 25),
                ph=3.9,
                moisture=65.5,
                temperature=25.0,
                crude_protein=8.2,
                ndf=44.0,
                adf=26.5,
                ash=4.8,
                visual_odor="Pleasant / Fruity Acidic",
                visual_color="Olive Green / Light Brown",
                notes="Bunker silo opened 4 weeks ago. Tightly packed."
            )
            db.add(sample1)
            db.commit()
            db.refresh(sample1)
            run_and_save_assessment(sample1, db)

            # Sample 2: Aerobically deteriorating silage (High pH & heating)
            sample2 = Sample(
                sample_id="SMP-2026-002",
                farmer_id=demo_farmer.id,
                sample_type="Corn Silage",
                sample_date=date(2026, 9, 28),
                ph=5.2,
                moisture=74.0,
                temperature=41.5,
                crude_protein=7.1,
                ndf=52.0,
                adf=33.0,
                ash=6.2,
                visual_odor="Vinegar / Sharp Acetic",
                visual_color="Dark Brown / Surface Mold",
                notes="Top layer had rain ingress after plastic sheet tear."
            )
            db.add(sample2)
            db.commit()
            db.refresh(sample2)
            run_and_save_assessment(sample2, db)

            # Sample 3: Sorghum Silage with mild heating
            sample3 = Sample(
                sample_id="SMP-2026-003",
                farmer_id=demo_farmer.id,
                sample_type="Sorghum Silage",
                sample_date=date(2026, 9, 29),
                ph=4.6,
                moisture=68.0,
                temperature=34.0,
                crude_protein=7.4,
                ndf=54.0,
                visual_odor="Pleasant / Acidic",
                visual_color="Golden Brown",
                notes="Pit silage. Mild warmth felt at feed-out face."
            )
            db.add(sample3)
            db.commit()
            db.refresh(sample3)
            run_and_save_assessment(sample3, db)
            print("[SmartSilageAI] Initial seed data created successfully.")
    except Exception as e:
        print(f"[SmartSilageAI Warning] Seed error: {e}")
        db.rollback()
    finally:
        db.close()


# Initialize tables and seed demo records on import
try:
    Base.metadata.create_all(bind=engine)
    seed_initial_demo_data()
except Exception as e:
    print(f"[SmartSilageAI Startup Warning] Database init error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="SmartSilageAI API",
    description="SIH26111: Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS with trusted origins for secure local development and deployment
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

# Include Routers (predict_router provides both /predict and /api/predict)
app.include_router(auth_router)
app.include_router(samples_router)
app.include_router(assessment_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
app.include_router(predict_router)

# Mount Uploads directory
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Mount Frontend directory so full application is accessible on a single port
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SmartSilageAI Backend (SIH26111)",
        "version": "1.0.0"
    }


# Route root and HTML page endpoints directly for single-server convenience
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/login.html")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


@app.get("/register.html")
def serve_register():
    return FileResponse(os.path.join(FRONTEND_DIR, "register.html"))


@app.get("/dashboard.html")
def serve_dashboard():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))


@app.get("/sample.html")
def serve_sample():
    return FileResponse(os.path.join(FRONTEND_DIR, "sample.html"))


@app.get("/result.html")
def serve_result():
    return FileResponse(os.path.join(FRONTEND_DIR, "result.html"))


@app.get("/history.html")
def serve_history():
    return FileResponse(os.path.join(FRONTEND_DIR, "history.html"))


@app.get("/admin.html")
def serve_admin():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))
