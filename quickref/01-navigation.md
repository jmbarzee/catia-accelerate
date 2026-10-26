# Navigation: zoom, pan, rotate, fit, hide

## Mouse (3-button mouse, default settings)

| Action | How |
|---|---|
| Pan | Hold middle button, drag |
| Rotate | Hold middle button, then also press and hold left (or right) button, drag |
| Zoom | Hold middle button, click and release left button, then drag up/down |
| Zoom in/out steps | Ctrl + PgUp / Ctrl + PgDn, or the Zoom In / Zoom Out icons |
| Fit all | Fit All In icon (bottom toolbar) |
| Rotate with keyboard | Shift + arrow keys |
| Pan with keyboard | Arrow keys |

Rotation happens around the point you click first, so click near the detail you care about
before rotating. A small axis marker shows the pivot.

## Zoom to a specific thing

- Select it in the tree or the viewer, right-click > **Reframe On**. The view recenters and
  zooms to that object. This is the single most useful command for large assemblies.
- **Center Graph** (same right-click menu) scrolls the spec tree to the selected object
  instead. Use both together: find it in 3D, Center Graph, read its context in the tree.

## Named views

- View > Named Views. Save the current viewpoint with a name, recall later. Ask whether your
  company ships standard named views in templates (`company/conventions.md`).
- Standard views: the View toolbar has Iso, Front, Back, Top, Bottom, Left, Right.

## Hide, show, isolate

- **Hide/Show**: select, then the Hide/Show icon (bottom toolbar) or right-click > Hide/Show.
  Hidden objects are drawn dimmed in the tree.
- **Swap Visible Space**: shows the hidden set instead of the visible one. Select items there
  and Hide/Show them back.
- **Isolate one thing in a big assembly**: select it, Edit > Search (Ctrl+F) is not needed.
  Instead: select the part, then View > Hide/Show > "Hide all but selected"? That command is
  not standard in all releases. The reliable path: select everything else (Ctrl+A in the tree,
  Ctrl+click to deselect your part) and Hide/Show. Or run
  `macros/examples/IsolateSelection.CATScript`.

## Rendering modes

View > Render Style: Shading with Edges (default), Wireframe (fastest on huge models),
Shading with Material. Switch to Wireframe when rotation stutters.

## Viewer tricks

- **Multiple views**: Window > New Window gives a second viewer on the same document.
  Window > Tile Vertically. Useful for one zoomed-out and one zoomed-in view.
- **Fly mode**: View > Navigation Mode > Fly. Walk through an assembly. Examine mode is normal.
- **Lighting and depth effect**: View > Lighting, View > Depth Effect. Depth Effect lets you
  set near/far clipping planes, a quick way to see inside without sectioning.
- **Perspective vs parallel**: View > Render Style > Perspective. Parallel is better for
  checking alignment.

## Spec tree navigation and 3D are separate

Clicking the tree's vertical line, or pressing Shift+F3, puts the viewer in "tree mode":
zoom and pan now move the tree, not the geometry. If your model stopped responding to the
mouse and the tree is moving instead, you are in tree mode. Click the line or Shift+F3 again.
F3 hides and shows the tree entirely.
