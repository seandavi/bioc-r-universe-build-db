"""Data models for the build tracker."""

import re
from datetime import datetime

from pydantic import BaseModel, Field


class RSSItem(BaseModel):
    """Parsed RSS feed item representing a package update."""

    package: str
    version: str
    run_id: str
    title: str
    link: str
    pub_date: datetime
    description: str = ""

    @property
    def pub_date_iso(self) -> str:
        """Return pub_date as ISO format string."""
        return self.pub_date.isoformat()


class Cursor(BaseModel):
    """Tracks the last processed RSS item."""

    last_pub_date: datetime | None = None
    last_package: str | None = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def should_process(self, item: RSSItem) -> bool:
        """Check if an RSS item should be processed based on cursor state."""
        if self.last_pub_date is None:
            return True
        # Process items strictly newer than cursor
        return item.pub_date > self.last_pub_date


class BuildRecord(BaseModel):
    """Metadata about a stored build."""

    package: str
    run_id: str
    version: str | None = None
    commit: str | None = None
    is_failure: bool = False
    filename: str
    stored_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_package_json(cls, data: dict, run_id: str | None = None) -> "BuildRecord":
        """Create a BuildRecord from package JSON data."""
        package = data["Package"]
        is_failure = data.get("_type") == "failure" or "Version" not in data
        version = data.get("Version")
        commit = _extract_commit(data)

        # Extract run_id from _buildurl if not provided
        if run_id is None:
            run_id = extract_run_id(data.get("_buildurl", ""))

        return cls(
            package=package,
            run_id=run_id,
            version=version,
            commit=commit,
            is_failure=is_failure,
            filename=make_filename(package, run_id),
        )


def make_filename(package: str, run_id: str) -> str:
    """Generate unique filename for a build."""
    return f"{package}_{run_id}.json"


def extract_run_id(url: str) -> str:
    """Extract GitHub Actions run ID from build URL.

    URL format: https://github.com/r-universe/bioc/actions/runs/21698513671
    """
    match = re.search(r"/actions/runs/(\d+)", url)
    if match:
        return match.group(1)
    return "unknown"


def _extract_commit(data: dict) -> str | None:
    """Extract commit SHA from package data."""
    if "RemoteSha" in data:
        return data["RemoteSha"]
    if "_commit" in data and isinstance(data["_commit"], dict):
        return data["_commit"].get("id")
    return None
