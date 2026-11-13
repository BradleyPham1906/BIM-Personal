"""__acad3dV176: the app's adapter to IfcOpenShell (LGPL-3.0, its WebAssembly wheel, unchanged), run by the app's own
Pyodide. docs/work-orders/v176/SPEC.md says what each function does; docs/work-orders/v176/v176.test.mjs tests them.

Every function takes plain values and answers a plain dict (JSON), so JavaScript calls it the same way it calls the
Ladybug adapter. The project being built is kept in _bim_ifcos_file. A failure answers {"error": "..."}; nothing is
printed or raised to the caller."""
import math
import os

import numpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.unit

_bim_ifcos_file = None


def bim_ifcos_summary(path):
    try:
        if path:
            if not os.path.exists(path):
                return {"error": "not found"}
            f = ifcopenshell.open(path)
        else:
            f = _bim_ifcos_file
            if f is None:
                return {"error": "no project"}
        scale = ifcopenshell.util.unit.calculate_unit_scale(f)
        products = {}
        for element in f.by_type("IfcProduct"):
            if element.is_a() == "IfcOpeningElement":
                continue
            products[element.is_a()] = products.get(element.is_a(), 0) + 1
        storeys = [{"name": s.Name,
                    "elevation": round((s.Elevation or 0) * scale, 6)}
                   for s in f.by_type("IfcBuildingStorey")]
        return {"schema": f.schema, "products": products, "storeys": storeys}
    except Exception:
        return {"error": "unreadable"}
