# Python Learning Guide 🐍

> **Goal:** Learn Python by building a real weather application from scratch.  
> No prior programming experience needed.

---

## Table of Contents

1. [What is Python?](#1-what-is-python)
2. [Setting Up Your Environment](#2-setting-up-your-environment)
3. [Variables and Data Types](#3-variables-and-data-types)
4. [Operators](#4-operators)
5. [String Formatting](#5-string-formatting)
6. [User Input](#6-user-input)
7. [Conditional Statements](#7-conditional-statements)
8. [Loops](#8-loops)
9. [Functions](#9-functions)
10. [Lists and Dictionaries](#10-lists-and-dictionaries)
11. [Error Handling](#11-error-handling)
12. [Modules and Imports](#12-modules-and-imports)
13. [Working with APIs](#13-working-with-apis)
14. [Object-Oriented Programming](#14-object-oriented-programming)
15. [Running the Weather App](#15-running-the-weather-app)
16. [Next Steps](#16-next-steps)

---

## 1. What is Python?

Python is a **high-level, general-purpose programming language** known for its clean, readable syntax.

**Why Python?**

- Easy to read — code looks almost like plain English.
- Huge ecosystem — thousands of free libraries for everything (AI, web, data, games…).
- Versatile — used at Google, Netflix, NASA, and by millions of developers worldwide.
- Great for beginners — fast feedback loop, no need to compile before running.

**How Python runs your code:**

```
You write code in a .py file
         ↓
Python interpreter reads the file top-to-bottom
         ↓
Each line is executed immediately
```

---

## 2. Setting Up Your Environment

### Install Python

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest **Python 3.x** installer for your operating system.
3. During installation, **check "Add Python to PATH"**.

Verify installation by opening a terminal and running:

```bash
python --version
# Expected: Python 3.x.x
```

### Install a Code Editor

We recommend **Visual Studio Code** (free):  
[https://code.visualstudio.com/](https://code.visualstudio.com/)

Install the **Python extension** from the VS Code marketplace for syntax highlighting and auto-completion.

### Install Project Dependencies

In your terminal, navigate to the project folder and run:

```bash
pip install -r requirements.txt
```

`pip` is Python's package installer. `requirements.txt` lists all the extra libraries this project needs.

---

## 3. Variables and Data Types

A **variable** is a named container that stores a value.

```python
# Assigning a value to a variable
city = "Kuala Lumpur"   # str  (text, always in quotes)
temperature = 31.5      # float (decimal number)
humidity = 80           # int   (whole number)
is_raining = False      # bool  (True or False)
```

### The Four Basic Data Types

| Type    | Example          | Description            |
|---------|------------------|------------------------|
| `str`   | `"Hello"`        | Text (string)          |
| `int`   | `42`             | Whole number           |
| `float` | `3.14`           | Decimal number         |
| `bool`  | `True` / `False` | Boolean (yes/no)       |

### Check the type of a variable

```python
print(type(city))        # <class 'str'>
print(type(temperature)) # <class 'float'>
print(type(humidity))    # <class 'int'>
```

### Convert between types

```python
age_str = "25"
age_int = int(age_str)   # convert string "25" → integer 25
temp_int = int(31.8)     # float → int: result is 31 (truncates decimal)
result = str(100)        # integer → string: "100"
```

> 💡 **Practice:** Open a Python file and create 5 variables representing weather data (city name, temperature, humidity, wind speed, description). Print each one.

---

## 4. Operators

### Arithmetic Operators

```python
a = 10
b = 3

print(a + b)   # 13  — addition
print(a - b)   # 7   — subtraction
print(a * b)   # 30  — multiplication
print(a / b)   # 3.333… — division (always returns float)
print(a // b)  # 3   — floor division (integer result)
print(a % b)   # 1   — modulo (remainder)
print(a ** b)  # 1000 — exponentiation (a to the power of b)
```

### Comparison Operators (return True or False)

```python
print(10 == 10)   # True  — equal to
print(10 != 5)    # True  — not equal to
print(10 > 5)     # True  — greater than
print(10 < 5)     # False — less than
print(10 >= 10)   # True  — greater than or equal to
print(10 <= 9)    # False — less than or equal to
```

### Logical Operators

```python
print(True and False)  # False — both must be True
print(True or False)   # True  — at least one must be True
print(not True)        # False — flips the boolean
```

---

## 5. String Formatting

There are three ways to build strings with variables.

### ❌ Old way — string concatenation (avoid)

```python
name = "Alice"
print("Hello, " + name + "!")  # works but messy
```

### ✅ Modern way — f-strings (recommended)

Prefix the string with `f` and put variables inside `{ }`:

```python
name = "Alice"
temp = 28.567

print(f"Hello, {name}!")                  # Hello, Alice!
print(f"Temperature: {temp:.1f}°C")       # Temperature: 28.6°C
print(f"Temperature: {temp:.0f}°C")       # Temperature: 29°C
```

**Format specifiers inside `{}`:**

| Specifier | Meaning                          | Example input | Output    |
|-----------|----------------------------------|---------------|-----------|
| `.1f`     | 1 decimal place, float           | `28.567`      | `28.6`    |
| `.2f`     | 2 decimal places, float          | `3.1`         | `3.10`    |
| `d`       | Integer                          | `42`          | `42`      |
| `>10`     | Right-align in a field of width 10 | `"hi"`      | `"        hi"` |
| `<10`     | Left-align in a field of width 10  | `"hi"`      | `"hi        "` |

### Useful string methods

```python
s = "  hello world  "

print(s.strip())         # "hello world"  — removes leading/trailing spaces
print(s.upper())         # "  HELLO WORLD  "
print(s.lower())         # "  hello world  "
print(s.title())         # "  Hello World  "
print(s.replace("o","0"))# "  hell0 w0rld  "
print(s.split(" "))      # split into a list by space
print(len("hello"))      # 5  — length of the string
```

---

## 6. User Input

`input()` pauses the program, shows a prompt, and returns what the user typed as a **string**.

```python
name = input("What is your name? ")
print(f"Hello, {name}!")
```

> ⚠️ **Important:** `input()` always returns a **string** even if the user types a number.
> Convert it if you need a number:
>
> ```python
> age = int(input("How old are you? "))
> ```

In the weather app:

```python
city = input("Enter a city name: ").strip()
```

`.strip()` removes any accidental spaces the user might have typed.

---

## 7. Conditional Statements

Allow your program to make decisions.

### Basic if / elif / else

```python
temperature = 35

if temperature > 30:
    print("It's hot outside!")
elif temperature > 20:
    print("It's warm.")
elif temperature > 10:
    print("It's mild.")
else:
    print("It's cold.")
```

**Rules:**
- Indentation (4 spaces) is **mandatory** in Python — it defines code blocks.
- `elif` = "else if" (you can have as many as you need).
- `else` is optional and catches everything not matched above.

### Checking for empty input

```python
city = input("City: ").strip()

if not city:           # empty string is "falsy"
    print("No city entered.")
else:
    print(f"Looking up {city}…")
```

### Truthy and Falsy values

In Python, every value is either **truthy** or **falsy** in a boolean context:

| Falsy (treated as False) | Truthy (treated as True) |
|--------------------------|--------------------------|
| `False`                  | `True`                   |
| `0`, `0.0`               | Any non-zero number      |
| `""` (empty string)      | Any non-empty string     |
| `None`                   | Any object               |
| `[]`, `{}`, `()`         | Any non-empty collection |

---

## 8. Loops

### while loop — repeat until a condition is False

```python
count = 0

while count < 3:
    print(f"Count is {count}")
    count = count + 1   # or: count += 1

# Output:
# Count is 0
# Count is 1
# Count is 2
```

### for loop — iterate over a sequence

```python
cities = ["London", "Tokyo", "Sydney"]

for city in cities:
    print(f"City: {city}")

# Output:
# City: London
# City: Tokyo
# City: Sydney
```

### range() — generate a sequence of numbers

```python
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):       # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8 (step = 2)
    print(i)
```

### break and continue

```python
while True:
    choice = input("Type q to quit: ")
    if choice == "q":
        break       # exit the loop immediately
    else:
        continue    # skip the rest of this iteration, go back to top
```

### List comprehension (compact for loop)

```python
# Traditional loop
squares = []
for n in range(1, 6):
    squares.append(n ** 2)

# Same thing as a list comprehension
squares = [n ** 2 for n in range(1, 6)]
# Result: [1, 4, 9, 16, 25]

# With a filter
even_squares = [n ** 2 for n in range(1, 11) if n % 2 == 0]
# Result: [4, 16, 36, 64, 100]
```

---

## 9. Functions

A function is a **reusable named block of code**.

### Define and call a function

```python
# Definition
def greet(name):
    print(f"Hello, {name}!")

# Call
greet("Alice")   # Hello, Alice!
greet("Bob")     # Hello, Bob!
```

### Parameters and return values

```python
def celsius_to_fahrenheit(celsius):
    fahrenheit = (celsius * 9 / 5) + 32
    return fahrenheit   # send the result back

temp_f = celsius_to_fahrenheit(25)
print(f"25°C = {temp_f}°F")   # 25°C = 77.0°F
```

### Default parameter values

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Alice")               # Hello, Alice!
greet("Bob", "Good morning") # Good morning, Bob!
```

### Keyword arguments

```python
def describe_weather(city, temp, unit="C"):
    print(f"{city}: {temp}°{unit}")

describe_weather("London", 15)
describe_weather(temp=28, city="Sydney", unit="F")  # order doesn't matter
```

### Docstrings

Always document your functions:

```python
def get_weather(city_name):
    """
    Fetch current weather data for a given city.

    Parameters:
        city_name (str): The name of the city.

    Returns:
        dict: Weather data, or None if the request failed.
    """
    # … function body …
```

---

## 10. Lists and Dictionaries

### Lists — ordered, changeable sequences

```python
cities = ["London", "Paris", "Tokyo"]

# Access elements by index (starts at 0)
print(cities[0])    # "London"
print(cities[-1])   # "Tokyo" (negative index = from the end)

# Modify
cities.append("Sydney")     # add to end
cities.insert(1, "Berlin")  # insert at position 1
cities.remove("Paris")      # remove by value
popped = cities.pop()       # remove and return last item

# Iterate
for city in cities:
    print(city)

# Check membership
if "Tokyo" in cities:
    print("Found Tokyo!")

print(len(cities))  # number of items
```

### Dictionaries — key/value pairs

```python
weather = {
    "city": "Kuala Lumpur",
    "temperature": 32.5,
    "humidity": 85,
    "description": "partly cloudy",
}

# Access by key
print(weather["city"])              # "Kuala Lumpur"
print(weather.get("wind_speed"))    # None (no crash if key missing)
print(weather.get("wind_speed", 0)) # 0 (custom default)

# Modify
weather["temperature"] = 31.0      # update existing key
weather["wind_speed"] = 3.5        # add new key

# Iterate
for key, value in weather.items():
    print(f"{key}: {value}")
```

### Nested dictionaries (what the API returns)

```python
data = {
    "name": "London",
    "main": {
        "temp": 15.3,
        "humidity": 72,
    },
    "weather": [
        {"description": "light rain"}
    ],
}

# Access nested values
temp = data["main"]["temp"]           # 15.3
desc = data["weather"][0]["description"]  # "light rain"
```

---

## 11. Error Handling

Programs can fail for many reasons. `try / except` lets you handle errors gracefully.

```python
try:
    number = int(input("Enter a number: "))
    result = 10 / number
    print(f"Result: {result}")
except ValueError:
    print("That's not a valid number!")
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    print("This always runs, error or not.")
```

### Exception hierarchy (most specific first)

```
Exception
├── ValueError       — wrong value type (e.g. int("abc"))
├── TypeError        — wrong type used in operation
├── ZeroDivisionError
├── FileNotFoundError
├── KeyError         — dictionary key doesn't exist
├── IndexError       — list index out of range
└── … (hundreds more)
```

Always catch **specific** exceptions first (before generic ones).

### Requests exceptions (used in the weather app)

```python
import requests

try:
    response = requests.get(url)
    response.raise_for_status()      # raises HTTPError for 4xx/5xx
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")        # e.g. 404 Not Found
except requests.exceptions.ConnectionError:
    print("No internet connection.") # DNS failure, refused connection
except requests.exceptions.Timeout:
    print("Request timed out.")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")    # catch-all for requests errors
```

---

## 12. Modules and Imports

A **module** is a Python file that contains reusable code.

### Import a module

```python
import math

print(math.pi)           # 3.141592653589793
print(math.sqrt(16))     # 4.0
print(math.ceil(3.2))    # 4
```

### Import specific names from a module

```python
from math import pi, sqrt

print(pi)        # no need to write math.pi
print(sqrt(25))  # no need to write math.sqrt(25)
```

### Common built-in modules

| Module    | What it does                        |
|-----------|-------------------------------------|
| `math`    | Mathematical functions              |
| `random`  | Random number generation            |
| `datetime`| Working with dates and times        |
| `os`      | Operating system interactions       |
| `json`    | Encode/decode JSON data             |
| `sys`     | System-specific parameters          |
| `re`      | Regular expressions (text patterns) |

### Third-party modules (install with pip)

```bash
pip install requests      # HTTP requests
pip install flask         # web framework
pip install pandas        # data analysis
pip install matplotlib    # data visualisation
```

---

## 13. Working with APIs

An **API** (Application Programming Interface) is a way for programs to talk to each other over the internet.

### How a web API works

```
Your Python script
       │
       │  HTTP GET request (with parameters)
       ▼
  Remote Server (e.g. openweathermap.org)
       │
       │  JSON response (text data)
       ▼
Your Python script receives the data
```

### What is JSON?

**JSON** (JavaScript Object Notation) is a text format that looks exactly like Python dictionaries and lists:

```json
{
  "name": "London",
  "main": {
    "temp": 15.3,
    "humidity": 72
  },
  "weather": [
    {
      "description": "light rain"
    }
  ]
}
```

Python's `requests` library automatically converts this into a Python dictionary with `.json()`.

### Step-by-step: Making your first API call

```python
import requests

# 1. Choose the endpoint URL
url = "https://api.openweathermap.org/data/2.5/weather"

# 2. Build the query parameters
params = {
    "q": "London",
    "appid": "YOUR_API_KEY",
    "units": "metric",
}

# 3. Make the GET request
response = requests.get(url, params=params)

# 4. Check the status code
print(response.status_code)  # 200 = success

# 5. Parse the JSON body
data = response.json()
print(data)

# 6. Extract what you need
temperature = data["main"]["temp"]
print(f"London: {temperature}°C")
```

### Common HTTP status codes

| Code | Meaning                      |
|------|------------------------------|
| 200  | OK – request succeeded       |
| 400  | Bad Request – invalid params |
| 401  | Unauthorized – bad API key   |
| 404  | Not Found – city doesn't exist |
| 429  | Too Many Requests – rate limit|
| 500  | Server Error                 |

---

## 14. Object-Oriented Programming

OOP lets you model the real world as **objects** that have **properties** (data) and **behaviours** (methods).

### Classes and Objects

```python
# A class is a blueprint
class Dog:
    # __init__ is the constructor — runs when you create a Dog
    def __init__(self, name, breed):
        self.name = name    # instance attribute
        self.breed = breed

    # An instance method
    def bark(self):
        print(f"{self.name} says: Woof!")

    # __str__ controls what print(dog) shows
    def __str__(self):
        return f"{self.name} ({self.breed})"


# Create instances (objects) from the class
dog1 = Dog("Buddy", "Labrador")
dog2 = Dog("Max", "Poodle")

dog1.bark()         # Buddy says: Woof!
print(dog1)         # Buddy (Labrador)
print(dog1.name)    # Buddy
```

### Dataclasses (used in weather_app_advanced.py)

```python
from dataclasses import dataclass

@dataclass
class WeatherData:
    city: str
    temperature: float
    humidity: int

# Python auto-generates __init__, __repr__, __eq__
w = WeatherData(city="Tokyo", temperature=28.5, humidity=75)
print(w)  # WeatherData(city='Tokyo', temperature=28.5, humidity=75)
```

### Properties

```python
@dataclass
class WeatherData:
    city: str
    temperature: float

    @property
    def comfort_level(self):
        if self.temperature > 30:
            return "Hot"
        elif self.temperature > 20:
            return "Warm"
        else:
            return "Cool"

w = WeatherData("Singapore", 33.0)
print(w.comfort_level)   # "Hot"  (accessed like an attribute, not a method)
```

### Static methods

```python
class WeatherService:
    @staticmethod
    def celsius_to_fahrenheit(c):
        return (c * 9 / 5) + 32

# Call without creating an instance
f = WeatherService.celsius_to_fahrenheit(25)
print(f)   # 77.0
```

---

## 15. Running the Weather App

### Step 1 — Get a free API key

1. Sign up at [https://openweathermap.org/api](https://openweathermap.org/api)
2. Go to **API keys** in your account dashboard.
3. Copy the default key (it may take a few minutes to activate).

### Step 2 — Edit weather_app.py

Open `weather_app.py` and set your API key.  
Either export it as an environment variable (recommended):

```bash
# macOS / Linux
export OPENWEATHER_API_KEY="abc123def456..."

# Windows (Command Prompt)
set OPENWEATHER_API_KEY=abc123def456...
```

Or, for a quick test, replace the placeholder directly in the file:

```python
# Before
API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")

# After (replace only the default fallback)
API_KEY = os.getenv("OPENWEATHER_API_KEY", "abc123def456...")
```

### Step 3 — Run the beginner app

```bash
python weather_app.py
```

Example session:

```
========================================
  🌤️  Python Weather App
========================================
Enter a city name: London

========================================
  Weather in London, GB
========================================
  Description : Overcast clouds
  Temperature : 12.4 °C  (feels like 10.1 °C)
  Humidity    : 78 %
  Wind speed  : 5.1 m/s
========================================
```

### Step 4 — Run the advanced app

```bash
python weather_app_advanced.py
```

This version supports comparing multiple cities at once.

---

## 16. Next Steps

You have now learned the core Python concepts needed to build a real application. Here is what to explore next:

### Beginner → Intermediate

- [ ] **File I/O** — save weather history to a `.txt` or `.csv` file.
- [ ] **Modules** — split the app into multiple files (`api.py`, `display.py`).
- [ ] **Unit tests** — use `pytest` to test your functions automatically.
- [ ] **Environment variables** — store your API key safely using `python-dotenv`.

### Intermediate → Advanced

- [ ] **Flask** — build a web version of the weather app.
- [ ] **SQLite** — store weather data in a database.
- [ ] **Async/await** — fetch multiple cities simultaneously without waiting.
- [ ] **Type annotations** — annotate all your functions with types.

### Ideas for extending this project

1. Show a 5-day weather forecast (the API supports it).
2. Let the user choose Celsius or Fahrenheit.
3. Display a UV index and air quality index.
4. Save the last 10 searches to a file and show history.
5. Build a GUI version using `tkinter`.
6. Create a Telegram or Discord bot that responds to weather queries.

### Useful resources

| Resource | URL |
|----------|-----|
| Official Python docs | [https://docs.python.org/3/](https://docs.python.org/3/) |
| OpenWeatherMap API docs | [https://openweathermap.org/api](https://openweathermap.org/api) |
| Real Python tutorials | [https://realpython.com/](https://realpython.com/) |
| Python exercises | [https://exercism.org/tracks/python](https://exercism.org/tracks/python) |
| Requests library docs | [https://requests.readthedocs.io/](https://requests.readthedocs.io/) |

---

> **Happy coding! 🎉**  
> The best way to learn Python is to write Python. Break things, fix them, and keep building.
