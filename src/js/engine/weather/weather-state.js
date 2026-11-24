

  /* ================= __acad3dV304: Live weather, the pure part =================
     docs/research/research-world-look.md (part 4.2) and docs/research/research-world-look/weather-sky.md (4.3, 4.6, 7);
     docs/work-orders/v304/SPEC.md. WMO 4677 codes, precipitation intensity, fog from visibility (WMO-No. 8), clouds,
     the WeatherState, frame-rate independent blending, wetness, the Open-Meteo request, sampling the cached answer at a
     moment, when to fetch, and the fallback order. Each function is a work order, added below as it is built; none uses
     another file's names. */

