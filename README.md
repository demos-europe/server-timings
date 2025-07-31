# Server Timings

A Django middleware/Flask Extension/FastAPI middleware for adding Server-Timing headers to HTTP responses with automatic
database query
instrumentation (only supported for Django).

## Features

- Thread-safe server timing collection
- Automatic database query timing with SQL operation detection (Django only)
- Context manager and decorator utilities for custom timing

## Installation

Specify the package in your `Pipfile` or install it directly using pipenv:

```bash
pipenv install -e server-timings[flask]
```

The extras flask, django, and fastapi are optional and only needed if you want to use the Flask extension, Django
Middleware, or FastAPI middleware.

## Quick Start

### Flask

1. Install with Flask support:

```bash
pipenv install -e server-timings[flask]
```

2. Initialize the extension in your Flask app:

```python
from flask import Flask
from timings import ServerTimingsExtension

app = Flask(__name__)
timings = ServerTimingsExtension()
timings.init_app(app)  # Initialize the extension with the Flask app
```

3. That's it! Server-Timing headers will now be automatically added to all responses.
   Check [Usage](#usage) for more details on how to use the extension.

### Django

1. Install with Django support:

```bash
pipenv install -e server-timings[django]
```

2. Add to your Django settings:

```python
# settings.py
INSTALLED_APPS = [
    # ... your other apps
    'timings',
]

MIDDLEWARE = [
    # ... your other middlewares
    'timings.middleware.FastAPIServerTimingMiddleware',
]
```

3. That's it! Server-Timing headers will now be automatically added to all responses, including automatic database query
   timing.
   Note: Django Database queries are automatically timed and included in the Server-Timing header when the middleware is
   enabled.
   Check [Usage](#usage) for more details on how to track time using ServerTimingMetric.

### FastAPI

1. Install with FastAPI support:

```bash
pipenv install -e server-timings[fastapi]
```

2. Add the middleware to your FastAPI app:

```python
from fastapi import FastAPI
from timings.fastapi.middleware import FastAPIServerTimingMiddleware

app = FastAPI()
app.add_middleware(FastAPIServerTimingMiddleware)
```

3. That's it! Server-Timing headers will now be automatically added to all responses.
   Check [Usage](#usage) for more details on how to track time using ServerTimingMetric.

## Usage

### Adding Metrics

#### Manually

```python
from timings.models import ServerTimingMetric

metric = ServerTimingMetric("custom_metric", "Custom operation")
metric.start()
# ... do work ...
metric.end()
```

#### Using Context Manager

```python
from timings.util import timed_metric


def my_view(request):
    with timed_metric("expensive_operation", "Processing data"):
        # Your expensive operation here
        result = process_data()
    return HttpResponse(result)
```

#### Using Decorator

```python
from timings.util import timed


@timed(name="data_processing", description="Complex calculations")
def process_data():
    # Your function logic
    return result
```

## Requirements

| Framework | Python |         Dependencies         |
|-----------|--------|:----------------------------:|
| Core      | 3.12+  |              -               |
| Django    | 3.12+  | Django 4.0+, sqlparse 0.4.0+ |
| Flask     | 3.12+  |          Flask 2.0+          |
| FastAPI   | 3.12+  |       FastAPI 0.116.1+       |

## License

EUPL-1.2
