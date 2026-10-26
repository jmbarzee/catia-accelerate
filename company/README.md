# company/

Facts about *your* company's CATIA setup that no public source knows. Fill these in and
commit them in your internal fork. The AI assistant reads them (see `CLAUDE.md`) before
answering, so an unfilled template means generic answers.

| File | Fill in |
|---|---|
| `environment.md` | CATIA release, licensed workbenches, where it is installed, how settings are deployed |
| `conventions.md` | Naming, units, part numbering, where macros may live, standard views, color codes |
| `plm-workflow.md` | How files are checked out, saved, released. The thing that breaks new hires |
| `people.md` | Who to ask. CATIA admin, macro owners, PLM support |
| `known-issues.md` | Things that are broken or weird in your environment and the workaround |

Keep each under a page. The hookup indexer (`tools/hookup.py`) covers the *files*; these
cover the *tribal knowledge*.
