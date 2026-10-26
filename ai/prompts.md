# Starter prompts

Paste into Claude Code (or any assistant with `CLAUDE.md` loaded). Replace the bracketed bits.

## Orientation

- "I just opened [filename]. The tree shows [paste the first 20 lines]. What am I looking at and what should I avoid clicking?"
- "Explain what Visualization Mode means for the part I have selected and how to edit it."
- "Which card in quickref/ answers: [your question]?"

## Finding things

- "Write the Edit > Search query that finds every part whose name starts with BRK in the whole document."
- "I need to see only the hydraulic lines in this assembly. What is the fastest way without expanding the tree?"

## Macros

- "Is there already a macro in our library (local/index/macros.md) that exports a BOM? If not, write one in CATScript based on macros/templates/WalkProductTree.CATScript."
- "Convert this recorded macro into something readable with error handling: [paste]."
- "This CATScript fails with 'Object doesn't support this property or method' on line [n]: [paste]. Check the member against local/chm/ and tell me what the right call is in release [X]."
- "Write a CATScript that lists every part in Design Mode and asks before switching them to Visualization Mode."
- "Turn macros/examples/ExportTreeToCsv.CATScript into a CATVBA module with typed declarations."

## Settings

- "Give me the Tools > Options path and value for every setting in quickref/07-settings-for-speed.md that is not locked in our deployment (company/environment.md)."

## Company-specific (after filling company/ and running the hookup)

- "According to company/plm-workflow.md, what are the exact steps to save the sub-assembly I am editing?"
- "Which templates in local/index/templates.md should I start from for a new sheet-metal bracket?"
- "Summarize company/known-issues.md entries that relate to the cache."

## Maintaining this repo

- "I found that the menu path in quickref/03 for Selective Load is different in our release. It is [path]. Update the card."
- "Re-run the hookup indexer and tell me what changed since the last index."
