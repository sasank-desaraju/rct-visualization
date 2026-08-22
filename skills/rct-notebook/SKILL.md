---
name: rct-notebook
description: >-
  Author a marimo notebook that reads a randomized controlled trial through the
  CONSORT 2025 checklist. Use when building a visual, auditable trial summary
  from a paper (PDF or verified public sources) for the rct-visualization repo.
version: 1.1.0
license: MIT
metadata:
  hermes:
    tags: [clinical-research, marimo, visualization, consort, epidemiology]
---

# Authoring an RCT notebook

You are turning one published RCT into a single-file marimo notebook that is a
**CONSORT-shaped read of the trial**: every section anchored to checklist items,
every number traceable to a stated source, every figure computed from literals.

The reference exemplar is `notebooks/nice-sugar.py` in this repo. Read it before
writing anything; your notebook should feel like it belongs next to it.

## Non-negotiable principles

1. **Single source of truth.** One early cell holds ALL trial data as plain
   Python dicts/lists (`TRIAL`, `FLOW`, `ARMS`, `EFFECTS`, `BASELINE`,
   `SECONDARY`, plus any trial-specific structures). Every later cell renders
   FROM those structures. No numbers hardcoded in prose, HTML, or chart code.
2. **Provenance per number.** The data cell opens with a comment block citing
   title, journal/year/DOI, registration number, and which source supplied each
   group of values. If you reconstructed a denominator from a published
   percentage (so arithmetic reproduces the printed rate), say so in that
   comment and in the provenance footer.
3. **Never invent.** A value you cannot find in the paper or its verified public
   sources gets status `"na"` / "Not reported" — never a guess. If the paper's
   full text was unavailable and you worked from abstract + registry + critical
   appraisals, say so explicitly in the provenance footer.
4. **Absolute effects first.** CONSORT item 26 asks for absolute AND relative
   effect. Always show counts → rates → absolute difference → NNH/NNT (when the
   paper permits) → OR/HR with CI. For NNT/NNH, round away from zero (normally
   `ceil(1 / absolute_risk_difference)`), never to the nearest integer. The icon
   array (see below) is the default signature figure, but do not force it onto a
   time-to-event endpoint when the paper gives only annualized rates or HRs; use
   a rate/CI view and explain the choice.
5. **Harms get equal billing.** Every trial has item 15/27 harms. Show them as
   data (counts/rates), not adjectives.
6. **CONSORT 2025 as lens, not judge.** For pre-2025 trials, note that newer
   items (e.g. patient & public involvement, data sharing) postdate the report.
   The checklist table ends with a sentence on what the gap pattern says about
   how reporting norms moved.

## The remarkable bar

A notebook is not finished when it has a title, a few charts, and a working
WASM export. It earns attention by making the trial easier to think with:

- **One evidence spine:** state the clinical decision, eligible population,
  randomized contrast, primary outcome, uncertainty, and principal harm/benefit
  before adding secondary detail.
- **One memory figure:** choose the visual that makes the central result hard to
  forget (NICE-SUGAR's 100-person mortality arrays; SPRINT/ISCHEMIA's temporal
  risk curves or rate comparison when fixed denominators would mislead).
- **One honest surprise:** make the result falsifiable and specific, not a
  generic title such as "trial results visualized." The hero should let a reader
  repeat the main conclusion in one sentence.
- **Earned interactivity:** every control changes a meaningful view (units,
  CONSORT section, subgroup, time horizon); do not add widgets as decoration.
- **Visible limits:** missing data, post-randomization exclusions, open-label
  design, platform-trial scope, and endpoint definitions should be readable at
  the moment they matter, not buried only in a footer.

The technical quality bar is in service of this reading experience: a beautiful
but generic dashboard is a failed notebook, while a restrained notebook that
makes one difficult trial unmistakable is a success.

## Notebook structure (in this order)

1. PEP 723 header: `requires-python >=3.12`; deps exactly
   `altair==6.1.0`, `marimo`, `polars==1.40.0`.
2. Shared-visual-language cell: the `colors` dict, `FONT = "Georgia, serif"`,
   `CHART_W = 600`, and helpers `style()`, `card()`, `box()`, `pill()` — copy
   them verbatim from the exemplar so all notebooks in the repo look related.
   Arm colors: harmful/exposed arm `#b3544c` (clay), reference/control arm
   `#3f7d78` (teal), accent `#b48b32`. If the trial's "intensive" arm turned out
   BENEFICIAL, keep red=exposed-arm but retitle the narrative around benefit;
   do not silently swap colors mid-notebook.
3. Data cell(s) — the single source of truth (principle 1).
4. CONSORT checklist cell: a list of tuples
   `(section, item_id, topic, status, note)` covering all 30 top-level items of
   CONSORT 2025 (BMJ 2025;388:e081123). Because several items split into a/b/c
   subitems, a complete table commonly has 42 reporting rows; state both counts
   in the coverage summary instead of claiming that the row count is 30.
   `status ∈ {"reported","partial","na","gap"}`.
5. Interactive controls cell: `mo.ui.radio`/`dropdown` for anything unit- or
   section-scoped. Controls must be referenced by cells that USE them and must
   be displayed via `mo.vstack([...])` somewhere — an undisplayed control still
   works but confuses readers.
6. Hero cell: kicker line ("A randomised trial, read through CONSORT 2025"),
   trial name/title, one-paragraph what-this-is, then 3–4 `card()` stats:
   randomised N, primary-outcome rate per arm, absolute difference (+NNH/NNT).
7. Design-in-one-paragraph cell (items 1, 9, 11, 12, 17–21): design, blinding
   status, allocation mechanism, targets/interventions, analysis population,
   recruitment window and setting.
8. Intervention-vs-delivery chart (items 13 & 24): target range bands +
   achieved-mean points (or equivalent fidelity display for non-glucose trials:
   achieved BP for SPRINT-type trials, actual drug exposure, etc.). Add a unit
   toggle only if units genuinely differ across audiences (mg/dL vs mmol/L);
   otherwise skip it.
9. Participant-flow cell (item 22): rebuilt flow diagram using `box()` and CSS
   grid, screened → randomised → allocated per arm → analysed per arm, with
   exclusions shown at each stage where reported.
10. Baseline cell (item 25): markdown table from `BASELINE`.
11. Primary outcome visual: use two 10×10 waffle charts (one per arm) when the
    paper provides clean fixed-denominator risks; each square = one patient per
    hundred, event squares filled first, arm color on events, `#e7e2d8` on
    survivors. Caption states counts, %, and absolute difference. For
    time-to-event endpoints reported as annualized rates/HRs, use paired
    cumulative-rate or rate/CI views instead and state why an icon array would
    imply false precision. This is the figure people remember — make its
    caption carry the numbers too.
12. Forest plot (item 26): log-scale OR/HR rules+points with dashed null line at
    1.0, CIs as tooltips. Include primary + key secondary/harm estimates the
    paper reports with CI.
13. Harms & secondary outcomes cell (items 15, 26, 27): prose WITH numbers from
    the data structures + a "Why it matters" callout tying mechanism to outcome.
14. Open science cell (items 2–5): registration, protocol/SAP, data sharing,
    funding/COI as a small card grid.
15. Checklist table cell: filterable by section (the dropdown), pill-coded
    statuses, running counts of each status, closing coverage paragraph.
16. Provenance footer cell: citation with DOI link, CONSORT 2025 citation
    (Hopewell S, et al. BMJ 2025;388:e081123), reconstruction disclosures, and
    the lens-not-judge caveat when applicable.

Every view cell ends by displaying its assembled `mo.vstack(...)` (or bare
element). Cells that build data used elsewhere return it via `return`.

## Chart rules (Altair)

- Wrap every final chart in `style(...)`.
- Encode arms via `alt.Scale(domain=[...arm names...], range=[colors[...], ...])`
  built from the data, never inline hex in encodes.
- Icon arrays: `mark_square(size=150, cornerRadius=2)`, ordered ordinal axes,
  axis=None both dimensions.
- Forest plots: x scale `type="log"` with domain padded to cover all CIs;
  explicit null rule `pl.DataFrame({"x": [1.0]})`.
- Disable max rows once in the helpers cell: `alt.data_transformers.disable_max_rows()`.
- Tooltips carry exact values incl. units; titles use `alt.TitleParams` with a
  subtitle explaining how to READ the encoding (e.g. "Shaded bar = protocol
  target range · dot = time-weighted achieved mean").

## Marimo pitfalls (each has bitten real notebooks)

- A variable defined in a cell but never returned causes silent NameError in
  dependents; return EVERYTHING downstream cells need (see exemplar returns).
- `mo.ui.*` elements must be constructed in their own cell and referenced
  (not re-created) elsewhere; two constructions of the same widget desync state.
- Never mutate module-level data structures inside multiple cells; marimo's
  DAG assumes cell purity. Derive copies instead.
- f-string braces in HTML helper functions: escape `{` / `}` literally where
  needed (CSS uses none here, but double-check any added style blocks).
- Markdown strings with interpolated multiline content are fragile: a table
  injected into an indented `f"""..."""` can lose common indentation and render
  as a code block. Build long Markdown with explicit concatenated lines (or
  `textwrap.dedent`) and execute the browser-rendered notebook once to check
  headings, tables, and captions are actually semantic HTML.
- Keep `width="medium"` on `marimo.App`; the site embed assumes it.
- File must end with `if __name__ == "__main__": app.run()`.

## Verification gate (do not skip)

Run, in order, from the repo root:

```bash
uv run python scripts/verify_notebook.py notebooks/<trial>.py
```

The harness runs Ruff, exports the notebook to a temporary script, executes the
exported script, and checks the structural markers. For a lower-level diagnosis,
the equivalent commands are:

```bash
uv run ruff check notebooks/<trial>.py
uv run marimo export script notebooks/<trial>.py > /tmp/export_check.py && echo EXPORT_OK
uv run python /tmp/export_check.py
```

The reference notebooks intentionally end display cells with bare expressions;
put `# ruff: noqa: B018,PLR1711` **after** the closing `# ///` marker (never
inside the PEP 723 TOML block) so Ruff checks real code without misclassifying
marimo's display convention.
- `EXPORT_OK` proves the file parses and cells compile.
- Executing the exported script proves every cell runs top-to-bottom with no
  NameError/marimo dependency errors (charts render as Altair specs; that is fine).
- Arithmetic audit: assert (in a throwaway script, not shipped) that every rate
  shown equals counts/denominator from the data cell, and that reconstructed
  denominators reproduce the published rates within rounding (<0.05 pp).
- If `uv` is unavailable, use `pip install altair==6.1.0 polars==1.40.0 marimo`
  into a venv; the gate is execution, not the toolchain.

Report at the end: file path, verification-gate outputs verbatim, list of
checklist items marked `gap`/`na`, and any numbers you could NOT source (with
what you tried).

## Trial-specific adaptations

- Composite outcomes (SPRINT, ISCHEMIA): the icon array shows the primary
  composite annualized event rate ONLY IF the paper gives denominators; if it
  reports rates-per-year without clean counts, replace icon arrays with paired
  point-and-CI rate charts and say why in the caption.
- Platform trials (RECOVERY): describe the platform in the design paragraph and
  pin WHICH comparison the notebook covers (e.g. dexamethasone vs usual care)
  in the hero subtitle; do not visualize other domains' arms.
- Time-to-event outcomes with HRs only: forest plot carries the weight; icon
  array may be omitted if no usable risk is derivable — document the omission
  in the provenance footer.
- Equivalence/noninferiority trials: add the margin to the forest plot as a
  second rule and explain it in the subtitle.
