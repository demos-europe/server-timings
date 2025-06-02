# Django Server Timings

A Django middleware for adding Server-Timing headers to HTTP responses with automatic database query instrumentation.

## Features

- Thread-safe server timing collection
- Automatic database query timing with SQL operation detection
- Context manager and decorator utilities for custom timing
- Configurable via Django settings

## Installation

```bash
pip install django-server-timings
```

## Quick Start

### 1. Add to your Django `INSTALLED_APPS` and `MIDDLEWARE` settings:
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

### 2. Enable timings in your Django settings
In debug mode, timings are always enabled. In production, you can explicitly enable them.

```python
DEBUG = True
```

explicitly enable timings to force the inclusion of Server-Timing headers in production:
```python
DEBUG = False
ENABLE_TIMINGS = True
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

- Python 3.11+
- Django 4.0+
- sqlparse 0.4.0+

## License

EUPL-1.2
