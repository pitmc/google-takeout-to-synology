#!/usr/bin/env python3
"""Inject EXIF metadata from Google Takeout JSON sidecars into media files.

Writes:
- DateTimeOriginal, CreateDate, FileModifyDate from photoTakenTime
- GPSLatitude, GPSLongitude, GPSAltitude from geoData
- ImageDescription from description
- For videos: Keys:GPSCoordinates in ISO 6709 format
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.3gp', '.m4v'}


def build_exiftool_args(metadata, media_path):
  """Build exiftool arguments from JSON metadata."""
  args = []
  is_video = media_path.suffix.lower() in VIDEO_EXTENSIONS

  # Date/time
  taken_time = metadata.get('photoTakenTime', {})
  timestamp = taken_time.get('timestamp')
  if timestamp:
    dt = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    date_str = dt.strftime('%Y:%m:%d %H:%M:%S')
    args.extend([
      f'-DateTimeOriginal={date_str}',
      f'-CreateDate={date_str}',
      f'-FileModifyDate={date_str}',
    ])

  # GPS coordinates
  geo = metadata.get('geoData', {})
  lat = geo.get('latitude', 0)
  lon = geo.get('longitude', 0)
  alt = geo.get('altitude', 0)

  if lat != 0 or lon != 0:
    if is_video:
      # ISO 6709 format for QuickTime containers
      lat_str = f"{'+' if lat >= 0 else ''}{lat:.6f}"
      lon_str = f"{'+' if lon >= 0 else ''}{lon:.6f}"
      alt_str = f"{'+' if alt >= 0 else ''}{alt:.2f}" if alt else ""
      iso6709 = f"{lat_str}{lon_str}{alt_str}/"
      args.append(f'-Keys:GPSCoordinates={iso6709}')
    else:
      lat_ref = 'N' if lat >= 0 else 'S'
      lon_ref = 'E' if lon >= 0 else 'W'
      args.extend([
        f'-GPSLatitude={abs(lat)}',
        f'-GPSLatitudeRef={lat_ref}',
        f'-GPSLongitude={abs(lon)}',
        f'-GPSLongitudeRef={lon_ref}',
      ])
      if alt:
        alt_ref = 0 if alt >= 0 else 1
        args.extend([
          f'-GPSAltitude={abs(alt)}',
          f'-GPSAltitudeRef={alt_ref}',
        ])

  # Description
  description = metadata.get('description', '')
  if description:
    args.append(f'-ImageDescription={description}')

  return args


def inject_metadata(source_dir):
  source = Path(source_dir)
  if not source.exists():
    print(f"Error: {source_dir} does not exist")
    sys.exit(1)

  processed = 0
  errors = 0

  json_files = list(source.rglob('*.json'))
  total = len(json_files)

  for i, json_file in enumerate(json_files, 1):
    media_path = json_file.with_suffix('')
    if not media_path.exists():
      continue

    try:
      with open(json_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
      continue

    args = build_exiftool_args(metadata, media_path)
    if not args:
      continue

    cmd = ['exiftool', '-overwrite_original'] + args + [str(media_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
      processed += 1
    else:
      errors += 1
      print(f"  ERROR: {media_path.name}: {result.stderr.strip()}")

    if i % 500 == 0:
      print(f"  Progress: {i}/{total} ({processed} OK, {errors} errors)")

  print(f"\nProcessed: {processed} | Errors: {errors} | Total JSONs: {total}")


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <source_directory>")
    sys.exit(1)
  inject_metadata(sys.argv[1])
