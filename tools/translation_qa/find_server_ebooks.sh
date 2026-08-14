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
echo "Private HTML masters (admin/translations/private):"
if [ -d "$FOUND/admin/translations/private" ]; then
  find "$FOUND/admin/translations/private" \( -iname '*.html' -o -iname '*.htm' -o -iname '*.xhtml' \) 2>/dev/null | wc -l
  find "$FOUND/admin/translations/private" \( -iname '*.html' -o -iname '*.htm' -o -iname '*.xhtml' \) 2>/dev/null | head -20
else
  echo "  not present at $FOUND/admin/translations/private"
  find "$FOUND" -type d -path '*/admin/translations/private' 2>/dev/null | head -5
fi
echo
echo "Bookstore relay / pipeline files (list only; do not edit):"
find "$FOUND" \( -iname 'WORKORDERS_RELAY*.md' -o -iname 'LIC_EN_metadata.md' -o -iname 'translate_html.py' -o -iname 'fix_refusal_text.py' \) 2>/dev/null | head -20
echo
echo "First 40 EPUB/PDF paths:"
find "$FOUND" \( -iname '*.epub' -o -iname '*.pdf' \) \
  ! -path '*/assets/covers/*' ! -path '*/_PENDING_DELETE_*' \
  2>/dev/null | head -40
echo
echo "To copy translations onto the Windows PC (run from the docroot):"
echo "  mkdir -p /tmp/ab-ebooks"
echo "  find \"$FOUND/data\" -iname '*.epub' -exec cp -n {} /tmp/ab-ebooks/ \\;"
echo "  if [ -d \"$FOUND/admin/translations/private\" ]; then"
echo "    mkdir -p /tmp/ab-ebooks/private_html"
echo "    find \"$FOUND/admin/translations/private\" \\( -iname '*.html' -o -iname '*.htm' \\) -exec cp -n {} /tmp/ab-ebooks/private_html/ \\;"
echo "  fi"
echo "  tar -C /tmp -czf /tmp/ab-ebooks.tgz ab-ebooks"
echo "Then download /tmp/ab-ebooks.tgz in cPanel File Manager and unpack into"
echo "  C:\\Alertness AI\\website books\\store_epubs"
echo "Copy private_html into a bookstore clone at admin\\translations\\private if you have one."
echo "Do NOT copy sidecar JSON. Its text field is the contamination that was removed,"
echo "not the original English. Repair goes through the English master, never that field."
echo "Do NOT re-harden translate_html.py (CC-Translate already landed task #58)."
echo "Then pull the checker branch and run rescan.bat. Leave any in-progress PDF scan running."
