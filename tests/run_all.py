"""run_all.py -- run every bim_phase suite against one build, N at a time.

Usage: python3 run_all.py [path/to/canvas_v10.html] [name-substring-filter] [-jN]

-j1 gives the old one-at-a-time behaviour. The default is 6. There is ONE runner rather than a
serial one and a parallel one, because two runners are two verdicts that can disagree.

Why this is worth having: these suites are almost entirely WAITING, not computing. A single
suite spends six or seven seconds inside wait_for_timeout calls plus a couple of seconds
loading a 2 MB file, and almost none of that is CPU. Running them one at a time leaves two
cores idle for minutes. The default of 4 workers oversubscribes 2 cores deliberately, because
the resource actually being contended is wall-clock sleep.

Output is buffered per suite and printed on completion, so a parallel run reads exactly like a
serial one rather than interleaving. Same verdict rules, same exit code.
"""
import concurrent.futures
import pathlib
import re
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent

args = [a for a in sys.argv[1:] if not a.startswith('-j')]
jobs = 4
for a in sys.argv[1:]:
    if a.startswith('-j'):
        jobs = int(a[2:] or 4)

HTML = args[0] if len(args) > 0 else str(HERE.parent / 'canvas_v10.html')
FILT = args[1] if len(args) > 1 else ''

suites = sorted(p.name for p in HERE.glob('bim_phase*.py') if FILT in p.name)


def run_one(s):
    try:
        r = subprocess.run([sys.executable, s, HTML], cwd=str(HERE),
                           capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return s, None, 'TIMEOUT', 'timeout'
    m = re.search(r'^(\d+)/(\d+) checks passed', out, re.M)
    if re.search(r'^RESULT: PASS', out, re.M):
        verdict = 'PASS'
    elif re.search(r'^RESULT: FAIL', out, re.M):
        verdict = 'FAIL'
    elif m and m.group(1) == m.group(2):
        verdict = 'PASS'
    else:
        verdict = 'FAIL'
    return s, m, verdict, out


t0 = time.time()
total = passed = 0
bad = []
with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
    futs = {ex.submit(run_one, s): s for s in suites}
    done = {}
    for f in concurrent.futures.as_completed(futs):
        s, m, verdict, out = f.result()
        done[s] = (m, verdict, out)
    # printed in suite order, so a parallel run reads like a serial one
    for s in suites:
        m, verdict, out = done[s]
        if verdict == 'TIMEOUT':
            print('%-62s TIMEOUT' % s)
            bad.append((s, 'timeout'))
            continue
        if m:
            passed += int(m.group(1))
            total += int(m.group(2))
            print('%-62s %6s/%-6s %s' % (s, m.group(1), m.group(2), verdict))
        else:
            print('%-62s %-14s %s' % (s, 'NO COUNT', verdict))
        if verdict != 'PASS':
            bad.append((s, out))

print('\n%d suites, %d/%d checks passed in %.1fs with %d workers'
      % (len(suites), passed, total, time.time() - t0, jobs))
if bad:
    print('\nFAILING SUITES:')
    for s, out in bad:
        print('\n===== %s =====' % s)
        for line in out.splitlines():
            if line.startswith('  FAIL') or line.startswith('  - '):
                print(line)
sys.exit(1 if bad else 0)
