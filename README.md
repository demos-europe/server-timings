# Server Timings

A Django middleware/Flask Extension for adding Server-Timing headers to HTTP responses with automatic database query instrumentation (only supported for Django).

## Features

- Thread-safe server timing collection
- Automatic database query timing with SQL operation detection (Django only)
- Context manager and decorator utilities for custom timing

## Installation

Specify the package in your `Pipfile` or install it directly using pipenv:

```bash
pipenv install -e server-timings[flask]
```

The extras flask and django are optional and only needed if you want to use the Flask extension or Django Middleware.

## Quick Start

### Add to your Django `INSTALLED_APPS` and `MIDDLEWARE` settings

```python
INSTALLED_APPS = [
    # ... your other apps
    'timings',
]

MIDDLEWARE = [
    # ... your other middlewares
    'timings.middleware.ServerTimingMiddleware'
]
```

### Add extension to your Flask app

Import and initialize the `ServerTimingsExtension` in your Flask application:

```python

from timings import ServerTimingsExtension

st = ServerTimingsExtension()
app = Flask("diplanportal-api")
st.init_app(app)
```

## Usage

### Automatic Database Query Timing

Database queries are automatically timed and included in the Server-Timing header when the middleware is enabled.

### Manual Tracking

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

#### Manual Metric Creation

```python
from timings.models import ServerTimingMetric

metric = ServerTimingMetric("custom_metric", "Custom operation")
metric.start()
# ... do work ...
metric.end()
```

## Requirements

- Python 3.12+

### Django

- Django 4.0+
- sqlparse 0.4.0+

### Flask

- Flask 2.0+

## License

EUPL-1.2
