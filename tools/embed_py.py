#!/usr/bin/env python3
"""embed_py.py -- the Ladybug adapter's Python, as the ES5 string the engine hands its worker (V172b).

  python3 tools/embed_py.py          write src/js/engine/ladybug/adapter-py.js from src/py/bim_ladybug.py
  python3 tools/embed_py.py --check  exit 1 when the two differ

The adapter is the app's own Python (src/py/bim_ladybug.py: read it, edit it, run it natively in the suites'
reference). The worker writes it into Pyodide's site-packages beside the pinned wheels, so it travels inside the
app's build, versioned with the JavaScript that calls it, never fetched beside the runtime. Each line is a JSON
string, ASCII only, so the engine stays ASCII and ES5."""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = ROOT / 'src' / 'py' / 'bim_ladybug.py'
JS = ROOT / 'src' / 'js' / 'engine' / 'ladybug' / 'adapter-py.js'

HEAD = '''  /* ================= __acad3dV172b: the Ladybug adapter's Python, as text =================
     Written by tools/embed_py.py from src/py/bim_ladybug.py: edit the .py, then run the tool (--check proves the two
     agree). The worker writes it into Pyodide's site-packages beside the pinned wheels; Ladybug's own code runs
     unchanged beneath it (reference/research-ladybug-weather-comfort.md). */
  var BIM_LB_PY=[
'''


def render():
    lines = PY.read_text(encoding='utf-8').split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    body = ',\n'.join('    ' + json.dumps(ln, ensure_ascii=True) for ln in lines)
    return HEAD + body + "\n  ].join('\\n')+'\\n';\n"


def main():
    out = render()
    if '--check' in sys.argv[1:]:
        have = JS.read_text(encoding='utf-8') if JS.exists() else ''
        if have != out:
            print('%s is not what %s embeds: run python3 tools/embed_py.py' % (JS.relative_to(ROOT), PY.relative_to(ROOT)))
            sys.exit(1)
        print('%s embeds %s (%d lines)' % (JS.relative_to(ROOT), PY.relative_to(ROOT), out.count('\n') - 6))
        return
    JS.parent.mkdir(parents=True, exist_ok=True)
    JS.write_text(out, encoding='utf-8')
    print('wrote %s: %d bytes' % (JS.relative_to(ROOT), len(out)))


if __name__ == '__main__':
    main()
