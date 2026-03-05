"""
app/weather/service.py — Business logic for fetching weather data.

LEARNING NOTE: What is a "service" layer?
    In well-structured apps, we separate concerns into layers:
        router.py  → Handles HTTP (what routes exist, what they return)
        service.py → Business logic (how to actually get/process data)

    This makes code easier to:
        - Test (you can test service.py without a running HTTP server)
        - Reuse (other parts of the app can call service functions too)
        - Read (each file has a single, clear purpose)

LEARNING NOTE: What is Open-Meteo?
    Open-Meteo is a FREE, open-source weather API.
    No account or API key needed! 
    Docs: https://open-meteo.com/en/docs

    We use two of its endpoints:
        1. Geocoding API  → city name → latitude/longitude
        2. Forecast API   → lat/lon    → 7-day weather data

LEARNING NOTE: Async functions (async/await)
    FastAPI is an "async" framework — it can handle many requests at once
    without waiting for each to finish before starting the next.

    `async def` defines an asynchronous function.
    `await` pauses execution until the awaited operation finishes,
    but meanwhile the server can handle other requests.

    Think of it like ordering food at a restaurant:
        - Synchronous: waiter takes order, WAITS in kitchen, then takes next order.
        - Async: waiter takes order, gives it to kitchen, takes MORE orders while
                 kitchen is cooking. Then delivers food when it's ready.
"""

import httpx  # Third-party library for making HTTP requests (async-friendly)
from typing import Optional
from app.models import DailyWeather, GeocodingResult, WeatherForecastResponse

# ── API Base URLs ─────────────────────────────────────────────────────────────
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# ── WMO Weather Code Mapping ──────────────────────────────────────────────────
# LEARNING NOTE:
#   Open-Meteo returns a "WMO weather code" — a number like 0, 1, 61, etc.
#   These codes are from the World Meteorological Organisation (WMO).
#   We map them to human-readable descriptions using a Python dictionary.
#
#   A dictionary (dict) stores key-value pairs:
#       {key: value, key: value, ...}
#   You look up a value by its key: WMO_CODES[0] → "Clear sky"
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight showers",
    81: "Moderate showers",
    82: "Violent showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


def decode_weather_code(code: int) -> str:
    """
    Convert a WMO weather code integer to a human-readable string.

    LEARNING NOTE:
        dict.get(key, default) returns the value for `key` if it exists,
        or `default` if the key is not found.
        This prevents a KeyError if we receive an unknown code.

    Args:
        code: WMO weather interpretation code (integer)

    Returns:
        A human-readable weather condition string.
    """
    return WMO_CODES.get(code, f"Unknown condition (code {code})")


async def geocode_city(city: str) -> Optional[GeocodingResult]:
    """
    Look up a city name and return its coordinates + timezone.

    LEARNING NOTE: What is geocoding?
        Geocoding = converting a place name ("Kuala Lumpur") into
        geographic coordinates (latitude 3.1478, longitude 101.6953).
        Weather APIs need coordinates, not city names.

    LEARNING NOTE: httpx.AsyncClient
        httpx is like Python's built-in `requests` library, but supports async.
        `async with` is a context manager — it opens the client, lets us use it
        inside the block, and automatically closes it when the block ends.
        This is important to avoid "connection leaks".

    Args:
        city: City name as a string (e.g. "Kuala Lumpur")

    Returns:
        GeocodingResult if city found, None if city not found.
    """
    # LEARNING NOTE:
    #   "params" are query string parameters appended to the URL.
    #   e.g. ?name=Kuala+Lumpur&count=1&language=en&format=json
    params = {
        "name": city,
        "count": 1,          # We only want the top result
        "language": "en",
        "format": "json",
    }

    async with httpx.AsyncClient() as client:
        # LEARNING NOTE:
        #   await client.get(url, params=params) sends a GET HTTP request.
        #   We "await" it because it's a network call — takes time.
        response = await client.get(GEOCODING_URL, params=params)

        # LEARNING NOTE:
        #   response.raise_for_status() raises an exception if the server
        #   returned an error status code (4xx or 5xx).
        response.raise_for_status()

        # LEARNING NOTE:
        #   response.json() parses the JSON text into a Python dictionary.
        data = response.json()

    # "results" key contains a list of matching cities
    results = data.get("results")
    if not results:
        return None  # City not found

    # Take the first (best) match
    first = results[0]

    return GeocodingResult(
        city=first.get("name", city),
        latitude=first["latitude"],
        longitude=first["longitude"],
        country=first.get("country", ""),
        timezone=first.get("timezone", "auto"),
    )


async def get_weather_forecast(city: str) -> WeatherForecastResponse:
    """
    Fetch a 7-day weather forecast for the given city using Open-Meteo.

    Flow:
        1. Geocode the city → get lat/lon + timezone
        2. Call Open-Meteo forecast API with those coordinates
        3. Parse the response into our DailyWeather model
        4. Return a WeatherForecastResponse

    Args:
        city: City name string (e.g. "Petaling Jaya")

    Returns:
        WeatherForecastResponse containing a 7-day forecast list.

    Raises:
        ValueError: If the city cannot be found via geocoding.
        httpx.HTTPStatusError: If the weather API returns an error.
    """
    # ── Step 1: Geocode the city ───────────────────────────────────────────────
    geo = await geocode_city(city)
    if geo is None:
        # LEARNING NOTE:
        #   raise ValueError(...) throws an exception that will be caught
        #   by the router and turned into a 404 HTTP response.
        raise ValueError(f"City '{city}' not found. Please check the spelling.")

    # ── Step 2: Fetch forecast ─────────────────────────────────────────────────
    params = {
        "latitude": geo.latitude,
        "longitude": geo.longitude,
        "timezone": geo.timezone,
        "forecast_days": 7,
        # "daily" specifies which variables we want per day:
        "daily": [
            "temperature_2m_max",      # Max temperature in °C
            "temperature_2m_min",      # Min temperature in °C
            "precipitation_sum",       # Total rain/snow in mm
            "windspeed_10m_max",       # Max wind speed in km/h
            "weathercode",             # WMO weather condition code
            "sunrise",                 # Sunrise time
            "sunset",                  # Sunset time
        ],
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(FORECAST_URL, params=params)
        response.raise_for_status()
        data = response.json()

    # ── Step 3: Parse the response ────────────────────────────────────────────
    # LEARNING NOTE:
    #   Open-Meteo returns "parallel lists" for daily data:
    #       daily["time"]                 = ["2026-03-04", "2026-03-05", ...]
    #       daily["temperature_2m_max"]   = [31.2, 30.5, ...]
    #       daily["temperature_2m_min"]   = [24.1, 23.8, ...]
    #   We use zip() to combine these lists element-by-element.
    daily = data["daily"]

    # zip() takes multiple lists and returns tuples of matching elements.
    # Example: zip([1,2], ["a","b"]) → (1,"a"), (2,"b")
    forecast_days = []
    for (
        day_date,
        temp_max,
        temp_min,
        precipitation,
        windspeed,
        code,
        sunrise,
        sunset,
    ) in zip(
        daily["time"],
        daily["temperature_2m_max"],
        daily["temperature_2m_min"],
        daily["precipitation_sum"],
        daily["windspeed_10m_max"],
        daily["weathercode"],
        daily["sunrise"],
        daily["sunset"],
    ):
        forecast_days.append(
            DailyWeather(
                date=day_date,
                temp_max=temp_max,
                temp_min=temp_min,
                precipitation_mm=precipitation if precipitation is not None else 0.0,
                windspeed_max=windspeed if windspeed is not None else 0.0,
                condition=decode_weather_code(code),
                sunrise=sunrise,
                sunset=sunset,
            )
        )

    # ── Step 4: Return formatted response ─────────────────────────────────────
    return WeatherForecastResponse(
        city=geo.city,
        latitude=geo.latitude,
        longitude=geo.longitude,
        timezone=geo.timezone,
        forecast=forecast_days,
    )
