# =============================================================================
# weather_app.py  –  Beginner Weather App
# =============================================================================
#
# WHAT THIS FILE TEACHES YOU:
#   1. Variables and data types (str, int, float, dict)
#   2. User input with the input() function
#   3. Functions – how to define and call them
#   4. Conditional statements (if / elif / else)
#   5. Working with external libraries (requests)
#   6. Parsing JSON data (like a Python dictionary)
#   7. Error handling (try / except)
#   8. String formatting with f-strings
#
# HOW TO RUN:
#   python weather_app.py
#
# =============================================================================

# ── STEP 1: Import libraries ──────────────────────────────────────────────────
#
# Python comes with a "standard library" of built-in modules.
# We can also install EXTRA libraries using pip (e.g. pip install requests).
#
# `requests` lets us make HTTP calls to web APIs — just like a browser does
# when it loads a web page, except we get raw data back instead of HTML.

import os       # built-in module for reading environment variables
import requests  # third-party library (install with: pip install requests)


# ── STEP 2: Define constants ──────────────────────────────────────────────────
#
# A CONSTANT is a variable whose value never changes while the program runs.
# In Python we write constants in UPPER_CASE by convention.
#
# BEST PRACTICE – never commit secret keys to source code!
# Store your key in an environment variable instead:
#
#   On macOS / Linux:
#     export OPENWEATHER_API_KEY="your_key_here"
#
#   On Windows (Command Prompt):
#     set OPENWEATHER_API_KEY=your_key_here
#
# os.getenv("VAR_NAME", "default") reads the environment variable called
# VAR_NAME and falls back to "default" when it is not set.

API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")

# This is the base URL for the OpenWeatherMap "current weather" endpoint.
# We will add the city name and our key to it later.
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


# ── STEP 3: Define helper functions ──────────────────────────────────────────
#
# A FUNCTION is a reusable block of code.
# Syntax:
#   def function_name(parameter1, parameter2):
#       # code goes here
#       return result
#
# PARAMETERS are the inputs the function needs.
# RETURN VALUE is what the function sends back to the caller.

def get_weather(city_name):
    """
    Fetch current weather data for a given city.

    Parameters:
        city_name (str): The name of the city to look up.

    Returns:
        dict: A dictionary containing weather data, or None if the request
              failed.

    LEARNING NOTE – Docstrings:
        The triple-quoted text right after `def` is called a *docstring*.
        It documents what the function does. It is good practice to write one
        for every function you create.
    """

    # Build the URL by combining the base URL with our parameters.
    # `params` is a Python DICTIONARY – a collection of key/value pairs
    # written as {key: value, key: value, ...}.
    params = {
        "q": city_name,       # city name (q = query)
        "appid": API_KEY,     # our API key
        "units": "metric",    # use Celsius; use "imperial" for Fahrenheit
    }

    # ── STEP 4: Error handling with try / except ──────────────────────────
    #
    # Network calls can fail (no internet, bad city name, invalid API key…).
    # A `try` block lets us attempt risky code; if something goes wrong Python
    # jumps to the matching `except` block instead of crashing.

    try:
        # Make an HTTP GET request and store the response.
        # `requests.get()` returns a Response object.
        response = requests.get(BASE_URL, params=params)

        # `response.status_code` is an integer (200 = OK, 404 = Not Found …).
        # Calling `.raise_for_status()` turns any 4xx / 5xx code into an
        # exception so we don't have to check manually.
        response.raise_for_status()

        # `.json()` parses the JSON text from the server into a Python dict.
        # JSON looks like: {"name": "London", "main": {"temp": 15.3}, ...}
        data = response.json()

        return data  # send the dictionary back to the caller

    except requests.exceptions.HTTPError as http_err:
        # This runs when the server returned an error status (e.g. 404).
        print(f"HTTP error: {http_err}")
    except requests.exceptions.ConnectionError:
        # This runs when we cannot reach the server at all.
        print("Connection error: please check your internet connection.")
    except requests.exceptions.RequestException as err:
        # Catch-all for any other requests-related error.
        print(f"An error occurred: {err}")

    # If we reach here, something went wrong – return None to signal failure.
    return None


def display_weather(data):
    """
    Print a nicely formatted weather report to the console.

    Parameters:
        data (dict): Weather data returned by get_weather().

    LEARNING NOTE – Accessing dictionary values:
        data["key"]        raises a KeyError if "key" is missing.
        data.get("key")    returns None (no crash) if "key" is missing.
        data.get("key", 0) returns 0 as a default if "key" is missing.
    """

    # ── STEP 5: Extract values from the nested dictionary ────────────────
    #
    # The API returns nested JSON.  In Python this becomes nested dicts:
    #   data["main"]["temp"]  →  the temperature value deep inside the dict

    city = data.get("name", "Unknown city")
    country = data.get("sys", {}).get("country", "")

    # data["main"] is itself a dictionary.
    main = data.get("main", {})
    temp = main.get("temp")          # current temperature (float or None)
    feels_like = main.get("feels_like")
    humidity = main.get("humidity", "N/A")  # percentage

    # data["weather"] is a LIST (Python list = ordered collection).
    # We take the first element [0] which contains the description.
    weather_list = data.get("weather", [{}])
    description = weather_list[0].get("description", "N/A")

    wind = data.get("wind", {})
    wind_speed = wind.get("speed", "N/A")   # metres per second

    # ── STEP 6: f-strings (formatted string literals) ────────────────────
    #
    # Prefix a string with `f` and embed expressions inside `{ }`.
    # Example:  f"Hello, {name}!"  →  "Hello, Alice!"
    #
    # You can also format numbers:
    #   f"{temp:.1f}"  →  round to 1 decimal place

    print("\n" + "=" * 40)
    print(f"  Weather in {city}, {country}")
    print("=" * 40)
    print(f"  Description : {description.capitalize()}")
    # Use the format specifier only when the value is a number; show "N/A"
    # otherwise so the app does not crash when the API returns incomplete data.
    temp_str = f"{temp:.1f}" if isinstance(temp, (int, float)) else "N/A"
    feels_str = f"{feels_like:.1f}" if isinstance(feels_like, (int, float)) else "N/A"
    print(f"  Temperature : {temp_str} °C  (feels like {feels_str} °C)")
    print(f"  Humidity    : {humidity} %")
    print(f"  Wind speed  : {wind_speed} m/s")
    print("=" * 40 + "\n")


# ── STEP 7: The main function ─────────────────────────────────────────────────
#
# By convention, the entry point of a script is put in a function called
# `main()`.  This keeps code organised and makes it easy to test.

def main():
    """Run the weather app."""

    print("=" * 40)
    print("  🌤️  Python Weather App")
    print("=" * 40)

    # ── STEP 8: User input ────────────────────────────────────────────────
    #
    # `input(prompt)` prints `prompt`, waits for the user to type something,
    # and returns what they typed as a STRING.
    # `.strip()` removes any accidental leading/trailing spaces.

    city = input("Enter a city name: ").strip()

    # ── STEP 9: Conditional statement ────────────────────────────────────
    #
    # `if` checks whether the condition is True.
    # An empty string "" is "falsy" in Python, so `not city` is True when
    # the user pressed Enter without typing anything.

    if not city:
        print("No city entered. Please try again.")
        return  # exit the function early

    # Call our function and store the returned dictionary.
    data = get_weather(city)

    # Check whether we actually got data back before trying to display it.
    if data is None:
        print(f"Could not retrieve weather data for '{city}'.")
    else:
        display_weather(data)


# ── STEP 10: The if __name__ == "__main__" guard ──────────────────────────────
#
# When Python runs a .py file directly it sets the special variable
# __name__ to "__main__".
# When the file is IMPORTED by another file, __name__ is set to the
# module name instead.
#
# This guard ensures that main() is only called when we run THIS file
# directly, not when it is imported as a module elsewhere.

if __name__ == "__main__":
    main()
