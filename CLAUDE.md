# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **data repository** containing example data files from the Bioconductor R-Universe build infrastructure. It aggregates package build results, metadata, and status information for Bioconductor packages. There is no source code to build, test, or lint.

## Key Data Files

- **example_current_packages.ndjson** - All current Bioconductor packages in NDJSON format (one JSON object per line). Contains package metadata, build job results across platforms, dependencies, and repository statistics.
- **geoquery_build_result.json** - Detailed example of a single package (GEOquery) build result showing the full build matrix.
- **example_xml_feed.xml** - RSS/XML feed sample showing recent package updates.

## API Endpoints

```
Full package list (NDJSON): https://bioc.r-universe.dev/api/packages/?stream=1
Single package (JSON):      https://bioc.r-universe.dev/api/packages/{PACKAGENAME}
RSS/XML feed:               https://bioc.r-universe.dev/feed.xml
```

## Build Matrix Architecture

Packages are tested across multiple platforms and R versions:
- bioc-checks, source (R 4.5.2)
- linux-devel-x86_64 (R 4.6.0), linux-release-x86_64 (R 4.5.2)
- macos-devel-arm64 (R 4.6.0), macos-release-arm64 (R 4.5.2)
- windows-devel (R 4.6.0), windows-release (R 4.5.2), windows-oldrel (R 4.4.3)
- wasm-release (R 4.5.1)

Each build records: check results (OK/NOTE/WARNING/ERROR), duration, artifact IDs, GitHub Actions job numbers, and commit info.

## Package Metadata Structure

Records include: Package, Title, Version, Authors, License, Depends/Imports/Suggests, Downloads, Stars, Contributors, Vignettes, build job results per platform, and bioccheck warnings/errors/notes.
