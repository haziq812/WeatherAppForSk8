# =============================================================================
# weather_app_advanced.py  –  Intermediate / OOP Weather App
# =============================================================================
#
# WHAT THIS FILE TEACHES YOU (beyond the beginner version):
#   1. Classes and Objects (Object-Oriented Programming)
#   2. Class attributes vs instance attributes
#   3. Special / "dunder" methods (__init__, __str__, __repr__)
#   4. Properties (@property decorator)
#   5. Static methods vs instance methods
#   6. Dataclasses (Python 3.7+) for clean data containers
#   7. Type hints / annotations
#   8. Loops with `for` and list comprehensions
#   9. Multiple city comparison
#
# HOW TO RUN:
#   python weather_app_advanced.py
#
# =============================================================================

import requests
from dataclasses import dataclass  # built-in module for simple data containers


# ── PART 1: Data container using @dataclass ───────────────────────────────────
#
# A DATACLASS is a special class decorator that automatically generates
# __init__, __repr__, and __eq__ methods based on the fields you define.
# It removes a lot of repetitive boilerplate code.
#
# TYPE HINTS (e.g. `name: str`) tell readers (and tools) what type each
# attribute should be.  Python does NOT enforce them at runtime, but they
# make code much easier to understand.

@dataclass
class WeatherData:
    """Stores weather information for one city."""

    city: str
    country: str
    temperature: float      # Celsius
    feels_like: float       # Celsius
    humidity: int           # percentage
    description: str
    wind_speed: float       # metres per second

    # ── Special method: __str__ ───────────────────────────────────────────
    #
    # Python calls __str__(self) when you use str(obj) or print(obj).
    # It should return a human-readable string representation.

    def __str__(self) -> str:
        return (
            f"{self.city}, {self.country}: "
            f"{self.temperature:.1f}°C, {self.description}"
        )

    # ── Property ──────────────────────────────────────────────────────────
    #
    # A @property turns a method into an attribute you can access like
    # `obj.comfort_level` (no parentheses).
    # Use it to expose derived / computed values.

    @property
    def comfort_level(self) -> str:
        """Return a human-friendly comfort label based on temperature."""
        if self.temperature < 0:
            return "❄️  Freezing"
        elif self.temperature < 10:
            return "🧥 Cold"
        elif self.temperature < 20:
            return "🌤️  Mild"
        elif self.temperature < 30:
            return "☀️  Warm"
        else:
            return "🔥 Hot"


# ── PART 2: Service class for API calls ──────────────────────────────────────
#
# A CLASS bundles related data (attributes) and behaviour (methods) together.
#
# Syntax:
#   class ClassName:
#       def __init__(self, param):   # constructor – called when creating obj
#           self.param = param       # instance attribute
#
# `self` refers to the specific INSTANCE of the class.

class WeatherService:
    """Handles communication with the OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    # ── Constructor ───────────────────────────────────────────────────────
    #
    # __init__ runs automatically whenever you create a new instance:
    #   service = WeatherService("my_key")
    #
    # `api_key` is stored on `self` so every method in the class can use it.

    def __init__(self, api_key: str):
        self.api_key = api_key

    # ── Instance method ───────────────────────────────────────────────────
    #
    # An instance method always receives `self` as its first argument.
    # It can read / modify instance attributes.

    def fetch(self, city_name: str) -> WeatherData | None:
        """
        Fetch weather for one city.

        Parameters:
            city_name (str): City to query.

        Returns:
            WeatherData object, or None on failure.
        """
        params = {
            "q": city_name,
            "appid": self.api_key,
            "units": "metric",
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return self._parse(response.json())
        except requests.exceptions.HTTPError as err:
            print(f"  ✗ HTTP error for '{city_name}': {err}")
        except requests.exceptions.ConnectionError:
            print("  ✗ Connection error. Check your internet connection.")
        except requests.exceptions.RequestException as err:
            print(f"  ✗ Request failed for '{city_name}': {err}")
        return None

    def fetch_multiple(self, city_names: list[str]) -> list[WeatherData]:
        """
        Fetch weather for several cities.

        LEARNING NOTE – List comprehension:
            [expression for item in iterable if condition]

            This is a compact way to build a list.  The code below is
            equivalent to:

                results = []
                for name in city_names:
                    data = self.fetch(name)
                    if data is not None:
                        results.append(data)
                return results

        Parameters:
            city_names (list[str]): List of city names.

        Returns:
            list[WeatherData]: Successfully retrieved weather records.
        """
        return [
            data
            for name in city_names
            if (data := self.fetch(name)) is not None   # walrus operator :=
        ]

    # ── Static method ─────────────────────────────────────────────────────
    #
    # A @staticmethod does NOT receive `self`.  Use it for helper logic that
    # belongs conceptually to the class but doesn't need instance data.

    @staticmethod
    def _parse(raw: dict) -> WeatherData:
        """Convert a raw API response dict into a WeatherData object."""
        main = raw.get("main", {})
        weather_list = raw.get("weather", [{}])
        wind = raw.get("wind", {})

        return WeatherData(
            city=raw.get("name", "Unknown"),
            country=raw.get("sys", {}).get("country", ""),
            temperature=main.get("temp", 0.0),
            feels_like=main.get("feels_like", 0.0),
            humidity=main.get("humidity", 0),
            description=weather_list[0].get("description", ""),
            wind_speed=wind.get("speed", 0.0),
        )


# ── PART 3: Display helpers ───────────────────────────────────────────────────

def print_weather_card(wd: WeatherData) -> None:
    """Print a single weather card."""
    print(f"\n  {'=' * 36}")
    print(f"  {wd.city}, {wd.country}  –  {wd.comfort_level}")
    print(f"  {'─' * 36}")
    print(f"  Description : {wd.description.capitalize()}")
    print(f"  Temperature : {wd.temperature:.1f} °C "
          f"(feels like {wd.feels_like:.1f} °C)")
    print(f"  Humidity    : {wd.humidity} %")
    print(f"  Wind speed  : {wd.wind_speed} m/s")
    print(f"  {'=' * 36}\n")


def print_comparison_table(weather_list: list[WeatherData]) -> None:
    """
    Print a comparison table for multiple cities.

    LEARNING NOTE – String .ljust() / .rjust():
        "text".ljust(20)  →  "text                "  (left-align, pad right)
        "42".rjust(6)     →  "    42"               (right-align, pad left)
    These are useful for creating aligned columns in plain-text output.
    """
    if not weather_list:
        print("No data to display.")
        return

    # Column widths
    col_city = 16
    col_temp = 8
    col_hum = 10
    col_desc = 20

    header = (
        "City".ljust(col_city)
        + "Temp(°C)".rjust(col_temp)
        + "Humidity".rjust(col_hum)
        + "  Description".ljust(col_desc)
    )
    separator = "─" * len(header)

    print(f"\n  {separator}")
    print(f"  {header}")
    print(f"  {separator}")

    for wd in weather_list:
        row = (
            wd.city.ljust(col_city)
            + f"{wd.temperature:.1f}".rjust(col_temp)
            + f"{wd.humidity}%".rjust(col_hum)
            + f"  {wd.description.capitalize()}"
        )
        print(f"  {row}")

    print(f"  {separator}\n")


# ── PART 4: Main entry point ──────────────────────────────────────────────────

def main() -> None:
    """Run the advanced weather app."""

    print("=" * 44)
    print("  🌤️  Python Weather App – Advanced Edition")
    print("=" * 44)

    api_key = input("Enter your OpenWeatherMap API key: ").strip()
    if not api_key:
        print("API key is required.")
        return

    service = WeatherService(api_key)

    # ── for loop ──────────────────────────────────────────────────────────
    #
    # A `for` loop iterates over any iterable (list, string, range, …).
    # Here we loop until the user types "quit".

    while True:
        print("\nOptions:")
        print("  1 – Look up a single city")
        print("  2 – Compare multiple cities")
        print("  q – Quit")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "1":
            city = input("City name: ").strip()
            if city:
                wd = service.fetch(city)
                if wd:
                    print_weather_card(wd)

        elif choice == "2":
            raw = input("Enter city names separated by commas: ").strip()
            # str.split(separator) splits a string into a list:
            #   "a, b, c".split(",")  →  ["a", " b", " c"]
            # We then strip whitespace from each element:
            cities = [c.strip() for c in raw.split(",") if c.strip()]
            if cities:
                print(f"\nFetching data for {len(cities)} cities…")
                results = service.fetch_multiple(cities)
                print_comparison_table(results)

        elif choice == "q":
            print("Goodbye! 👋")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or q.")


if __name__ == "__main__":
    main()
