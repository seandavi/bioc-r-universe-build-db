"""HTTP client for Bioconductor R-Universe API."""

import json
from collections.abc import Iterator
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import (
    ENVIRONMENTS,
    HTTP_RETRIES,
    HTTP_TIMEOUT,
)

# Default base URL (devel)
_DEFAULT_BASE_URL = ENVIRONMENTS["devel"]


class APIClient:
    """Synchronous HTTP client for R-Universe API."""

    def __init__(self, base_url: str = _DEFAULT_BASE_URL, timeout: float = HTTP_TIMEOUT):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazy-initialize HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self._timeout, follow_redirects=True)
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    @retry(
        stop=stop_after_attempt(HTTP_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def fetch_package_json(self, package_name: str) -> dict[str, Any]:
        """Fetch full package JSON from API.

        Args:
            package_name: Name of the package to fetch

        Returns:
            Package data as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails after retries
        """
        url = f"{self._base_url}/api/packages/{package_name}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def stream_all_packages(self) -> Iterator[dict[str, Any]]:
        """Stream all packages from NDJSON endpoint.

        Yields:
            Package data dictionaries one at a time
        """
        url = f"{self._base_url}/api/packages?stream=1"
        with self.client.stream("GET", url) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line.strip():
                    yield json.loads(line)

    @retry(
        stop=stop_after_attempt(HTTP_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def fetch_feed(self, feed_url: str) -> str:
        """Fetch RSS feed content.

        Args:
            feed_url: URL of the RSS feed

        Returns:
            Feed content as string
        """
        response = self.client.get(feed_url)
        response.raise_for_status()
        return response.text

    @property
    def feed_url(self) -> str:
        """RSS feed URL for this environment."""
        return f"{self._base_url}/feed.xml"
