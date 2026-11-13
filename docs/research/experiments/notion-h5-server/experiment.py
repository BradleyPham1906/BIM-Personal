import json,pathlib
# Oracle says whether a user-chosen 1-D probe overlaps a hidden 1-D interval.
a,b=37.125,42.875
calls=0
def overlaps(lo,hi):
 global calls; calls+=1;return lo<=b and hi>=a
# Probe [-100, x] to localize the left boundary; user controls x.
lo,hi=0.,100.
for _ in range(20):
 mid=(lo+hi)/2
 if overlaps(-100,mid):hi=mid
 else:lo=mid
r={'hidden_interval':[a,b],'left_boundary_inferred_interval':[lo,hi],'queries':calls,'interval_width':hi-lo,'assumptions':'adversary may submit adaptive arbitrary probes and see each yes/no result; no policy/rate limiting; simplified 1D illustrative oracle, not a real backend attack test'}
print(json.dumps(r,indent=2));pathlib.Path(__file__).with_name('results.json').write_text(json.dumps(r,indent=2)+'\n')
