#!/usr/bin/env python3
"""Independent analytic toy cases; no app or CAD library is invoked."""
import math, platform
print('Python',platform.python_version(),platform.system())
w=math.sqrt(0.5)
def curve(t,wm):
    b0=(1-t)**2; b1=2*t*(1-t); b2=t*t
    d=b0+wm*b1+b2
    return ((b0+wm*b1)/d,(wm*b1+b2)/d)
def err(wm):
    return max(abs(math.hypot(*curve(i/100,wm))-1) for i in range(101))
print('quarter-circle samples = 101')
print('rational max radius error = %.17g' % err(w))
print('unit weights max radius error = %.17g' % err(1.0))
assert err(w)<1e-14 and err(1)>0.05
r=10000.; sweep=math.pi; tol=.002
requested=math.ceil(sweep/(2*math.acos(1-tol/r)))
n=max(2,min(256,requested))
sag=r*(1-math.cos(sweep/(2*n)))
print('arc radius m =',r,'sweep rad =',sweep,'target chord error m =',tol)
print('segments required =',requested,'cap =',n,'actual sagitta m = %.12g' % sag)
assert requested>256 and sag>tol
print('PASS analytic checks; not an application test')
