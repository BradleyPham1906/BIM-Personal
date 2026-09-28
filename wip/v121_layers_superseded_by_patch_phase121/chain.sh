#!/bin/bash
# Assemble patch_phase121[a-z].py and run them in order from the V119 build.
set -e
set -o pipefail
W=/home/claude/work
cp $W/canvas_v10.html.bak_phase121_pre $W/canvas_v10.html
H=$(sha256sum $W/canvas_v10.html | cut -d' ' -f1)
for L in "$@"; do
  OUT=$W/patches/patch_phase121$L.py
  if [ -f ${L}_full.py ]; then cp ${L}_full.py $OUT; else cat $L.py head.py ${L}_body.py tail.py > $OUT; fi
  sed -i "s/^BASE = 'CHAIN'/BASE = '$H'/" $OUT
  ( cd $W && python3 $OUT canvas_v10.html ) | tee chain_$L.txt
  H=$(sha256sum $W/canvas_v10.html | cut -d' ' -f1)
done
echo FINAL $H $(wc -c < $W/canvas_v10.html)
