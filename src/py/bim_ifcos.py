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
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.guid
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


def bim_ifcos_add_wall(name, x0, y0, x1, y1, height, thickness):
    global _bim_ifcos_file
    try:
        f = _bim_ifcos_file
        if f is None:
            return {"error": "no project"}
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-9:
            return {"error": "zero length"}
        storey = f.by_type("IfcBuildingStorey")[0]
        body = None
        for c in f.by_type("IfcGeometricRepresentationSubContext"):
            if c.ContextIdentifier == "Body":
                body = c
                break
        wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name=name)
        representation = ifcopenshell.api.geometry.add_wall_representation(
            f, context=body, length=L, height=height, thickness=thickness
        )
        ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=representation)
        a = math.atan2(y1 - y0, x1 - x0)
        M = numpy.array([
            [math.cos(a), -math.sin(a), 0, x0],
            [math.sin(a), math.cos(a), 0, y0],
            [0, 0, 1, storey.Elevation],
            [0, 0, 0, 1],
        ], dtype=float)
        ifcopenshell.api.geometry.edit_object_placement(f, product=wall, matrix=M)
        ifcopenshell.api.spatial.assign_container(f, products=[wall], relating_structure=storey)
        return {"guid": wall.GlobalId}
    except Exception:
        return {"error": "unreadable"}


def bim_ifcos_write_read(path):
    global _bim_ifcos_file
    try:
        f = _bim_ifcos_file
        if f is None:
            return {"error": "no project"}
        f.write(path)
        return {"bytes": os.path.getsize(path), "summary": bim_ifcos_summary(path)}
    except Exception:
        return {"error": "unreadable"}


def bim_ifcos_matrix(x, y, z, a):
    return numpy.array([
        [math.cos(a), -math.sin(a), 0, x],
        [math.sin(a), math.cos(a), 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1],
    ], dtype=float)


def bim_ifcos_storey(level):
    storeys = _bim_ifcos_file.by_type("IfcBuildingStorey")
    if isinstance(level, int) and 0 <= level < len(storeys):
        return storeys[level]
    return storeys[0]


def bim_ifcos_body():
    for c in _bim_ifcos_file.by_type("IfcGeometricRepresentationSubContext"):
        if c.ContextIdentifier == "Body":
            return c


def bim_ifcos_keep_guid(product, guid):
    ok = (
        isinstance(guid, str)
        and len(guid) == 22
        and all(c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$" for c in guid)
    )
    if ok:
        try:
            _bim_ifcos_file.by_guid(guid)
        except Exception:
            product.GlobalId = guid
    return product.GlobalId


def bim_ifcos_begin(name, levels):
    global _bim_ifcos_file
    try:
        if not levels:
            levels = [{"name": "Level 0", "elev": 0}]
        r = bim_ifcos_new_project(name, levels[0]["elev"])
        if "error" in r:
            return r
        f = _bim_ifcos_file
        storeys = f.by_type("IfcBuildingStorey")
        storeys[0].Name = levels[0]["name"]
        building = f.by_type("IfcBuilding")[0]
        for lv in levels[1:]:
            storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name=lv["name"])
            storey.Elevation = lv["elev"]
            ifcopenshell.api.aggregate.assign_object(f, products=[storey], relating_object=building)
        for s in f.by_type("IfcBuildingStorey"):
            ifcopenshell.api.geometry.edit_object_placement(
                f, product=s, matrix=bim_ifcos_matrix(0, 0, s.Elevation, 0)
            )
        return bim_ifcos_summary("")
    except Exception:
        return {"error": "failed"}


def bim_ifcos_put_wall(w):
    global _bim_ifcos_file
    try:
        f = _bim_ifcos_file
        if f is None:
            return {"error": "no project"}
        L = math.hypot(w["x1"] - w["x0"], w["y1"] - w["y0"])
        if L < 1e-9:
            return {"error": "zero length"}
        wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name=w.get("name"))
        rep = ifcopenshell.api.geometry.add_wall_representation(
            f, context=bim_ifcos_body(), length=L, height=w["height"],
            thickness=w["thickness"], offset=w.get("offset", 0)
        )
        ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=rep)
        a = math.atan2(w["y1"] - w["y0"], w["x1"] - w["x0"])
        M = bim_ifcos_matrix(w["x0"], w["y0"], w["base"], a)
        ifcopenshell.api.geometry.edit_object_placement(f, product=wall, matrix=M)
        ifcopenshell.api.spatial.assign_container(
            f, products=[wall], relating_structure=bim_ifcos_storey(w.get("level"))
        )
        return {"guid": bim_ifcos_keep_guid(wall, w.get("guid"))}
    except Exception:
        return {"error": "failed"}


def bim_ifcos_put_prism(p):
    global _bim_ifcos_file
    try:
        f = _bim_ifcos_file
        if f is None:
            return {"error": "no project"}
        pts = p.get("pts") or []
        depth = p.get("depth")
        if len(pts) < 3 or depth is None or depth <= 0:
            return {"error": "bad outline"}
        element = ifcopenshell.api.root.create_entity(
            f, ifc_class=p.get("cls") or "IfcSlab", name=p.get("name")
        )
        rep = ifcopenshell.api.geometry.add_slab_representation(
            f, context=bim_ifcos_body(), depth=p["depth"],
            polyline=[(float(x), float(y)) for (x, y) in pts]
        )
        ifcopenshell.api.geometry.assign_representation(f, product=element, representation=rep)
        ifcopenshell.api.geometry.edit_object_placement(
            f, product=element, matrix=bim_ifcos_matrix(0, 0, p["base"], 0)
        )
        ifcopenshell.api.spatial.assign_container(
            f, products=[element], relating_structure=bim_ifcos_storey(p.get("level"))
        )
        return {"guid": bim_ifcos_keep_guid(element, p.get("guid"))}
    except Exception:
        return {"error": "failed"}


def bim_ifcos_put_opening(o):
    global _bim_ifcos_file
    try:
        f = _bim_ifcos_file
        if f is None:
            return {"error": "no project"}
        try:
            host = f.by_guid(o["host"])
        except Exception:
            return {"error": "no host"}
        if not host.is_a("IfcWall"):
            return {"error": "no host"}
        if o["width"] <= 0 or o["height"] <= 0 or o["depth"] <= 0:
            return {"error": "bad size"}
        a = o["a"]
        M = bim_ifcos_matrix(o["x"] - math.cos(a) * o["width"] / 2, o["y"] - math.sin(a) * o["width"] / 2, o["base"], a)
        body = bim_ifcos_body()
        opening = ifcopenshell.api.root.create_entity(f, ifc_class="IfcOpeningElement", name=o.get("name"))
        rep = ifcopenshell.api.geometry.add_wall_representation(
            f, context=body, length=o["width"], height=o["height"], thickness=o["depth"], offset=-o["depth"] / 2
        )
        ifcopenshell.api.geometry.assign_representation(f, product=opening, representation=rep)
        ifcopenshell.api.geometry.edit_object_placement(f, product=opening, matrix=M)
        ifcopenshell.api.feature.add_feature(f, feature=opening, element=host)
        if o.get("cls") == "IfcWindow":
            element = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWindow", name=o.get("name"))
            rep2 = ifcopenshell.api.geometry.add_window_representation(f, context=body, overall_height=o["height"], overall_width=o["width"])
        else:
            element = ifcopenshell.api.root.create_entity(f, ifc_class="IfcDoor", name=o.get("name"))
            rep2 = ifcopenshell.api.geometry.add_door_representation(f, context=body, overall_height=o["height"], overall_width=o["width"])
        ifcopenshell.api.geometry.assign_representation(f, product=element, representation=rep2)
        ifcopenshell.api.geometry.edit_object_placement(f, product=element, matrix=M)
        ifcopenshell.api.feature.add_filling(f, opening=opening, element=element)
        ifcopenshell.api.spatial.assign_container(f, products=[element], relating_structure=ifcopenshell.util.element.get_container(host))
        return {"guid": bim_ifcos_keep_guid(element, o.get("guid")), "opening": opening.GlobalId}
    except Exception:
        return {"error": "failed"}


def bim_ifcos_put_mesh(m):
    global _bim_ifcos_file
    try:
        f = _bim_ifcos_file
        if f is None:
            return {"error": "no project"}
        verts = m.get("verts")
        faces = m.get("faces")
        if not verts or not faces:
            return {"error": "empty mesh"}
        element = ifcopenshell.api.root.create_entity(
            f, ifc_class=m.get("cls") or "IfcBuildingElementProxy", name=m.get("name")
        )
        rep = ifcopenshell.api.geometry.add_mesh_representation(
            f, context=bim_ifcos_body(),
            vertices=[[(float(x), float(y), float(z)) for (x, y, z) in verts]],
            faces=[[(int(i), int(j), int(k)) for (i, j, k) in faces]],
        )
        ifcopenshell.api.geometry.assign_representation(f, product=element, representation=rep)
        ifcopenshell.api.geometry.edit_object_placement(
            f, product=element, matrix=bim_ifcos_matrix(0, 0, 0, 0)
        )
        ifcopenshell.api.spatial.assign_container(
            f, products=[element], relating_structure=bim_ifcos_storey(m.get("level"))
        )
        return {"guid": bim_ifcos_keep_guid(element, m.get("guid"))}
    except Exception:
        return {"error": "failed"}


def bim_ifcos_put_psets(guid, psets):
    global _bim_ifcos_file
    try:
        f = _bim_ifcos_file
        if f is None:
            return {"error": "no project"}
        try:
            element = f.by_guid(guid)
        except Exception:
            return {"error": "not found"}
        count = 0
        for s in psets or []:
            props = s.get("props")
            if not props:
                continue
            pset = ifcopenshell.api.pset.add_pset(f, product=element, name=s["name"])
            ifcopenshell.api.pset.edit_pset(f, pset=pset, properties=props)
            count += 1
        return {"psets": count}
    except Exception:
        return {"error": "failed"}


def bim_ifcos_export(model, path):
    global _bim_ifcos_file
    try:
        r = bim_ifcos_begin(model.get("name") or "Project", model.get("levels") or [])
        if "error" in r:
            return r
        written = 0; skipped = []; written_guids = {}
        for w in model.get("walls") or []:
            res = bim_ifcos_put_wall(w)
            if "error" in res:
                skipped.append({"id": w.get("id"), "why": res["error"]})
            else:
                written_guids[w.get("id")] = res["guid"]; written += 1
                if w.get("psets"): bim_ifcos_put_psets(res["guid"], w["psets"])
        for p in model.get("prisms") or []:
            res = bim_ifcos_put_prism(p)
            if "error" in res:
                skipped.append({"id": p.get("id"), "why": res["error"]})
            else:
                written_guids[p.get("id")] = res["guid"]; written += 1
                if p.get("psets"): bim_ifcos_put_psets(res["guid"], p["psets"])
        for o in model.get("openings") or []:
            item = dict(o); item["host"] = written_guids.get(o.get("host"), "")
            res = bim_ifcos_put_opening(item)
            if "error" in res:
                skipped.append({"id": o.get("id"), "why": res["error"]})
            else:
                written_guids[o.get("id")] = res["guid"]; written += 1
                if o.get("psets"): bim_ifcos_put_psets(res["guid"], o["psets"])
        for m in model.get("meshes") or []:
            res = bim_ifcos_put_mesh(m)
            if "error" in res:
                skipped.append({"id": m.get("id"), "why": res["error"]})
            else:
                written_guids[m.get("id")] = res["guid"]; written += 1
                if m.get("psets"): bim_ifcos_put_psets(res["guid"], m["psets"])
        return {**bim_ifcos_write_read(path), "skipped": skipped, "written": written}
    except Exception:
        return {"error": "failed"}
