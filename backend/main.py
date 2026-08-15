import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from api.endpoints import router as api_router
from data.database import init_db
import os

app = FastAPI(
    title="SurakshaNet API",
    description="Privacy-Preserving Community Health Anomaly Detection Platform API",
    version="1.0.0"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for prototype simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount main router under /api
app.include_router(api_router, prefix="/api")

# Serve static files and frontend index.html
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "SurakshaNet static site not found. Check backend/static/index.html."

@app.on_event("startup")
def startup_event():
    # Automatically initialize SQLite database on app startup if not exists
    db_file = os.path.join(os.path.dirname(__file__), "data", "surakshanet.db")
    if not os.path.exists(db_file):
        print("Database not found. Initializing database...")
        init_db()
    else:
        print("Database found. Starting SurakshaNet API.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
