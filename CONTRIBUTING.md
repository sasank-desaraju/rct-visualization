# Add a trial

Every notebook in this repo follows one method, written down in
[`skills/rct-notebook/SKILL.md`](skills/rct-notebook/SKILL.md). Read that skill
and one existing notebook before you start. The skill is the source of truth for
structure, style, and rules. This page is the short path.

## The path

1. **Get the paper.** Add the source to [`papers/`](papers/). Store an
   open-access PDF directly. For a paywalled paper, write a `SOURCE-NOTE.md` that
   lists every public source you used, then add a row to
   [`papers/INDEX.md`](papers/INDEX.md).
2. **Write the notebook.** Give the skill and the paper to a capable agent, or
   write it by hand against `notebooks/nice-sugar.py` as the reference. Put all
   trial data in one early cell. Cite the source of each number in a comment
   next to it. Render every figure from that data cell.
3. **Never invent a number.** A value the paper does not report is marked "not
   reported," not guessed. When you reconstruct a denominator from a published
   percentage, say so next to the number and in the provenance footer.
4. **Run the gate.**

   ```bash
   uv run python scripts/verify_notebook.py notebooks/<trial>.py
   ```

   The gate must print `EXECUTE_OK` and `ALL_OK` before you open a pull request.

## What the gate does and does not check

The gate proves the notebook parses, exports, runs top to bottom, and has the
required structure. It does **not** prove the clinical numbers are right. That is
a human job: read the paper, check that each displayed rate reproduces from the
data-cell literals, and confirm the flow counts and arm totals sum correctly. The
skill describes this arithmetic audit in detail.

## House writing style

Follow the reading and writing standard in the skill: the Google Developer
Documentation Style Guide, GitHub's guidance for clear change descriptions, and
ASD-STE100 Simplified Technical English. In short: put the result first, use
short active sentences, use one term for one concept, and avoid hype. State every
result with its uncertainty.
