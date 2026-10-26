# Macros

CATIA V5 automation in three flavors. Pick one.

| Flavor | File | Pros | Cons |
|---|---|---|---|
| **CATScript** | `.CATScript` | Plain text, runs on every CATIA, easy to share and diff | No IDE, no IntelliSense, weak error messages |
| **CATVBA** | `.catvba` project | Real IDE (Alt+F11), IntelliSense, forms, debugger | Binary project files, needs the VBA option installed, release-sensitive |
| **Python** | `.py` via `pycatia` | Modern language, tests, libraries | Needs Python on the CATIA machine, alpha-quality wrapper |

Start with CATScript. Switch to CATVBA when you need a dialog or a debugger.
All three talk to the same COM object model, so the API knowledge transfers.

## Run a CATScript

1. Tools > Macro > **Macros** (Alt+F8).
2. **Macro libraries** > Library type: Directories > Add existing library > pick
   `macros/examples` (and `macros/scratch`). Close.
3. Back in the Macros dialog, pick the library, pick the macro, **Run**.
4. Or **Edit** to open it in the editor set at Tools > Options > General > Macros.

Macros can also be bound to a toolbar icon: Tools > Customize > Commands > Macros,
drag the macro onto a toolbar.

## Record one

Tools > Macro > **Start Recording**. Do the thing. Stop Recording. CATIA writes a
CATScript of the object-model calls it made. Recording covers a surprising amount
(selection, property edits, most Part Design features) and nothing in some areas (DMU).
Recorded code is verbose and brittle. Treat it as a way to discover the API names, then
rewrite using the templates here.

## Anatomy

```vbscript
Language="VBSCRIPT"

Sub CATMain()
    Dim doc
    Set doc = CATIA.ActiveDocument
    MsgBox doc.Name
End Sub
```

- First line declares the language. `CATMain` is the entry point.
- `CATIA` is the global Application object. Everything hangs off it.
- CATScript is VBScript: no typed `Dim`, `Set` for objects, `On Error Resume Next` for
  error handling, `MsgBox` and `InputBox` for UI.
- In CATVBA you get typed declarations (`Dim doc As PartDocument`) and IntelliSense.
  Add references through the VBA editor's Tools > References if a type library is missing.

## Where the API documentation is

- **The official reference** is `V5Automation.chm`, shipped in your CATIA install under
  `win_b64\code\bin`, also reachable from Help > CATIA V5 Help > Automation.
  Run `python tools/extract_chm.py` to turn it into text in `local/chm/` so you and an
  AI assistant can search it. It is the only complete reference. It is also known to omit
  some members and have stale signatures, so when a call fails, try the recorded-macro
  trick to see what CATIA itself emits.
- **Curated map** of what new users need: [../docs-index/automation-object-model.md](../docs-index/automation-object-model.md).
- **pycatia docs** at https://pycatia.readthedocs.io mirror the object model in a browsable,
  searchable form, useful even if you write VBScript.
- **Object browser** in the CATVBA editor (F2) lists every class and member of the loaded
  type libraries. Fast way to check whether a property exists in your release.

## Templates

| File | Use |
|---|---|
| `templates/Skeleton.CATScript` | Minimal CATMain with document-type check and error handling |
| `templates/SelectionHelper.CATScript` | Ask the user to pick things, with type filters |
| `templates/WalkProductTree.CATScript` | Recursive product traversal, the base of most assembly macros |
| `templates/Skeleton.bas` | The same skeleton as a CATVBA module to import |
| `templates/skeleton_pycatia.py` | Python equivalent |

## Examples

All examples are read-only against the model unless the name says otherwise.

| File | What it does |
|---|---|
| `examples/ExportTreeToCsv.CATScript` | Walks the active product and writes part number, instance, type, depth, file path to CSV |
| `examples/CountParts.CATScript` | Counts parts and products, reports unique part numbers |
| `examples/ListDesignModeParts.CATScript` | Lists which parts are currently loaded in Design Mode |
| `examples/SetVisualizationMode.CATScript` | Switches the whole active product to Visualization Mode (releases memory) |
| `examples/IsolateSelection.CATScript` | Hides everything except the selection (modifies show/hide state only) |
| `examples/CaptureViews.CATScript` | Saves iso, front, top, right screenshots of the active window to a folder |
| `examples/SearchAndReframe.CATScript` | Prompts for a name pattern, selects matches, reframes the view on them |
| `examples/MeasureSelected.CATScript` | Volume, area, and CoG of selected items through SPAWorkbench |

Save your own in `scratch/`. It is git-ignored. Promote to `examples/` or your company's
macro share (see `company/conventions.md`) once it is worth keeping.

## Gotchas

- Macros run against **the active document**. Check its type before casting.
  `TypeName(CATIA.ActiveDocument)` returns `PartDocument`, `ProductDocument`, `DrawingDocument`.
- A product opened in Visualization Mode has limited objects: `Product.Products` and
  names work, `PartDocument.Part` does not until the part is in Design Mode.
  `Product.ApplyWorkMode DESIGN_MODE` switches it (and loads the part).
- `Selection.Search` takes the same query string as the Edit > Search dialog. Build the
  query in the dialog, then paste it.
- `CATIA.RefreshDisplay = False` at the start and `True` at the end speeds up long loops.
- `CATIA.DisplayFileAlerts = False` suppresses dialogs during batch opens. Restore it.
- Paths in CATScript use backslashes and no quoting magic. `CATIA.FileSystem` gives you
  file and folder objects.
- A CATVBA project built on release N may fail on release N+1 because referenced libraries
  moved. Keep the source in `.bas` files (File > Export in the VBA editor) and commit those.
