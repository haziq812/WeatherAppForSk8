import json
import os
import sqlite3
from datetime import datetime, timezone

import requests
from flask import Flask, g, jsonify, render_template, request

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(__file__), "sessions.db")
OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Skating condition helper
# ---------------------------------------------------------------------------

def skate_score(weather_day: dict) -> dict:
    """
    Return a score (0-100) and a human-readable label for how good a day is
    for skating based on weather conditions.

    Parameters come from the OpenWeatherMap forecast 'list' item.
    """
    score = 100
    reasons = []

    # Rain / snow
    pop = weather_day.get("pop", 0)  # probability of precipitation, range 0–1 (OpenWeatherMap)
    if pop > 0.7:
        score -= 50
        reasons.append("High chance of rain/snow")
    elif pop > 0.4:
        score -= 25
        reasons.append("Moderate chance of precipitation")

    rain_mm = weather_day.get("rain", {}).get("3h", 0)
    snow_mm = weather_day.get("snow", {}).get("3h", 0)
    if rain_mm > 2 or snow_mm > 0:
        score -= 30
        reasons.append("Active precipitation")

    # Wind speed (m/s)
    wind_speed = weather_day.get("wind", {}).get("speed", 0)
    if wind_speed > 10:
        score -= 30
        reasons.append(f"Very windy ({wind_speed:.1f} m/s)")
    elif wind_speed > 6:
        score -= 15
        reasons.append(f"Gusty winds ({wind_speed:.1f} m/s)")

    # Temperature (°C)
    temp_c = weather_day.get("main", {}).get("temp", 20) - 273.15
    if temp_c < 5:
        score -= 30
        reasons.append(f"Too cold ({temp_c:.1f}°C)")
    elif temp_c < 10:
        score -= 15
        reasons.append(f"Chilly ({temp_c:.1f}°C)")
    elif temp_c > 38:
        score -= 25
        reasons.append(f"Very hot ({temp_c:.1f}°C)")
    elif temp_c > 32:
        score -= 10
        reasons.append(f"Hot ({temp_c:.1f}°C)")

    score = max(0, score)

    if score >= 75:
        label = "Great"
        badge = "success"
    elif score >= 50:
        label = "Good"
        badge = "info"
    elif score >= 25:
        label = "Fair"
        badge = "warning"
    else:
        label = "Poor"
        badge = "danger"

    return {"score": score, "label": label, "badge": badge, "reasons": reasons}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def weather():
    city = request.args.get("city", "").strip()
    api_key = request.args.get("api_key", "").strip()
    if not city:
        return jsonify({"error": "city is required"}), 400
    if not api_key:
        return jsonify({"error": "api_key is required"}), 400

    # Current weather
    current_url = f"{OPENWEATHER_BASE}/weather"
    current_resp = requests.get(
        current_url,
        params={"q": city, "appid": api_key},
        timeout=10,
    )
    if current_resp.status_code != 200:
        try:
            msg = current_resp.json().get("message", "Weather API error")
        except Exception:
            msg = "Weather API error"
        return jsonify({"error": msg}), current_resp.status_code

    current_data = current_resp.json()

    # 5-day / 3-hour forecast (40 entries)
    forecast_url = f"{OPENWEATHER_BASE}/forecast"
    forecast_resp = requests.get(
        forecast_url,
        params={"q": city, "appid": api_key},
        timeout=10,
    )
    forecast_data = forecast_resp.json() if forecast_resp.status_code == 200 else {}

    # Build daily summaries (pick the midday slot per day)
    daily = {}
    for item in forecast_data.get("list", []):
        dt_txt = item.get("dt_txt", "")
        day = dt_txt[:10]
        hour = dt_txt[11:13]
        if day not in daily or hour == "12":
            item["skate"] = skate_score(item)
            item["temp_c"] = round(item["main"]["temp"] - 273.15, 1)
            item["temp_f"] = round(item["temp_c"] * 9 / 5 + 32, 1)
            daily[day] = item

    current_data["temp_c"] = round(current_data["main"]["temp"] - 273.15, 1)
    current_data["temp_f"] = round(current_data["temp_c"] * 9 / 5 + 32, 1)
    current_data["skate"] = skate_score(current_data)

    return jsonify({"current": current_data, "forecast": list(daily.values())[:7]})


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM sessions ORDER BY date ASC"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/sessions", methods=["POST"])
def add_session():
    data = request.get_json(force=True)
    date = (data.get("date") or "").strip()
    location = (data.get("location") or "").strip()
    notes = (data.get("notes") or "").strip()
    if not date or not location:
        return jsonify({"error": "date and location are required"}), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO sessions (date, location, notes, created_at) VALUES (?, ?, ?, ?)",
        (date, location, notes, datetime.now(timezone.utc).isoformat()),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "date": date, "location": location, "notes": notes}), 201


@app.route("/api/sessions/<int:session_id>", methods=["DELETE"])
def delete_session(session_id):
    db = get_db()
    db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    db.commit()
    return jsonify({"deleted": session_id})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
