# local/

Per-user, git-ignored. Holds the configuration and generated indexes that connect this repo
to *your* CATIA install and *your company's* files. Nothing under here is copied model data:
indexes hold paths, names, and short summaries only.

## Set up

```bash
python tools/hookup.py init
```

Creates `local/hookup.json`. On Windows it auto-discovers the CATIA install and the
automation CHM. Then edit the file and add the roots you want indexed:

```json
{
  "catia": {
    "install_path": "C:\\Program Files\\Dassault Systemes\\B30",
    "release": "B30",
    "automation_chm": "C:\\Program Files\\Dassault Systemes\\B30\\win_b64\\code\\bin\\V5Automation.chm",
    "user_settings_path": "C:\\Users\\me\\AppData\\Roaming\\DassaultSystemes\\CATSettings"
  },
  "roots": {
    "macros":    ["\\\\server\\share\\catia\\macros", "C:\\Users\\me\\Documents\\catia-macros"],
    "docs":      ["\\\\server\\share\\catia\\standards"],
    "templates": ["\\\\server\\share\\catia\\templates", "\\\\server\\share\\catia\\catalogs"],
    "settings":  ["C:\\Users\\me\\AppData\\Roaming\\DassaultSystemes\\CATSettings"]
  },
  "exclude": ["**/.git/**", "**/archive/**", "**/old/**"]
}
```

Roots can be local paths or UNC shares. Read access is all that is needed.

```bash
python tools/hookup.py index     # writes local/index/*.md and index.json
python tools/extract_chm.py      # writes local/chm/ (needs hh.exe on Windows, or 7z / extract_chmLib elsewhere)
python tools/hookup.py doctor    # checks everything
```

Re-run `index` whenever the shares change. It is fast (it reads headers, not whole files).

## What gets generated

| File | Contents |
|---|---|
| `index/INDEX.md` | Summary: release, install path, counts per category, timestamp. Read this first. |
| `index/environment.md` | CATIA release, paths, environment variables, settings files found |
| `index/macros.md` | Every macro found: language, entry points, tags, header comment, path |
| `index/docs.md` | Standards, guides, and other documents with titles |
| `index/templates.md` | Part, product, drawing templates, catalogs, materials |
| `index/settings.md` | CATSettings files present (names tell you which option groups are customized) |
| `index/index.json` | Everything above, machine-readable |
| `chm/INDEX.md` and `chm/text/` | The official automation reference as searchable text |

## Sharing

`local/` is per user because paths differ per machine. If your company wants a shared
baseline, commit a `local/hookup.example.json` with the UNC roots and tell people to copy it.
