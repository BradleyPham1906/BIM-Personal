# V172c experiment: the reference sky on a horizontal plane against the EPW's own GHI.
import sys, json
S = sys.argv[1]; sys.path[:0] = [S + '/dl/lbc', S + '/dl/lbg']
from ladybug.viewsphere import view_sphere
from ladybug.epw import EPW
ref = json.load(open(S + '/exp/ref_sky_phl.json'))
epw = EPW(sys.argv[2])
ghi = sum(epw.global_horizontal_radiation.values) / 1000
dni = sum(epw.direct_normal_radiation.values) / 1000
dhi = sum(epw.diffuse_horizontal_radiation.values) / 1000
print('EPW annual: GHI %.1f, DHI %.1f, DNI %.1f kWh/m2' % (ghi, dhi, dni))
for k, vecs in (('tregenza', view_sphere.tregenza_dome_vectors), ('reinhart', view_sphere.reinhart_dome_vectors)):
    d = sum(v * vec.z for v, vec in zip(ref[k]['dir'], vecs))
    f = sum(v * vec.z for v, vec in zip(ref[k]['dif'], vecs))
    print('%s: direct on horizontal %.1f, diffuse on horizontal %.1f, total %.1f (%.1f%% of GHI)' % (k, d, f, d + f, 100 * (d + f) / ghi))
