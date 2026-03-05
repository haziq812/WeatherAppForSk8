# WeatherApp Backend — Python Learning Guide

This guide walks you through the concepts used in this project.
Read it alongside the code comments for the best learning experience.

---

## Table of Contents
1. [Project Structure](#1-project-structure)
2. [Python Basics Used Here](#2-python-basics-used-here)
3. [FastAPI Concepts](#3-fastapi-concepts)
4. [How the Weather Feature Works](#4-how-the-weather-feature-works)
5. [How the Planner Feature Works](#5-how-the-planner-feature-works)
6. [How to Run the Project](#6-how-to-run-the-project)
7. [How to Test the API](#7-how-to-test-the-api)
8. [Common Errors and Fixes](#8-common-errors-and-fixes)
9. [What to Learn Next](#9-what-to-learn-next)

---

## 1. Project Structure

```
WeatherAppForSk8/
│
├── main.py                  ← Entry point. Starts the app, registers routes.
├── requirements.txt         ← Lists all Python packages needed.
│
└── app/                     ← All application code lives here.
    ├── __init__.py          ← Marks `app/` as a Python package.
    ├── database.py          ← SQLite database setup and connection helper.
    ├── models.py            ← Pydantic schemas: describes data shapes.
    │
    ├── weather/             ← Everything related to weather.
    │   ├── __init__.py
    │   ├── service.py       ← Logic: talks to Open-Meteo API.
    │   └── router.py        ← Routes: GET /weather/forecast, etc.
    │
    └── planner/             ← Everything related to the week planner.
        ├── __init__.py
        ├── service.py       ← Logic: CRUD operations on the database.
        └── router.py        ← Routes: GET/POST/PUT/DELETE /planner/...
```

**Why separate files?**  
Each file has **one job**. This is called the *Single Responsibility Principle*.  
When something breaks, you know exactly where to look.

---

## 2. Python Basics Used Here

### Variables and Types
```python
city = "Kuala Lumpur"   # str   (text)
temp = 31.5             # float (decimal number)
days = 7                # int   (whole number)
is_rainy = True         # bool  (True or False)
nothing = None          # NoneType (absence of value)
```

### Functions
```python
# Define a function with `def`
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Call it
message = greet("Haziq")  # "Hello, Haziq!"
```

The `: str` after `name` is a **type hint** — it tells you and your editor  
what type of value is expected. Python doesn't enforce these at runtime,  
but Pydantic and FastAPI use them for validation.

### Async Functions
```python
import httpx

async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)  # Wait for the HTTP response
        return response.json()
```

`async def` + `await` lets the server handle other requests while waiting  
for slow operations (network calls, file reads).

### Dictionaries
```python
# A dictionary maps keys to values
forecast = {
    "date": "2026-03-04",
    "temp_max": 31.2,
    "condition": "Sunny"
}

# Access by key
print(forecast["date"])         # "2026-03-04"
print(forecast.get("rain", 0))  # 0 (default if key missing)
```

### Lists and List Comprehensions
```python
numbers = [1, 2, 3, 4, 5]

# List comprehension — compact way to build a new list
doubled = [n * 2 for n in numbers]  # [2, 4, 6, 8, 10]

# With a condition
evens = [n for n in numbers if n % 2 == 0]  # [2, 4]
```

### Classes
```python
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self):
        return f"Hi, I'm {self.name}, age {self.age}"

p = Person("Haziq", 25)
print(p.greet())  # "Hi, I'm Haziq, age 25"
```

Pydantic's `BaseModel` is a class. When we write `class DailyWeather(BaseModel)`,  
we're **inheriting** from BaseModel, getting all its validation features for free.

---

## 3. FastAPI Concepts

### Decorators
A decorator starts with `@` and "wraps" the function below it:
```python
@app.get("/hello")
def say_hello():
    return {"message": "Hello!"}
```
`@app.get("/hello")` tells FastAPI: "When someone sends a GET request to /hello,  
run the `say_hello` function and return its result as JSON."

### Query Parameters
Appear after `?` in the URL:
```
GET /weather/forecast?city=Penang
```
In FastAPI:
```python
from fastapi import Query

@router.get("/forecast")
async def get_forecast(city: str = Query(...)):
    ...
```

### Path Parameters
Embedded in the URL itself:
```
GET /planner/42
```
In FastAPI:
```python
@router.get("/{event_id}")
def get_event(event_id: int):
    ...
```

### Request Body (POST/PUT)
Data sent in the body of the request (not in the URL):
```python
@router.post("/")
def create(event: PlannerEventCreate):
    # FastAPI automatically parses the JSON body into `event`
    ...
```

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200  | OK — successful GET, PUT |
| 201  | Created — successful POST |
| 204  | No Content — successful DELETE |
| 400  | Bad Request — invalid input |
| 404  | Not Found — resource doesn't exist |
| 422  | Unprocessable — validation failed |
| 500  | Internal Server Error |

---

## 4. How the Weather Feature Works

```
User requests: GET /weather/forecast?city=Petaling+Jaya
         │
         ▼
weather/router.py  →  Receives request, validates city parameter
         │
         ▼
weather/service.py →  geocode_city("Petaling Jaya")
         │                  ↓
         │             Open-Meteo Geocoding API
         │                  ↓
         │             Returns: lat=3.10726, lon=101.60671
         │
         ▼
weather/service.py →  get_weather_forecast(lat, lon, timezone)
         │                  ↓
         │             Open-Meteo Forecast API
         │                  ↓
         │             Returns: 7-day JSON data
         │
         ▼
    Parse data into DailyWeather objects (one per day)
         │
         ▼
    Return WeatherForecastResponse JSON to the user
```

**Open-Meteo API** (no key needed):
- Geocoding: `https://geocoding-api.open-meteo.com/v1/search?name=Kuala+Lumpur`
- Forecast:  `https://api.open-meteo.com/v1/forecast?latitude=3.14&longitude=101.69&daily=...`

---

## 5. How the Planner Feature Works

The planner stores events in a local SQLite file (`app/weather_app.db`).

### Database Table: `planner_events`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-incremented unique ID |
| date | TEXT | Event date (YYYY-MM-DD) |
| title | TEXT | Short event name |
| description | TEXT | Optional details |
| activity_type | TEXT | outdoor / indoor / travel / general |
| weather_dependent | INTEGER | 0 = no, 1 = yes |
| created_at | TEXT | Auto-filled timestamp |

### API Flow Example: Creating an event

```
POST /planner/
Body: { "date": "2026-03-07", "title": "Morning run", "activity_type": "outdoor" }
         │
         ▼
planner/router.py  →  Validates body against PlannerEventCreate schema
         │
         ▼
planner/service.py →  create_event(event)
         │                  ↓
         │             INSERT INTO planner_events VALUES (...)
         │                  ↓
         │             cursor.lastrowid → get the new ID
         │
         ▼
    Return the created event as JSON with status 201
```

---

## 6. How to Run the Project

### Step 1: Install Python (if not installed)
Download from https://www.python.org/downloads/ — use Python 3.10 or higher.

### Step 2: Install dependencies
Open a terminal in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 3: Start the server
```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
✅ Database initialised.
```

### Step 4: Open the interactive docs
Visit: **http://127.0.0.1:8000/docs**

FastAPI automatically generates a beautiful interactive API documentation page  
(called Swagger UI). You can test every endpoint directly from the browser!

---

## 7. How to Test the API

### Using the Swagger UI (easiest)
1. Go to `http://127.0.0.1:8000/docs`
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters and click "Execute"

### Using curl (terminal)
```bash
# Get 7-day forecast
curl "http://127.0.0.1:8000/weather/forecast?city=Kuala+Lumpur"

# Create a planner event
curl -X POST "http://127.0.0.1:8000/planner/" \
     -H "Content-Type: application/json" \
     -d '{"date":"2026-03-07","title":"Morning run","activity_type":"outdoor","weather_dependent":true}'

# List all planner events
curl "http://127.0.0.1:8000/planner/"

# Get week overview (events + weather)
curl "http://127.0.0.1:8000/planner/week/overview?city=Kuala+Lumpur"
```

### Using Python (requests library)
```python
import requests

# Forecast
r = requests.get("http://127.0.0.1:8000/weather/forecast", params={"city": "Kuala Lumpur"})
print(r.json())

# Create event
r = requests.post("http://127.0.0.1:8000/planner/", json={
    "date": "2026-03-07",
    "title": "Morning run",
    "activity_type": "outdoor",
    "weather_dependent": True
})
print(r.json())
```

---

## 8. Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `422 Unprocessable Entity` | Request data failed validation | Check the error detail — it shows exactly which field is wrong |
| `404 Not Found` for a city | City name not recognised by geocoding | Try a different spelling, or a major nearby city |
| `City not found` error | Typo in city name | Double-check spelling |
| `Address already in use` | Port 8000 is busy | Run with `uvicorn main:app --reload --port 8001` |

---

## 9. What to Learn Next

Now that you have a working backend, here are great next steps:

1. **Python fundamentals** — [Official Python Tutorial](https://docs.python.org/3/tutorial/)
2. **FastAPI deep dive** — [FastAPI Docs](https://fastapi.tiangolo.com/) (excellent docs!)
3. **SQLAlchemy ORM** — A more powerful way to work with databases in Python
4. **Environment variables** — Use `.env` files to store configuration (e.g. API keys)
5. **Authentication** — Add user login with JWT tokens (`python-jose` library)
6. **Testing** — Write automated tests with `pytest` and `httpx`
7. **Docker** — Package your app so it runs anywhere
8. **Frontend** — Connect this backend to a React, Vue, or plain HTML frontend

Good luck, and enjoy the build! 🛹
