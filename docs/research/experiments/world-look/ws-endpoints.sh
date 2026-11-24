#!/usr/bin/env bash
# ws-endpoints.sh: live weather sources, tested from here (2026-11-24).
# For each source: a GET with an Origin header (the browser's CORS answer), an OPTIONS preflight
# (as a browser sends for a request with a non-simple header such as User-Agent), the status,
# the CORS headers, cache headers, rate-limit headers and the time to first byte.
# Data, never a suite. Output: ws-endpoints-results.txt beside this script.
# Location: London (51.5074, -0.1278) and, for the US-only service, Washington DC (38.8894, -77.0352).
set -u
OUT="$(dirname "$0")/ws-endpoints-results.txt"
ORIGIN="https://example.github.io"
UA="BIM-Personal research (generic client)"
: > "$OUT"
probe() {
  local name="$1" url="$2" extra="${3:-}"
  {
    echo "=== $name"
    echo "URL: $url"
    echo "--- GET with Origin"
    curl -s -o /tmp/ws_body.$$ -D /tmp/ws_head.$$ -w 'status=%{http_code} ttfb=%{time_starttransfer}s total=%{time_total}s bytes=%{size_download}\n' \
      -H "Origin: $ORIGIN" -A "$UA" $extra "$url"
    grep -i -E '^(access-control|cache-control|expires|last-modified|x-ratelimit|retry-after|content-type|age|etag)' /tmp/ws_head.$$ | tr -d '\r'
    echo "--- body (first 600 bytes)"
    head -c 600 /tmp/ws_body.$$; echo
    echo "--- OPTIONS preflight (Access-Control-Request-Headers: user-agent)"
    curl -s -o /dev/null -D /tmp/ws_pre.$$ -w 'status=%{http_code}\n' -X OPTIONS \
      -H "Origin: $ORIGIN" -H 'Access-Control-Request-Method: GET' -H 'Access-Control-Request-Headers: user-agent' "$url"
    grep -i '^access-control' /tmp/ws_pre.$$ | tr -d '\r'
    echo
  } >> "$OUT" 2>&1
  rm -f /tmp/ws_body.$$ /tmp/ws_head.$$ /tmp/ws_pre.$$
}
date -u +"run at %Y-%m-%dT%H:%M:%SZ" >> "$OUT"
# 1. Open-Meteo forecast: current, 15-minutely and hourly weather variables
probe "open-meteo forecast" "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current=temperature_2m,relative_humidity_2m,is_day,precipitation,rain,showers,snowfall,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,wind_gusts_10m,visibility&minutely_15=precipitation,rain,snowfall,weather_code,visibility,wind_speed_10m&hourly=cloud_cover_low,cloud_cover_mid,cloud_cover_high,visibility,weather_code&forecast_days=1&timezone=auto"
# 1b. Open-Meteo customer-free mirror check: the same with a model chosen (UKMO, 2 km)
probe "open-meteo forecast ukmo" "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current=cloud_cover,weather_code&models=ukmo_seamless&forecast_days=1"
# 1c. Open-Meteo model metadata (update times)
probe "open-meteo meta dwd_icon" "https://api.open-meteo.com/data/dwd_icon/static/meta.json"
probe "open-meteo meta ecmwf_ifs025" "https://api.open-meteo.com/data/ecmwf_ifs025/static/meta.json"
# 2. US National Weather Service: points, then the latest observation of a station
probe "nws points" "https://api.weather.gov/points/38.8894,-77.0352"
probe "nws latest observation KDCA" "https://api.weather.gov/stations/KDCA/observations/latest"
# 3. AviationWeather.gov METAR (Data API)
probe "aviationweather metar EGLL" "https://aviationweather.gov/api/data/metar?ids=EGLL&format=json"
# 4. MET Norway locationforecast compact (needs an identifying User-Agent)
probe "met.no locationforecast" "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.5074&lon=-0.1278"
probe "met.no nowcast (Nordic only)" "https://api.met.no/weatherapi/nowcast/2.0/complete?lat=59.91&lon=10.75"
# 5. RainViewer radar index (tiles listed inside)
probe "rainviewer maps index" "https://api.rainviewer.com/public/weather-maps.json"
# 6. Bright Sky (DWD open data, Germany)
probe "brightsky current" "https://api.brightsky.dev/current_weather?lat=52.52&lon=13.40"
