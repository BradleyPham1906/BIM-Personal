import re, subprocess, sys, pathlib
t = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
op = re.compile(r'<!--|<(script|style)\b[^>]*>', re.I)
i = 0; n = 0; bad = 0
while True:
    m = op.search(t, i)
    if not m: break
    if m.group(0) == '<!--':
        i = t.index('-->', m.end()) + 3; continue
    tag = m.group(1).lower(); e = t.index('</%s>' % tag, m.end())
    if tag == 'script':
        n += 1
        p = pathlib.Path('/tmp/p119/js/s%03d.js' % n); p.write_text(t[m.end():e], encoding='utf-8')
        r = subprocess.run(['node', '--check', str(p)], capture_output=True, text=True)
        if r.returncode:
            bad += 1; print('SCRIPT', n, 'line', t[:m.end()].count('\n') + 1, r.stderr[:400])
    i = e + len(tag) + 3
print('scripts', n, 'syntax errors', bad)
