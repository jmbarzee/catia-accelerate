#!/usr/bin/env python3
"""hookup.py: connect this repo to one user's / one company's CATIA environment.

Usage:
    python tools/hookup.py init            create local/hookup.json (auto-discovers CATIA on Windows)
    python tools/hookup.py index           scan configured roots, write local/index/*.md and index.json
    python tools/hookup.py doctor          report what is configured, found, and missing
    python tools/hookup.py index --quiet   same, less output

Standard library only. Read-only against everything outside local/.
Indexes hold paths, names, signatures, and short summaries. They never copy file contents.
"""
from __future__ import annotations

import datetime as _dt
import fnmatch
import glob
import json
import os
import re
import sys
from pathlib import Path, PurePath

REPO = Path(__file__).resolve().parent.parent
LOCAL = REPO / "local"
CONFIG = LOCAL / "hookup.json"
INDEX_DIR = LOCAL / "index"
CHM_DIR = LOCAL / "chm"

MACRO_EXT = {
    ".catscript": "CATScript",
    ".catvbs": "CATScript (vbs)",
    ".catvba": "CATVBA project (binary)",
    ".bas": "VBA module",
    ".cls": "VBA class",
    ".frm": "VBA form",
    ".vbs": "VBScript",
    ".vb": "VB.NET",
    ".cs": "C#",
    ".py": "Python",
    ".ps1": "PowerShell",
}
DOC_EXT = {".md", ".txt", ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".html", ".htm", ".chm", ".rtf"}
MODEL_EXT = {
    ".catpart": "Part",
    ".catproduct": "Product",
    ".catdrawing": "Drawing",
    ".catshape": "Shape",
    ".cgr": "CGR",
    ".catalog": "Catalog",
    ".catmaterial": "Material library",
    ".catfct": "Feature dictionary",
    ".catprocess": "Process",
    ".catanalysis": "Analysis",
    ".model": "V4 model",
    ".3dxml": "3DXML",
    ".stp": "STEP",
    ".step": "STEP",
    ".igs": "IGES",
    ".iges": "IGES",
}
SETTINGS_EXT = {".catsettings"}

DEFAULT_CONFIG = {
    "_comment": "Edit roots. Backslashes must be doubled in JSON. UNC paths are fine.",
    "catia": {
        "install_path": "",
        "release": "",
        "automation_chm": "",
        "user_settings_path": "",
        "env_dir": "",
    },
    "roots": {"macros": [], "docs": [], "templates": [], "settings": []},
    "exclude": ["**/.git/**", "**/archive/**", "**/~$*"],
    "max_files_per_root": 20000,
}

# Regexes for macro parsing
SUB_RE = re.compile(r"^\s*(?:Public\s+|Private\s+)?(Sub|Function)\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", re.I | re.M)
LANG_RE = re.compile(r"^\s*Language\s*=\s*\"?(\w+)\"?", re.I | re.M)
PY_DEF_RE = re.compile(r"^\s*def\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", re.M)
PS_FN_RE = re.compile(r"^\s*function\s+([A-Za-z_][\w-]*)", re.I | re.M)

# Object-model tokens -> tag. Order matters only for readability.
TAG_HINTS = [
    ("Assembly", re.compile(r"ProductDocument|\.Products\b|ReferenceProduct|ApplyWorkMode|Connections", re.I)),
    ("Part", re.compile(r"PartDocument|ShapeFactory|\.Bodies\b|PartBody|Sketches", re.I)),
    ("Surfaces", re.compile(r"HybridShapeFactory|HybridBodies", re.I)),
    ("Drafting", re.compile(r"DrawingDocument|DrawingSheet|DrawingView", re.I)),
    ("Selection", re.compile(r"\.Selection\b|SelectElement|\.Search\s*\(|\.Search\s+\"", re.I)),
    ("Measure", re.compile(r"SPAWorkbench|GetMeasurable|Inertia", re.I)),
    ("Parameters", re.compile(r"\.Parameters\b|\.Relations\b|CreateFormula|DesignTable", re.I)),
    ("Export", re.compile(r"ExportData|CaptureToFile|FileSystemObject|CreateTextFile|\.SaveAs", re.I)),
    ("Modifies model", re.compile(r"AddNew|\.Delete\b|\.Remove\b|SetRealColor|Part\.Update|\.Value\s*=", re.I)),
    ("Excel", re.compile(r"Excel\.Application", re.I)),
    ("UI", re.compile(r"InputBox|UserForm|\.Show\b", re.I)),
]


# ----------------------------------------------------------------------------- helpers

def log(msg: str, quiet: bool = False) -> None:
    if not quiet:
        print(msg)


def load_config() -> dict:
    if not CONFIG.exists():
        sys.exit(f"No config at {CONFIG}. Run: python tools/hookup.py init")
    with CONFIG.open(encoding="utf-8") as fh:
        cfg = json.load(fh)
    # Fill in missing keys so later code can assume shape.
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v if not isinstance(v, dict) else dict(v))
    for k in DEFAULT_CONFIG["roots"]:
        cfg["roots"].setdefault(k, [])
    for k in DEFAULT_CONFIG["catia"]:
        cfg["catia"].setdefault(k, "")
    return cfg


def excluded(path: Path, patterns: list[str]) -> bool:
    s = PurePath(path).as_posix()
    for pat in patterns:
        if fnmatch.fnmatch(s, pat) or fnmatch.fnmatch(path.name, pat):
            return True
    return False


def iter_files(root: str, patterns: list[str], limit: int):
    """Yield files under root, honoring exclude patterns and a hard cap."""
    rp = Path(root)
    if not rp.exists():
        return
    n = 0
    for dirpath, dirnames, filenames in os.walk(rp, followlinks=False):
        d = Path(dirpath)
        dirnames[:] = [x for x in dirnames if not excluded(d / x, patterns)]
        for fn in filenames:
            p = d / fn
            if excluded(p, patterns):
                continue
            yield p
            n += 1
            if n >= limit:
                return


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def rel_or_abs(p: Path) -> str:
    return str(p)


def safe_stat(p: Path):
    try:
        st = p.stat()
        return st.st_size, _dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d")
    except OSError:
        return 0, ""


def read_head(p: Path, max_bytes: int = 65536) -> str:
    try:
        with p.open("r", encoding="utf-8", errors="replace") as fh:
            return fh.read(max_bytes)
    except OSError:
        return ""


def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ").strip()


# ----------------------------------------------------------------------------- discovery

def discover() -> dict:
    """Best-effort auto-discovery. Only reads env vars and well-known paths."""
    found = {"install_path": "", "release": "", "automation_chm": "", "user_settings_path": "", "env_dir": ""}
    env = os.environ
    if env.get("CATInstallPath"):
        found["install_path"] = env["CATInstallPath"]
    if env.get("CATUserSettingPath"):
        found["user_settings_path"] = env["CATUserSettingPath"]
    if env.get("CATEnv"):
        found["env_dir"] = env["CATEnv"]

    candidates: list[str] = []
    if os.name == "nt":
        for base in (env.get("ProgramFiles", r"C:\Program Files"), env.get("ProgramFiles(x86)", r"C:\Program Files (x86)")):
            candidates += glob.glob(os.path.join(base, "Dassault Systemes", "*", "win_b64", "code", "bin", "V5Automation.chm"))
            candidates += glob.glob(os.path.join(base, "Dassault Systemes", "*", "intel_a", "code", "bin", "V5Automation.chm"))
        if found["install_path"]:
            candidates += glob.glob(os.path.join(found["install_path"], "code", "bin", "V5Automation.chm"))
            candidates += glob.glob(os.path.join(found["install_path"], "win_b64", "code", "bin", "V5Automation.chm"))
        appdata = env.get("APPDATA", "")
        if appdata and not found["user_settings_path"]:
            p = os.path.join(appdata, "DassaultSystemes", "CATSettings")
            if os.path.isdir(p):
                found["user_settings_path"] = p
        if appdata and not found["env_dir"]:
            p = os.path.join(appdata, "DassaultSystemes", "CATEnv")
            if os.path.isdir(p):
                found["env_dir"] = p
    if candidates:
        chm = sorted(set(candidates))[-1]  # highest release sorts last
        found["automation_chm"] = chm
        # .../Dassault Systemes/B30/win_b64/code/bin/V5Automation.chm -> install B30, release B30
        parts = Path(chm).parts
        try:
            i = parts.index("Dassault Systemes")
            found["release"] = parts[i + 1]
            if not found["install_path"]:
                found["install_path"] = str(Path(*parts[: i + 2]))
        except (ValueError, IndexError):
            pass
    return found


def cmd_init(args: list[str]) -> None:
    LOCAL.mkdir(exist_ok=True)
    INDEX_DIR.mkdir(exist_ok=True)
    if CONFIG.exists() and "--force" not in args:
        print(f"{CONFIG} already exists. Use --force to overwrite.")
        return
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    disc = discover()
    cfg["catia"].update({k: v for k, v in disc.items() if v})
    if disc["user_settings_path"]:
        cfg["roots"]["settings"].append(disc["user_settings_path"])
    with CONFIG.open("w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)
    print(f"Wrote {CONFIG}")
    for k, v in disc.items():
        print(f"  {k:20} {v or '(not found)'}")
    print("\nNext: edit the roots in that file, then run: python tools/hookup.py index")


# ----------------------------------------------------------------------------- parsing

def header_comment(text: str, markers: tuple[str, ...]) -> str:
    """Leading comment block, markers stripped, up to 12 lines."""
    out: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            if out:
                break
            continue
        low = s.lower()
        if low.startswith("language=") or low.startswith("option explicit") or low.startswith("attribute vb_name"):
            continue
        hit = None
        for m in markers:
            if low.startswith(m.lower()):
                hit = m
                break
        if hit is None:
            break
        body = s[len(hit):].strip()
        # Skip pure decoration lines
        if body and set(body) <= set("-=*#'"):
            continue
        out.append(body)
        if len(out) >= 12:
            break
    return " ".join(out).strip()


def strip_filename(summary: str, name: str) -> str:
    """Header comments usually start with the file's own name. Drop it."""
    if summary.lower().startswith(name.lower()):
        summary = summary[len(name):].lstrip(" :-")
    return summary


def parse_macro(p: Path, text: str) -> dict:
    ext = p.suffix.lower()
    rec: dict = {"language": MACRO_EXT.get(ext, ext), "entry_points": [], "routines": [], "summary": "", "tags": []}
    if ext == ".catvba":
        rec["summary"] = "Binary CATVBA project. Open in CATIA (Alt+F11) to inspect, or export modules to .bas."
        return rec
    if ext == ".py":
        rec["routines"] = [f"{m.group(1)}({m.group(2).strip()})" for m in PY_DEF_RE.finditer(text)]
        rec["entry_points"] = [r for r in rec["routines"] if r.startswith("main(")]
        rec["summary"] = header_comment(text, ("#",)) or docstring(text)
        if "pycatia" in text:
            rec["tags"].append("pycatia")
    elif ext == ".ps1":
        rec["routines"] = [m.group(1) for m in PS_FN_RE.finditer(text)]
        rec["summary"] = header_comment(text, ("#",))
    else:
        m = LANG_RE.search(text)
        if m:
            rec["language"] = f"{rec['language']} [{m.group(1)}]"
        for sm in SUB_RE.finditer(text):
            sig = f"{sm.group(2)}({sm.group(3).strip()})"
            rec["routines"].append(sig)
            if sm.group(2).lower() == "catmain":
                rec["entry_points"].append(sig)
        rec["summary"] = header_comment(text, ("'", "REM "))
    rec["summary"] = strip_filename(rec["summary"], p.name)
    for tag, rx in TAG_HINTS:
        if rx.search(text):
            rec["tags"].append(tag)
    return rec


def docstring(text: str) -> str:
    m = re.search(r'^\s*[rub]*"""(.*?)"""', text, re.S | re.M)
    if not m:
        return ""
    return " ".join(m.group(1).strip().splitlines()[:6]).strip()


def doc_title(p: Path, text: str) -> str:
    if p.suffix.lower() in (".md", ".txt", ".rtf"):
        for line in text.splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                return s.lstrip("#").strip()[:120]
            return s[:120]
    if p.suffix.lower() in (".html", ".htm"):
        m = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
        if m:
            return re.sub(r"\s+", " ", m.group(1)).strip()[:120]
    return p.stem


# ----------------------------------------------------------------------------- indexing

def classify(p: Path):
    ext = p.suffix.lower()
    if ext in MACRO_EXT:
        return "macros"
    if ext in MODEL_EXT:
        return "templates"
    if ext in SETTINGS_EXT:
        return "settings"
    if ext in DOC_EXT:
        return "docs"
    return None


def scan(cfg: dict, quiet: bool) -> dict:
    patterns = cfg.get("exclude", [])
    limit = int(cfg.get("max_files_per_root", 20000))
    result = {"macros": [], "docs": [], "templates": [], "settings": [], "roots": {}, "missing_roots": []}
    for category, roots in cfg["roots"].items():
        for root in roots:
            if not Path(root).exists():
                result["missing_roots"].append((category, root))
                log(f"  missing root ({category}): {root}", quiet)
                continue
            count = 0
            for p in iter_files(root, patterns, limit):
                kind = classify(p)
                if kind is None:
                    continue
                # A root declared as "macros" may still contain docs; keep each file in the
                # category its extension says, but remember which root it came from.
                size, mtime = safe_stat(p)
                rec = {"name": p.name, "path": str(p), "root": root, "root_category": category, "size": size, "mtime": mtime}
                if kind == "macros":
                    rec.update(parse_macro(p, read_head(p)))
                elif kind == "docs":
                    rec["title"] = doc_title(p, read_head(p, 8192))
                    rec["kind"] = p.suffix.lower().lstrip(".")
                elif kind == "templates":
                    rec["kind"] = MODEL_EXT[p.suffix.lower()]
                elif kind == "settings":
                    rec["group"] = p.stem
                result[kind].append(rec)
                count += 1
            result["roots"][root] = count
            log(f"  {category:10} {root}  ({count} indexed)", quiet)
    for k in ("macros", "docs", "templates", "settings"):
        result[k].sort(key=lambda r: (r["root"], r["path"].lower()))
    return result


def environment(cfg: dict) -> dict:
    c = cfg["catia"]
    env_vars = {k: os.environ.get(k, "") for k in ("CATInstallPath", "CATEnv", "CATUserSettingPath", "CATReport", "CATTemp", "CATReferenceSettingPath")}
    chm = c.get("automation_chm", "")
    return {
        "release": c.get("release", ""),
        "install_path": c.get("install_path", ""),
        "install_exists": bool(c.get("install_path")) and Path(c["install_path"]).exists(),
        "automation_chm": chm,
        "chm_exists": bool(chm) and Path(chm).exists(),
        "chm_extracted": (CHM_DIR / "INDEX.md").exists(),
        "user_settings_path": c.get("user_settings_path", ""),
        "env_dir": c.get("env_dir", ""),
        "env_vars": {k: v for k, v in env_vars.items() if v},
        "host_os": f"{os.name} / {sys.platform}",
        "python": sys.version.split()[0],
    }


def write_index(cfg: dict, data: dict, quiet: bool) -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    env = environment(cfg)
    gen = f"Generated {now} by `tools/hookup.py index`. Do not edit; re-run to refresh.\n\n"

    # INDEX.md
    lines = [f"# Local index\n\n{gen}"]
    lines.append("## Environment\n")
    lines.append(f"- CATIA release: **{env['release'] or 'unknown'}**")
    lines.append(f"- Install path: `{env['install_path'] or 'unknown'}`" + ("" if env["install_exists"] or not env["install_path"] else " (not found)"))
    chm_state = "extracted to `local/chm/`" if env["chm_extracted"] else ("found, not extracted (run `python tools/extract_chm.py`)" if env["chm_exists"] else "not found")
    lines.append(f"- Automation reference (V5Automation.chm): {chm_state}")
    lines.append(f"- Details: [environment.md](environment.md)\n")
    lines.append("## Counts\n")
    lines.append("| Category | Files | File |\n|---|---|---|")
    for k, fn in (("macros", "macros.md"), ("docs", "docs.md"), ("templates", "templates.md"), ("settings", "settings.md")):
        lines.append(f"| {k} | {len(data[k])} | [{fn}]({fn}) |")
    lines.append("\n## Roots\n")
    for root, n in data["roots"].items():
        lines.append(f"- `{root}` ({n} files)")
    for cat, root in data["missing_roots"]:
        lines.append(f"- `{root}` ({cat}) **missing or unreachable**")
    if not data["roots"] and not data["missing_roots"]:
        lines.append("- No roots configured. Edit `local/hookup.json`.")
    lines.append("\n## For the assistant\n")
    lines.append("- Prefer an existing macro in macros.md over writing a new one.")
    lines.append("- Answer for the release above. Members and menu paths differ between releases.")
    lines.append("- Company conventions live in `company/`, not here.")
    (INDEX_DIR / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # environment.md
    e = [f"# Environment\n\n{gen}"]
    for k in ("release", "install_path", "automation_chm", "user_settings_path", "env_dir", "host_os", "python"):
        e.append(f"- {k}: `{env[k] or ''}`")
    e.append(f"- chm_exists: {env['chm_exists']}")
    e.append(f"- chm_extracted: {env['chm_extracted']}")
    if env["env_vars"]:
        e.append("\n## CATIA environment variables (current shell)\n")
        for k, v in env["env_vars"].items():
            e.append(f"- `{k}` = `{v}`")
    else:
        e.append("\nNo CATIA environment variables in the current shell. Normal when run outside a CATIA environment shortcut.")
    if data["settings"]:
        e.append("\n## CATSettings files present\n")
        e.append("Each file name is an option group that has been customized. See [settings.md](settings.md).")
    (INDEX_DIR / "environment.md").write_text("\n".join(e) + "\n", encoding="utf-8")

    # macros.md
    m = [f"# Macros\n\n{gen}"]
    if not data["macros"]:
        m.append("No macros indexed. Add macro folders to `roots.macros` in `local/hookup.json`.")
    else:
        m.append("| Name | Language | Entry | Tags | Summary | Path |\n|---|---|---|---|---|---|")
        for r in data["macros"]:
            entry = "CATMain" if r["entry_points"] else ""
            m.append(f"| {md_escape(r['name'])} | {md_escape(r['language'])} | {entry} | {', '.join(r['tags'])} | {md_escape(r['summary'][:160])} | `{r['path']}` |")
        m.append("\n## Details\n")
        for r in data["macros"]:
            m.append(f"### {r['name']}\n")
            m.append(f"- Path: `{r['path']}`")
            m.append(f"- Language: {r['language']}  Size: {human(r['size'])}  Modified: {r['mtime']}")
            if r["tags"]:
                m.append(f"- Tags: {', '.join(r['tags'])}")
            if r["summary"]:
                m.append(f"- Summary: {r['summary']}")
            if r["routines"]:
                m.append("- Routines:")
                for s in r["routines"][:40]:
                    m.append(f"  - `{s}`")
                if len(r["routines"]) > 40:
                    m.append(f"  - ... {len(r['routines']) - 40} more")
            m.append("")
    (INDEX_DIR / "macros.md").write_text("\n".join(m) + "\n", encoding="utf-8")

    # docs.md
    d = [f"# Documents\n\n{gen}"]
    if not data["docs"]:
        d.append("No documents indexed. Add standards or guide folders to `roots.docs` in `local/hookup.json`.")
    else:
        d.append("| Title | Type | Modified | Path |\n|---|---|---|---|")
        for r in data["docs"]:
            d.append(f"| {md_escape(r['title'])} | {r['kind']} | {r['mtime']} | `{r['path']}` |")
    (INDEX_DIR / "docs.md").write_text("\n".join(d) + "\n", encoding="utf-8")

    # templates.md
    t = [f"# Templates, catalogs, and model libraries\n\n{gen}"]
    if not data["templates"]:
        t.append("No templates indexed. Add template or catalog folders to `roots.templates` in `local/hookup.json`.")
    else:
        t.append("| Name | Kind | Size | Modified | Path |\n|---|---|---|---|---|")
        for r in data["templates"]:
            t.append(f"| {md_escape(r['name'])} | {r['kind']} | {human(r['size'])} | {r['mtime']} | `{r['path']}` |")
    (INDEX_DIR / "templates.md").write_text("\n".join(t) + "\n", encoding="utf-8")

    # settings.md
    s = [f"# CATSettings\n\n{gen}"]
    if not data["settings"]:
        s.append("No settings files indexed. Add the CATSettings folder to `roots.settings` in `local/hookup.json`.")
    else:
        s.append("Binary files; the name says which option group is customized. Delete one (CATIA closed) to reset that group.\n")
        s.append("| Group | Size | Modified | Path |\n|---|---|---|---|")
        for r in data["settings"]:
            s.append(f"| {r['group']} | {human(r['size'])} | {r['mtime']} | `{r['path']}` |")
    (INDEX_DIR / "settings.md").write_text("\n".join(s) + "\n", encoding="utf-8")

    # index.json
    payload = {"generated": now, "environment": env, **{k: data[k] for k in ("macros", "docs", "templates", "settings")}, "roots": data["roots"], "missing_roots": data["missing_roots"]}
    (INDEX_DIR / "index.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    log(f"\nWrote {INDEX_DIR}/INDEX.md, environment.md, macros.md, docs.md, templates.md, settings.md, index.json", quiet)
    log(f"  macros {len(data['macros'])}  docs {len(data['docs'])}  templates {len(data['templates'])}  settings {len(data['settings'])}", quiet)


def cmd_index(args: list[str]) -> None:
    quiet = "--quiet" in args
    cfg = load_config()
    log("Scanning roots...", quiet)
    data = scan(cfg, quiet)
    write_index(cfg, data, quiet)


# ----------------------------------------------------------------------------- doctor

def cmd_doctor(_args: list[str]) -> None:
    ok = True

    def check(cond: bool, good: str, bad: str) -> None:
        nonlocal ok
        print(("  [ok]   " if cond else "  [miss] ") + (good if cond else bad))
        ok = ok and cond

    print(f"Python {sys.version.split()[0]} on {sys.platform}")
    check(sys.version_info >= (3, 8), "Python 3.8+", "Python 3.8+ required")
    if not CONFIG.exists():
        check(False, "", f"{CONFIG} missing. Run: python tools/hookup.py init")
        return
    cfg = load_config()
    c = cfg["catia"]
    check(bool(c["release"]), f"release {c['release']}", "catia.release not set in hookup.json")
    check(bool(c["install_path"]) and Path(c["install_path"]).exists(), f"install {c['install_path']}", f"catia.install_path missing or not found: {c['install_path'] or '(empty)'}")
    chm = c["automation_chm"]
    check(bool(chm) and Path(chm).exists(), f"V5Automation.chm at {chm}", "V5Automation.chm not found. Look in <install>\\win_b64\\code\\bin\\ and set catia.automation_chm")
    check((CHM_DIR / "INDEX.md").exists(), "CHM extracted to local/chm/", "CHM not extracted. Run: python tools/extract_chm.py")
    any_root = False
    for cat, roots in cfg["roots"].items():
        for r in roots:
            any_root = True
            check(Path(r).exists(), f"{cat} root {r}", f"{cat} root unreachable: {r}")
    check(any_root, "at least one root configured", "no roots configured in hookup.json")
    check((INDEX_DIR / "INDEX.md").exists(), "index generated", "index not generated. Run: python tools/hookup.py index")
    for name in ("environment.md", "conventions.md", "plm-workflow.md"):
        p = REPO / "company" / name
        filled = p.exists() and "<!-- Fill in" not in p.read_text(encoding="utf-8", errors="replace")
        check(filled, f"company/{name} filled in", f"company/{name} still a template")
    gi = (REPO / ".gitignore").read_text(encoding="utf-8", errors="replace") if (REPO / ".gitignore").exists() else ""
    check("local/*" in gi, "local/ is git-ignored", ".gitignore does not ignore local/")
    print("\nAll good." if ok else "\nSome items missing. Nothing above blocks using the quickref cards.")


# ----------------------------------------------------------------------------- main

def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        return
    cmd, args = argv[1], argv[2:]
    {"init": cmd_init, "index": cmd_index, "doctor": cmd_doctor}.get(cmd, lambda _a: sys.exit(f"Unknown command: {cmd}\n{__doc__}"))(args)


if __name__ == "__main__":
    main(sys.argv)
