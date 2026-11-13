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
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.unit

_bim_ifcos_file = None
