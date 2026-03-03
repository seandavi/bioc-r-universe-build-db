"""Storage layer using UPath for cloud-ready file operations."""

import json
from datetime import datetime, timezone
from typing import Any

from upath import UPath

from .config import BUILDS_DIRNAME, CURSOR_FILENAME
from .models import BuildRecord, Cursor, make_filename


class BuildStorage:
    """File-based storage for build records using UPath."""

    def __init__(self, data_dir: str | UPath):
        """Initialize storage with data directory.

        Args:
            data_dir: Path to data directory (local or cloud URI)
        """
        self.data_dir = UPath(data_dir)
        self.builds_dir = self.data_dir / BUILDS_DIRNAME
        self.cursor_path = self.data_dir / CURSOR_FILENAME

    def _get_build_path(self, package: str, pub_date: datetime, filename: str) -> UPath:
        """Get the full path for a build file.

        Directory structure: builds/package/YYYY/MM/filename.json
        """
        year = pub_date.strftime("%Y")
        month = pub_date.strftime("%m")
        return self.builds_dir / package / year / month / filename

    def build_exists(self, package: str, run_id: str) -> bool:
        """Check if a build already exists in storage.

        Searches the current layout (package/YYYY/MM/file) 
        for existence. 
        """
        filename = make_filename(package, run_id)
        # New layout: builds/package/YYYY/MM/filename
        new_pattern = f"{package}/**/{filename}"
        return any(self.builds_dir.glob(new_pattern))

    def save_build(
        self,
        data: dict[str, Any],
        run_id: str | None = None,
        pub_date: datetime | None = None,
    ) -> BuildRecord:
        """Save a package build to storage.

        Args:
            data: Full package JSON data
            run_id: GitHub Actions run ID (extracted from _buildurl if not provided)
            pub_date: Publication date for directory organization (defaults to now)

        Returns:
            BuildRecord with metadata about the saved build
        """
        record = BuildRecord.from_package_json(data, run_id=run_id)

        if pub_date is None:
            pub_date = datetime.now(timezone.utc)

        path = self._get_build_path(record.package, pub_date, record.filename)

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON file
        with path.open("w") as f:
            json.dump(data, f, indent=2)

        return record

    def load_cursor(self) -> Cursor:
        """Load cursor from storage, or return empty cursor if not exists."""
        if not self.cursor_path.exists():
            return Cursor()

        with self.cursor_path.open() as f:
            data = json.load(f)

        return Cursor.model_validate(data)

    def save_cursor(self, cursor: Cursor) -> None:
        """Save cursor to storage."""
        self.cursor_path.parent.mkdir(parents=True, exist_ok=True)

        cursor.last_updated = datetime.now(timezone.utc)

        with self.cursor_path.open("w") as f:
            json.dump(cursor.model_dump(mode="json"), f, indent=2)

    def get_stats(self) -> dict[str, Any]:
        """Get storage statistics."""
        stats = {
            "data_dir": str(self.data_dir),
            "cursor_exists": self.cursor_path.exists(),
            "builds_dir_exists": self.builds_dir.exists(),
            "total_builds": 0,
            "packages": set(),
            "years": set(),
        }

        if self.builds_dir.exists():
            # Count all JSON files
            for json_file in self.builds_dir.glob("**/*.json"):
                stats["total_builds"] += 1
                parts = json_file.relative_to(self.builds_dir).parts
                if len(parts) >= 4:
                    # Detect layout by checking if first component is a 4-digit year
                    # Legacy layout: builds/YYYY/MM/package/file.json
                    # New layout:    builds/package/YYYY/MM/file.json
                    if parts[0].isdigit() and len(parts[0]) == 4 and 1900 <= int(parts[0]) <= 2100:
                        stats["years"].add(parts[0])
                        stats["packages"].add(parts[2])
                    else:
                        stats["packages"].add(parts[0])
                        stats["years"].add(parts[1])

        stats["packages"] = len(stats["packages"])
        stats["years"] = sorted(stats["years"])

        return stats
