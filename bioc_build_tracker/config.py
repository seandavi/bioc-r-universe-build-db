"""Configuration settings for the build tracker."""

from pathlib import Path

# API Endpoints
RSS_FEED_URL = "https://bioc.r-universe.dev/feed.xml"
PACKAGE_API_URL = "https://bioc.r-universe.dev/api/packages/{package}"
NDJSON_STREAM_URL = "https://bioc.r-universe.dev/api/packages?stream=1"

# Default data directory (relative to project root)
DEFAULT_DATA_DIR = Path("data")

# HTTP client settings
HTTP_TIMEOUT = 30.0  # seconds
HTTP_RETRIES = 3
HTTP_RETRY_WAIT = 1.0  # seconds between retries

# Storage settings
CURSOR_FILENAME = "cursor.json"
BUILDS_DIRNAME = "builds"
