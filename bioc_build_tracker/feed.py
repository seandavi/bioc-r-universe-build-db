"""RSS feed consumer for Bioconductor R-Universe updates."""

import re
from datetime import datetime, timezone

import feedparser

from .config import RSS_FEED_URL
from .models import RSSItem, extract_run_id


def parse_feed(feed_url: str = RSS_FEED_URL) -> list[RSSItem]:
    """Parse RSS feed and return list of RSSItem objects sorted by date (oldest first)."""
    feed = feedparser.parse(feed_url)

    items = []
    for entry in feed.entries:
        item = _parse_entry(entry)
        if item:
            items.append(item)

    # Sort by pub_date ascending (oldest first) for processing order
    items.sort(key=lambda x: x.pub_date)
    return items


def _parse_entry(entry: feedparser.FeedParserDict) -> RSSItem | None:
    """Parse a single feed entry into an RSSItem."""
    try:
        title = entry.get("title", "")
        link = entry.get("link", "")

        # Extract package name and version from title
        # Format: "[bioc] PackageName Version" e.g. "[bioc] AnVIL 1.23.8"
        package, version = _extract_package_and_version(title)

        if not package:
            return None

        # Extract run_id from link (GitHub Actions URL)
        run_id = extract_run_id(link)

        # Parse publication date
        pub_date = _parse_date(entry)

        return RSSItem(
            package=package,
            version=version,
            run_id=run_id,
            title=title,
            link=link,
            pub_date=pub_date,
            description=entry.get("description", ""),
        )
    except Exception:
        return None


def _extract_package_and_version(title: str) -> tuple[str, str]:
    """Extract package name and version from RSS entry title.

    Expected format: "[bioc] PackageName Version"
    Examples:
        "[bioc] AnVIL 1.23.8" -> ("AnVIL", "1.23.8")
        "[bioc] cBioPortalData 2.23.4" -> ("cBioPortalData", "2.23.4")
    """
    # Pattern: [bioc] followed by package name and version
    match = re.match(r"\[bioc\]\s+([A-Za-z][A-Za-z0-9.]*)\s+(\d+\.\d+[\.\d]*)", title)
    if match:
        return match.group(1), match.group(2)

    # Fallback: try to parse without [bioc] prefix
    # Format: "PackageName Version"
    match = re.match(r"([A-Za-z][A-Za-z0-9.]*)\s+(\d+\.\d+[\.\d]*)", title.strip())
    if match:
        return match.group(1), match.group(2)

    return "", "unknown"


def _parse_date(entry: feedparser.FeedParserDict) -> datetime:
    """Parse publication date from feed entry."""
    # feedparser provides parsed time tuple
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

    # Fallback to current time
    return datetime.now(timezone.utc)
