"""patch_phase163a.py -- V163: the SketchUp reader goes into the page.

vendor/openskp/openskp_reader.es5.js -- openskp's TypeScript reader (MIT) with fflate (MIT) and
earcut (ISC), bundled and compiled to ES5 syntax by tools/openskp/build_reader.mjs -- is inlined
as a script block of its own between the shell and the engine. Its own block: a browser that
cannot run it still starts the app, and the import then says the reader did not load. It adds one
global, OpenSkp. The file is taken by its hash, so what is inlined is what the build tool wrote.
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'e206ae4501c1b76d143f7df47ccbabce6a5efbf39401c5b943ffdb662fed7796'
READER = pathlib.Path('vendor/openskp/openskp_reader.es5.js')
READER_SHA = '12816bb781931d10eed2ee0137007e69e6afa20ea0b8983e85bdbf64515f5543'

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
rd = READER.read_bytes()
if hashlib.sha256(rd).hexdigest() != READER_SHA:
    sys.exit('reader sha mismatch: %s' % hashlib.sha256(rd).hexdigest())
reader = rd.decode('ascii')
assert '</script' not in reader.lower()
assert reader.endswith('})();\n')


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


rep("</script>\n\n<script>\n/* The BIM engine: the model and its objects, the views, the tools, documentation and persistence.\n",
    "</script>\n\n<script>\n" + reader +
    "</script>\n\n<script>\n/* The BIM engine: the model and its objects, the views, the tools, documentation and persistence.\n")

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
