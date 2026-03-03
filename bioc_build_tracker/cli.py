"""Command-line interface for the build tracker."""

import logging
import sys
from pathlib import Path

import click

from .client import APIClient
from .config import DEFAULT_DATA_DIR, ENVIRONMENTS
from .storage import BuildStorage
from .sync import run_backfill, run_sync


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Bioconductor R-Universe Build Tracker.

    Track and store Bioconductor package builds over time.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    setup_logging(verbose)


@cli.command()
@click.option(
    "--data-dir",
    type=click.Path(),
    default=str(DEFAULT_DATA_DIR),
    help="Data directory for storage",
)
@click.option("--dry-run", is_flag=True, help="Don't save anything, just show what would happen")
@click.pass_context
def sync(ctx: click.Context, data_dir: str, dry_run: bool) -> None:
    """Run incremental sync from RSS feed.

    Fetches the RSS feed, finds new items since the last sync,
    downloads full package JSON for each, and saves to storage.
    Runs for both devel and release environments.
    """
    click.echo(f"Syncing builds to {data_dir}")
    if dry_run:
        click.echo("(dry run - no changes will be saved)")

    any_errors = False
    for env_name, base_url in ENVIRONMENTS.items():
        env_dir = Path(data_dir) / env_name
        storage = BuildStorage(env_dir)
        click.echo(f"\n[{env_name}] Syncing from {base_url}")

        with APIClient(base_url=base_url) as client:
            result = run_sync(storage, client, dry_run=dry_run)

        click.echo(f"  Processed: {result.processed}")
        click.echo(f"  Skipped:   {result.skipped}")
        click.echo(f"  Failed:    {result.failed}")

        if result.errors:
            click.echo(f"  Errors:")
            for error in result.errors:
                click.echo(f"    - {error}")
            any_errors = True

    if any_errors:
        sys.exit(1)


@cli.command()
@click.option(
    "--data-dir",
    type=click.Path(),
    default=str(DEFAULT_DATA_DIR),
    help="Data directory for storage",
)
@click.option("--limit", type=int, help="Maximum number of packages to process")
@click.option("--dry-run", is_flag=True, help="Don't save anything, just show what would happen")
@click.pass_context
def backfill(ctx: click.Context, data_dir: str, limit: int | None, dry_run: bool) -> None:
    """Fetch all current packages from NDJSON endpoint.

    Downloads the complete package list and saves each one for both
    devel and release environments. Use --limit for testing with a subset.
    """
    click.echo(f"Backfilling builds to {data_dir}")
    if limit:
        click.echo(f"(limited to {limit} packages)")
    if dry_run:
        click.echo("(dry run - no changes will be saved)")

    any_errors = False
    for env_name, base_url in ENVIRONMENTS.items():
        env_dir = Path(data_dir) / env_name
        storage = BuildStorage(env_dir)
        click.echo(f"\n[{env_name}] Backfilling from {base_url}")

        with APIClient(base_url=base_url) as client:
            result = run_backfill(storage, client, limit=limit, dry_run=dry_run)

        click.echo(f"  Processed: {result.processed}")
        click.echo(f"  Skipped:   {result.skipped}")
        click.echo(f"  Failed:    {result.failed}")

        if result.errors:
            click.echo(f"  Errors ({len(result.errors)} total):")
            for error in result.errors[:10]:
                click.echo(f"    - {error}")
            if len(result.errors) > 10:
                click.echo(f"    ... and {len(result.errors) - 10} more")
            any_errors = True

    if any_errors:
        sys.exit(1)


@cli.command()
@click.option(
    "--data-dir",
    type=click.Path(),
    default=str(DEFAULT_DATA_DIR),
    help="Data directory for storage",
)
@click.pass_context
def status(ctx: click.Context, data_dir: str) -> None:
    """Show cursor state and storage statistics for each environment."""
    click.echo(f"Data directory: {data_dir}")

    for env_name in ENVIRONMENTS:
        env_dir = Path(data_dir) / env_name
        storage = BuildStorage(env_dir)

        click.echo()
        click.echo(f"[{env_name}]")

        # Load cursor
        cursor = storage.load_cursor()

        click.echo("  Cursor:")
        if cursor.last_pub_date:
            click.echo(f"    Last processed: {cursor.last_pub_date.isoformat()}")
            click.echo(f"    Last package:   {cursor.last_package}")
            click.echo(f"    Last updated:   {cursor.last_updated.isoformat()}")
        else:
            click.echo("    (no cursor - sync has not been run)")

        # Get storage stats
        stats = storage.get_stats()

        click.echo("  Storage:")
        click.echo(f"    Total builds:    {stats['total_builds']}")
        click.echo(f"    Unique packages: {stats['packages']}")
        if stats["years"]:
            click.echo(f"    Years:           {', '.join(stats['years'])}")


if __name__ == "__main__":
    cli()
