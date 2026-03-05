"""
main.py — The entry point of our Weather App backend.

LEARNING NOTE:
    In Python, every file is called a "module".
    This file is the starting point — when we run the server,
    Python starts reading from here.

HOW TO RUN THE SERVER:
    uvicorn main:app --reload

    - "uvicorn" is the server program
    - "main" means it should look in this file (main.py)
    - "app" means it looks for a variable called `app` inside main.py
    - "--reload" auto-restarts the server whenever you save a change

ONCE RUNNING, VISIT:
    http://127.0.0.1:8000        → See "Hello" response
    http://127.0.0.1:8000/docs   → Auto-generated interactive API docs (FREE!)
"""

# ── Imports ──────────────────────────────────────────────────────────────────
# "from X import Y" means: go to library X, and bring in Y for us to use.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# We import our own routers (blueprints of our API routes)
from app.weather.router import router as weather_router
from app.planner.router import router as planner_router
from app.database import init_db

# ── App Setup ─────────────────────────────────────────────────────────────────
# FastAPI() creates the actual application object.
# Think of it as "turning on" the app.
app = FastAPI(
    title="WeatherApp API",
    description=(
        "Backend API for the Weather App. "
        "Provides 7-day weather forecasts and a weekly activity planner."
    ),
    version="1.0.0",
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
# LEARNING NOTE:
#   CORS = Cross-Origin Resource Sharing.
#   When your future frontend (e.g., a website or React app) tries to talk to
#   this backend, the browser will BLOCK it by default for security reasons.
#   This middleware tells the browser: "It's okay, allow those requests."
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # "*" means allow ALL origins (fine for development)
    allow_credentials=True,
    allow_methods=["*"],      # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# ── Startup Event ─────────────────────────────────────────────────────────────
# LEARNING NOTE:
#   @app.on_event("startup") is a "decorator" — it tells FastAPI:
#   "Run this function automatically when the server starts."
#   We use it to create our database tables if they don't exist yet.
@app.on_event("startup")
def on_startup():
    """Run once when the server starts up."""
    init_db()  # Create the SQLite database and tables
    print("✅ Database initialised.")

# ── Routers ───────────────────────────────────────────────────────────────────
# LEARNING NOTE:
#   A "router" is like a mini-app that handles a specific group of routes.
#   - weather_router handles everything under /weather/...
#   - planner_router handles everything under /planner/...
#   Using prefix keeps things organised instead of putting everything in one file.
app.include_router(weather_router, prefix="/weather", tags=["Weather"])
app.include_router(planner_router, prefix="/planner", tags=["Planner"])

# ── Root Route ────────────────────────────────────────────────────────────────
# LEARNING NOTE:
#   @app.get("/") is a "route decorator".
#   It tells FastAPI: when someone visits GET /, run the function below it.
@app.get("/", tags=["Health"])
def root():
    """Simple health check — confirms the API is running."""
    return {
        "status": "running",
        "message": "Welcome to the WeatherApp API!",
        "docs": "Visit /docs to explore all available endpoints",
    }
