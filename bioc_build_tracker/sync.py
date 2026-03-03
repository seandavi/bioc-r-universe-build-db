"""Main sync logic for incremental RSS feed processing."""

import logging

from .client import APIClient
from .feed import parse_feed
from .models import Cursor, RSSItem, extract_run_id
from .storage import BuildStorage

logger = logging.getLogger(__name__)


class SyncResult:
    """Results from a sync operation."""

    def __init__(self) -> None:
        self.processed = 0
        self.skipped = 0
        self.failed = 0
        self.errors: list[str] = []

    @property
    def total(self) -> int:
        return self.processed + self.skipped + self.failed


def run_sync(
    storage: BuildStorage,
    client: APIClient | None = None,
    dry_run: bool = False,
) -> SyncResult:
    """Run incremental sync from RSS feed.

    Args:
        storage: BuildStorage instance
        client: Optional APIClient (created if not provided)
        dry_run: If True, don't save anything

    Returns:
        SyncResult with statistics
    """
    result = SyncResult()
    own_client = client is None

    if own_client:
        client = APIClient()

    try:
        # Load cursor
        cursor = storage.load_cursor()
        logger.info(f"Loaded cursor: last_pub_date={cursor.last_pub_date}")

        # Fetch and parse RSS feed using the client's configured base URL
        items = parse_feed(client.feed_url)
        logger.info(f"Found {len(items)} items in RSS feed")

        # Filter to items newer than cursor
        new_items = [item for item in items if cursor.should_process(item)]
        logger.info(f"Processing {len(new_items)} new items")

        last_successful_item: RSSItem | None = None

        for item in new_items:
            try:
                # Check if build already exists by run_id
                if storage.build_exists(item.package, item.run_id):
                    logger.debug(f"Skipping existing build: {item.package} run={item.run_id}")
                    result.skipped += 1
                    last_successful_item = item
                    continue

                # Fetch full package JSON
                logger.debug(f"Fetching {item.package}")
                package_data = client.fetch_package_json(item.package)

                # Save build with run_id from RSS feed
                if not dry_run:
                    record = storage.save_build(
                        package_data,
                        run_id=item.run_id,
                        pub_date=item.pub_date,
                    )
                    logger.info(f"Saved: {record.filename}")

                result.processed += 1
                last_successful_item = item

            except Exception as e:
                logger.error(f"Failed to process {item.package}: {e}")
                result.failed += 1
                result.errors.append(f"{item.package}: {e}")
                # Don't update cursor past failures
                break

        # Update cursor to last successful item
        if last_successful_item and not dry_run:
            cursor.last_pub_date = last_successful_item.pub_date
            cursor.last_package = last_successful_item.package
            storage.save_cursor(cursor)
            logger.info(f"Updated cursor to {cursor.last_pub_date}")

    finally:
        if own_client:
            client.close()

    return result


def run_backfill(
    storage: BuildStorage,
    client: APIClient | None = None,
    limit: int | None = None,
    dry_run: bool = False,
) -> SyncResult:
    """Backfill all current packages from NDJSON endpoint.

    Args:
        storage: BuildStorage instance
        client: Optional APIClient (created if not provided)
        limit: Maximum number of packages to process (for testing)
        dry_run: If True, don't save anything

    Returns:
        SyncResult with statistics
    """
    result = SyncResult()
    own_client = client is None

    if own_client:
        client = APIClient()

    try:
        count = 0
        for package_data in client.stream_all_packages():
            if limit and count >= limit:
                break

            try:
                package = package_data.get("Package", "unknown")

                # Extract run_id from _buildurl
                run_id = extract_run_id(package_data.get("_buildurl", ""))

                if run_id == "unknown":
                    logger.warning(f"Skipping {package}: no run_id in _buildurl")
                    result.skipped += 1
                    count += 1
                    continue

                # Check if build already exists
                if storage.build_exists(package, run_id):
                    logger.debug(f"Skipping existing: {package} run={run_id}")
                    result.skipped += 1
                    count += 1
                    continue

                # Save build with current timestamp
                if not dry_run:
                    record = storage.save_build(package_data, run_id=run_id)
                    logger.info(f"Saved: {record.filename}")

                result.processed += 1

            except Exception as e:
                package = package_data.get("Package", "unknown")
                logger.error(f"Failed to process {package}: {e}")
                result.failed += 1
                result.errors.append(f"{package}: {e}")

            count += 1

    finally:
        if own_client:
            client.close()

    return result
