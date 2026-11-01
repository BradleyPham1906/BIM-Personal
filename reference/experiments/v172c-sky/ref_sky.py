# V172c experiment: the reference sky matrix, by Ladybug's own path with the native gendaymtx.
import sys, os, json, time
S = sys.argv[1]
sys.path[:0] = [S + '/dl/lbc', S + '/dl/lbr', S + '/dl/lbg']
os.environ['PATH'] = S + '/ref:' + os.environ['PATH']
from ladybug.wea import Wea
import ladybug_radiance.skymatrix as sm
sm.GENDAYMTX_EXE = S + '/ref/gendaymtx'
from ladybug_radiance.skymatrix import SkyMatrix
epw = sys.argv[2]
out = {}
for dens in (False, True):
    t = time.time()
    m = SkyMatrix.from_epw(epw, high_density=dens)
    m.folder = S + '/exp/tmp'
    m.compute_sky()
    out['reinhart' if dens else 'tregenza'] = {'dir': m.direct_values, 'dif': m.diffuse_values,
        'sec': time.time() - t}
    print('density', dens, len(m.direct_values), 'patches; direct sum', round(sum(m.direct_values), 1),
          'diffuse sum', round(sum(m.diffuse_values), 1), 'kWh/m2 x sr-weighted;', round(time.time() - t, 2), 's')
json.dump(out, open(S + '/exp/ref_sky_phl.json', 'w'))
