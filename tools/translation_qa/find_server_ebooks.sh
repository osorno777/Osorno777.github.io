#!/bin/bash
# Run this ON the Alertness Books server (cPanel Terminal or SSH).
# It only lists EPUB/PDF paths; it does not change files.
# Docroot comment in robots.txt: /alertnessai.com/AlertnessBooks

set -euo pipefail
ROOTS=(
  "$HOME/alertnessai.com/AlertnessBooks"
  "$HOME/public_html/AlertnessBooks"
  "$HOME/public_html"
  "/home/*/alertnessai.com/AlertnessBooks"
  "/var/www/alertnessai.com/AlertnessBooks"
  "/var/www/html/AlertnessBooks"
)

echo "Looking for the Alertness Books docroot..."
FOUND=""
for root in "${ROOTS[@]}"; do
  for path in $root; do
    if [ -d "$path/data" ] && [ -d "$path/lib" ] && [ -d "$path/reader" ]; then
      FOUND="$path"
      break 2
    fi
  done
done

if [ -z "$FOUND" ]; then
  echo "Docroot not in the usual places. Search the whole account:"
  echo "  find \"\$HOME\" -type d -name AlertnessBooks 2>/dev/null"
  echo "Then: find /path/to/AlertnessBooks -iname '*.epub' | wc -l"
  exit 1
fi

echo "Docroot: $FOUND"
echo
echo "EPUB count:"
find "$FOUND" -iname '*.epub' 2>/dev/null | wc -l
echo
echo "First 40 EPUB paths:"
find "$FOUND" \( -iname '*.epub' -o -iname '*.pdf' \) \
  ! -path '*/assets/covers/*' ! -path '*/_PENDING_DELETE_*' \
  2>/dev/null | head -40
echo
echo "To copy translations onto the Windows PC (run from the docroot):"
echo "  mkdir -p /tmp/ab-ebooks"
echo "  find \"$FOUND/data\" -iname '*.epub' -exec cp -n {} /tmp/ab-ebooks/ \\;"
echo "  tar -C /tmp -czf /tmp/ab-ebooks.tgz ab-ebooks"
echo "Then download /tmp/ab-ebooks.tgz in cPanel File Manager and unpack into"
echo "  C:\\Alertness AI\\website books\\store_epubs"
echo "Then pull the checker branch (it now reads .epub) and run rescan.bat."
