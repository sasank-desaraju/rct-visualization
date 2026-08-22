# rct-visualization

Marimo notebooks that read landmark randomized controlled trials through the
CONSORT 2025 checklist. Each notebook is a self-contained, reproducible visual
essay: every figure renders from data literals transcribed from the trial
publication, with provenance stated inline.

The project thesis is simple: an RCT should be something a reader can inspect,
not just a paragraph of results. This is not a chart gallery; it is a repeatable
method for moving from paper → evidence map → visual argument → audit trail.
The flagship example is NICE-SUGAR (NEJM 2009), also hosted as WebAssembly on
sasank-desaraju.github.io.

## Layout

```
papers/       source publications (PDFs where open-access; SOURCE-NOTE.md where paywalled)
notebooks/    one marimo notebook per trial (nice-sugar.py, recovery-dexamethasone.py, ...)
skills/rct-notebook/SKILL.md   the authoring skill: how to build a new trial notebook
```

## Usage

```bash
uv sync                      # install marimo + altair + polars
uv run marimo edit notebooks/nice-sugar.py
```

Headless verification that a notebook builds and runs:

```bash
uv run marimo export script notebooks/nice-sugar.py > /dev/null && echo OK
```

## The skill

`skills/rct-notebook/SKILL.md` encodes the whole method: the CONSORT-shaped
data model, extraction-with-provenance rules, chart-type-to-checklist-item
mapping, the shared visual language, marimo pitfalls, and a verification gate.
Feed it to any capable agent together with a trial paper to get a consistent,
auditable notebook.
