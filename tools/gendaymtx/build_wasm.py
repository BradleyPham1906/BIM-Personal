#!/usr/bin/env python3
"""build_wasm.py -- Radiance's gendaymtx as a WASI module, for the V172c sky (runtime/radiance/).

  python3 tools/gendaymtx/build_wasm.py RADIANCE_DIR WASI_DIR [OUT]

Ladybug's SkyMatrix (ladybug-radiance) runs Radiance's gendaymtx as a program; Pyodide cannot start one, so the app
runs the same C, compiled to WebAssembly, from the Ladybug worker (the owner, 2026-11-01:
reference/research-ladybug-sun-radiation.md). This builds it from:
- RADIANCE_DIR: a checkout of https://github.com/LBNL-ETA/Radiance at the commit RADIANCE_COMMIT (branch master; the
  default branch, cvsimport, holds only a README). Its eight files below are compiled unchanged.
- WASI_DIR: wasi-sdk 22's wasi-sysroot-22.0.tar.gz and libclang_rt.builtins-wasm32-wasi-22.0.tar.gz, unpacked there
  (github.com/WebAssembly/wasi-sdk/releases/tag/wasi-sdk-22), each checked against the SHA-256 below.
- clang 18 with the wasm32 target, and wasm-ld 18.
It prints the module's size and SHA-256, which runtime/MANIFEST.json pins. The module reads the weather (a Wea) on
stdin and writes the matrix on stdout; it opens no files. Nothing here is run by the app or the suites."""
import hashlib, pathlib, subprocess, sys

RADIANCE_COMMIT = '5b2a2154cc7d97a997d3d9a3929567b75d78174a'
SOURCES = ['src/gen/gendaymtx.c', 'src/gen/sun.c', 'src/gen/loadEPW.c', 'src/common/fixargv0.c',
           'src/common/header.c', 'src/common/portio.c', 'src/common/tcos.c', 'src/common/fputword.c']
WASI_TARS = {'wasi-sysroot-22.0.tar.gz': '23881870d5a9c94df0529bc3e9b13682b7bbb07e5167555132fdc14e1faf1bb8',
             'libclang_rt.builtins-wasm32-wasi-22.0.tar.gz':
                 '9c2f54ff7e3597ed1014f9a8e818ce60ec5d2099f1f4bdbf22310d799b46fdf6'}
CLANG_INCLUDE = '/usr/lib/llvm-18/lib/clang/18/include'


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    rad, wasi = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
    out = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else 'gendaymtx.wasm').resolve()
    if out.name != 'gendaymtx.wasm':
        sys.exit('name the output gendaymtx.wasm: the linker writes its name into the module, so another name gives another hash')
    head = subprocess.run(['git', '-C', str(rad), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    if head != RADIANCE_COMMIT:
        sys.exit('Radiance is at %s, not %s' % (head or '(not a git checkout)', RADIANCE_COMMIT))
    for name, want in WASI_TARS.items():
        if sha(wasi / name) != want:
            sys.exit('%s does not match its SHA-256' % name)
    # clang's own headers, and the wasm32 builtins from wasi-sdk, as one resource folder
    rd = wasi / 'resource-dir'
    (rd / 'lib').mkdir(parents=True, exist_ok=True)
    if not (rd / 'include').exists():
        (rd / 'include').symlink_to(CLANG_INCLUDE)
    if not (rd / 'lib' / 'wasi').exists():
        (rd / 'lib' / 'wasi').symlink_to(wasi / 'lib' / 'wasi')
    cmd = ['clang', '--target=wasm32-wasi', '--sysroot=%s' % (wasi / 'wasi-sysroot'), '-resource-dir=%s' % rd,
           '-O2', '-w', '-I', str(rad / 'src/common'), '-D_WASI_EMULATED_PROCESS_CLOCKS', '-D_WASI_EMULATED_SIGNAL',
           '-o', str(out)] + [str(rad / s) for s in SOURCES] + \
          ['-lm', '-lwasi-emulated-process-clocks', '-lwasi-emulated-signal']
    subprocess.run(cmd, check=True, cwd=str(rad / 'src/gen'))
    print('%s: %d bytes, sha256 %s' % (out, out.stat().st_size, sha(out)))


if __name__ == '__main__':
    main()
