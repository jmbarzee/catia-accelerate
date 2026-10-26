# ai/

Using an AI assistant with this repo.

- `CLAUDE.md` at the repo root tells Claude Code what to read and how to behave.
  Other assistants: paste its contents as a system or project instruction.
- `prompts.md` has starter prompts that work well once `local/` is populated.
- Run `python tools/hookup.py index` first. Without it the assistant knows generic CATIA,
  not your release, your macros, or your conventions.
- Run `python tools/extract_chm.py` so the assistant can read the official API reference.

What the assistant cannot do: see your CATIA screen, run macros, or read model files.
Paste the spec tree text, the error dialog text, or a recorded macro and it can work from that.
