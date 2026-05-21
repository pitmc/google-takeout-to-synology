#!/usr/bin/env python3
"""Normalize file extensions to lowercase and rename matching JSON sidecars."""

import os
import sys
from pathlib import Path

MEDIA_EXTENSIONS = {
  '.JPG', '.JPEG', '.PNG', '.GIF', '.BMP', '.TIFF', '.TIF',
  '.HEIC', '.HEIF', '.WEBP', '.RAW', '.CR2', '.NEF', '.ARW',
  '.MP4', '.MOV', '.AVI', '.MKV', '.WMV', '.FLV', '.3GP', '.M4V'
}


def normalize_extensions(source_dir):
  source = Path(source_dir)
  if not source.exists():
    print(f"Error: {source_dir} does not exist")
    sys.exit(1)

  renamed = 0
  for filepath in source.rglob('*'):
    if not filepath.is_file():
      continue
    ext = filepath.suffix
    if ext.upper() in MEDIA_EXTENSIONS and ext != ext.lower():
      new_path = filepath.with_suffix(ext.lower())
      if new_path.exists():
        print(f"  SKIP (conflict): {filepath.name}")
        continue
      filepath.rename(new_path)
      renamed += 1
      json_sidecar = Path(str(filepath) + '.json')
      if json_sidecar.exists():
        new_json = Path(str(new_path) + '.json')
        json_sidecar.rename(new_json)
      print(f"  {filepath.name} -> {new_path.name}")

  print(f"\nRenamed {renamed} files")


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <source_directory>")
    sys.exit(1)
  normalize_extensions(sys.argv[1])
