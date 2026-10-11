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

The builds are a page each (3 MB by V165), and a run used to leave every one in its folder. Each
build goes once its suite has run, but a variant the suite did not catch keeps its build, to be
looked at; the report names the folder, which is then the reader's to delete. A run stopped before
its end (Ctrl-C, a killed job) leaves its folder behind: the folder holds the id of the process
that made it, and the next run takes it away once that process is gone.
"""
import concurrent.futures
import os
import pathlib
import re
import shutil
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


def sweep():
    """the folders of runs stopped before their end: each goes once the process named in it is gone.
    A folder naming none (another tool's, or a run from before folders were marked) is left alone."""
    for d in pathlib.Path(tempfile.gettempdir()).glob('falsify_*'):
        try:
            pid = int((d / 'pid').read_text())
        except (OSError, ValueError):
            continue
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            shutil.rmtree(d, ignore_errors=True)
        except OSError:
            pass   # alive, and not ours to signal


sweep()
tmp = pathlib.Path(tempfile.mkdtemp(prefix='falsify_'))
(tmp / 'pid').write_text(str(os.getpid()))


def one(name):
    """a variant built and checked; its build kept only when the suite did not catch it"""
    out = tmp / (name + '.html')
    name, verdict, fails = check(name, out)
    if verdict in ('caught', 'BUILD-ERROR'):
        out.unlink(missing_ok=True)
    return name, verdict, fails


def check(name, out):
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
try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as ex:
        for name, verdict, fails in ex.map(one, names):
            results[name] = (verdict, fails)
except BaseException:
    shutil.rmtree(tmp, ignore_errors=True)   # stopped: nothing in it was looked at
    raise

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
kept = sorted(p.name for p in tmp.glob('*.html'))
if kept:
    (tmp / 'pid').unlink(missing_ok=True)   # the reader's now: no later run takes it away
    print('\nTheir builds are kept to look at, in %s (%s); delete the folder when done.' % (tmp, ', '.join(kept)))
else:
    shutil.rmtree(tmp, ignore_errors=True)
sys.exit(1 if bad else 0)
