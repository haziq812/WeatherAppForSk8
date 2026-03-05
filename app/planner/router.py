"""
app/planner/router.py — HTTP routes for the weekly planner.

AVAILABLE ENDPOINTS (after prefix /planner):
    GET  /planner/                      → List all events
    POST /planner/                      → Create a new event
    GET  /planner/{id}                  → Get one event by ID
    PUT  /planner/{id}                  → Update an event
    DELETE /planner/{id}                → Delete an event
    GET  /planner/week?city=<city>      → Week view: events + weather forecast

HTTP METHODS (quick reference):
    GET    — Read/retrieve data (does NOT modify anything)
    POST   — Create new data
    PUT    — Update/replace existing data
    DELETE — Remove data

LEARNING NOTE: Path Parameters vs Query Parameters
    Path parameter:   /planner/{id}   → /planner/42
        Used to identify a specific resource (e.g., a specific event).
        Declared with {curly_braces} in the route string.

    Query parameter:  /planner/?date=2026-03-04
        Used for filtering, search, optional options.
        Appears after the ? in the URL.
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from datetime import date, timedelta

from app.planner.service import (
    create_event,
    get_event_by_id,
    get_all_events,
    get_events_by_date_range,
    update_event,
    delete_event,
)
from app.weather.service import get_weather_forecast
from app.models import (
    PlannerEventCreate,
    PlannerEventUpdate,
    PlannerEventResponse,
    PlannerWeekResponse,
)

router = APIRouter()


# ── CREATE ────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=PlannerEventResponse,
    status_code=201,           # 201 Created is the standard for successful POST
    summary="Create a planner event",
    description="Add a new event to your week planner.",
)
def create_planner_event(event: PlannerEventCreate) -> PlannerEventResponse:
    """
    Create a new planner event.

    LEARNING NOTE: Request Body
        For POST/PUT requests, data is sent in the request "body" (not the URL).
        FastAPI automatically reads the JSON body and validates it against
        the PlannerEventCreate schema.

        Example request body:
            {
                "date": "2026-03-07",
                "title": "Morning run",
                "activity_type": "outdoor",
                "weather_dependent": true
            }

    Args:
        event: Parsed and validated PlannerEventCreate from the request body.

    Returns:
        The newly created event with its assigned ID.
    """
    return create_event(event)


# ── READ ALL ──────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[PlannerEventResponse],
    summary="List all planner events",
    description="Returns all events in the planner, sorted by date.",
)
def list_planner_events() -> List[PlannerEventResponse]:
    """
    Return all planner events.

    LEARNING NOTE: List[PlannerEventResponse] return type
        This means the function returns a list where each item
        is a PlannerEventResponse. FastAPI serialises this into a JSON array.
    """
    return get_all_events()


# ── READ ONE ──────────────────────────────────────────────────────────────────

@router.get(
    "/{event_id}",
    response_model=PlannerEventResponse,
    summary="Get a single planner event",
)
def get_planner_event(
    event_id: int = Path(..., description="The ID of the event to retrieve", gt=0)
) -> PlannerEventResponse:
    """
    Return a single planner event by its ID.

    LEARNING NOTE: Path()
        Path(...) is used to annotate path parameters with extra validation.
        gt=0 means "greater than 0" — rejects IDs of 0 or negative numbers.
        FastAPI returns a 422 error automatically if this check fails.

    Args:
        event_id: The integer ID from the URL path (e.g. /planner/5 → 5)

    Returns:
        PlannerEventResponse for the found event.
    """
    event = get_event_by_id(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail=f"Event with id={event_id} not found.")
    return event


# ── UPDATE ────────────────────────────────────────────────────────────────────

@router.put(
    "/{event_id}",
    response_model=PlannerEventResponse,
    summary="Update a planner event",
    description="Update one or more fields of an existing event. Only send the fields you want to change.",
)
def update_planner_event(
    event_id: int = Path(..., description="The ID of the event to update", gt=0),
    updates: PlannerEventUpdate = ...,
) -> PlannerEventResponse:
    """
    Partially update an existing planner event.

    LEARNING NOTE: Partial updates
        We accept PlannerEventUpdate which has all Optional fields.
        Only fields you include in the JSON body will be changed.
        Fields you leave out stay unchanged.

    Args:
        event_id: ID from the URL path.
        updates:  JSON body with the fields to update.

    Returns:
        The updated PlannerEventResponse.
    """
    updated = update_event(event_id, updates)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Event with id={event_id} not found.")
    return updated


# ── DELETE ────────────────────────────────────────────────────────────────────

@router.delete(
    "/{event_id}",
    status_code=204,           # 204 No Content — success but nothing to return
    summary="Delete a planner event",
)
def delete_planner_event(
    event_id: int = Path(..., description="The ID of the event to delete", gt=0)
):
    """
    Delete a planner event by ID.

    LEARNING NOTE: status_code=204
        HTTP 204 means "success, but there's no content to return."
        We return None here instead of a response body.

    Args:
        event_id: ID from the URL path.
    """
    deleted = delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Event with id={event_id} not found.")
    return None  # 204 No Content


# ── WEEK VIEW (COMBINED WEATHER + PLANNER) ────────────────────────────────────

@router.get(
    "/week/overview",
    response_model=PlannerWeekResponse,
    summary="Week overview: events + weather",
    description=(
        "Returns all planner events for the next 7 days, combined with "
        "the weather forecast for those days. Useful for the week planner UI."
    ),
)
async def get_week_overview(
    city: str = Query(..., description="City for weather forecast", example="Kuala Lumpur")
) -> PlannerWeekResponse:
    """
    Combine the 7-day weather forecast with planner events for that week.

    LEARNING NOTE: async def vs def
        This route is `async def` because it calls an async function
        (get_weather_forecast), which makes HTTP requests.
        Regular planner functions are plain `def` because they only
        touch the local database (fast, synchronous).

    LEARNING NOTE: date.today() and timedelta
        date.today() returns today's date as a date object.
        timedelta(days=6) creates a "duration" of 6 days.
        Adding them gives a date 6 days from now.
        isoformat() converts the date to a "YYYY-MM-DD" string.

    Args:
        city: City name for the weather forecast.

    Returns:
        PlannerWeekResponse with both events and forecast.
    """
    today = date.today()
    week_end = today + timedelta(days=6)  # 7 days total (today + 6 more)

    # Fetch both weather and planner events (weather needs await, DB does not)
    try:
        forecast_response = await get_weather_forecast(city)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather fetch failed: {str(e)}")

    events = get_events_by_date_range(
        start_date=today.isoformat(),        # "2026-03-04"
        end_date=week_end.isoformat(),       # "2026-03-10"
    )

    return PlannerWeekResponse(
        city=forecast_response.city,
        events=events,
        forecast=forecast_response.forecast,
    )
