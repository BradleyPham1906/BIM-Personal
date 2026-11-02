# V172c experiment (after the second reader, 2026-11-01): does Ladybug's SkyMatrix._parse_mtx_data put each of
# gendaymtx's patches on the right dome patch? An independent parse finds the header's end by its blank line (the
# Radiance header format), skips the ground (patch 0, gendaymtx.c), and converts each sky patch the same way.
# Run on each gendaymtx build given; a build whose header Ladybug's fixed slice does not fit must fail.
import sys, subprocess
S = sys.argv[1]; sys.path[:0] = [S + '/dl/lbc', S + '/dl/lbg', S + '/dl/lbr']
from ladybug_radiance.skymatrix import SkyMatrix
wea = open(sys.argv[2], 'rb').read()
for exe in sys.argv[3:]:
    for dens in (1, 2):
        for part in ('-d', '-s'):
            out = subprocess.run([exe, '-m', str(dens), part, '-O1', '-A'], input=wea, capture_output=True).stdout
            hours = 8760
            lb = SkyMatrix._parse_mtx_data(SkyMatrix.__new__(SkyMatrix), out, hours, dens)
            lines = out.split(b'\n')
            k = lines.index(b'')                 # the blank line that ends the header
            rows = lines[k + 2:-1]               # skip the ground
            mine, i = [], 0
            for r, n in enumerate(SkyMatrix.PATCHES_PER_ROW[dens]):
                for line in rows[i:i + n]:
                    R, G, B = (float(x) for x in line.split())
                    w = 0.265074126 * R + 0.670114631 * G + 0.064811243 * B
                    mine.append(w * SkyMatrix.PATCH_ROW_COEFF[dens][r] * hours / 1000)
                i += n
            bad = sum(1 for a, b in zip(lb, mine) if abs(a - b) > 1e-12)
            print('%-40s -m %d %s: header %d lines, %d patches, %d misplaced by Ladybug%s' % (
                exe.split('/')[-1] + (' (' + exe.split('/')[-2] + ')'), dens, part, k + 1, len(mine), bad,
                '' if len(lb) == len(mine) else ' (Ladybug gave %d)' % len(lb)))
