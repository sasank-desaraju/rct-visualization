# RCT Visualization

Landmark randomized controlled trials, made easier to read.

Randomized Controlled Trials (RCT) are the gold standard of medical evidence for new interventions.
However, their dense journal articles can be difficult to read.
This repository is about reproducible visual artifacts of RCTs.

Each example notebook here rebuilds one published trial as a reactive [marimo](https://marimo.io) notebook,
structured using the [CONSORT 2025](https://pubmed.ncbi.nlm.nih.gov/40228833/) reporting standard for randomized trials.

## Examples

The examples in this repo are hosted live [here](https://sasank-desaraju.github.io/rct-examples/).


| Trial | Clinical question | Headline result (from the notebook) |
|---|---|---|
| [**NICE-SUGAR**](notebooks/nice-sugar.py) (NEJM 2009) | In critically ill adults, does tight glucose control (81–108 mg/dL) beat conventional control? | It caused harm. 90-day mortality 27.5% vs 24.9%, odds ratio 1.14 (95% CI 1.02–1.28). Severe hypoglycemia 6.8% vs 0.5%. |
| [**RECOVERY · Dexamethasone**](notebooks/recovery-dexamethasone.py) (NEJM 2020) | In hospitalized Covid-19 patients, does dexamethasone reduce 28-day death? | Yes, but only for the sick end. Overall rate ratio 0.83 (0.75–0.93); 0.64 (0.51–0.81) on ventilation; 1.19 (0.91–1.55) on no oxygen. |
| [**SPRINT**](notebooks/sprint.py) (NEJM 2015) | Does a systolic target below 120 mm Hg beat below 140 in high-risk adults? | Yes, and it stopped early. Primary composite hazard ratio 0.75 (0.64–0.89); all-cause death 0.73 (0.60–0.90). |
| [**ISCHEMIA**](notebooks/ischemia.py) (NEJM 2020) | In stable coronary disease, does an initial invasive strategy (surgery) beat a conservative one? | No clear difference. Primary composite hazard ratio 0.93 (0.80–1.08), p = 0.34. |

Each headline above is one line from a notebook that walks you through the full
result. Open any notebook to read the question, the population, the comparison,
and the uncertainty as a clear visual sequence.

## Build the notebooks yourself

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

## How it works

To generate a notebook, you can point your AI agent at this skill:
[`skills/rct-notebook/SKILL.md`](skills/rct-notebook/SKILL.md).

The skill encodes the whole pipeline: the
[CONSORT 2025](https://pubmed.ncbi.nlm.nih.gov/40228833/) structure,
extraction rules for authenticity, how to map from checklist item to
chart type, and the shared visual language.
Give the skill to a capable agent together
with a trial paper and you get a consistent, auditable notebook that belongs next
to the others.

## Why marimo

- **Beautiful visualizations**
- **Portable**
- **Agent-friendly**
- **Easy to deploy**

## Repository layout

```
notebooks/    one marimo notebook per trial (nice-sugar.py, sprint.py, ...)
papers/       source publications and source notes, with a provenance index
skills/       rct-notebook/SKILL.md, the authoring method
scripts/      verify_notebook.py
```

## License

Code and notebooks are released under the [MIT License](LICENSE). Source papers
in `papers/` remain under their publishers' terms; check those before you
redistribute a PDF.
