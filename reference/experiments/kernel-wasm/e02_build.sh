#!/usr/bin/env bash
# e02_build.sh -- the B-rep kernel research (reference/research-usd-brep.md), 2026-11-01.
# Builds NVIDIA's SMLib + SM_API (usd-brep, unchanged) and e02_driver.cpp to WebAssembly with
# Emscripten, outside the repository. Approved by the owner on 2026-11-01. Compile flags follow
# IFClite's native/smlib-adapter/CMakeLists.txt (C++17, SM_NO_DEBUG_CODE, SM_NO_GFX_OUTPUT_CODE,
# NDEBUG, -fexceptions; links ALLOW_MEMORY_GROWTH and an 8 MiB stack), with -O3 added.
# Usage: E02_SRC=<usd-brep checkout> E02_OUT=<scratch dir> EMSDK_ENV=<emsdk_env.sh> bash e02_build.sh
# Outputs in $E02_OUT: smlib.mjs + smlib.wasm (ES module, as IFClite), smlib_single.js (classic script,
# MODULARIZE, the wasm embedded as base64: the form a one-file app would carry), and build.log.
set -euo pipefail
: "${E02_SRC:?}" "${E02_OUT:?}" "${EMSDK_ENV:?}"
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$EMSDK_ENV" >/dev/null 2>&1
mkdir -p "$E02_OUT/obj"
BASEFLAGS="-O3 -std=c++17 -fexceptions -DSM_NO_DEBUG_CODE -DSM_NO_GFX_OUTPUT_CODE -DNDEBUG -w"
# Both trees have a StdAfx.h: kernel files take SMLib's first, API files (and the driver) SM_API's,
# as IFClite's CMakeLists.txt does with "BEFORE PRIVATE" for smlib_api.
KFLAGS="$BASEFLAGS -I$E02_SRC/source/SMLib/inc -I$E02_SRC/source/SM_API/inc"
AFLAGS="$BASEFLAGS -I$E02_SRC/source/SM_API/inc -I$E02_SRC/source/SMLib/inc"
echo "revision $(git -C "$E02_SRC" rev-parse HEAD)" > "$E02_OUT/build.log"
em++ --version | head -1 >> "$E02_OUT/build.log"
start=$(date +%s)
ls "$E02_SRC"/source/SMLib/src/*.cpp "$E02_SRC"/source/SM_API/src/*.cpp "$HERE/e02_driver.cpp" > "$E02_OUT/sources.txt"
echo "sources $(wc -l < "$E02_OUT/sources.txt")" >> "$E02_OUT/build.log"
compile() { # $1 = flags, stdin = source list
  xargs -P "$(nproc)" -I{} sh -c 'f="{}"; o="'"$E02_OUT"'/obj/$(echo "$f" | md5sum | cut -c1-12).o"; [ -f "$o" ] || em++ '"$1"' -c "$f" -o "$o" || { echo "FAILED $f"; exit 255; }'
}
grep '/source/SMLib/src/' "$E02_OUT/sources.txt" | compile "$KFLAGS"
grep -v '/source/SMLib/src/' "$E02_OUT/sources.txt" | compile "$AFLAGS"
echo "compile_seconds $(( $(date +%s) - start ))" >> "$E02_OUT/build.log"
EXPORTS="['_e02_init','_e02_box_minus_cylinder','_e02_plate16','_e02_wall_join_union','_e02_fillet_box_edge','_e02_tessellate_plate']"
LINK="-O3 -fexceptions -sALLOW_MEMORY_GROWTH=1 -sSTACK_SIZE=8388608 -sMODULARIZE=1 --no-entry -sEXPORTED_FUNCTIONS=$EXPORTS -sEXPORTED_RUNTIME_METHODS=['HEAPU8']"
em++ "$E02_OUT"/obj/*.o $LINK -sEXPORT_ES6=1 -sENVIRONMENT=web,worker,node -o "$E02_OUT/smlib.mjs"
em++ "$E02_OUT"/obj/*.o $LINK -sSINGLE_FILE=1 -sEXPORT_NAME=SmlibModule -sENVIRONMENT=web,worker,node -o "$E02_OUT/smlib_single.js"
# Upper bound: the whole kernel kept (no dead-code removal), for the size a full API binding would approach.
em++ "$E02_OUT"/obj/*.o -O3 -fexceptions -sALLOW_MEMORY_GROWTH=1 -sSTACK_SIZE=8388608 -sMODULARIZE=1 --no-entry \
  -sEXPORT_ES6=1 -sENVIRONMENT=web,worker,node -Wl,--no-gc-sections \
  "-sEXPORTED_FUNCTIONS=['_e02_init','_e02_box_minus_cylinder']" -o "$E02_OUT/smlib_full.mjs"
echo "full_wasm $(stat -c %s "$E02_OUT/smlib_full.wasm") gzip9 $(gzip -9c "$E02_OUT/smlib_full.wasm" | wc -c)" >> "$E02_OUT/build.log"
echo "total_seconds $(( $(date +%s) - start ))" >> "$E02_OUT/build.log"
ls -l "$E02_OUT"/smlib.wasm "$E02_OUT"/smlib.mjs "$E02_OUT"/smlib_single.js >> "$E02_OUT/build.log"
echo "wasm_gzip9 $(gzip -9c "$E02_OUT/smlib.wasm" | wc -c)" >> "$E02_OUT/build.log"
echo "single_gzip9 $(gzip -9c "$E02_OUT/smlib_single.js" | wc -c)" >> "$E02_OUT/build.log"
cat "$E02_OUT/build.log"
