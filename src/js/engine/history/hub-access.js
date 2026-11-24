

  /* ================= __acad3dV217: Hub H5, the server's access rules, the pure part =================
     docs/research/research-notion-hub-h5-server.md and docs/work-orders/v217/SPEC.md. Access rules: the role on an element,
     whether it allows an action, what a private check may return, the audit entry. Each function is a work order, added
     below as it is built; none uses another file's names. */
function bimSrvRole(acl, user, elId) {
  var u, i;
  // First pass: look for element-specific entry
  for (i = 0; i < acl.length; i += 1) {
    u = acl[i];
    if (u.user === user && u.element !== undefined && u.element !== null && u.element === elId) {
      if (u.deny) return null;
      return u.role;
    }
  }
  // Second pass: look for project-wide entry (no element or element is null/undefined)
  for (i = 0; i < acl.length; i += 1) {
    u = acl[i];
    if (u.user === user && (u.element === undefined || u.element === null)) {
      if (u.deny) return null;
      return u.role;
    }
  }
  return null;
}

var BIM_SRV_RANK = {viewer: 1, commenter: 2, editor: 3, owner: 4};
var BIM_SRV_NEED = {read: 1, comment: 2, edit: 3, share: 4, delete: 4};

function bimSrvCan(acl, user, elId, action) {
  var need, role, rank;
  if (BIM_SRV_NEED[action] === undefined) return false;
  need = BIM_SRV_NEED[action];
  role = bimSrvRole(acl, user, elId);
  if (role === null) return false;
  rank = BIM_SRV_RANK[role] === undefined ? 0 : BIM_SRV_RANK[role];
  return rank >= need;
}

function bimSrvRedact(result, fields) {
  var i, out = {}, f;
  for (i = 0; i < fields.length; i += 1) {
    f = fields[i];
    if (result[f] !== undefined) out[f] = result[f];
  }
  return out;
}

function bimSrvAudit(user, action, elId, allowed, when) {
  return { at: when, user: user, action: action, element: elId, allowed: !!allowed };
}
