# rct-visualization

Landmark randomized controlled trials, made easier to read.

Reading a trial straight from the journal is hard work. One article carries the
design, the population, the comparison, the outcomes, and every caveat, mostly in
long paragraphs and footnoted tables. Specialists learn to mine it. Most other
readers bounce off.

Each notebook here rebuilds one published trial as a reactive
[marimo](https://marimo.io) notebook, laid out along
[CONSORT 2025](https://pubmed.ncbi.nlm.nih.gov/40228833/), the reporting standard
for randomized trials. The same evidence arrives as a sequence of figures: the
question, who was studied, what was compared, the result, and how much
uncertainty is left. Every number is transcribed from the paper and carries its
source in a comment beside it, so the visual version stays true to the original.

It is a method, not a chart gallery: a repeatable way to take a dense paper and
turn it into something a much wider audience can actually get through.

## The four trials

The same method holds whether the trial says yes, no, or "it caused harm." That
is the point. Read across these four and the shape of the evidence, not the
headline, is what you remember.

| Trial | Clinical question | Headline result (from the notebook) |
|---|---|---|
| [**NICE-SUGAR**](notebooks/nice-sugar.py) (NEJM 2009) | In critically ill adults, does tight glucose control (81–108 mg/dL) beat conventional control? | It caused harm. 90-day mortality 27.5% vs 24.9%, odds ratio 1.14 (95% CI 1.02–1.28). Severe hypoglycemia 6.8% vs 0.5%. |
| [**RECOVERY · Dexamethasone**](notebooks/recovery-dexamethasone.py) (NEJM 2020) | In hospitalized Covid-19 patients, does dexamethasone reduce 28-day death? | Yes, but only for the sick end. Overall rate ratio 0.83 (0.75–0.93); 0.64 (0.51–0.81) on ventilation; 1.19 (0.91–1.55) on no oxygen. |
| [**SPRINT**](notebooks/sprint.py) (NEJM 2015) | Does a systolic target below 120 mm Hg beat below 140 in high-risk adults? | Yes, and it stopped early. Primary composite hazard ratio 0.75 (0.64–0.89); all-cause death 0.73 (0.60–0.90). |
| [**ISCHEMIA**](notebooks/ischemia.py) (NEJM 2020) | In stable coronary disease, does an initial invasive strategy beat a conservative one? | No clear difference. Primary composite hazard ratio 0.93 (0.80–1.08), p = 0.34. |

Each headline above is one line from a notebook that walks you through the full
result. Open any notebook to read the question, the population, the comparison,
and the uncertainty as a clear visual sequence.

## Try one in about a minute

Every notebook is a standalone script with its dependencies declared inline
([PEP 723](https://peps.python.org/pep-0723/)). You do not clone, create a
virtual environment, and install by hand. You run one line:

```bash
uvx marimo edit --sandbox notebooks/nice-sugar.py
```

`uvx` reads the inline dependency block, builds a throwaway environment, and
opens the reactive notebook in your browser. That is the whole setup.

Prefer to work in the repo?

```bash
uv sync                                   # marimo + altair + polars
uv run marimo edit notebooks/nice-sugar.py
```

> **Live browser demo:** a WebAssembly build that runs with no install at all is
> planned, not yet published. Until then, the one-line command above is the
> fastest way to see a notebook run. You can build a local WASM copy yourself
> with `uv run marimo export html-wasm notebooks/nice-sugar.py -o site/`.

## Why marimo

The method needs a notebook that is honest by construction. marimo supplies
exactly that:

- **Reactive, not stateful.** Change a control and every dependent cell
  recomputes. A reader cannot see a figure that disagrees with the data cell
  above it, because marimo will not let a stale cell survive.
- **One file, plain Python.** Each notebook is a `.py` file you can read, diff,
  and review in a pull request. Provenance lives in comments next to the data.
- **Inline dependencies.** PEP 723 headers pin `altair`, `marimo`, and `polars`,
  so the notebook you share is the notebook that runs.
- **Runs in the browser.** marimo compiles to WebAssembly, so a finished trial
  read can reach a clinician, a trainee, or a curious reader with no Python
  install. That reach is the point: an easier read only helps if people can open
  it.

The visual language is shared across every notebook: the same color system, the
same card, box, and pill helpers, the same chart styling. Read one and you can
read all four.

## How a notebook is built

The method is not tribal knowledge. It is written down as an authoring skill:
[`skills/rct-notebook/SKILL.md`](skills/rct-notebook/SKILL.md).

The skill encodes the whole pipeline: a
[CONSORT 2025](https://pubmed.ncbi.nlm.nih.gov/40228833/)-shaped data model,
extraction rules that forbid inventing a number, a mapping from checklist item to
chart type, the shared visual language, the marimo pitfalls that have bitten real
notebooks, and a verification gate. Give the skill to a capable agent together
with a trial paper and you get a consistent, auditable notebook that belongs next
to the others.

To build or check a notebook, run the gate:

```bash
uv run python scripts/verify_notebook.py notebooks/nice-sugar.py
```

The gate runs Ruff, exports the notebook to a script, executes it, and checks the
structural markers. It proves the notebook parses, runs, and is shaped right. It
does not prove the clinical numbers are correct. That still needs a human reading
the paper. See [CONTRIBUTING.md](CONTRIBUTING.md) to add a trial.

## Faithful to the source

Making a trial easier to read must not make it less accurate. A visual read is
only worth trusting if every number still traces back to the paper. So this repo
treats "where did this number come from" as a first-class question.

- Source papers live in [`papers/`](papers/). Open-access PDFs are stored
  directly. Paywalled papers get a `SOURCE-NOTE.md` that lists every public
  source used instead.
- No notebook invents a value. A number the paper does not report is marked "not
  reported," never guessed.
- When a denominator is reconstructed from a published percentage so the
  arithmetic reproduces the printed rate, the notebook says so, next to the
  number and in its provenance footer.

## Repository layout

```
notebooks/    one marimo notebook per trial (nice-sugar.py, sprint.py, ...)
papers/       source publications and source notes, with a provenance index
skills/       rct-notebook/SKILL.md, the authoring method
scripts/      verify_notebook.py, the verification gate
```

## License

Code and notebooks are released under the [MIT License](LICENSE). Source papers
in `papers/` remain under their publishers' terms; check those before you
redistribute a PDF.
