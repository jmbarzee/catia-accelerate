# catia-accelerate

Quick references and an AI-ready workspace for engineers who are new to CATIA V5
and need to be productive inside a large-assembly environment this week, not next quarter.

This is **not a tutorial**. Every page is a card you read in under two minutes while
CATIA is open on the other monitor.

## Five-minute start

1. Read [quickref/00-first-hour.md](quickref/00-first-hour.md).
2. Read [quickref/03-large-assemblies.md](quickref/03-large-assemblies.md). This is the one that
   stops CATIA from eating your afternoon.
3. Keep [quickref/08-shortcuts.md](quickref/08-shortcuts.md) open.
4. When you want CATIA to do something repetitive, open [macros/README.md](macros/README.md).

## Hook it up to *your* CATIA (recommended)

The public web has almost no CATIA automation documentation. The real reference ships
inside your CATIA install, and the macros and standards that matter live on your company's
shares. `tools/hookup.py` indexes those into `local/` so an AI assistant working in this repo
knows your actual environment instead of generic CATIA.

```bash
python tools/hookup.py init      # creates local/hookup.json, auto-discovers CATIA on Windows
# edit local/hookup.json: add your macro shares, standards folders, template libraries
python tools/hookup.py index     # writes local/index/*.md and index.json
python tools/extract_chm.py      # turns V5Automation.chm into searchable text in local/chm/
python tools/hookup.py doctor    # tells you what is still missing
```

`local/` is git-ignored. It only ever contains paths and indexes, never copies of your models.
See [local/README.md](local/README.md).

## Layout

| Folder | What it is |
|---|---|
| `quickref/` | One card per task. Navigation, spec tree, large assemblies, measuring, settings. |
| `macros/` | How to run macros, skeleton templates, small working examples, and your own `scratch/`. |
| `docs-index/` | A curated map of the V5 automation object model and links to the few good public sources. |
| `company/` | Fill-in templates for conventions, PLM workflow, and environment facts specific to your company. Commit these in your internal fork. |
| `local/` | Per-user, git-ignored. Config plus generated indexes of your macros, docs, templates, and the extracted API reference. |
| `ai/` | Starter prompts and guidance for using an AI assistant with this repo. |
| `tools/` | The hookup indexer and CHM extractor. Python 3, standard library only. |

## Assumptions

- CATIA **V5** (V5-6R20xx). The navigation cards mostly carry over to 3DEXPERIENCE but the
  large-assembly and automation story differs there. See [docs-index/links.md](docs-index/links.md).
- Macros are CATScript or CATVBA. Python via `pycatia` is mentioned where it helps.
- Nothing here modifies CATIA settings or files. Every settings change is written out as a
  menu path for you to apply yourself.
