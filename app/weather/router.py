"""
app/weather/router.py — HTTP routes for weather-related endpoints.

LEARNING NOTE: What is a Router?
    A "router" defines API endpoints (URLs) and maps them to functions.
    When your frontend calls GET /weather/forecast?city=London,
    FastAPI finds the matching route function and runs it.

    APIRouter is like a mini FastAPI app specifically for one feature area.
    In main.py we attach it to the full app with a "/weather" prefix.

AVAILABLE ENDPOINTS (after prefix /weather):
    GET /weather/forecast?city=<city_name>
        → Returns 7-day forecast for the specified city

    GET /weather/forecast/today?city=<city_name>
        → Returns just today's forecast

HTTP STATUS CODES (quick reference):
    200 OK             — Request succeeded
    400 Bad Request    — Client sent invalid input
    404 Not Found      — The requested resource doesn't exist
    422 Unprocessable  — FastAPI validation error (wrong data type etc.)
    500 Internal Error — Something went wrong on the server side
"""

from fastapi import APIRouter, HTTPException, Query
from app.weather.service import get_weather_forecast
from app.models import WeatherForecastResponse, DailyWeather

# LEARNING NOTE:
#   APIRouter() creates a router object.
#   We give it a prefix tag "Weather" so it appears grouped in /docs.
router = APIRouter()


@router.get(
    "/forecast",
    response_model=WeatherForecastResponse,
    summary="Get 7-day weather forecast",
    description=(
        "Returns a full 7-day weather forecast for the given city. "
        "Uses Open-Meteo API — no API key required."
    ),
)
async def get_forecast(
    city: str = Query(
        ...,                            # Required parameter
        description="City name to get the forecast for",
        example="Kuala Lumpur",
        min_length=1,
    )
) -> WeatherForecastResponse:
    """
    Fetch and return a 7-day weather forecast.

    LEARNING NOTE: Query Parameters
        Query parameters appear after the `?` in a URL:
            /forecast?city=London
        FastAPI automatically reads them from the URL.

        Query(...) means it's REQUIRED.
        Query("default") would make it optional with a default value.

    LEARNING NOTE: HTTPException
        When something goes wrong, we raise HTTPException.
        FastAPI converts it to a proper JSON error response automatically.
        Example: {"detail": "City not found"} with status 404.

    Args:
        city: City name provided as a query parameter.

    Returns:
        WeatherForecastResponse with 7-day forecast data.
    """
    try:
        forecast = await get_weather_forecast(city)
        return forecast
    except ValueError as e:
        # City not found during geocoding
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Unexpected error (network issue, API down, etc.)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch weather data: {str(e)}",
        )


@router.get(
    "/forecast/today",
    response_model=DailyWeather,
    summary="Get today's weather",
    description="Returns only today's weather forecast for the given city.",
)
async def get_today_forecast(
    city: str = Query(..., description="City name", example="Petaling Jaya")
) -> DailyWeather:
    """
    Fetch the full 7-day forecast but return only today's data.

    LEARNING NOTE:
        We reuse get_weather_forecast() instead of writing new logic.
        This is called "code reuse" — a core programming principle.
        The forecast[0] index gets the first item in the list (today).

    Args:
        city: City name string.

    Returns:
        DailyWeather for today only.
    """
    try:
        forecast = await get_weather_forecast(city)
        # LEARNING NOTE:
        #   Lists in Python are zero-indexed: first item is at index [0].
        return forecast.forecast[0]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch weather data: {str(e)}",
        )
