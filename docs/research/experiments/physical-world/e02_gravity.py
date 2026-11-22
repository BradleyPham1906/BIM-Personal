"""e02: is 'geodetic gravity' worth modelling for buildings? WGS 84 normal gravity on the ellipsoid
(Somigliana closed form, NIMA TR8350.2 3rd ed. eq. 4-1, constants table 3.4) with the free-air
gradient ~ -3.086e-6 s^-2 per m, and the angle gravity turns through across a site. Data only."""
import math
GE, K, E2 = 9.7803253359, 0.00193185265241, 0.00669437999013
def g(lat_deg, h=0.0):
    s2 = math.sin(math.radians(lat_deg)) ** 2
    return GE * (1 + K * s2) / math.sqrt(1 - E2 * s2) - 3.086e-6 * h
std = 9.80665
for lat in (0, 20, 34, 40.4, 45, 60, 90):
    print(f"lat {lat:5.1f}  g {g(lat):.5f}  vs 9.80665 {100*(g(lat)-std)/std:+.3f}%   at 500 m {g(lat,500):.5f}")
R = 6371000.0
for span in (100, 1000, 10000):
    print(f"gravity turns {math.degrees(span/R):.5f} deg over {span} m; a 300 m tower's top is "
          f"{300*span/R*1000:.2f} mm off a parallel line at that distance")
print("range equator to pole:", f"{100*(g(90)-g(0))/g(0):.3f}%")
