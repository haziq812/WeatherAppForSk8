"""
app/models.py — Pydantic data models (schemas) for request/response validation.

LEARNING NOTE: What is Pydantic?
    Pydantic is a library for data validation. It works by letting you
    describe the "shape" of your data using Python classes.

    When someone sends data to your API, Pydantic automatically:
        1. Checks that all required fields are present
        2. Validates that the data types are correct
        3. Converts data to the right type when possible (e.g. "1" → 1)
        4. Returns a clear error message if something is wrong

LEARNING NOTE: What is a Schema?
    A schema is a "blueprint" that describes what data looks like.
    For example, a PlannerEventCreate schema says:
        "A new event must have a date, a title, and optionally other fields."

LEARNING NOTE: What is BaseModel?
    Every Pydantic model must inherit from BaseModel.
    "Inherit" means our class gets all the built-in Pydantic features.
    Think of BaseModel as a template we extend.

LEARNING NOTE: Field types in Python (type hints):
    str      — a text string, e.g. "hello"
    int      — a whole number, e.g. 42
    float    — a decimal number, e.g. 3.14
    bool     — True or False
    Optional  — the value can be None (missing/null)
    List     — a list of values, e.g. [1, 2, 3]
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# ═══════════════════════════════════════════════════════════════════
#  WEATHER MODELS
# ═══════════════════════════════════════════════════════════════════

class DailyWeather(BaseModel):
    """Represents the weather forecast for a single day."""

    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2026-03-04")
    temp_max: float = Field(..., description="Maximum temperature in °C")
    temp_min: float = Field(..., description="Minimum temperature in °C")
    precipitation_mm: float = Field(..., description="Total rainfall in millimetres")
    windspeed_max: float = Field(..., description="Maximum wind speed in km/h")
    condition: str = Field(..., description="Human-readable weather condition, e.g. 'Sunny'")
    sunrise: str = Field(..., description="Sunrise time in ISO format")
    sunset: str = Field(..., description="Sunset time in ISO format")
    # LEARNING NOTE: ... (Ellipsis) means the field is REQUIRED.


class WeatherForecastResponse(BaseModel):
    """
    The full response returned by GET /weather/forecast.
    Contains the city name and a list of 7-day forecasts.
    """

    city: str = Field(..., description="Name of the requested city")
    latitude: float = Field(..., description="Latitude coordinate used")
    longitude: float = Field(..., description="Longitude coordinate used")
    timezone: str = Field(..., description="Timezone used for the forecast")
    forecast: List[DailyWeather] = Field(..., description="7-day daily forecast list")


class GeocodingResult(BaseModel):
    """Internal model used when looking up a city's coordinates."""

    city: str
    latitude: float
    longitude: float
    country: str
    timezone: str


# ═══════════════════════════════════════════════════════════════════
#  PLANNER MODELS
# ═══════════════════════════════════════════════════════════════════

class PlannerEventCreate(BaseModel):
    """
    Schema for CREATING a new planner event.
    This is what the client (frontend) sends to us.

    LEARNING NOTE:
        Optional[str] = None means this field is not required.
        If the client doesn't send it, it defaults to None.
    """

    date: str = Field(
        ...,
        description="Event date in YYYY-MM-DD format",
        example="2026-03-07",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Short event title",
        example="Morning run at the park",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional longer description",
        example="5km jog before work",
    )
    activity_type: Optional[str] = Field(
        "general",
        description="One of: outdoor, indoor, travel, general",
        example="outdoor",
    )
    weather_dependent: Optional[bool] = Field(
        False,
        description="Set to true if this activity might be cancelled due to bad weather",
    )


class PlannerEventUpdate(BaseModel):
    """
    Schema for UPDATING an existing planner event.
    All fields are optional — you only need to send what you want to change.
    """

    date: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    activity_type: Optional[str] = None
    weather_dependent: Optional[bool] = None


class PlannerEventResponse(BaseModel):
    """
    Schema for a planner event returned in API responses.
    Includes all fields including the auto-generated ones (id, created_at).
    """

    id: int = Field(..., description="Unique auto-incremented ID")
    date: str
    title: str
    description: Optional[str]
    activity_type: str
    weather_dependent: bool
    created_at: str = Field(..., description="Timestamp of when the event was created")


class PlannerWeekResponse(BaseModel):
    """
    Response for GET /planner/week?city=...
    Combines planner events with their matching weather forecasts.
    """

    city: str
    events: List[PlannerEventResponse]
    forecast: List[DailyWeather]
