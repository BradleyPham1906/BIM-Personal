

  /* ================= __acad3dV216: Hub H4, share and sync through GitHub, the pure part =================
     docs/research/research-notion-hub-h4-sharing.md and docs/work-orders/v216/SPEC.md. One canonical file per element:
     canonical JSON, its FNV-1a hash, its path, the manifest, orphaned references after a merge. Each function is a work
     order, added below as it is built; none uses another file's names. */
function bimHubCanonical(x) {
  if (x === null || x === undefined) {
    return null;
  }
  if (typeof x === 'number') {
    if (!isFinite(x)) {
      return null;
    }
    return String(Number(x.toPrecision(12)));
  }
  if (typeof x === 'string' || typeof x === 'boolean') {
    return JSON.stringify(x);
  }
  if (Array.isArray(x)) {
    var out = '[';
    var i;
    for (i = 0; i < x.length; i += 1) {
      if (i > 0) {
        out += ',';
      }
      out += bimHubCanonical(x[i]);
    }
    return out + ']';
  }
  if (typeof x === 'object') {
    var keys = [];
    var k;
    for (k in x) {
      if (Object.prototype.hasOwnProperty.call(x, k) && x[k] !== undefined) {
        keys.push(k);
      }
    }
    keys.sort();
    var out2 = '{';
    for (i = 0; i < keys.length; i += 1) {
      if (i > 0) {
        out2 += ',';
      }
      out2 += JSON.stringify(keys[i]) + ':' + bimHubCanonical(x[keys[i]]);
    }
    return out2 + '}';
  }
  return null;
}

function bimHubHash(s) {
  var h = 0x811c9dc5;
  var i;
  for (i = 0; i < s.length; i += 1) {
    h ^= s.charCodeAt(i);
    h = (h + (h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24)) | 0;
  }
  var hex = (h >>> 0).toString(16);
  while (hex.length < 8) {
    hex = '0' + hex;
  }
  return hex;
}

function bimHubPath(el) {
  var bim = el.bim;
  var kind = 'object';
  if (bim && bim.type) {
    kind = bim.type;
  } else if (el.t) {
    kind = el.t;
  }
  var ksafe = '';
  var i;
  for (i = 0; i < kind.length; i += 1) {
    var c = kind.charAt(i);
    if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c === '_' || c === '-') {
      ksafe += c;
    } else {
      ksafe += '_';
    }
  }
  var id = el.id || '';
  var idsafe = '';
  for (i = 0; i < id.length; i += 1) {
    var c2 = id.charAt(i);
    if ((c2 >= 'A' && c2 <= 'Z') || (c2 >= 'a' && c2 <= 'z') || (c2 >= '0' && c2 <= '9') || c2 === '_' || c2 === '.' || c2 === '-') {
      idsafe += c2;
    } else {
      idsafe += '_';
    }
  }
  return 'elements/' + ksafe + '/' + idsafe + '.json';
}

function bimHubManifest(els, schema) {
  var sc = 1;
  if (schema !== undefined && schema !== null) {
    sc = schema;
  }
  var ids = [];
  var i;
  for (i = 0; i < els.length; i += 1) {
    ids.push(els[i].id);
  }
  ids.sort();
  var elements = {};
  for (i = 0; i < ids.length; i += 1) {
    var id = ids[i];
    var el;
    var j;
    for (j = 0; j < els.length; j += 1) {
      if (els[j].id === id) {
        el = els[j];
        break;
      }
    }
    elements[id] = bimHubHash(bimHubCanonical(el));
  }
  return { schema: sc, elements: elements };
}

function bimHubOrphans(els) {
  var byId = {};
  var i;
  for (i = 0; i < els.length; i += 1) {
    byId[els[i].id] = els[i];
  }
  var fields = ['hostWallId', 'levelId', 'sourceId', 'buildingId'];
  var orphans = [];
  for (i = 0; i < els.length; i += 1) {
    var el = els[i];
    var bim = el.bim;
    var j;
    for (j = 0; j < fields.length; j += 1) {
      var field = fields[j];
      var val = (bim && bim[field] !== undefined) ? bim[field] : el[field];
      if (typeof val === 'string' && val !== '' && !(val in byId)) {
        orphans.push({ id: el.id, field: field, missing: val });
      }
    }
  }
  return orphans;
}
