# V172c experiment: Ladybug's patch vectors and solid angles, as JSON for the ray checks.
import sys, json
sys.path[:0] = [sys.argv[1] + '/dl/lbc', sys.argv[1] + '/dl/lbg']
from ladybug.viewsphere import view_sphere as V
def sa(rows, coeff):
    out = []
    for n, c in zip(rows, coeff):
        out += [c] * n
    return out
json.dump({'tregenza': {'v': [list(v.to_array()) for v in V.tregenza_dome_vectors],
                        'sr': sa(V.TREGENZA_PATCHES_PER_ROW + (1,), V.TREGENZA_COEFFICIENTS)},
           'reinhart': {'v': [list(v.to_array()) for v in V.reinhart_dome_vectors],
                        'sr': sa(V.REINHART_PATCHES_PER_ROW + (1,), V.REINHART_COEFFICIENTS)}},
          open(sys.argv[1] + '/exp/dome.json', 'w'))
