

  /* ================= __acad3dV216: Hub H4, share and sync through GitHub, the pure part =================
     docs/research/research-notion-hub-h4-sharing.md and docs/work-orders/v216/SPEC.md. One canonical file per element:
     canonical JSON, its FNV-1a hash, its path, the manifest, orphaned references after a merge. Each function is a work
     order, added below as it is built; none uses another file's names. */
function bimHubCanonical(x) {
  if (x === null || x === undefined) return 'null';
  if (typeof x === 'number') return isFinite(x) ? String(Number(x.toPrecision(12))) : 'null';
  if (typeof x === 'string' || typeof x === 'boolean') return JSON.stringify(x);
  var i, out = [];
  if (Object.prototype.toString.call(x) === '[object Array]') {
    for (i = 0; i < x.length; i++) out.push(bimHubCanonical(x[i]));
    return '[' + out.join(',') + ']';
  }
  var keys = [], k;
  for (k in x) if (Object.prototype.hasOwnProperty.call(x, k) && x[k] !== undefined) keys.push(k);
  keys.sort();
  for (i = 0; i < keys.length; i++) out.push(JSON.stringify(keys[i]) + ':' + bimHubCanonical(x[keys[i]]));
  return '{' + out.join(',') + '}';
}
function bimHubHash(s) {
  var h = 0x811c9dc5, i;
  s = String(s);
  for (i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h + (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24)) >>> 0;
  }
  return ('0000000' + h.toString(16)).slice(-8);
}
function bimHubPath(el) {
  el = el || {};
  var type = (el.bim && el.bim.type) || el.t || 'object';
  return 'elements/' + String(type).replace(/[^A-Za-z0-9_-]/g, '_') + '/' +
    String(el.id).replace(/[^A-Za-z0-9_.-]/g, '_') + '.json';
}
function bimHubManifest(els, schema) {
  var byId = {}, ids = [], i, out = {};
  els = els || [];
  for (i = 0; i < els.length; i++) if (els[i] && els[i].id != null) { byId[els[i].id] = els[i]; ids.push(String(els[i].id)); }
  ids.sort();
  for (i = 0; i < ids.length; i++) out[ids[i]] = bimHubHash(bimHubCanonical(byId[ids[i]]));
  return { schema: schema == null ? 1 : schema, elements: out };
}
function bimHubOrphans(els) {
  var FIELDS = ['hostWallId', 'levelId', 'sourceId', 'buildingId'];
  var have = {}, out = [], i, j, el, v;
  els = els || [];
  for (i = 0; i < els.length; i++) if (els[i] && els[i].id != null) have[els[i].id] = true;
  for (i = 0; i < els.length; i++) {
    el = els[i];
    if (!el) continue;
    for (j = 0; j < FIELDS.length; j++) {
      v = el.bim && el.bim[FIELDS[j]] != null ? el.bim[FIELDS[j]] : el[FIELDS[j]];
      if (typeof v === 'string' && v !== '' && !have[v]) out.push({ id: el.id, field: FIELDS[j], missing: v });
    }
  }
  return out;
}
