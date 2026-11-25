/* ================= __acad3dV223: 4D/5D construction planning, CP4 and CP5: procurement and drawing intake, the pure part ================
   docs/research/research-4d-5d-cp4-cp5.md and docs/work-orders/v223/SPEC.md. Calendar dates, the working day n days
   before a need, precision and recall of a check. Each function is a work order, added below as it is built; none uses another file's names.
*/
function bimCpDate(s) {
  // YYYY-MM-DD as Date.UTC(year, month - 1, day); null for anything else
  var m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return null;
  var year = parseInt(m[1], 10);
  var month = parseInt(m[2], 10) - 1;
  var day = parseInt(m[3], 10);
  if (month < 0 || month > 11 || day < 1 || day > 31) return null;
  return Date.UTC(year, month, day);
}
function bimCpIso(t) {
  // 'YYYY-MM-DD' from Date.UTC(t); null for anything else
  if (typeof t !== 'number') return null;
  var d = new Date(t);
  return d.getUTCFullYear() + '-' + ('0' + (d.getUTCMonth() + 1)).slice(-2) + '-' + ('0' + d.getUTCDate()).slice(-2);
}
function bimCpWorkdayBefore(need, n, holidays) {
  // null for a bad date or n under 0
  if (typeof need !== 'string' || n < 0 || !need.match(/^(\d{4})-(\d{2})-(\d{2})$/)) return null;
  if (n === 0) return need;
  var h = {};
  for (var i = 0; i < holidays.length; i++) h[holidays[i]] = true;
  var d = bimCpDate(need);
  if (d === null) return null;
  var r = n;
  while (r > 0) {
    d -= 86400000;
    var D = new Date(d);
    var w = D.getUTCDay();
    if (w === 0 || w === 6) continue;
    var I = D.getUTCFullYear() + '-' + ('0' + (D.getUTCMonth() + 1)).slice(-2) + '-' + ('0' + D.getUTCDate()).slice(-2);
    if (h[I]) continue;
    r--;
  }
  return D.getUTCFullYear() + '-' + ('0' + (D.getUTCMonth() + 1)).slice(-2) + '-' + ('0' + D.getUTCDate()).slice(-2);
}
function bimCpScores(tp, fp, fn) {
  // {precision: tp / (tp + fp), recall: tp / (tp + fn)}, each null when its denominator is 0
  return { precision: tp + fp > 0 ? tp / (tp + fp) : null, recall: tp + fn > 0 ? tp / (tp + fn) : null };
}


  /* ================= __acad3dV223: 4D/5D construction planning, CP4 and CP5: procurement and drawing intake, the pure part =================
     docs/research/research-4d-5d-cp4-cp5.md and docs/work-orders/v223/SPEC.md. Calendar dates, the working day n days
     before a need, precision and recall of a check. Each function is a work order, added below as it is built; none uses
     another file's names. */
