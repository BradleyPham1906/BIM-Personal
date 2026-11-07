// e02_driver.cpp -- the B-rep kernel research (reference/research-usd-brep.md), 2026-11-01.
// Our own test driver for NVIDIA's SMLib (usd-brep), compiled to WebAssembly by e02_build.sh with the
// kernel unchanged. Each e02_* function runs one operation and returns a number the harness checks:
// a volume (positive) on success, or -(1000 + status) on failure, so a failure is never mistaken for
// a result. Usage follows upstream's Examples/SM_API/boolean_bounds.cpp (Apache-2.0): every status
// checked against SM_SUCCESS, the Boolean's second operand released only on success.
// Exceptions thrown by the kernel are caught here and returned as -2.
#include <SmApiBrep.h>
#include <SmApiGeneral.h>
#include <SmApiPrimitives.h>
#include <SmApiQueries.h>
#include <SmBrep.h>
#include <SmPoly.h>
#include <SmVector3d.h>
#include <cmath>

static double fail(SmApiStatus s) { return -(1000.0 + (double)s); }

// Volume of a manifold solid, or a failure code (-3 when it is not a manifold solid).
static double solidVolume(SmBrep* b) {
  SmBoolean manifold = FALSE;
  SmApiStatus s = SmApiBrepIsManifoldSolid(b, manifold);
  if (s != SM_SUCCESS) return fail(s);
  if (manifold != TRUE) return -3.0;
  double v = 0.0;
  s = SmApiBrepComputeVolume(b, 1.0e-7, v);
  if (s != SM_SUCCESS) return fail(s);
  return v;
}

extern "C" {

void e02_init() { SmApiCreateContext(); }

// A 10 x 10 x 3 box less a cylinder of radius 2 through it. Expected 300 - 12 pi.
double e02_box_minus_cylinder() {
  try {
    SmBrep* a = nullptr; SmBrep* b = nullptr; SmBrep* r = nullptr;
    SmApiStatus s = SmApiCreateBox(SmVector3d(0, 0, 0), 10, 10, 3, a);
    if (s != SM_SUCCESS) return fail(s);
    s = SmApiCreateCylinder(SmVector3d(5, 5, -1), 2, 5, b);
    if (s != SM_SUCCESS) { delete a; return fail(s); }
    s = SmApiBooleanDifference(a, b, r);
    if (s != SM_SUCCESS) { delete a; delete b; return fail(s); }
    double v = solidVolume(r); delete r; return v;
  } catch (...) { return -2.0; }
}

// Upstream's fixture: a 12 x 12 x 1.5 plate with 4 x 4 through-holes of radius 0.75 (16 differences).
double e02_plate16() {
  try {
    SmBrep* plate = nullptr;
    SmApiStatus s = SmApiCreateBox(SmVector3d(0, 0, 0), 12, 12, 1.5, plate);
    if (s != SM_SUCCESS) return fail(s);
    for (int row = 0; row < 4; row++) for (int col = 0; col < 4; col++) {
      SmBrep* tool = nullptr; SmBrep* r = nullptr;
      s = SmApiCreateCylinder(SmVector3d((col + 0.5) * 3, (row + 0.5) * 3, -1), 0.75, 3.5, tool);
      if (s != SM_SUCCESS) { delete plate; return fail(s); }
      s = SmApiBooleanDifference(plate, tool, r);
      if (s != SM_SUCCESS) { delete plate; delete tool; return fail(s); }
    }
    double v = solidVolume(plate); delete plate; return v;
  } catch (...) { return -2.0; }
}

// Two walls meeting at a shared face, the case BIM joins lean on: 4 x 0.2 x 3 and 0.2 x 4 x 3, L-shaped,
// overlapping in a 0.2 x 0.2 corner. Expected 2.4 + 2.4 - 0.12 = 4.68.
double e02_wall_join_union() {
  try {
    SmBrep* a = nullptr; SmBrep* b = nullptr; SmBrep* r = nullptr;
    SmApiStatus s = SmApiCreateBox(SmVector3d(0, 0, 0), 4, 0.2, 3, a);
    if (s != SM_SUCCESS) return fail(s);
    s = SmApiCreateBox(SmVector3d(0, 0, 0), 0.2, 4, 3, b);
    if (s != SM_SUCCESS) { delete a; return fail(s); }
    s = SmApiBooleanUnion(a, b, r);
    if (s != SM_SUCCESS) { delete a; delete b; return fail(s); }
    double v = solidVolume(r); delete r; return v;
  } catch (...) { return -2.0; }
}

// A circular fillet of radius 1 on one edge of a 10 x 10 x 10 box. Expected 1000 - (1 - pi/4) * 10.
double e02_fillet_box_edge() {
  try {
    SmBrep* a = nullptr;
    SmApiStatus s = SmApiCreateBox(SmVector3d(0, 0, 0), 10, 10, 10, a);
    if (s != SM_SUCCESS) return fail(s);
    SmTArray<SmEdge*> edges, one;
    s = SmApiGetEdges(a, edges);
    if (s != SM_SUCCESS || edges.GetSize() == 0) { delete a; return s != SM_SUCCESS ? fail(s) : -4.0; }
    one.Add(edges[0]);
    s = SmApiFilletEdges(a, one, 1.0, 1, 1, 1.0);
    if (s != SM_SUCCESS) { delete a; return fail(s); }
    double v = solidVolume(a); delete a; return v;
  } catch (...) { return -2.0; }
}

// Tessellate the 16-hole plate with the default parameters; returns 1 on success.
double e02_tessellate_plate() {
  try {
    SmBrep* plate = nullptr;
    SmApiStatus s = SmApiCreateBox(SmVector3d(0, 0, 0), 12, 12, 1.5, plate);
    if (s != SM_SUCCESS) return fail(s);
    for (int row = 0; row < 4; row++) for (int col = 0; col < 4; col++) {
      SmBrep* tool = nullptr; SmBrep* r = nullptr;
      s = SmApiCreateCylinder(SmVector3d((col + 0.5) * 3, (row + 0.5) * 3, -1), 0.75, 3.5, tool);
      if (s != SM_SUCCESS) { delete plate; return fail(s); }
      s = SmApiBooleanDifference(plate, tool, r);
      if (s != SM_SUCCESS) { delete plate; delete tool; return fail(s); }
    }
    SmPolyBrep* mesh = nullptr;
    s = SmApiTessellate(plate, mesh);
    delete plate;
    if (s != SM_SUCCESS) return fail(s);
    delete mesh;
    return 1.0;
  } catch (...) { return -2.0; }
}

}
