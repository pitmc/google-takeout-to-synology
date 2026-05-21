#!/usr/bin/env python3
"""Organize media files into YYYY/MM-Month/ folder structure.

Date resolution order:
1. EXIF DateTimeOriginal from file
2. Date parsed from filename (e.g., IMG_20200315_...)
3. Parent folder name (e.g., "Photos from 2020")
4. Fallback: no-date/
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

MEDIA_EXTENSIONS = {
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
  '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef', '.arw',
  '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.3gp', '.m4v'
}

MONTHS = {
  1: '01-January', 2: '02-February', 3: '03-March', 4: '04-April',
  5: '05-May', 6: '06-June', 7: '07-July', 8: '08-August',
  9: '09-September', 10: '10-October', 11: '11-November', 12: '12-December'
}


def get_exif_date(filepath):
  """Extract DateTimeOriginal via exiftool."""
  result = subprocess.run(
    ['exiftool', '-s3', '-DateTimeOriginal', str(filepath)],
    capture_output=True, text=True
  )
  date_str = result.stdout.strip()
  if date_str and date_str != '0000:00:00 00:00:00':
    match = re.match(r'(\d{4}):(\d{2}):\d{2}', date_str)
    if match:
      return int(match.group(1)), int(match.group(2))
  return None, None


def get_filename_date(filepath):
  """Try to extract date from filename patterns."""
  name = filepath.stem
  patterns = [
    r'(\d{4})(\d{2})\d{2}',       # IMG_20200315, VID_20200315
    r'(\d{4})-(\d{2})-\d{2}',     # 2020-03-15
    r'(\d{4})_(\d{2})_\d{2}',     # 2020_03_15
  ]
  for pattern in patterns:
    match = re.search(pattern, name)
    if match:
      year, month = int(match.group(1)), int(match.group(2))
      if 1990 <= year <= 2030 and 1 <= month <= 12:
        return year, month
  return None, None


def get_folder_date(filepath):
  """Try to extract year from parent folder name like 'Photos from 2020'."""
  folder_name = filepath.parent.name
  match = re.search(r'(\d{4})', folder_name)
  if match:
    year = int(match.group(1))
    if 1990 <= year <= 2030:
      return year, None
  return None, None


def organize(source_dir, output_dir):
  source = Path(source_dir)
  output = Path(output_dir)

  if not source.exists():
    print(f"Error: {source_dir} does not exist")
    sys.exit(1)

  output.mkdir(parents=True, exist_ok=True)
  moved = 0
  no_date = 0

  media_files = [f for f in source.rglob('*') if f.is_file() and f.suffix.lower() in MEDIA_EXTENSIONS]
  total = len(media_files)
  print(f"Found {total} media files to organize")

  for i, filepath in enumerate(media_files, 1):
    year, month = get_exif_date(filepath)

    if not year:
      year, month = get_filename_date(filepath)

    if not year:
      year, month = get_folder_date(filepath)

    if year:
      if month:
        dest_dir = output / str(year) / MONTHS[month]
      else:
        dest_dir = output / str(year)
    else:
      dest_dir = output / 'no-date'
      no_date += 1

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filepath.name

    if dest_path.exists():
      stem = filepath.stem
      suffix = filepath.suffix
      counter = 1
      while dest_path.exists():
        dest_path = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    shutil.move(str(filepath), str(dest_path))
    moved += 1

    if i % 500 == 0:
      print(f"  Progress: {i}/{total}")

  print(f"\nMoved: {moved} | No date: {no_date}")


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <source_directory> <output_directory>")
    sys.exit(1)
  organize(sys.argv[1], sys.argv[2])
