# Research: how structural analysis fits the interface (V125)

The owner, while V125 was being built: "make sure this feature is cleanly add-in the design and not
overloading the UI/UX. everything must be consistent. I also wants u to look into rhinoceros
documentation of their apps. this would refine our design"

The McNeel documentation sites (docs.mcneel.com, developer.rhino3d.com, www.rhino3d.com) were not
reachable from the build environment. What follows comes from search summaries of those pages and
from V123's Gumball research (`research-direct-manipulation.md`). Each point is marked with where it
came from.

## What Rhino does

1. **One Properties panel, with pages chosen by the selection.** "The availability of properties
   [is] based on the selected object types", and "if no objects are selected, viewport properties
   display" (Rhino 8 Help: Properties, PropertiesPage). A plug-in adds its settings as another page
   of that same panel (`ObjectPropertiesPage` in RhinoCommon). It does not add a window of its own.
2. **Command-line options are part of the command.** Options "appear as clickable hyperlinks on the
   command line", and you can type the underlined letter instead (Rhino 8 Help: Command options).
   A command's settings are chosen while it runs, not on a separate settings screen.
3. **Analysis is a display mode, switched on and off by its command.** Zebra, CurvatureAnalysis and
   DraftAngleAnalysis overlay false colour or stripes on the model you are already looking at.
   Each is a command that turns the mode on, and an Off form turns it back off (Rhino Help:
   Zebra, Curvature, DraftAngleAnalysis; RhinoCommon `VisualAnalysisMode`). An analysis is never a
   second copy of the model.
4. **Panels are tabs in one docked column,** and you open only the ones you use (Rhino 8 Help:
   Panels; the Rhino window).
5. **Karamba3D,** the structural engine people use inside Rhino, runs Analyze on the model and
   reports a handful of headline numbers: the maximum displacement, the maximum resultant force
   and the deformation energy. It shows the deformed shape at a stated scale (Karamba3D manual:
   Analyze).

## What V125 takes from it

- **No new panel, rail tab or window.** Following (1), the structural settings are pages in the
  Properties panel this app already has:
  - A column or beam selected: its Structural group (support, loads).
  - Nothing selected: the Analysis settings (combination, self-weight, what the display shows) and
    the last result's headline numbers. That is where V106 already put the level's floor loads.
- **ANALYZE turns the analysis display on; ANALYZEOFF turns it off.** Following (3), results draw
  over the model on screen, and the model underneath is unchanged. When the model changes, the
  display is out of date: it draws nothing and says so, instead of showing a stale result.
- **The headline numbers follow Karamba's.** Following (5), ANALYZE reports the largest moment,
  the largest deflection with its span ratio, and the equilibrium check.
- **One button.** Analyze goes in the Structure tab's existing strip. Following (2), the other
  commands (SUPPORT, LOAD, ANALYZEOFF) are on the command line, and their options are in
  Properties.
- **The tables use the existing schedule registry,** as rooms, columns and loads already do.

## Sources

- [Rhino 8 Help: Properties](https://docs.mcneel.com/rhino/8/help/en-us/commands/properties.htm)
- [Rhino 8 Help: PropertiesPage](https://docs.mcneel.com/rhino/8/help/en-us/commands/propertiespage.htm)
- [Rhino 8 Help: Command options](http://docs.mcneel.com/rhino/8/help/en-us/popup_actions/specifycommandlineoption.htm)
- [Rhino 8 Help: Panels](https://docs.mcneel.com/rhino/8/help/en-us/user_interface/panels.htm)
- [Rhino 8 Help: The Rhino window](https://docs.mcneel.com/rhino/8/help/en-us/user_interface/rhino_window.htm)
- [Rhino 8 Help: Zebra](https://docs.mcneel.com/rhino/8/help/en-us/commands/zebra.htm)
- [RhinoCommon: VisualAnalysisMode](https://developer.rhino3d.com/api/rhinocommon/rhino.display.visualanalysismode)
- [RhinoCommon: ObjectPropertiesPage](https://developer.rhino3d.com/api/rhinocommon/rhino.ui.objectpropertiespage)
- [Karamba3D manual: Analyze](https://manual.karamba3d.com/3-in-depth-component-reference/3.5-algorithms/3.5.1-analyze)
