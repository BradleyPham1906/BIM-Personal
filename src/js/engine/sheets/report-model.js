

  /* ================= __acad3dV178: the report, the pure part =================
     docs/research/research-notion-v178-presentation.md (the owner's decisions 1 to 6 as recommended, 2026-11-14) and
     docs/work-orders/v178/SPEC.md. A report datum carries its value, unit, state and provenance; zero is a value,
     missing is a state. The plan of the eight Site Analysis boards and six DA sheets; the frozen manifest an export
     is bound to; legends that say what they leave out; components whose instances keep their overrides. Each function
     is a work order in docs/work-orders/v178/TASKS.md, added below as it is built; none uses another file's names. */
var BIM_RPT_STATES = ['available','partial','stale','unavailable','failed'];
function bimRptFromLive(st) {
  if (st === 'ok') return 'available';
  if (st === 'stale') return 'stale';
  if (st === 'gone') return 'failed';
  return 'unavailable';
}
function bimRptDatum(raw) {
  var d = raw;
  var r = { value: null, unit: '', state: 'unavailable', source: '', vintage: '', retrieved: '', method: '', license: '' };
  if (!d) return r;
  if (d.value !== null && typeof d.value !== 'undefined') {
    if (typeof d.value === 'number' && isFinite(d.value)) {
      r.value = d.value;
    } else if (typeof d.value === 'string' && d.value !== '') {
      r.value = d.value;
    }
  }
  if (typeof d.state === 'string' && BIM_RPT_STATES.indexOf(d.state) !== -1) {
    r.state = d.state;
  }
  if (typeof d.source === 'string') r.source = d.source;
  if (typeof d.unit === 'string') r.unit = d.unit;
  if (typeof d.vintage === 'string') r.vintage = d.vintage;
  if (typeof d.retrieved === 'string') r.retrieved = d.retrieved;
  if (typeof d.method === 'string') r.method = d.method;
  if (typeof d.license === 'string') r.license = d.license;
  if (typeof r.value === 'number' && !isFinite(r.value)) {
    r.value = null;
  }
  if (r.value === null && (r.state === 'available' || r.state === 'partial' || r.state === 'stale')) {
    r.state = 'unavailable';
  }
  if (r.state === 'unavailable' || r.state === 'failed') {
    r.value = null;
  }
  return r;
}
function bimRptIssue(data) {
  if (!data) return { status: 'complete', counts: { available: 0, partial: 0, stale: 0, unavailable: 0, failed: 0 }, marked: [] };
  var counts = { available: 0, partial: 0, stale: 0, unavailable: 0, failed: 0 };
  var marked = [];
  for (var key in data) {
    if (data.hasOwnProperty(key)) {
      var datum = bimRptDatum(data[key]);
      counts[datum.state]++;
      if (datum.state !== 'available') {
        marked.push(key);
      }
    }
  }
  marked.sort();
  var status = marked.length > 0 ? 'marked' : 'complete';
  return { status: status, counts: counts, marked: marked };
}
function bimRptManifest(report, revision, when) {
  var r = report;
  var id = r ? (typeof r.id === 'string' ? r.id : '') : '';
  var rev = revision !== undefined ? revision : 0;
  var gen = when !== undefined ? when : '';
  var boards = r && r.boards ? r.boards.filter(function(b) { return typeof b === 'string'; }) : [];
  var data = {};
  if (r && r.data) {
    var keys = Object.keys(r.data).sort();
    for (var i = 0; i < keys.length; i++) {
      data[keys[i]] = bimRptDatum(r.data[keys[i]]);
    }
  }
  return { id: id, revision: rev, generated: gen, boards: boards, data: data };
}
function bimRptStale(manifest, revision) {
  if (!manifest) return true;
  return manifest.revision !== revision;
}
function bimRptLegend(rows, max) {
  if (!rows) return { rows: [], more: 0 };
  var m = (typeof max === 'number' && max >= 1) ? Math.floor(max) : 12;
  var taken = rows.slice(0, m);
  var more = rows.length - m;
  if (more < 0) more = 0;
  return { rows: taken, more: more };
}
function bimCompResolve(def, inst) {
  if (!def) return {};
  var result = {};
  for (var k in def.props) {
    if (def.props.hasOwnProperty(k)) {
      result[k] = def.props[k];
    }
  }
  if (inst && inst.overrides) {
    for (var k in inst.overrides) {
      if (inst.overrides.hasOwnProperty(k) && result.hasOwnProperty(k)) {
        result[k] = inst.overrides[k];
      }
    }
  }
  return result;
}
function bimCompSync(inst, def) {
  if (!inst || !def) return { id: inst ? inst.id : undefined, defId: def.id, version: def.version, overrides: {} };
  var newOverlaps = {};
  if (inst.overrides) {
    for (var k in inst.overrides) {
      if (inst.overrides.hasOwnProperty(k) && def.props.hasOwnProperty(k)) {
        newOverlaps[k] = inst.overrides[k];
      }
    }
  }
  return { id: inst.id, defId: def.id, version: def.version, overrides: newOverlaps };
}
function bimCompDetach(def, inst) {
  if (!def || !inst) return { id: inst.id, props: {} };
  return { id: inst.id, props: bimCompResolve(def, inst) };
}
function bimRptText(d, digits) {
  if (!d || d.state === 'unavailable') return 'Not available';
  if (d.state === 'failed') return 'Failed';
  var s = '';
  if (typeof d.value === 'number' && isFinite(d.value)) {
    var dg = (typeof digits === 'number' && digits >= 0 && digits < 7) ? Math.floor(digits) : 0;
    s = d.value.toFixed(dg);
  } else if (typeof d.value === 'string') {
    s = d.value;
  }
  if (d.unit && typeof d.unit === 'string' && d.unit !== '') s = s + ' ' + d.unit;
  if (d.state === 'partial') s = s + ' (partial)';
  if (d.state === 'stale') s = s + ' (out of date)';
  return s;
}
function bimRptRings(radiiKm) {
  if (!radiiKm || typeof radiiKm !== 'object' || typeof radiiKm.length !== 'number') return [];
  var positives = [];
  var seen = {};
  for (var i = 0; i < radiiKm.length; i++) {
    var r = radiiKm[i];
    if (typeof r === 'number' && isFinite(r) && r > 0 && !seen[r]) {
      positives.push(r);
      seen[r] = true;
    }
  }
  positives.sort(function(a, b) { return a - b; });
  var result = [];
  for (var i = 0; i < positives.length; i++) {
    result.push({ km: positives[i], label: 'Within ' + positives[i] + ' km', cumulative: true });
  }
  return result;
}
var BIM_RPT_SA = [{ id: 'SA-01', title: 'Location and context' }, { id: 'SA-02', title: 'Zoning summary' }, { id: 'SA-03', title: 'Landform and water' }, { id: 'SA-04', title: 'Climate' }, { id: 'SA-05', title: 'Access' }, { id: 'SA-06', title: 'Risks' }, { id: 'SA-07', title: 'Constraints and opportunities' }, { id: 'SA-08', title: 'Buildable area and yield' }];
var BIM_RPT_DA = [{ id: 'DA-01', title: 'Context plan, sun and wind' }, { id: 'DA-02', title: 'Site coverage, GFA and FSR' }, { id: 'DA-03', title: 'Model and shadow studies' }, { id: 'DA-04', title: 'Buildings and schedule' }, { id: 'DA-05', title: 'Sections and elevations' }, { id: 'DA-06', title: 'Perspectives' }];
function bimRptPlan(families) {
  if (!families) return [];
  var result = [];
  var n = 1;
  if (families.sa) {
    for (var i = 0; i < BIM_RPT_SA.length; i++) {
      result.push({ id: BIM_RPT_SA[i].id, family: 'sa', title: BIM_RPT_SA[i].title, n: n++ });
    }
  }
  if (families.da) {
    for (var i = 0; i < BIM_RPT_DA.length; i++) {
      result.push({ id: BIM_RPT_DA[i].id, family: 'da', title: BIM_RPT_DA[i].title, n: n++ });
    }
  }
  return result;
}
