"""falsify_all.py -- build every broken variant and prove the suite catches each one.

Usage: python3 falsify_all.py patches/falsify_phaseNN.py tests/bim_phaseNN_....py [-jN]

The variant list is READ OUT OF the falsify script's own VARIANTS dict rather than passed in,
so the runner and the script cannot disagree about what is being tested (law 3).

Each variant must make the suite FAIL. A variant the suite still PASSES is reported as a
DEFECT, not a pass -- V94's lesson: it usually means the code it removed was unreachable, so
the check was measuring nothing. It is also worth checking that a variant failed for the RIGHT
reason: a variant that breaks the JavaScript makes the page fail to load, and the suite then
fails at its marker check without ever testing the thing that was broken. This runner flags
that case separately.
"""
import concurrent.futures
import pathlib
import re
import subprocess
import sys
import tempfile
import time

args = [a for a in sys.argv[1:] if not a.startswith('-j')]
jobs = 4
for a in sys.argv[1:]:
    if a.startswith('-j'):
        jobs = int(a[2:] or 4)

FALS = pathlib.Path(args[0]).resolve()
SUITE = pathlib.Path(args[1]).resolve()
ROOT = FALS.parent.parent

src = FALS.read_text(encoding='utf-8')
block = src.split('VARIANTS = {', 1)[1] if 'VARIANTS = {' in src else ''
names = re.findall(r"^\s{4}'([a-z0-9_]+)':", block, re.M)
if not names:
    print('No variants found in %s' % FALS)
    sys.exit(2)

tmp = pathlib.Path(tempfile.mkdtemp(prefix='falsify_'))


def one(name):
    out = tmp / (name + '.html')
    b = subprocess.run([sys.executable, str(FALS), name, str(out)],
                       cwd=str(ROOT), capture_output=True, text=True)
    if b.returncode != 0:
        return name, 'BUILD-ERROR', (b.stderr or b.stdout).strip().splitlines()[-1:]
    try:
        r = subprocess.run([sys.executable, str(SUITE), str(out)],
                           capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        # V123: a suite that never finishes is a defect of the suite (an unbounded wait), and one
        # such variant used to raise out of the pool and cancel every variant still queued
        return name, 'TIMEOUT', ['the suite did not finish in 900 s -- look for an unbounded loop']
    o = r.stdout + r.stderr
    fails = [l.strip() for l in o.splitlines() if l.startswith('  FAIL')]
    if re.search(r'^RESULT: FAIL', o, re.M):
        # a variant that only trips the marker check broke the BUILD, not the behaviour
        if len(fails) == 1 and 'marker is present' in fails[0]:
            return name, 'WRONG-REASON', fails
        return name, 'caught', fails
    return name, 'NOT-CAUGHT', fails


t0 = time.time()
results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
    for name, verdict, fails in ex.map(one, names):
        results[name] = (verdict, fails)

bad = []
for n in names:
    verdict, fails = results[n]
    mark = 'ok  ' if verdict == 'caught' else '>>> '
    first = (fails[0][:96] if fails else '')
    print('%s%-30s %-13s %s' % (mark, n, verdict, first))
    if verdict != 'caught':
        bad.append(n)

print('\n%d variants, %d caught, %d not, in %.1fs with %d workers'
      % (len(names), len(names) - len(bad), len(bad), time.time() - t0, jobs))
if bad:
    print('\nVARIANTS THE SUITE DID NOT CATCH PROPERLY: ' + ', '.join(bad))
    print('NOT-CAUGHT usually means the code the variant removed was unreachable -- fix the')
    print('code so the guard matters, never weaken the check to match.')
    print('WRONG-REASON means the variant broke the build, so nothing was actually tested.')
    print('TIMEOUT means the suite hung on the variant: bound the loop that waited, then run again.')
sys.exit(1 if bad else 0)
