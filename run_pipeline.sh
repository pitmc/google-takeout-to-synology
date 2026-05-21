#!/bin/bash
# Full pipeline: Google Takeout → organized photos with EXIF metadata
set -e

if [ $# -lt 2 ]; then
  echo "Usage: $0 <source_directory> <output_directory>"
  echo ""
  echo "  source_directory: Path to extracted Google Takeout 'Google Photos' folder"
  echo "  output_directory: Where to place organized photos (YYYY/MM-Month structure)"
  exit 1
fi

SOURCE_DIR="$1"
OUTPUT_DIR="$2"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)/scripts"

if [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: Source directory '$SOURCE_DIR' does not exist"
  exit 1
fi

if ! command -v exiftool &> /dev/null; then
  echo "Error: exiftool is not installed. See README.md for installation instructions."
  exit 1
fi

if ! command -v python3 &> /dev/null; then
  echo "Error: python3 is required"
  exit 1
fi

echo "========================================="
echo " Google Takeout to Synology Photos"
echo "========================================="
echo ""
echo "Source: $SOURCE_DIR"
echo "Output: $OUTPUT_DIR"
echo ""

echo "[1/5] Normalizing file extensions..."
python3 "$SCRIPT_DIR/01_normalize_extensions.py" "$SOURCE_DIR"
echo ""

echo "[2/5] Fixing orphan JSON sidecars..."
python3 "$SCRIPT_DIR/02_fix_orphan_jsons.py" "$SOURCE_DIR"
echo ""

echo "[3/5] Injecting EXIF metadata from JSONs..."
python3 "$SCRIPT_DIR/03_inject_exif_metadata.py" "$SOURCE_DIR"
echo ""

echo "[4/5] Organizing by date..."
python3 "$SCRIPT_DIR/04_organize_by_date.py" "$SOURCE_DIR" "$OUTPUT_DIR"
echo ""

echo "[5/5] Cleaning up JSON and HTML files..."
python3 "$SCRIPT_DIR/05_cleanup.py" "$SOURCE_DIR"
echo ""

echo "========================================="
echo " Done!"
echo "========================================="
echo ""
echo "Your photos are organized in: $OUTPUT_DIR"
echo "You can now copy this folder to your Synology NAS."
