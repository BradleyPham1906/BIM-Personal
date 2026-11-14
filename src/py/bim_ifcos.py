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


def bim_ifcos_new_project(name, elevation):
    global _bim_ifcos_file
    try:
        f = ifcopenshell.api.project.create_file(version="IFC4")
        _bim_ifcos_file = f
        project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name=name)
        units = [
            ifcopenshell.api.unit.add_si_unit(f, unit_type="LENGTHUNIT"),
            ifcopenshell.api.unit.add_si_unit(f, unit_type="AREAUNIT"),
            ifcopenshell.api.unit.add_si_unit(f, unit_type="VOLUMEUNIT"),
        ]
        ifcopenshell.api.unit.assign_unit(f, units=units)
        model = ifcopenshell.api.context.add_context(f, context_type="Model")
        ifcopenshell.api.context.add_context(
            f,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )
        site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="Site")
        building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="Building")
        storey = ifcopenshell.api.root.create_entity(
            f, ifc_class="IfcBuildingStorey", name="Level 0"
        )
        storey.Elevation = elevation
        ifcopenshell.api.aggregate.assign_object(f, products=[site], relating_object=project)
        ifcopenshell.api.aggregate.assign_object(f, products=[building], relating_object=site)
        ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=building)
        return bim_ifcos_summary("")
    except Exception:
        return {"error": "unreadable"}
