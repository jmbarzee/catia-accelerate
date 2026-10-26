# CATIA V5 automation object model, the parts new users need

A curated map, not a reference. The reference is `V5Automation.chm` in your CATIA install
(extract it with `python tools/extract_chm.py`, then search `local/chm/`). Member names
below are stable across V5 releases unless marked. Verify anything marked *(verify)*.

## Entry point

```
CATIA                      Application. Global in CATScript/CATVBA. GetObject(,"CATIA.Application") from outside.
  .ActiveDocument          Document currently in front
  .Documents               Collection. .Open(path), .Add("Part"|"Product"|"Drawing"), .Count, .Item(i)
  .ActiveWindow            Window. .ActiveViewer (Viewer3D)
  .Windows                 Collection
  .Selection               Shortcut to ActiveDocument.Selection (verify)
  .SystemService           .Environ("VAR"), .Evaluate(code, lang, name, args), .ExecuteScript(...)
  .FileSystem              .GetFile(path), .GetFolder(path), .FileExists(path), .FolderExists(path)
  .RefreshDisplay          Boolean. Set False during loops.
  .DisplayFileAlerts       Boolean. Set False for batch opens.
  .StatusBar               String. Write progress here.
  .Visible                 Boolean. Relevant when driving CATIA from outside.
  .Quit
```

## Documents

```
Document                   Base. .Name, .FullName, .Path, .Saved, .Save, .SaveAs(path), .Close, .Activate
  .Selection               Selection (see below)
  .ExportData(path, fmt)   "stp", "igs", "cgr", "stl", "pdf" (drawings) ... format set depends on licenses
  .GetWorkbench("SPAWorkbench")  Measurement workbench (see Measure)

PartDocument : Document
  .Part                    Part

ProductDocument : Document
  .Product                 Root Product

DrawingDocument : Document
  .Sheets                  DrawingSheets. .ActiveSheet, .Item(i)
    .Views                 DrawingViews. .ActiveView, .Item(i)
      .GenerativeBehavior  Link to the 3D. .Update
```

`TypeName(CATIA.ActiveDocument)` returns the class name. Check it before using `.Part` or `.Product`.

## Product structure (assemblies)

```
Product
  .Name                    Instance name
  .PartNumber              Reference identity
  .Products                Collection of child Products. .Count, .Item(i), .AddNewComponent(type, name), .AddComponent(prod), .AddComponentsFromFiles(arr, "All")
  .ReferenceProduct        The reference this instance points at. .Parent is its Document (ProductDocument or PartDocument)
  .Parent                  Parent collection / document
  .Source                  0 Unknown, 1 Made, 2 Bought
  .Revision, .Nomenclature, .Definition, .DescriptionRef, .DescriptionInst
  .Position                Position. .GetComponents(arr12), .SetComponents(arr12)   (3x3 rotation + translation)
  .Move                    Move. .Apply(arr12) applies a transform
  .ApplyWorkMode(mode)     0 = Design Mode, 1 = Visualization Mode   (CatWorkModeType)
  .Update
  .Parameters, .Relations, .Publications, .Connections (constraints), .UserRefProperties
  .GetTechnologicalObject("Inertia")   Inertia. .Mass, .Density, .GetCOGPosition(arr3)   (verify)
  .Analyze                 Analyze. .Mass, .Volume, .WetArea, .GetGravityCenter(arr3)
```

Walk pattern: recurse `Products`, treat `Products.Count = 0` as a part. See
`macros/templates/WalkProductTree.CATScript`.

Constraints: `Product.Connections.Item("CATIAConstraints")` returns the Constraints
collection; `.AddBiEltCst(type, ref1, ref2)`. Types are the `CatConstraintType` enum.

## Parts

```
Part
  .Bodies                  Bodies. .Item("PartBody"), .Add
    Body.Shapes            Features (Pad, Pocket, Hole, ...). .Item(i)
    Body.Sketches          Sketches. .Add(plane) -> Sketch
      Sketch.OpenEdition   -> Factory2D (.CreateLine, .CreateCircle, .CreateClosedCircle ...)
      Sketch.CloseEdition
  .HybridBodies            Geometrical Sets. .Add, .Item(name)
    .HybridShapes          Surfaces, wireframe
  .OriginElements          .PlaneXY, .PlaneYZ, .PlaneZX
  .ShapeFactory            .AddNewPad(sketch, length), .AddNewPocket, .AddNewHole, .AddNewEdgeFilletWithConstantRadius ...
  .HybridShapeFactory      .AddNewPointCoord, .AddNewLinePtPt, .AddNewPlaneOffset, .AddNewExtrude ...
  .Parameters              Parameters. .Item("name"), .CreateDimension(name, "LENGTH", value), .CreateReal, .CreateString, .CreateBoolean
    Parameter.Value, .Name, .ValueAsString
  .Relations               .CreateFormula(name, comment, parameter, formulaText), .CreateDesignTable
  .InWorkObject            Current work object (set it before adding features)
  .CreateReferenceFromObject(obj)      -> Reference, needed by most factory methods
  .CreateReferenceFromName(name)       Brep names like "Face:(Brp:(Pad.1;0:(Brp:(Sketch.1;1)));None:();Cf11:())"
  .Update
  .UpdateObject(feature)
```

## Selection

```
Selection
  .Count, .Item(i)         SelectedElement: .Value (the object), .Reference, .Type, .Document
  .Add(obj), .Remove(i), .Clear
  .Search(query)           Same syntax as Edit > Search: "Name=*bolt*,all"  "Type=Part,all"  "Color='Red',all"
  .SelectElement2(filterArray, prompt, multiSelect)  Interactive pick. Returns "Normal"|"Cancel"|"Undo"|"Redo"
  .SelectElement3(...), .SelectElement4(...)          Variants with more options (verify)
  .VisProperties           VisPropertySet. .SetShow(0 show|1 noshow), .SetRealColor(r,g,b,inherit), .SetRealOpacity(0..255,inherit), .SetVisibleLayer, .SetVisibleColor...
  .Copy, .Cut, .Paste, .PasteSpecial("CATPrtResult"), .Delete
  .FilteringMode
```

Search scope suffixes: `,all` (whole document), `,in` (active object), `,sel` (within selection).
Build the query in the Edit > Search dialog, read it from the Favorites tab, paste it.

## Measure

```
Document.GetWorkbench("SPAWorkbench")   -> SPAWorkbench
  .GetMeasurable(reference)             -> Measurable
    .Volume, .Area, .Length, .Perimeter, .Radius, .Angle
    .GetCOG(arr3), .GetPoint(arr3), .GetCenter(arr3), .GetDirection(arr3)
    .GetMinimumDistance(ref2), .GetMinimumDistancePoints(ref2, arr6), .GetAngleBetween(ref2)
  .Inertias.Add(body or product)        -> Inertia. .Mass, .Density, .GetCOGPosition(arr3), .GetInertiaMatrix(arr9)
  .Sections, .Clashes, .Distances       DMU analyses (license-dependent)
```

Values on Visualization Mode parts are tessellation-based. Put the part in Design Mode
for exact results.

## View and capture

```
CATIA.ActiveWindow.ActiveViewer : Viewer3D
  .Reframe, .ZoomIn, .ZoomOut, .Update
  .RenderingMode           catRenderShading, catRenderWireFrame, ... (CatRenderingMode)
  .Viewpoint3D             .PutSightDirection(arr3), .PutUpDirection(arr3), .PutOrigin(arr3), .FocusDistance, .Zoom
  .CaptureToFile(format, path)   CatCaptureFormat: PNG is 6 in recent releases (verify)
  .FullScreen
CATIA.ActiveWindow.Layout   catWindowSpecsAndGeom, catWindowGeomOnly ...
```

## Files and OS

```
CATIA.FileSystem           .GetFile(p).Size, .GetFolder(p).Files, .CreateFile(p, overwrite), .CopyFile, .DeleteFile
CATIA.SystemService.Environ("CATInstallPath")
CreateObject("Scripting.FileSystemObject")   Plain Windows scripting host objects also work from CATScript
CreateObject("Excel.Application")            Office automation works too
```

## Enums you will hit

| Enum | Values |
|---|---|
| CatWorkModeType | 0 DESIGN_MODE, 1 VISUALIZATION_MODE |
| CatProductSource | 0 Unknown, 1 Made, 2 Bought |
| CatVisPropertyShow | 0 Show, 1 NoShow |
| CatVisPropertyInherit (inheritance arg) | 0 inherit, 1 no inherit (verify order) |
| CatConstraintType | catCstTypeDistance, catCstTypeOn (coincidence), catCstTypeSurfaceContact, catCstTypeAngle, catCstTypeReference (fix)... numeric in CATScript |
| CatCaptureFormat | 0 CGM, 1 EMF, 2 TIFF, 3 TIFF greyscale, 4 BMP, 5 JPEG, 6 PNG (verify) |

In CATScript, enums are plain numbers. In CATVBA, the named constants work after the
type libraries load.

## Driving CATIA from outside (Python, PowerShell, C#)

```
GetObject(, "CATIA.Application")    attaches to the running instance
CreateObject("CATIA.Application")   starts one (slow). Set .Visible = True
```
`pycatia` wraps this in Python. PowerShell: `[Runtime.InteropServices.Marshal]::GetActiveObject("CATIA.Application")`.

## When the member you need is not here

1. Record a macro doing it by hand (Tools > Macro > Start Recording) and read the code.
2. Open the CATVBA editor (Alt+F11), press F2 for the Object Browser, search the member.
3. Search the extracted CHM in `local/chm/`.
4. Search pycatia's API tree at https://pycatia.readthedocs.io, which names the same members.
