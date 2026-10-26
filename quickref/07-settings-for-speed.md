# Settings checklist for day one

Everything is under Tools > Options. Apply these yourself. Where your company deploys
CATSettings centrally (see `company/environment.md`), some will be locked (padlock icon).
Settings are stored per user in `%APPDATA%\DassaultSystemes\CATSettings`.

## Must do on a large-assembly site

| Where | Setting | Value |
|---|---|---|
| Infrastructure > Product Structure > Cache Management | Work with the cache system | On |
| same | Cache location | Local SSD path, not 8 characters long |
| same | Maximum size | Large (tens of GB) |
| Infrastructure > Product Structure > Product Visualization | Do not activate default shapes on open | On |
| General > General | Automatic backup | Off or 60+ minutes |
| Mechanical Design > Assembly > Update | Update | Manual |
| General > Display > Performance | 3D accuracy (proportional) | 0.2 or higher |
| same | Level of detail while moving | Raise |
| same | Pixel culling while moving | Raise |

## Worth doing

| Where | Setting | Why |
|---|---|---|
| General > Display > Visualization | Anti-aliasing | Off. Smoother rotation |
| General > Display > Tree Appearance | Show features | Off on assemblies to shorten the tree |
| General > Display > Tree Manipulation | Automatic expand | Off |
| Infrastructure > Part Infrastructure > Display | Parameters, Relations | On, so you can see them |
| Infrastructure > Part Infrastructure > General | Keep link with selected object | Off unless your company does contextual design |
| General > Parameters and Measure > Units | Length | Match `company/conventions.md` |
| General > Macros | Default macro editor and language | CATScript or VBA per `macros/README.md` |
| General > Compatibility | Various | Only if you exchange STEP/IGES |

## Macro libraries

Tools > Macro > Macros > **Macro libraries** is where you register folders of CATScript
files and CATVBA projects. Register `macros/examples` and `macros/scratch` from this repo.
Details in [../macros/README.md](../macros/README.md).

## Back up your settings

Copy `%APPDATA%\DassaultSystemes\CATSettings` somewhere safe once you are happy. Reset a
single corrupted setting by deleting its `.CATSettings` file while CATIA is closed.
`tools/hookup.py index` lists which settings files exist on your machine.
