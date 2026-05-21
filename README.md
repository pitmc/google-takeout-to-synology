# Google Takeout to Synology Photos Migration

A complete toolkit for migrating Google Photos exports (Google Takeout) to Synology NAS with full EXIF metadata preservation including dates, GPS coordinates, and descriptions.

## What it does

Google Takeout exports photos/videos with metadata stored in separate `.json` sidecar files instead of embedded EXIF data. Synology Photos (and most photo management tools) rely on EXIF metadata for date sorting, GPS map views, and search.

This toolkit:

1. **Normalizes** file extensions to lowercase for consistency
2. **Fixes** Google's mismatched JSON sidecar naming patterns
3. **Injects** metadata (dates, GPS, descriptions) from JSON sidecars into EXIF headers
4. **Organizes** files into a `YYYY/MM-Month/` folder structure based on photo dates
5. **Cleans up** leftover JSON and HTML files

## Requirements

- **Python 3.6+**
- **exiftool** (Phil Harvey's ExifTool) — [Installation](https://exiftool.org/install.html)
- **Synology NAS** (tested on DSM 7.x) or any Linux/macOS system

### Installing exiftool on Synology (no package manager)

```bash
cd /tmp
git clone https://github.com/exiftool/exiftool.git
cp -r exiftool /usr/local/bin/exiftool-dist
ln -sf /usr/local/bin/exiftool-dist/exiftool /usr/local/bin/exiftool
exiftool -ver
```

## Quick Start

```bash
# 1. Extract your Google Takeout ZIP
7z x takeout-*.zip -o./extracted

# 2. Run the full pipeline
./run_pipeline.sh ./extracted/Takeout/Google\ Photos ./output
```

Or run each step individually:

```bash
# Step 1: Normalize extensions to lowercase
python3 scripts/01_normalize_extensions.py ./source_dir

# Step 2: Fix orphan JSON sidecars
python3 scripts/02_fix_orphan_jsons.py ./source_dir

# Step 3: Inject EXIF metadata from JSONs
python3 scripts/03_inject_exif_metadata.py ./source_dir

# Step 4: Organize into YYYY/MM-Month structure
python3 scripts/04_organize_by_date.py ./source_dir ./output_dir

# Step 5: Clean up JSON and HTML leftovers
python3 scripts/05_cleanup.py ./source_dir
```

## Pipeline Details

### Step 1: Normalize Extensions

Renames `.JPG`, `.PNG`, `.MP4`, etc. to lowercase (`.jpg`, `.png`, `.mp4`). Also renames matching JSON sidecars to keep them paired.

### Step 2: Fix Orphan JSONs

Google Takeout names sidecars inconsistently:
- File: `IMG_001(1).jpg` → JSON: `IMG_001.jpg(1).json`

This script detects and renames JSONs to match their actual media file.

### Step 3: Inject EXIF Metadata

Reads each `.json` sidecar and writes metadata directly into the media file's EXIF:
- `DateTimeOriginal`, `CreateDate`, `FileModifyDate` ← from `photoTakenTime.timestamp`
- `GPSLatitude`, `GPSLongitude`, `GPSAltitude` ← from `geoData`
- `ImageDescription` ← from `description`
- For videos (`.mp4`, `.mov`, `.avi`): writes `Keys:GPSCoordinates` in ISO 6709 format

### Step 4: Organize by Date

Moves files into a `YYYY/MM-Month/` structure. Date resolution order:
1. EXIF `DateTimeOriginal`
2. Date parsed from filename (e.g., `IMG_20200315_...`)
3. Parent folder name (e.g., "Photos from 2020")
4. Fallback: `no-date/`

### Step 5: Cleanup

Removes all `.json` and `.html` files from the source directory (metadata is now embedded in EXIF).

## Known Limitations

- **Synology Photos does NOT display GPS for videos** (as of DSM 7.x / 2026-05)
- `@eaDir` folders are Synology internal indexing — invisible to users, safe to ignore
- Google Takeout JSONs with `latitude: 0, longitude: 0` mean no GPS data ever existed (not actual coordinates)
- exiftool does NOT re-encode images — only writes/modifies EXIF headers, zero quality loss

## Tested With

- Large Google Takeout exports (50GB+, 25k+ files)
- Synology NAS running DSM 7.x
- exiftool 12.x
- Python 3.8+

## License

MIT
