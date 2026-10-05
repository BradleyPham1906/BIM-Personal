# Research: how professionals present climate and risk in a site analysis

The owner (V159): "please make sure u did some research online on how they present the analysis
(architectural, arcgis, data analysis,..) dont just give me mediore format. i want it to be really
really really professional."

This note records what the research found, in our own words, and the design it sets for V159's
Climate and risk board. No one's text, images or code is copied. We rebuild the ideas.

## 1. What the tools architects use show

**CBE Clima Tool** (UC Berkeley's Center for the Built Environment; free, open source, used by
architects and engineers worldwide). Its tabs set the professional baseline:
- **Climate summary:** the place (latitude, longitude, elevation), the Köppen–Geiger zone, the
  average, hottest and coldest temperatures, the year's horizontal solar radiation, and heating
  and cooling degree days.
- **Temperature and humidity:** the yearly course of the daily values, and hourly heat maps (the
  day of the year across, the hour of the day down).
- **Sun and clouds:** a sun path.
- **Wind:** wind roses, the year's and each season's.
- **Psychrometric chart:** dry-bulb temperature across, humidity ratio up, relative-humidity
  curves inside, and the hours of the year plotted on it.
- **Natural ventilation and outdoor comfort.**
- Every chart can be hovered, and downloaded as SVG; the data can be downloaded as CSV.
([CBE Clima Tool](https://clima.cbe.berkeley.edu/),
[paper, Building Simulation 2023](https://link.springer.com/content/pdf/10.1007/s12273-023-1090-5.pdf),
[source](https://github.com/CenterForTheBuiltEnvironment/clima),
[Climate summary tab](https://cbe-berkeley.gitbook.io/clima/documentation/tabs-explained/tab-summary),
[psychrometric chart](https://cbe-berkeley.gitbook.io/clima/documentation/tabs-explained/psychrometric-chart))

**Ladybug Tools** (Rhino/Grasshopper; free, open source). It reads EPW weather files and draws the
same family: sun path, wind rose, psychrometric chart, hourly plot and monthly chart, for decisions
in the early stages of design.
([Ladybug Tools](https://www.food4rhino.com/en/app/ladybug-tools),
[weather data](https://docs.ladybug.tools/climate-analysis/weather-data))

**Climate Consultant** (UCLA Energy Design Tools Group). It plots the hours on the psychrometric
chart over the Givoni–Milne bioclimatic chart: a comfort zone and the zones where each passive
strategy (shading, thermal mass, natural ventilation, passive solar) brings comfort.
([Givoni bioclimatic chart](https://aesg.com/perspective/elevating-sustainability-a-conceptual-strategy-for-facade-design-with-givonis-bioclimatic-graph/),
[psychrometric chart tutorial, SBSE](https://energy-design-tools.sbse.org/papers/ASES09-Yasmin.pdf))

**Weather Spark.** Its temperature chart is the model for a clear climate graph:
- the daily average high and low as two lines;
- percentile bands around them (25th to 75th, and 10th to 90th), so the spread of real days shows;
- the hourly temperature as a heat map with named bands (freezing, cold, cool, comfortable, warm,
  hot).
([Weather Spark, Denver](https://weatherspark.com/y/3709/Average-Weather-in-Denver-Colorado-United-States-Year-Round))

**The Walter–Lieth climate diagram** (ecology's standard since 1960). It puts temperature and
rainfall on one plot, with 10 °C matched to 20 mm, and marks the dry and wet seasons.
([ZooLex](https://zoolex.org/page/walter/),
[Benjamin Bell](https://www.benjaminbell.co.uk/2018/04/walter-and-lieth-climate-diagrams-in-r.html))
We do **not** copy its two scales on one plot. Data-visualisation practice holds that two y-scales
invent a relationship that is not in the data. So temperature and rainfall are two aligned charts
that share the months.

## 2. How each chart is drawn well

- **Wind rose:**
  - 16 sectors of 22.5°, north at the top;
  - petal length read against frequency rings (5%, 10%, ...), not against the chart's size;
  - each petal split into 3 to 5 speed bands, with the legend giving the bands in m/s;
  - calm hours stated separately.
  ([Climate4Buildings](https://climate4buildings.com/guides/how-to-read-a-wind-rose),
  [Vind AI](https://www.vind.ai/blog-post/wind-rose-guide),
  [Olsson, wind climatologies](http://www.pwswx.pwssc.org/rose_final.pdf))
- **Sun path:**
  - a polar chart, the centre overhead and the rim the horizon;
  - altitude rings every 10°, azimuth ticks every 15°;
  - the paths of 21 June, the equinox and 21 December;
  - the hour lines crossing them.
  ([ESRU, Strathclyde](https://www.esru.strath.ac.uk/courseware/Design_tools/Sun_chart/sun-chart.htm),
  [Andrew Marsh, 2D sun path](https://andrewmarsh.com/apps/releases/sunpath2d.html),
  [Autodesk](https://www.autodesk.com/support/technical/article/caas/tsarticles/ts/2pGZ0xLAMCrBMy9xLtObJM.html))
- **Degree days:**
  - heating and cooling degree days from the daily mean, (max + min) / 2, against a base of
    18 °C (65 °F; the US uses 18.3 °C, parts of Europe 15.5 °C);
  - a rough measure of the energy a building needs to heat or cool.
  ([Degree day](https://en.wikipedia.org/wiki/Degree_day), [degreedays.net](https://www.degreedays.net/))
- **Köppen–Geiger zone:** classed from the twelve monthly mean temperatures and rainfall totals by
  fixed thresholds, as in Beck et al. 2018:
  - 0 °C separates temperate (C) from cold (D);
  - the dry (B) threshold is 2 × the mean annual temperature, plus 28 when 70% of the rain falls
    in summer, or plus 14 when neither half takes 70%.
  ([Beck et al. 2018, Scientific Data](https://pmc.ncbi.nlm.nih.gov/articles/PMC6207062/),
  [Köppen climate classification](https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification))
- **Air quality:** PM2.5 against the WHO 2021 guideline of 15 µg/m³ over 24 hours and 5 µg/m³ a
  year, with interim targets of 75, 50, 37.5 and 25 µg/m³ over 24 hours.
  ([WHO global air quality guidelines](https://www.ncbi.nlm.nih.gov/books/NBK574594/))
- **Seismic history:** USGS's own convention runs from green (low) through yellow and orange to red
  (very high). Probabilistic hazard needs the national hazard model. What a browser can fetch for
  free, anywhere, is the past: the earthquakes of magnitude 4.5 and more within 100 km since 1976.
  ([USGS colours](https://earthquake.usgs.gov/education/shakingsimulations/colors.php),
  [USGS event service](https://earthquake.usgs.gov/fdsnws/event/1/))

## 3. How a professional board and a dashboard are laid out

- **ArcGIS Dashboards:**
  - lay elements out in the order people read (top to bottom, left to right), sized by
    importance, related elements grouped;
  - include only what the reader needs;
  - give indicators reference values, so a number says whether it is good;
  - use conditional colour only for state;
  - on a phone, indicators first and little text.
  ([Effective dashboards](https://doc.arcgis.com/en/dashboards/latest/reference/author-effective-dashboards.htm),
  [mobile views](https://doc.arcgis.com/en/dashboards/latest/reference/dashboards-on-your-smartphone.htm),
  [Esri: clear and effective dashboard design](https://www.esri.com/arcgis-blog/products/ops-dashboard/real-time/advice-for-clear-and-effective-dashboard-design))
- **Architectural site analysis boards:**
  - one diagram per condition, or layered diagrams that stay legible;
  - a clear hierarchy, with the data bolder than its reference;
  - every finding tied to the design response it calls for: harsh west sun, so shading; noise,
    so the layout turns away.
  ([First In Architecture](https://www.firstinarchitecture.co.uk/architecture-site-analysis-guide-2/),
  [archisoup](https://www.archisoup.com/architecture-site-analysis-presentation),
  [Novatr: climate site analysis](https://www.novatr.com/blog/climate-site-analysis-in-architecture-guide-for-architects))
- **Data journalism (the Financial Times, after Tufte):**
  - ink for data, not decoration;
  - but readers rank bare minimal charts lowest. Well-placed annotations, and a title that states
    the finding ("Summers are hot and humid"), make a chart read and remembered.
  ([GIJN: John Burn-Murdoch](https://gijn.org/stories/data-visualization-storytelling-tips-john-burn-murdoch/),
  [Chartjunk](https://en.wikipedia.org/wiki/Chartjunk))

## 4. The design this sets for V159: the Climate and risk board

A board in the Site tab, opened full screen, printed on A3 landscape. Its parts, in reading order:

1. **Header:** the site, its coordinates, the Köppen zone in words, the period of the data, and
   every source with its date.
2. **Indicator strip:** a number and a line saying what it means, with a reference and a state
   (icon and word, never colour alone) where one exists. The indicators:
   - climate zone;
   - annual mean temperature;
   - annual rainfall;
   - prevailing wind;
   - heating and cooling degree days;
   - solar energy a year;
   - comfort hours;
   - PM2.5 against WHO;
   - earthquakes nearby.
3. **Figures,** each a card with a numbered caption, a title that states the finding, the chart,
   its source line, and a table view:
   1. temperature: the monthly mean of the daily high and low, the 10th to 90th percentile band of
      real days, the mean;
   2. rainfall by month, with the wet days, sharing the months with figure 1;
   3. the hourly temperature of the most recent full year as a heat map, in named bands;
   4. the wind rose of the year, with winter and summer beside it;
   5. the sun path;
   6. degree days by month, heating and cooling mirrored on one axis;
   7. solar energy by month;
   8. the psychrometric chart: the year's hours as density, the comfort zone, the share of hours in
      it;
   9. PM2.5 for the last 92 days against the WHO guideline;
   10. earthquakes within 100 km by distance and direction, sized by magnitude, the largest listed.
4. **Notes on method:**
   - the reanalysis (ERA5, about 25 km cells, so a city's heat island is not in it);
   - the degree-day base;
   - the Köppen rules;
   - the comfort zone's definition;
   - the WHO guideline.

Every number becomes a finding in the Site analysis (V158) under Climate or Environmental risk,
with its source and date.

**Charts follow one set of rules:**
- one y-axis each;
- hairline grids;
- 2 px lines, bars no wider than 24 px with rounded ends;
- one hue for magnitude, two hues and a grey midpoint for temperature around comfort;
- categorical colours in a fixed order, validated for colour-blind readers;
- a legend for two or more series;
- text in ink, never in the data's colour;
- hover on every mark, and a table for every chart.

The board follows the app's light or dark theme and prints on white.

**Free sources, no keys, open to browsers:**
- [Open-Meteo historical weather](https://open-meteo.com/en/docs/historical-weather-api) (ERA5,
  1940 to now): ten years of daily values and a year of hourly ones;
- [Open-Meteo air quality](https://open-meteo.com/en/docs/air-quality-api) (CAMS): PM2.5 for the
  last 92 days;
- [USGS earthquake catalogue](https://earthquake.usgs.gov/fdsnws/event/1/).
