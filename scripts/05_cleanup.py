#!/usr/bin/env python3
"""Remove JSON sidecars and HTML files after metadata has been injected."""

import sys
from pathlib import Path


def cleanup(source_dir):
  source = Path(source_dir)
  if not source.exists():
    print(f"Error: {source_dir} does not exist")
    sys.exit(1)

  json_count = 0
  html_count = 0

  for f in source.rglob('*.json'):
    if f.is_file():
      f.unlink()
      json_count += 1

  for f in source.rglob('*.html'):
    if f.is_file():
      f.unlink()
      html_count += 1

  print(f"Removed: {json_count} JSON files, {html_count} HTML files")


if __name__ == '__main__':
  if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <source_directory>")
    sys.exit(1)
  cleanup(sys.argv[1])
