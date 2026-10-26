# Large assemblies: zooming in and out without waiting

The mental model: CATIA can hold a part in two ways.

| Mode | What is loaded | Can you edit it | Memory and open time |
|---|---|---|---|
| **Visualization Mode** | A tessellated shell (CGR) from the cache | No | Tiny |
| **Design Mode** | The full `.CATPart` with feature history | Yes | Large |

A 5,000-part product in Visualization Mode opens in seconds. The same product in Design Mode
can take ten minutes and more memory than the workstation has. Everything below is about
staying in Visualization Mode by default and dropping into Design Mode for exactly the parts
you touch.

## Turn on the cache (do this once)

Tools > Options > Infrastructure > Product Structure > **Cache Management**:

- Check **Work with the cache system**.
- Set a cache location on a fast local disk. Note: the path must not be exactly 8 characters
  long (a known CATIA quirk).
- Set a maximum size (tens of GB is normal for large-assembly work).
- Check **Check timestamps** so stale CGRs get regenerated.

Restart CATIA. Products now open in Visualization Mode. Ask whether your company already
sets this through a CATSettings deployment (`company/environment.md`); if so, do not fight it.

Also: Tools > Options > Infrastructure > Product Structure > Product Visualization >
check **Do not activate default shapes on open** to avoid loading representations you
did not ask for.

## Zoom in: get one part into Design Mode

Right-click the part or product in the tree > **Representations > Design Mode**.
Only that branch loads. Edit it. When done, right-click > Representations >
**Visualization Mode** to release it. You can do this on a sub-product to load one branch.

Edit > Representations has the same commands for the active selection.

## Zoom out: stop loading what you do not need

- **Deactivate Node**: right-click a product > `<name> object` > Deactivate Node. The branch
  is unloaded and drawn as an empty node. Activate Node brings it back. Deactivated nodes
  are saved with the product, so your colleagues will see them deactivated too. Check
  `company/conventions.md` before saving with deactivated nodes.
- **Selective Load**: Tools > Options > Infrastructure > Product Structure > Product Structure
  > uncheck **Load referenced documents**. Then opening a product loads only the structure,
  no geometry. Right-click any node > Selective Load (or Edit > Links > Load) to pull in
  the branches you want. Best way to open a giant top-level product for the first time.
- **Open a sub-assembly on its own**: File > Open the sub-product's `.CATProduct` directly.
  Constraints to parts outside it will show as broken; that is fine for read-only work.

## Display settings that keep rotation smooth

Tools > Options > General > Display > **Performance**:

- 3D Accuracy: raise the proportional value (0.2 or higher). Coarser tessellation, faster.
- Level of detail: raise "while moving". Pixel culling: raise "while moving". Small parts
  vanish during rotation and reappear when you stop.
- Occlusion culling: try it on and off. It helps on some hardware and hurts on others.

Tools > Options > General > Display > **Visualization**:

- Turn off anti-aliasing and stereo. Turn off "Display two sides" unless you need it.
- Reduce "Graduated color background" to a flat color.

View > Render Style > **Wireframe** when all else fails.

## Find things without expanding the tree

Edit > Search (Ctrl+F). See [02-spec-tree](02-spec-tree.md). Searching works on Visualization
Mode nodes because it reads the product structure, not the geometry.

## Section instead of hiding

Start > Digital Mockup > DMU Space Analysis > **Sectioning**. A plane you drag through the
model shows the cut. Works on CGR data, so it does not force Design Mode. Faster than hiding
hundreds of parts to see inside.

## Measure without Design Mode

Measure Between and Measure Item work on CGR geometry with reduced accuracy. If a measurement
dialog says it needs exact geometry, that is your cue to put only that part in Design Mode.

## Save and autosave

Tools > Options > General > General > **Automatic backup**: lengthen the interval or turn it
off on large assemblies. A 30-minute autosave of a 5,000-part product freezes CATIA for a
while, right when you are mid-command. Save manually with File > Save Management instead.

## Do not

- Expand All Levels on the top product.
- Ctrl+A in the viewer on a huge product and then try to change color or properties.
- Open a product with "Load referenced documents" on and the cache off. That is the
  ten-minute open.
- Leave dozens of parts in Design Mode "just in case".

## Automate it

`macros/examples/SetVisualizationMode.CATScript` releases every loaded part.
`macros/examples/ListDesignModeParts.CATScript` tells you what is currently heavy.
