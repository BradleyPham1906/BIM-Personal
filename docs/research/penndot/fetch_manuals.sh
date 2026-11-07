#!/usr/bin/env bash
# Download the public PennDOT engineering program user manuals.
# These are FREE and PUBLIC documentation. This script does not touch the licensed programs.
# Run from anywhere with normal internet access:  bash fetch_manuals.sh
set -u
BASE="https://penndot.engrprograms.com/home/Ordering/User%20Manual"
OUT="${1:-.}"
mkdir -p "$OUT"

# Verified present
VERIFIED="PSLRFD STLRFD ABLRFD BAR7 ARCH"
# Same naming pattern, not yet confirmed - the script reports which ones exist
UNVERIFIED="BXLRFD BPLRFD FBLRFD TRLRFD SNLRFD SPLRFD PS3 BOX5 ABUT5 CBA BRGEO BSP CAMBR"

get () {
  local name="$1" tag="$2"
  local url="$BASE/${name}%20Users%20Manual.pdf"
  local dest="$OUT/${name}_Users_Manual.pdf"
  local code
  code=$(curl -sS -L --max-time 120 -o "$dest" -w "%{http_code}" "$url" 2>/dev/null)
  if [ "$code" = "200" ] && [ -s "$dest" ] && head -c 4 "$dest" | grep -q "%PDF"; then
    printf "  OK       %-8s %-12s %s bytes\n" "$name" "$tag" "$(wc -c < "$dest")"
  else
    rm -f "$dest"
    printf "  MISSING  %-8s %-12s (http %s)\n" "$name" "$tag" "$code"
  fi
}

echo "PennDOT user manuals -> $OUT"
for n in $VERIFIED;   do get "$n" "[verified]";   done
for n in $UNVERIFIED; do get "$n" "[try]";        done

echo
echo "Other official documents"
for u in "OrderForm(2025-08).pdf" "UpdateForm(08-25).pdf" "EngAsst(2025-08).pdf"; do
  enc=$(printf '%s' "$u" | sed 's/(/%28/g; s/)/%29/g')
  curl -sS -L --max-time 60 -o "$OUT/$u" \
    "https://penndot.engrprograms.com/home/Ordering/$enc" 2>/dev/null \
    && printf "  OK       %s\n" "$u" || printf "  MISSING  %s\n" "$u"
done
echo
echo "Done. Manuals are public documentation; the programs themselves are licensed separately."
