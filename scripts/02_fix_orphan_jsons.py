#!/usr/bin/env python3
"""Fix Google Takeout's mismatched JSON sidecar naming.

Google names sidecars like: PHOTO.ext(N).json
But the actual file is:     PHOTO(N).ext

This script detects orphan JSONs and renames them to match their media file.
"""

import os
import re
import sys
from pathlib import Path

MEDIA_EXTENSIONS = {
  '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
  '.heic', '.heif', '.webp', '.raw', '.cr2', '.nef', '.arw',
  '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.3gp', '.m4v'
}


def find_media_match(json_path, directory):
  """Try to find the media file that a JSON sidecar belongs to."""
  stem = json_path.stem
  if stem.endswith('.json'):
    stem = stem[:-5]

  # Pattern: filename.ext(N) -> look for filename(N).ext
  match = re.match(r'^(.+?)(\.\w+)\((\d+)\)$', stem)
  if match:
    base, ext, num = match.groups()
    candidate = directory / f"{base}({num}){ext}"
    if candidate.exists():
      return candidate

  # Pattern: filename(N).ext -> already correct
  match = re.match(r'^(.+?)\((\d+)\)(\.\w+)$', stem)
  if match:
    base, num, ext = match.groups()
    candidate = directory / f"{base}({num}){ext}"
    if candidate.exists():
      return candidate

  # Try direct match without .json extension
  for ext in MEDIA_EXTENSIONS:
    candidate = directory / f"{stem}{ext}"
    if candidate.exists():
      return candidate

  return None


def fix_orphan_jsons(source_dir):
  source = Path(source_dir)
  if not source.exists():
    print(f"Error: {source_dir} does not exist")
    sys.exit(1)

  fixed = 0
  orphans = 0

  for json_file in source.rglob('*.json'):
    if not json_file.is_file():
      continue

    # Check if this JSON already has a matching media file
    expected_media = json_file.with_suffix('')
    if expected_media.suffix.lower() in MEDIA_EXTENSIONS and expected_media.exists():
      continue

    media_match = find_media_match(json_file, json_file.parent)
    if media_match:
      new_json_name = Path(str(media_match) + '.json')
      if new_json_name.exists():
        print(f"  SKIP (conflict): {json_file.name}")
        continue
      json_file.rename(new_json_name)
      fixed += 1
      print(f"  {json_file.name} -> {new_json_name.name}")
    else:
      orphans += 1

  print(f"\nFixed: {fixed} | Unresolved orphans: {orphans}")


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <source_directory>")
    sys.exit(1)
  fix_orphan_jsons(sys.argv[1])
