#!/usr/bin/env python3
"""embed_py.py -- the app's Python adapters, as the ES5 strings the engine hands its workers (V172b, V177).

  python3 tools/embed_py.py          write each adapter's .js from its .py
  python3 tools/embed_py.py --check  exit 1 when a pair differs

  src/py/bim_ladybug.py -> src/js/engine/ladybug/adapter-py.js  (BIM_LB_PY, the Ladybug analyses)
  src/py/bim_ifcos.py   -> src/js/engine/io/ifcos-py.js         (BIM_IFCOS_PY, Save as IFC through IfcOpenShell)

An adapter is the app's own Python (read it, edit it, run it natively in the suites' reference). Its worker writes
it into Pyodide's site-packages beside the pinned wheels, so it travels inside the app's build, versioned with the
JavaScript that calls it, never fetched beside the runtime. Each line is a JSON string, ASCII only, so the engine
stays ASCII and ES5."""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

PAIRS = [
    {'py': 'src/py/bim_ladybug.py', 'js': 'js/engine/ladybug/adapter-py.js', 'head': '''  /* ================= __acad3dV172b: the Ladybug adapter's Python, as text =================
     Written by tools/embed_py.py from src/py/bim_ladybug.py: edit the .py, then run the tool (--check proves the two
     agree). The worker writes it into Pyodide's site-packages beside the pinned wheels; Ladybug's own code runs
     unchanged beneath it (docs/research/research-ladybug-weather-comfort.md). */
  var BIM_LB_PY=[
'''},
    {'py': 'src/py/bim_ifcos.py', 'js': 'js/engine/io/ifcos-py.js', 'head': '''  /* ================= __acad3dV177: the IfcOpenShell adapter's Python, as text =================
     Written by tools/embed_py.py from src/py/bim_ifcos.py: edit the .py, then run the tool (--check proves the two
     agree). The IFC worker (io/ifcos-worker.js) writes it into Pyodide's site-packages beside the pinned wheels;
     IfcOpenShell's own code runs unchanged beneath it (docs/research/research-ifcopenshell-app.md). */
  var BIM_IFCOS_PY=[
'''},
]


def render(pair):
    lines = (ROOT / pair['py']).read_text(encoding='utf-8').split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    body = ',\n'.join('    ' + json.dumps(ln, ensure_ascii=True) for ln in lines)
    return pair['head'] + body + "\n  ].join('\\n')+'\\n';\n"


def main():
    # The engine file is an ES module: its import and export lines (tools/engine_modules.cjs) stay as they are.
    sys.path.insert(0, str(ROOT / 'tools'))
    import build_app
    check = '--check' in sys.argv[1:]
    bad = 0
    for pair in PAIRS:
        js = ROOT / 'src' / pair['js']
        have = js.read_text(encoding='utf-8') if js.exists() else ''
        code = build_app.unmodule(pair['js'], have)
        head = build_app.MOD_HEAD.match(have)
        tail = build_app.MOD_TAIL.search(have)
        body = render(pair)
        out = (head.group(0) if head else '') + (body[:-1] + tail.group(0) if tail else body)
        rel_js, rel_py = js.relative_to(ROOT), pathlib.Path(pair['py'])
        if check:
            if code != body:
                print('%s is not what %s embeds: run python3 tools/embed_py.py' % (rel_js, rel_py))
                bad = 1
            else:
                print('%s embeds %s (%d lines)' % (rel_js, rel_py, body.count('\n') - 6))
            continue
        if out == have:
            print('%s is current' % rel_js)
            continue
        js.parent.mkdir(parents=True, exist_ok=True)
        js.write_text(out, encoding='utf-8')
        print('wrote %s: %d bytes' % (rel_js, len(out)))
    sys.exit(bad)


if __name__ == '__main__':
    main()
