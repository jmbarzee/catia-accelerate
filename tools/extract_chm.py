#!/usr/bin/env python3
"""extract_chm.py: turn V5Automation.chm into searchable text under local/chm/.

Usage:
    python tools/extract_chm.py                      uses catia.automation_chm from local/hookup.json
    python tools/extract_chm.py path\\to\\V5Automation.chm
    python tools/extract_chm.py --out local/chm      output directory (default)
    python tools/extract_chm.py --limit 200          only convert the first N pages (for a quick test)

Decompiles with the first available tool:
    Windows:   hh.exe -decompile   (ships with Windows)
    anywhere:  7z x                 (7-Zip)         or   extract_chmLib   (chmlib)
Then converts every HTML page to plain text (headings kept) and writes local/chm/INDEX.md.

The CHM is Dassault's copyrighted documentation. The extracted text stays in local/,
which is git-ignored. Do not commit it or copy it into the repo.
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCAL = REPO / "local"
CONFIG = LOCAL / "hookup.json"
DEFAULT_OUT = LOCAL / "chm"


class TextExtractor(HTMLParser):
    """HTML -> plain text. Headings become markdown headings, tables become rows, code kept."""

    BLOCK = {"p", "div", "br", "tr", "li", "pre", "h1", "h2", "h3", "h4", "h5", "h6", "table", "ul", "ol", "dt", "dd", "hr"}
    SKIP = {"script", "style", "head"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title = ""
        self._in_title = False
        self._skip = 0
        self._heading: str | None = None
        self._in_pre = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
            self._heading = tag
        elif tag == "pre":
            self._in_pre = True
            self.parts.append("\n\n```\n")
        elif tag in ("td", "th"):
            self.parts.append(" | ")
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip = max(0, self._skip - 1)
        elif tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.parts.append("\n")
            self._heading = None
        elif tag == "pre":
            self._in_pre = False
            self.parts.append("\n```\n")
        elif tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self.title += data
            return
        if self._skip:
            return
        self.parts.append(data if self._in_pre else re.sub(r"[ \t\r\f\v]+", " ", data))

    def text(self) -> str:
        t = "".join(self.parts)
        t = re.sub(r"\n[ \t]+", "\n", t)
        t = re.sub(r"\n{3,}", "\n\n", t)
        return t.strip() + "\n"


def find_chm(argv: list[str]) -> Path | None:
    for a in argv[1:]:
        if a.lower().endswith(".chm"):
            return Path(a)
    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        p = cfg.get("catia", {}).get("automation_chm", "")
        if p:
            return Path(p)
    return None


def opt(argv: list[str], name: str, default):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return argv[i + 1]
    return default


def decompile(chm: Path, raw: Path) -> str:
    raw.mkdir(parents=True, exist_ok=True)
    attempts = []
    if os.name == "nt":
        hh = shutil.which("hh.exe") or shutil.which("hh") or r"C:\Windows\hh.exe"
        attempts.append(("hh.exe", [hh, "-decompile", str(raw), str(chm)]))
    for exe in ("7z", "7za", "7zz"):
        if shutil.which(exe):
            attempts.append((exe, [exe, "x", "-y", f"-o{raw}", str(chm)]))
            break
    if shutil.which("extract_chmLib"):
        attempts.append(("extract_chmLib", ["extract_chmLib", str(chm), str(raw)]))
    if not attempts:
        sys.exit("No decompiler found. Install 7-Zip (7z on PATH) or, on Windows, make sure hh.exe exists. "
                 "On macOS: brew install chmlib (extract_chmLib) or brew install p7zip.")
    for name, cmd in attempts:
        print(f"Decompiling with {name} ...")
        try:
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"  {name} failed: {exc}")
            continue
        pages = list(raw.rglob("*.htm")) + list(raw.rglob("*.html"))
        if pages:
            print(f"  {len(pages)} HTML pages extracted")
            return name
        print(f"  {name} produced no HTML pages")
    sys.exit("Decompilation produced nothing. Check that the .chm path is right and readable.")


def convert(raw: Path, out: Path, limit: int | None) -> list[dict]:
    text_dir = out / "text"
    text_dir.mkdir(parents=True, exist_ok=True)
    pages = sorted(list(raw.rglob("*.htm")) + list(raw.rglob("*.html")))
    if limit:
        pages = pages[:limit]
    records = []
    for i, page in enumerate(pages, 1):
        try:
            src = page.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        ex = TextExtractor()
        try:
            ex.feed(src)
        except Exception:  # noqa: BLE001  malformed HTML in old CHMs
            continue
        rel = page.relative_to(raw)
        dest = text_dir / rel.with_suffix(".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        title = html.unescape(re.sub(r"\s+", " ", ex.title)).strip() or page.stem
        dest.write_text(f"# {title}\n\nSource: {rel.as_posix()}\n\n{ex.text()}", encoding="utf-8")
        records.append({"title": title, "path": dest.relative_to(out).as_posix(), "source": rel.as_posix(), "group": rel.parts[0] if len(rel.parts) > 1 else ""})
        if i % 500 == 0:
            print(f"  converted {i}/{len(pages)}")
    return records


def classify_title(title: str) -> str:
    t = title.lower()
    if re.search(r"\b(interface|object)\b", t) or re.match(r"^[A-Z][A-Za-z0-9]+$", title):
        return "Objects and interfaces"
    if "collection" in t:
        return "Collections"
    if "enum" in t or t.startswith("cat") and " " not in title:
        return "Enumerations"
    if "method" in t or "property" in t:
        return "Members"
    return "Other"


def write_index(out: Path, records: list[dict], chm: Path, tool: str) -> None:
    by_group: dict[str, list[dict]] = {}
    for r in records:
        by_group.setdefault(r["group"] or "(root)", []).append(r)
    lines = ["# V5 automation reference (extracted)\n",
             f"Source: `{chm}`  Pages: {len(records)}  Decompiled with: {tool}\n",
             "Generated by `tools/extract_chm.py`. Text lives in `text/`. Search it with grep or your editor.",
             "This is Dassault's documentation; it stays in git-ignored `local/`.\n",
             "## How to use with an assistant\n",
             "Ask: \"search local/chm/text for `ApplyWorkMode` and show the signature\". The assistant greps",
             "the text files; it does not need to read this index page by page.\n",
             "## Groups\n"]
    for g in sorted(by_group):
        lines.append(f"- `{g}` ({len(by_group[g])} pages)")
    lines.append("\n## Pages\n")
    for g in sorted(by_group):
        lines.append(f"\n### {g}\n")
        for r in sorted(by_group[g], key=lambda x: x["title"].lower()):
            lines.append(f"- [{r['title']}]({r['path']})")
    (out / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "pages.json").write_text(json.dumps(records, indent=1), encoding="utf-8")


def main(argv: list[str]) -> None:
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return
    chm = find_chm(argv)
    if chm is None or not chm.exists():
        sys.exit(f"V5Automation.chm not found ({chm or 'no path given'}). Pass the path, or set catia.automation_chm in local/hookup.json. "
                 "It normally lives in <CATIA install>\\win_b64\\code\\bin\\.")
    out = Path(opt(argv, "--out", DEFAULT_OUT))
    limit = opt(argv, "--limit", None)
    limit = int(limit) if limit else None
    raw = out / "raw"
    if raw.exists() and any(raw.rglob("*.htm*")) and "--force" not in argv:
        print(f"Using already-decompiled pages in {raw} (pass --force to redo).")
        tool = "cached"
    else:
        if raw.exists():
            shutil.rmtree(raw)
        tool = decompile(chm, raw)
    print("Converting to text ...")
    records = convert(raw, out, limit)
    write_index(out, records, chm, tool)
    print(f"Done. {len(records)} pages in {out}/text, index at {out}/INDEX.md")
    print("Tip: the raw/ folder can be deleted once you are happy with the text output.")


if __name__ == "__main__":
    main(sys.argv)
