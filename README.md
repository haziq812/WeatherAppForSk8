# WeatherApp — Python Backend

A Python backend for a weather app with a 7-day forecast and weekly activity planner.  
Built with **FastAPI** + **Open-Meteo** (free, no API key) + **SQLite**.

---

## Features

- **7-day weather forecast** — powered by Open-Meteo (free, no signup needed)
- **Today's weather** — quick single-day summary
- **Week planner** — create, view, edit and delete events for the week
- **Week overview** — events combined with matching weather forecast
- **Auto-generated API docs** — visit `/docs` when the server is running

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
uvicorn main:app --reload
```

### 3. Open the interactive docs
Go to: **http://127.0.0.1:8000/docs**

---

## API Endpoints

### Weather
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/weather/forecast?city=<city>` | 7-day forecast |
| GET | `/weather/forecast/today?city=<city>` | Today's forecast only |

### Planner
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/planner/` | List all events |
| POST | `/planner/` | Create a new event |
| GET | `/planner/{id}` | Get one event |
| PUT | `/planner/{id}` | Update an event |
| DELETE | `/planner/{id}` | Delete an event |
| GET | `/planner/week/overview?city=<city>` | Week events + weather |

---

## Project Structure

```
WeatherAppForSk8/
├── main.py             ← FastAPI app entry point
├── requirements.txt    ← Python dependencies
├── docs/
│   └── GUIDE.md        ← Learning guide (read this!)
└── app/
    ├── database.py     ← SQLite setup
    ├── models.py       ← Pydantic schemas
    ├── weather/
    │   ├── service.py  ← Open-Meteo API calls
    │   └── router.py   ← Weather routes
    └── planner/
        ├── service.py  ← CRUD database operations
        └── router.py   ← Planner routes
```

---

## Learning

Read [docs/GUIDE.md](docs/GUIDE.md) for a full explanation of:
- Project structure and why it's organised this way
- Python concepts used (functions, classes, async, dicts, lists)
- FastAPI concepts (routes, parameters, status codes)
- How the weather and planner features work
- How to test the API
- What to learn next

---

## Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Programming language |
| FastAPI | Web framework |
| Uvicorn | ASGI server |
| Open-Meteo | Free weather API (no key needed) |
| SQLite | Local database (built into Python) |
| httpx | Async HTTP client |
| Pydantic | Data validation |
