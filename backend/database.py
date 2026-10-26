"""
Database Connection and Session Manager for SmartSilageAI (SIH26111)
Supports MySQL as the primary database with automatic graceful SQLite fallback
to ensure seamless local running and zero-setup demonstration for beginners.
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables
load_dotenv()

DB_TYPE = os.getenv("DB_TYPE", "mysql").lower()
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "smartsilage")

Base = declarative_base()
active_db_engine_name = "sqlite"

def get_engine():
    global active_db_engine_name
    if DB_TYPE == "mysql":
        try:
            # 1. First ensure database exists on MySQL server
            server_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?charset=utf8mb4"
            temp_engine = create_engine(server_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
            with temp_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
            temp_engine.dispose()
            
            # 2. Connect to the specific database
            mysql_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
            engine = create_engine(mysql_url, pool_recycle=3600, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"[SmartSilageAI] Connected successfully to MySQL Database: '{DB_NAME}' on {DB_HOST}:{DB_PORT}")
            active_db_engine_name = "mysql"
            return engine
        except Exception as e:
            print(f"[SmartSilageAI Warning] MySQL connection failed ({e}).")
            print("[SmartSilageAI Info] Seamlessly falling back to local SQLite ('smartsilage.db') so the application works out-of-the-box!")
            print("[SmartSilageAI Info] To use MySQL, update DB_PASSWORD in .env or run database/schema.sql in MySQL Workbench.")

    # SQLite fallback
    sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "smartsilage.db"))
    engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})
    active_db_engine_name = "sqlite"
    print(f"[SmartSilageAI] Active Database: SQLite ({sqlite_path})")
    return engine

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes tables in the active database engine."""
    import backend.models  # Ensure models are registered with Base
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI database dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

