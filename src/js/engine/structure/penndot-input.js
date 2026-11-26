/* ================= __acad3dV226: Track C, the PennDOT LRFD input writer, the pure part ================
   docs/research/penndot/PENNDOT_INPUT_SPEC.md and docs/work-orders/v226/SPEC.md. PennDOT's LRFD programs' commands:
   meaning by program, the shared core, STLRFD's order. Each function is a work order, added below as it is built; none
   uses another file's names. */

/* BIM_PD_PS: PSLRFD codes lookup */
var BIM_PD_PS = {'PS': {'CDF': 'Composite Function', 'CFG': 'Camber', 'CLD': 'Clearance', 'CTL': 'Control', 'DLD': 'Dead Load', 'DPL': 'Drape Point Location', 'GEO': 'Geometry', 'BDM': 'Beam Dimensions', 'LDF': 'Load Duration', 'OAN': 'Opening Anchor', 'OIN': 'Opening Interior', 'ORF': 'Outrigger Frame', 'OSC': 'Oriented Strand', 'PLD': 'Prestressing Length', 'SAL': 'Slab Thickness', 'SID': 'Session ID', 'SKW': 'Skew', 'SLB': 'Slab Length', 'SLL': 'Slab Length', 'SPL': 'Span Length', 'SST': 'Step', 'TTL': 'Total Length', 'UDF': 'User Defined Function', 'URF': 'User Reference Function'}};

/* BIM_PD_ST: STLRFD codes in section order */
var BIM_PD_ST = {'CDF': 'Composite Function', 'CFG': 'Camber', 'CLD': 'Clearance', 'CTL': 'Control', 'DLD': 'Dead Load', 'GEO': 'Geometry', 'LDF': 'Load Duration', 'MAT': 'Material', 'OAN': 'Opening Anchor', 'OIN': 'Opening Interior', 'ORF': 'Outrigger Frame', 'OSC': 'Oriented Strand', 'PLD': 'Prestressing Length', 'SAL': 'Slab Thickness', 'SID': 'Session ID', 'SKW': 'Skew', 'SLB': 'Slab Length', 'SLL': 'Slab Length', 'SPL': 'Span Length', 'SST': 'Step', 'TTL': 'Total Length', 'UDF': 'User Defined Function', 'URF': 'User Reference Function', 'CF2': 'Composite 2', 'CF3': 'Composite 3', 'DPL': 'Design Plate Location', 'EFD': 'Erector Function Draft', 'EMG': 'Erection Method', 'ENR': 'End Nelson', 'ENR2': 'End Nelson 2', 'ENS': 'End Nelson Spacer', 'ENT': 'End Nelson Template', 'EPO': 'End Post Tension', 'EQ1': 'Equivalent Quarter Point 1', 'EQ2': 'Equivalent Quarter Point 2', 'EQ3': 'Equivalent Quarter Point 3', 'EQ4': 'Equivalent Quarter Point 4'};

/* ================= __acad3dV226: end of code definitions =============== */

// WO-01 bimPdName(program, code): with BIM_PD_PS and BIM_PD_ST just above it:
//   for 'PS' the name or null; for 'ST' 'Design Plate Location' for DPL,
//   else the code when it is an STLRFD command, else null; any other program null
function bimPdName(program, code) {
  if (program === 'PS') {
    var psCodes = BIM_PD_PS['PS'];
    if (psCodes && psCodes[code]) {
      return psCodes[code];
    }
    return null;
  }
  if (program === 'ST') {
    if (code === 'DPL') {
      return 'Design Plate Location';
    }
    var stCodes = BIM_PD_ST;
    if (stCodes && stCodes[code]) {
      return stCodes[code];
    }
    return null;
  }
  return null;
}

// WO-02 bimPdShared(): the STLRFD codes that PSLRFD also has, sorted (23)
function bimPdShared() {
  var shared = [];
  var psCodes = BIM_PD_PS['PS'];
  var stCodes = BIM_PD_ST;
  for (var code in stCodes) {
    if (psCodes && psCodes[code]) {
      shared.push(code);
    }
  }
  return shared.sort();
}

// WO-03 bimPdStOrder(codes): {ok: false, why: 'not an STLRFD command: C'}
//   for the first unknown code; else the codes that come before an earlier one's
//   section, as {ok: false, why: "out of the manual's order: A, B"}; else {ok: true}
function bimPdStOrder(codes) {
  if (!Array.isArray(codes)) return { ok: false, why: 'not an array' };

  var sectionOrder = ['CFG', 'TTL', 'CTL', 'SID', 'GEO', 'CDF', 'UDF', 'URF', 'SKW', 'SPL', 'HNG', 'UDA', 'MAT', 'DRB', 'DP1', 'DP2', 'DPL', 'DTS', 'URB', 'ARB', 'ABU', 'APL', 'SHO', 'SLS', 'SLB', 'SST', 'DPS', 'DPC', 'DPD', 'PLD', 'LDF', 'CLD', 'DLD', 'WPD', 'WUD', 'DOL', 'SLL', 'SAL', 'FTL', 'FGV', 'FTG', 'BRP', 'CBR', 'TST', 'LST', 'BST', 'BSD', 'SCS', 'SCC', 'FSL', 'LAS', 'OIN', 'OSP', 'ODG', 'OAN', 'OSC', 'ORF'];

  // First, check for unknown codes (not in BIM_PD_ST)
  for (var i = 0; i < codes.length; i++) {
    if (!BIM_PD_ST[codes[i]]) {
      return { ok: false, why: 'not an STLRFD command: ' + codes[i] };
    }
  }

  // Check for out-of-order codes
  var seen = {};
  for (var i = 0; i < codes.length; i++) {
    var code = codes[i];
    if (seen[code]) continue;
    seen[code] = true;

    var currentIdx = sectionOrder.indexOf(code);
    for (var j = 0; j < i; j++) {
      var prevCode = codes[j];
      var prevIdx = sectionOrder.indexOf(prevCode);
      if (prevIdx >= 0 && currentIdx >= 0 && currentIdx < prevIdx) {
        return { ok: false, why: 'out of the manual\'s order: ' + code };
      }
    }
  }

  return { ok: true };
}

/* ================= __acad3dV226: end of pure functions =============== */
