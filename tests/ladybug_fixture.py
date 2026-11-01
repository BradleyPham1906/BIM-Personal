"""ladybug_fixture.py -- a made-up but realistic year of weather for V172b's suite, in the shapes the app reads.

An EPW (the EnergyPlus weather format: its data dictionary's 35 fields an hour, EnergyPlus 24.1 Auxiliary Programs),
a DDY (EnergyPlus SizingPeriod:DesignDay objects, laid out as a station's DDY from climate.onebuilding.org is), the
ZIP a station's files come in, and a year of Open-Meteo archive hours (its ten variables, in its answer's shape).
Deterministic (fixed seeds), for a site at 40 N 75 W in UTC-5 with a humid continental climate. Nothing here is from a
real station: the repository is public, and a station's files are a third party's.

Both formats sample the same hours: an EPW's "hour h" of a day is the hour ending at h:00, its temperature, humidity,
pressure and wind at h:00 and its radiation over the hour; Open-Meteo's value at time t is at t, and its radiation the
mean of the hour before t. So Open-Meteo's hour h:00 and the EPW's hour h hold the same numbers here, as they would
from one atmosphere.
"""
import datetime, io, json, math, random, zipfile

LAT, LON, TZ, ELEV = 40.0, -75.0, -5, 12.0
CITY, STATE, COUNTRY, WMO = 'Fixture City Intl AP', 'PA', 'USA', '999990'
STEM = 'USA_PA_Fixture.City.Intl.AP.999990_TMYx.2010-2024'
SIGMA = 5.6697e-8


def _es(t):
    """saturation vapour pressure over water, hPa (Magnus, for making humidity only)"""
    return 6.112 * math.exp(17.62 * t / (243.12 + t))


def _sun(lat, doy, hour_solar):
    d = math.radians(23.45) * math.sin(2 * math.pi * (284 + doy) / 365.0)
    w = math.radians(15.0 * (hour_solar - 12.0))
    p = math.radians(lat)
    return math.sin(p) * math.sin(d) + math.cos(p) * math.cos(d) * math.cos(w)


class Year(object):
    """the hours of one calendar year at the site, in its standard time; n+1 of them, to 1 January 00:00 of the next"""

    def __init__(self, year, seed=172):
        self.year = year
        self.leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        n = 8784 if self.leap else 8760
        self.n = n
        rnd = random.Random(seed)
        days = n // 24 + 2
        cloud = []
        c = 0.4
        for _ in range(days):
            c = min(1.0, max(0.0, 0.55 * c + 0.45 * rnd.random()))
            cloud.append(c)
        ph = [rnd.random() * 2 * math.pi for _ in range(4)]
        self.t0 = datetime.datetime(year, 1, 1)
        T, TD, RH, P, WS, WD, CC = [], [], [], [], [], [], []
        dirs = [(292.5, 0.30), (315.0, 0.16), (270.0, 0.14), (225.0, 0.11), (202.5, 0.09), (180.0, 0.07), (45.0, 0.07), (90.0, 0.06)]
        wd_prev = 292.5
        for i in range(n + 1):
            dt = self.t0 + datetime.timedelta(hours=i)
            doy = dt.timetuple().tm_yday
            hr = dt.hour
            day = i // 24
            season = math.sin(2 * math.pi * (doy - 110) / 365.25)
            t = 11.5 + 12.5 * season + 5.2 * math.sin(2 * math.pi * (hr - 9) / 24.0) + \
                2.6 * math.sin(2 * math.pi * i / (24 * 5.3) + ph[0]) + 1.4 * math.sin(2 * math.pi * i / (24 * 2.1) + ph[1]) + rnd.gauss(0, 0.5)
            spread = 2.0 + 3.2 * max(0.0, math.sin(2 * math.pi * (hr - 7) / 24.0)) + 1.6 * (1 - cloud[day]) + 0.8 * max(0.0, -season)
            td = t - spread
            rh = int(round(min(100.0, max(8.0, 100.0 * _es(td) / _es(t)))))
            pr = 101350 + 650 * math.sin(2 * math.pi * i / (24 * 4.7) + ph[2]) + 250 * math.sin(2 * math.pi * i / (24 * 1.9) + ph[3])
            if rnd.random() < 0.04:
                ws, wd = 0.0, 0.0   # calm, as EPW files record it: a speed of 0, a direction of 0
            else:
                r, acc = rnd.random(), 0.0
                for deg, share in dirs:
                    acc += share
                    if r <= acc:
                        break
                if 150 <= doy <= 240 and rnd.random() < 0.4:
                    deg = 202.5
                if rnd.random() < 0.6:
                    deg = wd_prev
                wd_prev = deg
                wd = round((deg + rnd.gauss(0, 9)) % 360.0)
                ws = round(max(0.3, rnd.gammavariate(2.3, 1.75) + (0.7 if not 150 <= doy <= 240 else -0.3)), 1)
            T.append(round(t, 1))
            TD.append(round(td, 1))
            RH.append(rh)
            P.append(int(round(pr)))
            WS.append(ws)
            WD.append(wd)
            CC.append(int(min(10, max(0, round(10 * cloud[day] + rnd.gauss(0, 0.8))))))
        self.T, self.TD, self.RH, self.P, self.WS, self.WD, self.CC = T, TD, RH, P, WS, WD, CC
        GH, DN, DF, EH, ED, IR = [], [], [], [], [], []
        for i in range(n + 1):
            dt = self.t0 + datetime.timedelta(hours=i)
            doy = dt.timetuple().tm_yday
            e0 = 1367.0 * (1 + 0.033 * math.cos(2 * math.pi * doy / 365.0))
            gh = dn = df = eh = ed = 0.0
            cl = CC[i] / 10.0
            for k in range(6):   # the hour before i, in six steps
                hs = (dt.hour - 1 + (k + 0.5) / 6.0) % 24.0 + (LON - 15 * TZ) / 15.0
                cz = _sun(LAT, doy, hs)
                if cz > 0.01:
                    am = 1.0 / cz
                    dnc = e0 * 0.7 ** (am ** 0.678)
                    ghc = dnc * cz + 0.12 * e0 * cz
                    g = ghc * (1 - 0.75 * cl ** 3.4)
                    b = dnc * (1 - cl) ** 1.4
                    dn += b / 6.0
                    gh += g / 6.0
                    df += max(0.0, g - b * cz) / 6.0
                    eh += e0 * cz / 6.0
                    ed += e0 / 6.0
            eps = (0.787 + 0.764 * math.log((TD[i] + 273.15) / 273.0)) * (1 + 0.0224 * CC[i] - 0.0035 * CC[i] ** 2 + 0.00028 * CC[i] ** 3)
            GH.append(int(round(gh)))
            DN.append(int(round(dn)))
            DF.append(int(round(df)))
            EH.append(int(round(eh)))
            ED.append(int(round(ed)))
            IR.append(int(round(eps * SIGMA * (T[i] + 273.15) ** 4)))
        self.GH, self.DN, self.DF, self.EH, self.ED, self.IR = GH, DN, DF, EH, ED, IR


def epw_text(year=2017, Y=None):
    """the EPW: hour h of a day is index i = day*24 + h of the year's hours (Year), h from 1 to 24"""
    Y = Y or Year(year)
    head = ['LOCATION,%s,%s,%s,SRC-Fixture,%s,%.5f,%.5f,%.1f,%.1f' % (CITY, STATE, COUNTRY, WMO, LAT, LON, TZ, ELEV),
            'DESIGN CONDITIONS,0',
            'TYPICAL/EXTREME PERIODS,0',
            'GROUND TEMPERATURES,0',
            'HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0',
            'COMMENTS 1,"A made-up year for the app\'s suite (tests/ladybug_fixture.py): not a real station"',
            'COMMENTS 2,"Deterministic; humid continental, 40 N 75 W, UTC-5"',
            'DATA PERIODS,1,1,Data,%s,1/ 1,12/31' % Y.t0.strftime('%A')]
    rows = []
    for i in range(1, Y.n + 1):
        dt = Y.t0 + datetime.timedelta(hours=i)
        ref = dt - datetime.timedelta(hours=1)   # the hour ends at dt: its day and its hour 1..24
        hour = dt.hour if dt.hour else 24
        rows.append('%d,%d,%d,%d,60,?9?9?9?9E0?9?9?9?9?9?9?9?9?9?9?9?9?9?9?9*9*9?9*9*9,%.1f,%.1f,%d,%d,%d,%d,%d,%d,%d,%d,999999,999999,999999,9999,%d,%.1f,%d,%d,777.7,77777,9,999999999,999,0.999,0,88,0.160,0.0,0.0' % (
            ref.year, ref.month, ref.day, hour, Y.T[i], Y.TD[i], Y.RH[i], Y.P[i], Y.EH[i], Y.ED[i], Y.IR[i], Y.GH[i], Y.DN[i], Y.DF[i],
            Y.WD[i], Y.WS[i], Y.CC[i], Y.CC[i]))
    return '\r\n'.join(head + rows) + '\r\n'


# the design days a station's DDY carries (made up here, in ASHRAE's naming): name's tail, month, day, type, the dry
# bulb, its daily range, the humidity's kind and value, pressure, wind speed and direction
DESIGN = [('Ann Htg 99.6% Condns DB', 1, 21, 'WinterDesignDay', -11.2, 0.0, 'Wetbulb', -11.2, 101207, 4.9, 320),
          ('Ann Htg 99% Condns DB', 1, 21, 'WinterDesignDay', -8.6, 0.0, 'Wetbulb', -8.6, 101207, 4.4, 320),
          ('Ann Clg .4% Condns DB=>MWB', 7, 21, 'SummerDesignDay', 33.0, 10.6, 'Wetbulb', 23.9, 101207, 4.6, 230),
          ('Ann Clg 1% Condns DB=>MWB', 7, 21, 'SummerDesignDay', 31.6, 10.6, 'Wetbulb', 23.4, 101207, 4.6, 230),
          ('Ann Clg 2% Condns DB=>MWB', 7, 21, 'SummerDesignDay', 30.4, 10.6, 'Wetbulb', 22.9, 101207, 4.6, 230)]


def ddy_text():
    out = [' ! A made-up DDY for the app\'s suite (tests/ladybug_fixture.py): not a real station', ' ',
           ' Site:Location,', '  %s_%s_%s Design_Conditions,     !- Location Name' % (CITY, STATE, COUNTRY),
           '      %.2f,     !- Latitude {N+ S-}' % LAT, '     %.2f,     !- Longitude {W- E+}' % LON,
           '      %.2f,     !- Time Zone Relative to GMT {GMT+/-}' % TZ, '      %.2f;     !- Elevation {m}' % ELEV, ' ']
    for nm, mo, dy, typ, db, rg, ht, hv, pr, ws, wd in DESIGN:
        out += [' SizingPeriod:DesignDay,', '  %s %s,     !- Name' % (CITY, nm), '         %2d,      !- Month' % mo,
                '         %2d,      !- Day of Month' % dy, '  %s,!- Day Type' % typ,
                '       %.1f,      !- Maximum Dry-Bulb Temperature {C}' % db, '       %.1f,      !- Daily Dry-Bulb Temperature Range {C}' % rg,
                ' DefaultMultipliers, !- Dry-Bulb Temperature Range Modifier Type', '           ,      !- Dry-Bulb Temperature Range Modifier Day Schedule Name',
                '    %s,      !- Humidity Condition Type' % ht, '       %.1f,      !- Wetbulb at Maximum Dry-Bulb {C}' % hv,
                '           ,      !- Humidity Indicating Day Schedule Name', '           ,      !- Humidity Ratio at Maximum Dry-Bulb {kgWater/kgDryAir}',
                '           ,      !- Enthalpy at Maximum Dry-Bulb {J/kg}', '           ,      !- Daily Wet-Bulb Temperature Range {deltaC}',
                '    %d.,      !- Barometric Pressure {Pa}' % pr, '        %.1f,      !- Wind Speed {m/s}' % ws,
                '        %d,      !- Wind Direction {Degrees; N=0, S=180}' % wd, '         No,      !- Rain {Yes/No}',
                '         No,      !- Snow on ground {Yes/No}', '         No,      !- Daylight Savings Time Indicator',
                '  ASHRAEClearSky, !- Solar Model Indicator', '           ,      !- Beam Solar Day Schedule Name',
                '           ,      !- Diffuse Solar Day Schedule Name',
                '           ,      !- ASHRAE Clear Sky Optical Depth for Beam Irradiance (taub)',
                '           ,      !- ASHRAE Clear Sky Optical Depth for Diffuse Irradiance (taud)',
                '       %s;      !- Clearness {0.0 to 1.1}' % ('0.00' if typ == 'WinterDesignDay' else '1.00'), ' ']
    return '\r\n'.join(out) + '\r\n'


def station_zip(year=2017, with_ddy=True):
    """the station's ZIP: the EPW, its DDY (the same stem), and a STAT the app does not read"""
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(STEM + '.epw', epw_text(year))
        if with_ddy:
            z.writestr(STEM + '.ddy', ddy_text())
        z.writestr(STEM + '.stat', 'A made-up STAT for the app\'s suite\r\n')
    return b.getvalue()


OM_VARS = ['temperature_2m', 'dew_point_2m', 'relative_humidity_2m', 'surface_pressure', 'wind_speed_10m', 'wind_direction_10m',
           'direct_normal_irradiance', 'diffuse_radiation', 'shortwave_radiation', 'cloud_cover']
GAPS = [100, 101, 102, 5000]   # hours Open-Meteo leaves empty here (null), for the app to fill


def openmeteo(year, gaps=True):
    """Open-Meteo's archive answer for the year's hours, start 1 January to the next 1 January 23:00, in Etc/GMT+5"""
    Y = Year(year)
    n = Y.n + 24   # the answer runs to the end of the end date's day
    Z = Y
    times, cols = [], {k: [] for k in OM_VARS}
    for i in range(n):
        dt = Y.t0 + datetime.timedelta(hours=i)
        times.append(dt.strftime('%Y-%m-%dT%H:%M'))
        j = min(i, Y.n)
        vals = {'temperature_2m': Z.T[j], 'dew_point_2m': Z.TD[j], 'relative_humidity_2m': Z.RH[j], 'surface_pressure': round(Z.P[j] / 100.0, 1),
                'wind_speed_10m': Z.WS[j], 'wind_direction_10m': Z.WD[j], 'direct_normal_irradiance': float(Z.DN[j]),
                'diffuse_radiation': float(Z.DF[j]), 'shortwave_radiation': float(Z.GH[j]), 'cloud_cover': Z.CC[j] * 10}
        for k in OM_VARS:
            cols[k].append(None if (gaps and i in GAPS and k in ('temperature_2m', 'relative_humidity_2m')) else vals[k])
    body = {'latitude': LAT, 'longitude': LON, 'generationtime_ms': 1.0, 'utc_offset_seconds': TZ * 3600, 'timezone': 'Etc/GMT+5',
            'timezone_abbreviation': 'GMT-5', 'elevation': ELEV, 'hourly_units': {'time': 'iso8601', 'temperature_2m': '°C'},
            'hourly': dict(cols, time=times)}
    return body


def route_handler(store):
    """a Playwright route handler for Open-Meteo's archive: the Ladybug year (its ten variables), recorded in store"""
    async def handle(route):
        u = route.request.url
        store.setdefault('hits', []).append(u)
        if store.get('mode') == 'abort':
            await route.abort('internetdisconnected')
            return
        if store.get('mode') == '429':
            await route.fulfill(status=429, body='busy', headers={'Access-Control-Allow-Origin': '*'})
            return
        y = int(u.split('start_date=')[1][:4])
        await route.fulfill(status=200, body=json.dumps(openmeteo(y)), headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
    return handle
