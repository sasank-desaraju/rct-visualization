# notebooks/

One marimo notebook per trial. See the [root README](../README.md) for the
project thesis and the [authoring skill](../skills/rct-notebook/SKILL.md) for how
each notebook is built.

## Files

| File | Trial |
|---|---|
| `nice-sugar.py` | NICE-SUGAR (NEJM 2009). Intensive vs conventional glucose control in the ICU. Reference exemplar for the method. |
| `recovery-dexamethasone.py` | RECOVERY, dexamethasone comparison (NEJM 2020). Dexamethasone vs usual care in Covid-19. |
| `sprint.py` | SPRINT (NEJM 2015). Intensive vs standard blood-pressure control. |
| `ischemia.py` | ISCHEMIA (NEJM 2020). Invasive vs conservative strategy for stable coronary disease. |

## Conventions

- **Naming:** `trial-shortname.py`, lowercase, hyphenated.
- **Standalone:** each file declares its dependencies inline with
  [PEP 723](https://peps.python.org/pep-0723/), so `uvx marimo edit --sandbox
  notebooks/<file>.py` runs it with no prior setup.
- **Single source of truth:** all trial data lives in one early cell. Every later
  cell renders from that cell. No number is hardcoded in prose or chart code.

## Run and verify

Run these from the repository root:

```bash
uv run marimo edit notebooks/nice-sugar.py                       # open and edit
uv run python scripts/verify_notebook.py notebooks/nice-sugar.py # run the gate
```
