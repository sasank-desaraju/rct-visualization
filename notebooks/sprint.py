# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "altair==6.1.0",
#     "marimo",
#     "polars==1.40.0",
# ]
# ///
# ruff: noqa: B018,PLR1711

import marimo

__generated_with = "0.17.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import marimo as mo
    import polars as pl

    alt.data_transformers.disable_max_rows()

    # ---- Shared visual language (kept close to the site's other notebooks) ----
    colors = {
        "ink": "#1f2933",
        "muted": "#65717c",
        "paper": "#ffffff",
        "panel": "#f5f3ef",
        "panel2": "#e8ece8",
        "grid": "#dde3e1",
        "intensive": "#b3544c",  # the exposed (intensive) arm -> clay red
        "standard": "#3f7d78",   # the reference (standard) arm -> teal
        "accent": "#b48b32",
        "good": "#3f7d78",
        "warn": "#b48b32",
        "bad": "#b3544c",
        "dark": "#263238",
    }
    FONT = "Georgia, serif"
    CHART_W = 600

    def style(chart):
        return (
            chart.configure_view(stroke=None)
            .configure_axis(
                labelColor=colors["ink"],
                titleColor=colors["ink"],
                gridColor=colors["grid"],
                tickColor=colors["grid"],
                domainColor=colors["grid"],
                labelFont=FONT,
                titleFont=FONT,
                labelLimit=420,
                titlePadding=10,
            )
            .configure_legend(
                titleColor=colors["ink"],
                labelColor=colors["ink"],
                titleFont=FONT,
                labelFont=FONT,
                orient="top",
            )
            .configure_title(
                color=colors["ink"],
                font=FONT,
                fontSize=15,
                subtitleColor=colors["muted"],
                subtitleFont=FONT,
                anchor="start",
            )
        )

    def card(kicker, big, small, color):
        return f"""
        <div style="background:#ffffff; border:1px solid #e1ddd4; border-radius:10px; padding:10px 12px;">
            <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:{colors['muted']};">{kicker}</div>
            <div style="font-size:1.42rem; color:{color}; margin:1px 0;">{big}</div>
            <div style="font-size:0.86rem; color:{colors['muted']}; line-height:1.28;">{small}</div>
        </div>"""

    def box(title, n, color, sub=""):
        sub_html = f'<div style="font-size:0.78rem; color:{colors["muted"]}; margin-top:2px;">{sub}</div>' if sub else ""
        return f"""
        <div style="background:{colors['paper']}; border:1px solid #d9d4ca; border-left:4px solid {color};
                    border-radius:8px; padding:8px 10px; text-align:center;">
            <div style="font-size:0.92rem; color:{colors['ink']};">{title}</div>
            <div style="font-size:1.25rem; color:{color}; font-weight:600;">n = {n:,}</div>
            {sub_html}
        </div>"""

    def pill(status):
        spec = {
            "reported": (colors["good"], "#e7f0ee", "Reported"),
            "partial": (colors["warn"], "#f5eede", "Partial"),
            "na": (colors["muted"], "#eceae5", "N/A"),
            "gap": (colors["bad"], "#f3e2e0", "Not addressed"),
        }[status]
        fg, bg, label = spec
        return (
            f'<span style="background:{bg}; color:{fg}; border:1px solid {fg}33; '
            f'border-radius:999px; padding:1px 9px; font-size:0.72rem; white-space:nowrap;">{label}</span>'
        )

    return CHART_W, FONT, alt, box, card, colors, mo, pill, pl, style


@app.cell
def _():
    # =====================================================================
    # SINGLE SOURCE OF TRUTH
    # SPRINT Research Group. A Randomized Trial of Intensive versus
    # Standard Blood-Pressure Control.
    # N Engl J Med 2015;373:2103-2116.  DOI 10.1056/NEJMoa1511939
    # Registered: NCT01206062.
    # Every figure below is rendered from these literals, taken from the
    # paper's main text, Tables 1-3, and Figures 1-2. SPRINT printed both
    # event counts and annualised rates, so NO denominator reconstruction
    # was needed anywhere in this notebook.
    # =====================================================================

    TRIAL = {
        "name": "SPRINT",
        "title": "A Randomized Trial of Intensive versus Standard Blood-Pressure Control",
        "citation": "SPRINT Research Group. N Engl J Med 2015;373:2103-2116.",
        "doi": "10.1056/NEJMoa1511939",
        "registration": "NCT01206062",
        "recruitment": "November 2010 – March 2013",
        "centers": 102,
        "networks": 5,
        "geography": "United States, including Puerto Rico",
        "stopped": "August 20, 2015",
        "median_fu_years": 3.26,
        "planned_fu_years": 5,
    }

    # Participant flow (item 22). Pre-randomisation screening counts appear
    # only inside Figure 1 (an image), which is not part of the extracted
    # full text, so they are carried as None and shown honestly as such.
    # There were no post-randomisation exclusions reported in the main text;
    # the analysis was intention-to-treat, so analysed = allocated.
    FLOW = {
        "screened": None,
        "randomized": 9361,
        "int_assigned": 4678,
        "std_assigned": 4683,
        "int_analyzed": 4678,
        "std_analyzed": 4683,
    }

    # Arms: systolic targets (mm Hg), achieved means, medication burden.
    # The standard arm's titration window (135-139, reduce if <130 once or
    # <135 twice consecutively) comes from the METHODS section.
    ARMS = [
        {
            "arm": "Intensive",
            "target_ceiling": 120,
            "target_label": "<120 mm Hg",
            "achieved_1yr": 121.4,
            "achieved_mean": 121.5,
            "meds": 2.8,
        },
        {
            "arm": "Standard",
            "target_ceiling": 140,
            "target_label": "<140 mm Hg",
            "achieved_1yr": 136.2,
            "achieved_mean": 134.6,
            "meds": 1.8,
        },
    ]

    # Outcomes (item 26): counts, trial-period percentages, annualised
    # rates (%/yr), hazard ratios with 95% CI, and P values, exactly as in
    # Table 2. The renal outcome is reported only among participants
    # WITHOUT chronic kidney disease at baseline (N = 3332 vs 3345), so its
    # denominators differ from the full cohort.
    OUTCOMES = [
        {"outcome": "Primary composite (MI, ACS, stroke, HF, CV death)", "short": "Primary composite",
         "int_n": 243, "int_pct": 5.2, "int_rate": 1.65, "std_n": 319, "std_pct": 6.8, "std_rate": 2.19,
         "hr": 0.75, "lo": 0.64, "hi": 0.89, "p": "<0.001", "kind": "benefit"},
        {"outcome": "Death from any cause", "short": "All-cause death",
         "int_n": 155, "int_pct": 3.3, "int_rate": 1.03, "std_n": 210, "std_pct": 4.5, "std_rate": 1.40,
         "hr": 0.73, "lo": 0.60, "hi": 0.90, "p": "0.003", "kind": "benefit"},
        {"outcome": "Death from cardiovascular causes", "short": "CV death",
         "int_n": 37, "int_pct": 0.8, "int_rate": 0.25, "std_n": 65, "std_pct": 1.4, "std_rate": 0.43,
         "hr": 0.57, "lo": 0.38, "hi": 0.85, "p": "0.005", "kind": "benefit"},
        {"outcome": "Heart failure", "short": "Heart failure",
         "int_n": 62, "int_pct": 1.3, "int_rate": 0.41, "std_n": 100, "std_pct": 2.1, "std_rate": 0.67,
         "hr": 0.62, "lo": 0.45, "hi": 0.84, "p": "0.002", "kind": "benefit"},
        {"outcome": "Myocardial infarction", "short": "Myocardial infarction",
         "int_n": 97, "int_pct": 2.1, "int_rate": 0.65, "std_n": 116, "std_pct": 2.5, "std_rate": 0.78,
         "hr": 0.83, "lo": 0.64, "hi": 1.09, "p": "0.19", "kind": "ns"},
        {"outcome": "Acute coronary syndrome (not MI)", "short": "ACS (not MI)",
         "int_n": 40, "int_pct": 0.9, "int_rate": 0.27, "std_n": 40, "std_pct": 0.9, "std_rate": 0.27,
         "hr": 1.00, "lo": 0.64, "hi": 1.55, "p": "0.99", "kind": "ns"},
        {"outcome": "Stroke", "short": "Stroke",
         "int_n": 62, "int_pct": 1.3, "int_rate": 0.41, "std_n": 70, "std_pct": 1.5, "std_rate": 0.47,
         "hr": 0.89, "lo": 0.63, "hi": 1.25, "p": "0.50", "kind": "ns"},
        {"outcome": "Primary outcome or death", "short": "Primary or death",
         "int_n": 332, "int_pct": 7.1, "int_rate": 2.25, "std_n": 423, "std_pct": 9.0, "std_rate": 2.90,
         "hr": 0.78, "lo": 0.67, "hi": 0.90, "p": "<0.001", "kind": "benefit"},
        {"outcome": "≥30% eGFR decline to <60 mL/min/1.73 m² (no CKD at baseline)", "short": "Renal: ≥30% eGFR decline (no baseline CKD)",
         "int_n": 127, "int_pct": 3.8, "int_rate": 1.21, "std_n": 37, "std_pct": 1.1, "std_rate": 0.35,
         "hr": 3.49, "lo": 2.44, "hi": 5.10, "p": "<0.001", "kind": "harm"},
    ]

    # Numbers needed to treat, AS PRINTED in the paper (over the median
    # 3.26-year follow-up) — not recomputed here.
    NNT = {"primary": 61, "any_death": 90, "cv_death": 172}

    # Harms (items 15 & 27): serious adverse events, conditions of
    # interest, from Table 3. Tier "ED or SAE" adds emergency-department
    # evaluations to the serious-adverse-event definition. sig reflects the
    # paper's own inference (which conditions were higher under intensive
    # control); injurious falls and bradycardia were not significantly
    # different.
    HARMS = [
        {"tier": "Serious adverse event", "condition": "Hypotension", "int_n": 110, "int_pct": 2.4, "std_n": 66, "std_pct": 1.4, "p": "0.001", "sig": True},
        {"tier": "Serious adverse event", "condition": "Syncope", "int_n": 107, "int_pct": 2.3, "std_n": 80, "std_pct": 1.7, "p": "0.05", "sig": True},
        {"tier": "Serious adverse event", "condition": "Electrolyte abnormality", "int_n": 144, "int_pct": 3.1, "std_n": 107, "std_pct": 2.3, "p": "0.02", "sig": True},
        {"tier": "Serious adverse event", "condition": "Acute kidney injury or acute renal failure", "int_n": 193, "int_pct": 4.1, "std_n": 117, "std_pct": 2.5, "p": "<0.001", "sig": True},
        {"tier": "Serious adverse event", "condition": "Injurious fall", "int_n": 105, "int_pct": 2.2, "std_n": 110, "std_pct": 2.3, "p": "0.71", "sig": False},
        {"tier": "Serious adverse event", "condition": "Bradycardia", "int_n": 87, "int_pct": 1.9, "std_n": 73, "std_pct": 1.6, "p": "0.28", "sig": False},
        {"tier": "ED visit or SAE", "condition": "Hypotension", "int_n": 158, "int_pct": 3.4, "std_n": 93, "std_pct": 2.0, "p": "<0.001", "sig": True},
        {"tier": "ED visit or SAE", "condition": "Syncope", "int_n": 163, "int_pct": 3.5, "std_n": 113, "std_pct": 2.4, "p": "0.003", "sig": True},
        {"tier": "ED visit or SAE", "condition": "Electrolyte abnormality", "int_n": 177, "int_pct": 3.8, "std_n": 129, "std_pct": 2.8, "p": "0.006", "sig": True},
        {"tier": "ED visit or SAE", "condition": "Acute kidney injury or acute renal failure", "int_n": 204, "int_pct": 4.4, "std_n": 120, "std_pct": 2.6, "p": "<0.001", "sig": True},
        {"tier": "ED visit or SAE", "condition": "Injurious fall", "int_n": 334, "int_pct": 7.1, "std_n": 332, "std_pct": 7.1, "p": "0.97", "sig": False},
        {"tier": "ED visit or SAE", "condition": "Bradycardia", "int_n": 104, "int_pct": 2.2, "std_n": 83, "std_pct": 1.8, "p": "0.13", "sig": False},
    ]
    SAE_OVERALL = {"int_n": 1793, "int_pct": 38.3, "std_n": 1736, "std_pct": 37.1, "hr": 1.04, "p": "0.25"}
    SAE_RELATED = {"int_n": 220, "int_pct": 4.7, "std_n": 118, "std_pct": 2.5, "hr": 1.88, "p": "<0.001"}

    # Baseline highlights (item 25), Table 1. Groups were balanced except
    # statin use (P = 0.04), the only difference the paper flags.
    BASELINE = [
        ("Age — mean (SD), yr", "67.9 ± 9.4", "67.9 ± 9.5"),
        ("Age ≥ 75 years", "1317 (28.2%)", "1319 (28.2%)"),
        ("Female sex", "1684 (36.0%)", "1648 (35.2%)"),
        ("Non-Hispanic black race", "1379 (29.5%)", "1423 (30.4%)"),
        ("Baseline systolic BP — mean (SD), mm Hg", "139.7 ± 15.8", "139.7 ± 15.4"),
        ("Chronic kidney disease (eGFR <60)", "1330 (28.4%)", "1316 (28.1%)"),
        ("Cardiovascular disease (clinical/subclinical)", "940 (20.1%)", "937 (20.0%)"),
        ("Framingham 10-yr risk ≥15%", "2870 (61.4%)", "2867 (61.2%)"),
        ("Body-mass index — mean (SD)", "29.9 ± 5.8", "29.8 ± 5.7"),
        ("Statin use", "1978/4645 (42.6%)", "2076/4640 (44.7%)"),
        ("Antihypertensive agents per patient", "1.8 ± 1.0", "1.8 ± 1.0"),
    ]
    return ARMS, BASELINE, FLOW, HARMS, NNT, OUTCOMES, SAE_OVERALL, SAE_RELATED, TRIAL


@app.cell
def _():
    # ------------------------------------------------------------------
    # CONSORT 2025 checklist (Hopewell S, et al. BMJ 2025;388:e081123),
    # each item paired with how SPRINT (2015) reports it.
    # status: reported | partial | na | gap
    # 42 reporting rows covering all 30 top-level items.
    # ------------------------------------------------------------------
    CHECKLIST = [
        ("Title and abstract", "1a", "Identification as a randomised trial", "reported", "“Randomized” in title and abstract"),
        ("Title and abstract", "1b", "Structured summary", "reported", "NEJM structured abstract"),
        ("Open science", "2", "Trial registration", "reported", "ClinicalTrials.gov NCT01206062"),
        ("Open science", "3", "Protocol & statistical analysis plan", "partial", "Protocol public (NEJM.org, sprinttrial.org); separate SAP not stated in main text"),
        ("Open science", "4", "Data sharing (de-identified IPD, code)", "gap", "Not addressed in the 2015 report — predates the item"),
        ("Open science", "5a", "Funding & role of funders", "reported", "NIH contracts (NHLBI + 3 institutes), VA support; donated drugs disclosed"),
        ("Open science", "5b", "Conflicts of interest", "reported", "Disclosure forms available at NEJM.org"),
        ("Introduction", "6", "Background & rationale", "reported", "Uncertain SBP target below 150; NHLBI-designated priority hypothesis"),
        ("Introduction", "7", "Objectives (benefits & harms)", "reported", "Lower primary-composite rate; safety monitored throughout"),
        ("Methods", "8", "Patient & public involvement", "gap", "Not reported — item new in 2025"),
        ("Methods", "9", "Trial design", "reported", "Randomised, controlled, open-label, parallel group"),
        ("Methods", "10", "Changes to trial methods", "partial", "Early intervention stop prominently reported; other amendments not described"),
        ("Methods", "11", "Trial setting", "reported", "102 clinical sites in 5 networks, US incl. Puerto Rico"),
        ("Methods", "12a", "Eligibility — participants", "reported", "Age ≥50, SBP 130–180, increased CV risk; diabetes & prior stroke excluded"),
        ("Methods", "12b", "Eligibility — sites / deliverers", "na", "Delivered in routine clinics; no special deliverer criteria"),
        ("Methods", "13", "Intervention & comparator", "reported", "<120 vs <140 mm Hg; algorithms, formulary, free medications specified"),
        ("Methods", "14", "Outcomes", "reported", "Composite primary outcome; blinded adjudication committee"),
        ("Methods", "15", "Harms — definition & assessment", "reported", "SAE definition; monitored conditions coded with MedDRA"),
        ("Methods", "16a", "Sample size", "reported", "9,250 target; 88.7% power for a 20% effect at 2.2%/yr"),
        ("Methods", "16b", "Interim analyses & stopping", "reported", "DSMB; Lan–DeMets, O'Brien–Fleming boundaries"),
        ("Methods", "17a", "Sequence generation", "partial", "Randomisation stratified by site; mechanism detailed in supplement"),
        ("Methods", "17b", "Randomisation type / restriction", "reported", "1:1 allocation, stratified by clinical site"),
        ("Methods", "18", "Allocation concealment", "partial", "Not described in the main text"),
        ("Methods", "19", "Implementation", "partial", "Coordinating centre ran the trial; allocation procedure not detailed"),
        ("Methods", "20a", "Blinding — who", "reported", "Open-label; participants/personnel aware, adjudicators masked"),
        ("Methods", "20b", "Blinding — how", "reported", "Masked adjudication; identical interview format in both arms"),
        ("Methods", "21a", "Statistical methods", "reported", "Cox model, clinic-stratified, ITT, two-sided 5%"),
        ("Methods", "21b", "Who is in each analysis", "reported", "All randomly assigned participants, as assigned"),
        ("Methods", "21c", "Missing data", "partial", "Censored at last ascertainment; ~2%/yr loss anticipated"),
        ("Methods", "21d", "Additional analyses", "reported", "Prespecified subgroups; Hommel-adjusted interactions; Fine–Gray sensitivity"),
        ("Results", "22a", "Participant flow", "partial", "Fig. 1 flow diagram; screening counts not in main text"),
        ("Results", "22b", "Losses & exclusions", "partial", "Discontinued-intervention category defined; counts live in Fig. 1"),
        ("Results", "23a", "Recruitment & follow-up dates", "reported", "Enrolment November 2010 – March 2013; median 3.26 yr"),
        ("Results", "23b", "Why the trial ended", "reported", "Stopped early for benefit on DSMB recommendation, August 20, 2015"),
        ("Results", "24a", "Intervention delivery / fidelity", "reported", "121.4 vs 136.2 mm Hg at 1 yr; 2.8 vs 1.8 medications"),
        ("Results", "24b", "Concomitant care", "reported", "Formulary classes, lifestyle advice; statin/aspirin use tabulated"),
        ("Results", "25", "Baseline data", "reported", "Table 1 — balanced except statin use (P = 0.04)"),
        ("Results", "26", "Numbers analysed, outcomes, estimation", "reported", "Counts, %/yr, HRs with CI, and published NNTs"),
        ("Results", "27", "Harms", "reported", "Table 3 — conditions of interest by tier"),
        ("Results", "28", "Ancillary analyses", "reported", "Renal outcomes by baseline CKD; orthostatic hypotension"),
        ("Discussion", "29", "Interpretation", "reported", "Benefit for major CV events and death; some harms higher"),
        ("Discussion", "30", "Limitations", "reported", "Generalisability (no diabetes/prior stroke/<50 yr); pending CNS & renal endpoints"),
    ]
    return (CHECKLIST,)


@app.cell
def _(CHECKLIST, mo):
    # Interactive controls — always shown (works in script/run/edit modes).
    section = mo.ui.dropdown(
        options=["All sections"] + list(dict.fromkeys(row[0] for row in CHECKLIST)),
        value="All sections",
        label="CONSORT section",
    )
    rate_mode = mo.ui.radio(
        options=["Annualised rate (%/yr)", "Events during trial (n)"],
        value="Annualised rate (%/yr)",
        label="Primary-outcome view",
        inline=True,
    )
    return rate_mode, section


@app.cell
def _(FLOW, NNT, OUTCOMES, TRIAL, colors, card, mo):
    # ---------------------------- HERO ----------------------------
    _pr = next(o for o in OUTCOMES if o["short"] == "Primary composite")
    _ard = _pr["int_rate"] - _pr["std_rate"]

    hero = mo.Html(
        f"""
        <div style="background:{colors['panel']}; border:1px solid #ddd8ce; border-radius:14px;
                    padding:18px 20px; font-family:{colors['ink']}; color:{colors['ink']};">
            <div style="text-transform:uppercase; letter-spacing:0.15em; font-size:0.72rem;
                        color:{colors['muted']}; margin-bottom:0.5rem;">
                A randomised trial, read through CONSORT 2025
            </div>
            <div style="font-size:1.82rem; line-height:1.12; margin-bottom:0.25rem;">{TRIAL['name']}</div>
            <div style="font-size:1.0rem; color:#45515b; margin-bottom:0.35rem;">{TRIAL['title']}</div>
            <div style="max-width:820px; font-size:0.96rem; line-height:1.42; color:#45515b; margin-bottom:0.85rem;">
                This notebook is a CONSORT-shaped read of SPRINT, the trial that moved the systolic blood-pressure
                target. Adults at high cardiovascular risk but without diabetes were randomised to a target of
                &lt;120 or &lt;140 mm Hg. Targeting &lt;120 cut fatal and nonfatal major cardiovascular events by a
                quarter and all-cause death by 27% — so convincing that the data and safety monitoring board's
                recommendation to stop early was accepted on {TRIAL['stopped']}, at a median follow-up of
                {TRIAL['median_fu_years']} of the planned {TRIAL['planned_fu_years']} years. The price was a higher
                rate of some serious adverse events. Every section below is anchored to checklist items and every
                number traces to the data cell at the top.
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
                {card("Randomised", f"{FLOW['randomized']:,}", "4,678 intensive &lt;120 · 4,683 standard &lt;140 mm Hg · 102 sites", colors["ink"])}
                {card("Primary outcome — intensive", f"{_pr['int_rate']}%/yr", f"{_pr['int_n']} events · HR {_pr['hr']} ({_pr['lo']}–{_pr['hi']}), P {_pr['p']}", colors["intensive"])}
                {card("Primary outcome — standard", f"{_pr['std_rate']}%/yr", f"{_pr['std_n']} events over median {TRIAL['median_fu_years']} yr", colors["standard"])}
                {card("Absolute benefit", f"{_ard:.2f} pts/yr", f"NNT {NNT['primary']} over median {TRIAL['median_fu_years']} years (as published)", colors["accent"])}
            </div>
        </div>
        """
    )
    hero
    return


@app.cell
def _(colors, mo):
    consort_blurb = mo.Html(
        f"""
        <div style="font-family:Georgia, serif; color:{colors['ink']}; line-height:1.42;
                    border:1px solid #ddd8ce; border-left:4px solid {colors['accent']};
                    border-radius:10px; padding:10px 14px; background:#fffdf8;">
            <strong>How the CONSORT adherence is made explicit.</strong>
            Each section below is anchored to checklist items, not just to the paper's narrative order:
            design and eligibility (items 9, 11, 12), intervention specification and delivery (13, 24),
            participant flow (22), baseline balance (25), absolute and relative effects (26), harms (15, 27),
            open-science expectations (2–5), and interpretation/limitations (29–30).
            The final table is the audit trail, showing what SPRINT reports in full, what lives only in the
            supplementary appendix, and what modern CONSORT expects that a 2015 paper never had to provide.
        </div>
        """
    )
    consort_blurb
    return


@app.cell
def _(TRIAL, mo):
    design = mo.md(
        "**The design in one paragraph**\n\n"
        f"**{TRIAL['name']}** was a randomised, controlled, **open-label** multicentre trial at "
        f"{TRIAL['centers']} clinical sites in {TRIAL['networks']} networks ({TRIAL['geography']}). "
        "Adults **≥50 years** with systolic BP **130–180 mm Hg** and increased cardiovascular risk "
        "(clinical/subclinical CVD other than stroke; CKD with eGFR 20–<60; Framingham 10-year risk ≥15%; or age ≥75) "
        "were eligible; **diabetes and prior stroke were excluded**. Participants were allocated 1:1 by "
        "**randomisation stratified according to clinical site** to an intensive target (**<120 mm Hg**) or a "
        "standard target (**<140 mm Hg**, titrated to 135–139, with dose reduction below those thresholds). "
        "Participants and study personnel knew the assignments, but **outcome adjudicators did not**. "
        "The primary analysis was **intention-to-treat**, comparing time to the first primary outcome with "
        "**Cox proportional-hazards regression stratified by clinic**; interim analyses used Lan–DeMets "
        "**O'Brien–Fleming** stopping boundaries reviewed by an independent DSMB. Recruitment ran "
        f"{TRIAL['recruitment']}; on {TRIAL['stopped']} the NHLBI director accepted the DSMB's recommendation to "
        f"end the intervention early, after the monitoring boundary was crossed at two consecutive looks "
        f"(median follow-up {TRIAL['median_fu_years']} years).\n\n"
        "_CONSORT items 1, 9, 11, 12, 17–21._"
    )
    design
    return


@app.cell
def _(ARMS, CHART_W, alt, colors, mo, pl, style):
    # ------------- INTERVENTIONS: target bands + achieved means -------------
    X_MIN = 112  # view floor only; the protocol sets no lower bound

    band_rows = []
    point_rows = []
    for a in ARMS:
        band_rows.append(
            {
                "arm": a["arm"],
                "lo": X_MIN,
                "hi": a["target_ceiling"],
                "label": f'Target {a["target_label"]} (no protocol lower bound)',
            }
        )
        point_rows.append({"arm": a["arm"], "kind": "Achieved mean at 1 year", "value": a["achieved_1yr"]})
        point_rows.append({"arm": a["arm"], "kind": "Mean over median 3.26-yr follow-up", "value": a["achieved_mean"]})
    bands = pl.DataFrame(band_rows)
    points = pl.DataFrame(point_rows)

    arm_scale = alt.Scale(domain=["Intensive", "Standard"], range=[colors["intensive"], colors["standard"]])
    y_sort = ["Intensive", "Standard"]

    _band = alt.Chart(bands).mark_bar(height=26, opacity=0.35, cornerRadius=3).encode(
        y=alt.Y("arm:N", title=None, sort=y_sort),
        x=alt.X("lo:Q", title="Systolic blood pressure (mm Hg)",
                scale=alt.Scale(zero=False, domain=[112, 142])),
        x2="hi:Q",
        color=alt.Color("arm:N", scale=arm_scale, legend=None),
        tooltip=[alt.Tooltip("arm:N"), alt.Tooltip("label:N", title="Protocol target")],
    )
    _achieved = alt.Chart(points).mark_point(size=170, filled=True, opacity=1.0).encode(
        y=alt.Y("arm:N", sort=y_sort),
        x=alt.X("value:Q"),
        color=alt.Color("arm:N", scale=arm_scale, legend=None),
        shape=alt.Shape(
            "kind:N",
            scale=alt.Scale(
                domain=["Achieved mean at 1 year", "Mean over median 3.26-yr follow-up"],
                range=["circle", "diamond"],
            ),
            legend=alt.Legend(title="Achieved SBP"),
        ),
        tooltip=[
            alt.Tooltip("arm:N"),
            alt.Tooltip("kind:N", title="Measurement"),
            alt.Tooltip("value:Q", title="SBP (mm Hg)"),
        ],
    )
    interventions = style(
        (_band + _achieved).properties(
            width=CHART_W,
            height=170,
            title=alt.TitleParams(
                "Two targets, a real separation",
                subtitle=(
                    "Shaded band = everything below each arm's systolic target ceiling (protocol sets no lower "
                    "bound) · circle = achieved mean at 1 year · diamond = mean over the trial."
                ),
            ),
        )
    )

    _int, _std = ARMS[0], ARMS[1]
    interventions_view = mo.vstack(
        [
            mo.md(
                """
                ## Interventions & separation achieved
                _CONSORT items 13 & 24 — the intervention as specified, and as actually delivered._
                """
            ),
            mo.ui.altair_chart(interventions),
            mo.md(
                f"The strategies separated quickly and stayed separated: at 1 year the achieved mean systolic BP was "
                f"**{_int['achieved_1yr']} mm Hg** under intensive control versus **{_std['achieved_1yr']} mm Hg** "
                f"under standard care — a **{_std['achieved_1yr'] - _int['achieved_1yr']:.1f} mm Hg** difference, "
                f"sustained as **{_int['achieved_mean']} vs {_std['achieved_mean']} mm Hg** across the whole "
                f"follow-up. The cost was medication burden: **{_int['meds']} vs {_std['meds']}** antihypertensive "
                f"agents per patient on average (1-year diastolic means: 68.7 vs 76.3 mm Hg). The contrast being "
                f"tested was real, which is what makes the outcome signal credible."
            ),
        ],
        gap=0.35,
    )
    interventions_view
    return


@app.cell
def _(FLOW, box, colors, mo):
    # ----------------------- CONSORT FLOW DIAGRAM -----------------------
    arrow = f'<div style="text-align:center; color:{colors["muted"]}; font-size:1.1rem; line-height:1;">↓</div>'

    def note_box(title, sub):
        return f"""
        <div style="background:{colors['panel']}; border:1px dashed {colors['grid']};
                    border-radius:8px; padding:8px 10px; text-align:center;">
            <div style="font-size:0.92rem; color:{colors['ink']};">{title}</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin-top:2px;">{sub}</div>
        </div>"""

    _screened = (
        box("Assessed for eligibility", FLOW["screened"], colors["dark"])
        if FLOW["screened"] is not None
        else note_box("Assessed for eligibility", "count appears only in Fig. 1 — not in the retrieved full text")
    )

    flow_html = mo.Html(
        f"""
        <div style="font-family:Georgia, serif; max-width:720px; margin:0 auto;">
            {_screened}
            <div style="text-align:center; color:{colors['muted']}; font-size:1.1rem; margin:2px 0;">↓</div>
            {box("Randomised", FLOW["randomized"], colors["accent"], "November 2010 – March 2013")}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div style="display:grid; gap:6px;">
                    {box("Allocated: intensive target", FLOW["int_assigned"], colors["intensive"], "target <120 mm Hg")}
                    {arrow}
                    {box("Analysed (intention-to-treat)", FLOW["int_analyzed"], colors["intensive"], "primary outcome")}
                </div>
                <div style="display:grid; gap:6px;">
                    {box("Allocated: standard target", FLOW["std_assigned"], colors["standard"], "target <140 mm Hg")}
                    {arrow}
                    {box("Analysed (intention-to-treat)", FLOW["std_analyzed"], colors["standard"], "primary outcome")}
                </div>
            </div>
        </div>
        """
    )

    flow_view = mo.vstack(
        [
            mo.md(
                """
                ## Participant flow
                _CONSORT item 22 — rebuilt from the counts. The main text reports no post-randomisation
                exclusions: everyone randomised was analysed as assigned. Pre-randomisation screening counts
                live in Figure 1 of the paper, which the retrieved full text does not include, so that box is
                left visibly empty rather than guessed._
                """
            ),
            flow_html,
        ],
        gap=0.35,
    )
    flow_view
    return


@app.cell
def _(BASELINE, mo):
    # --------------------------- BASELINE ---------------------------
    _rows = "\n".join(f"| {label} | {iv} | {sv} |" for label, iv, sv in BASELINE)
    baseline_text = (
        "## Baseline characteristics\n"
        "_CONSORT item 25. Highlights from Table 1 (N = 4,678 intensive / 4,683 standard). The paper reports "
        "no significant differences except statin use (42.6% vs 44.7%, P = 0.04) — the cohorts are twins, so "
        "the outcome contrast is unlikely to be confounding._\n\n"
        "| Characteristic | Intensive | Standard |\n"
        "|:---|:---|:---|\n"
        f"{_rows}"
    )
    baseline_view = mo.md(baseline_text)
    baseline_view
    return


@app.cell
def _(CHART_W, OUTCOMES, alt, colors, mo, pl, rate_mode, style):
    # ---------- PRIMARY OUTCOME: paired annualised rates / counts ----------
    # Why no icon array: SPRINT's endpoints are time-to-event. Events accrue
    # unevenly under censoring and the paper reports ANNUALISED rates and
    # hazard ratios, not fixed-denominator risks. A 10x10 "patients per
    # hundred" array would imply a common, closed follow-up period the trial
    # never had. Paired rates + a forest plot are the honest shapes here.
    _chart_outcomes = [o for o in OUTCOMES if o["short"] != "Renal: ≥30% eGFR decline (no baseline CKD)"]
    _order = [o["short"] for o in sorted(_chart_outcomes, key=lambda o: -o["std_rate"])]

    _by_rate = rate_mode.value == "Annualised rate (%/yr)"
    _i_field, _s_field = (("int_rate", "std_rate") if _by_rate else ("int_n", "std_n"))
    _unit = "% per year" if _by_rate else "events"

    _pair_rows = [
        {
            "short": o["short"],
            "int_v": o[_i_field],
            "std_v": o[_s_field],
            "ci": f'HR {o["hr"]} ({o["lo"]}–{o["hi"]})',
        }
        for o in _chart_outcomes
    ]
    _dot_rows = []
    for o in _chart_outcomes:
        _dot_rows.append({"short": o["short"], "arm": "Intensive", "v": o[_i_field]})
        _dot_rows.append({"short": o["short"], "arm": "Standard", "v": o[_s_field]})
    pairs = pl.DataFrame(_pair_rows)
    dots = pl.DataFrame(_dot_rows)

    rate_arm_scale = alt.Scale(domain=["Intensive", "Standard"], range=[colors["intensive"], colors["standard"]])

    _r_rule = alt.Chart(pairs).mark_rule(strokeWidth=3, color=colors["grid"]).encode(
        y=alt.Y("short:N", sort=_order, title=None),
        x=alt.X("int_v:Q", title=f'Annualised rate ({_unit})' if _by_rate else "Events during trial (n)",
                scale=alt.Scale(zero=False)),
        x2="std_v:Q",
        tooltip=[
            alt.Tooltip("short:N", title="Outcome"),
            alt.Tooltip("int_v:Q", title="Intensive"),
            alt.Tooltip("std_v:Q", title="Standard"),
            alt.Tooltip("ci:N", title="Effect"),
        ],
    )
    _pt = alt.Chart(dots).mark_point(size=150, filled=True).encode(
        y=alt.Y("short:N", sort=_order),
        x=alt.X("v:Q"),
        color=alt.Color("arm:N", scale=rate_arm_scale, legend=alt.Legend(title="Arm")),
        tooltip=[
            alt.Tooltip("short:N", title="Outcome"),
            alt.Tooltip("arm:N"),
            alt.Tooltip("v:Q", title=_unit),
        ],
    )
    rates = style(
        (_r_rule + _pt).properties(
            width=CHART_W,
            height=260,
            title=alt.TitleParams(
                "Every endpoint leans toward intensive control",
                subtitle=(
                    "Paired annualised event rates from Table 2 (renal endpoint excluded: different denominators — "
                    "participants without baseline CKD). Time-to-event endpoints: see the forest plot for HRs."
                    if _by_rate
                    else "Raw event counts from Table 2. Counts ignore unequal person-time — the annualised-rate "
                    "view is the fairer comparison."
                ),
            ),
        )
    )

    _pr = next(o for o in OUTCOMES if o["short"] == "Primary composite")
    rates_view = mo.vstack(
        [
            mo.md(
                """
                ## Primary outcome, in its native units
                _CONSORT item 26 asks for absolute AND relative effect. Each pair of dots is one outcome; the
                intensive dot sits left of the standard dot wherever intensive wins._
                """
            ),
            rate_mode,
            mo.ui.altair_chart(rates),
            mo.md(
                f"**Why no icon array here:** SPRINT reported **{_pr['int_n']} vs {_pr['std_n']} primary events as "
                f"annualised rates ({_pr['int_rate']}% vs {_pr['std_rate']}% per year)** with hazard ratios, not "
                "clean fixed-denominator risks. Patients entered over three years and were censored progressively, "
                "so any 10×10 \u201cpatients per hundred\u201d grid would imply a closed follow-up period the trial "
                "did not have. The absolute difference is real but time-indexed: "
                f"**{_pr['std_rate'] - _pr['int_rate']:.2f} percentage points per year**, worth **NNT 61 over the "
                "median 3.26 years** as the paper itself prints it."
            ),
        ],
        gap=0.35,
    )
    rates_view
    return


@app.cell
def _(CHART_W, OUTCOMES, alt, colors, mo, pl, style):
    # --------------- EFFECT ESTIMATES: forest plot (log HR) ---------------
    ef = pl.DataFrame(OUTCOMES)
    order = [o["short"] for o in OUTCOMES]

    kind_scale = alt.Scale(
        domain=["benefit", "harm", "ns"],
        range=[colors["good"], colors["bad"], colors["muted"]],
    )

    _f_rule = alt.Chart(ef).mark_rule(strokeWidth=2).encode(
        y=alt.Y("short:N", sort=order, title=None),
        x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=[0.3, 6]),
                title="Hazard ratio (log scale) — intensive vs standard"),
        x2="hi:Q",
        color=alt.Color("kind:N", scale=kind_scale, legend=None),
    )
    _f_pt = alt.Chart(ef).mark_point(size=110, filled=True).encode(
        y=alt.Y("short:N", sort=order),
        x="hr:Q",
        color=alt.Color("kind:N", scale=kind_scale, legend=alt.Legend(title="Direction")),
        tooltip=[
            alt.Tooltip("short:N", title="Outcome"),
            alt.Tooltip("hr:Q", title="HR"),
            alt.Tooltip("lo:Q", title="95% CI low"),
            alt.Tooltip("hi:Q", title="95% CI high"),
            alt.Tooltip("p:N", title="P"),
        ],
    )
    _null = alt.Chart(pl.DataFrame({"x": [1.0]})).mark_rule(
        strokeDash=[5, 4], color=colors["muted"]
    ).encode(x="x:Q")

    forest = style(
        (_null + _f_rule + _f_pt).properties(
            width=CHART_W,
            height=320,
            title=alt.TitleParams(
                "Benefit on the endpoints that kill; one harm to weigh",
                subtitle=(
                    "Hazard ratios with 95% CI, Table 2. Dashed line = HR 1 (no effect); intervals left of it "
                    "favour intensive control, right of it favour standard. The renal estimate comes from the "
                    "subgroup without baseline CKD."
                ),
            ),
        )
    )

    forest_view = mo.vstack(
        [
            mo.md(
                """
                ## Effect estimates
                _CONSORT item 26 — relative effects with precision. Death, heart failure, and the primary
                composite exclude HR = 1; the eGFR-decline signal excludes it in the other direction._
                """
            ),
            mo.ui.altair_chart(forest),
        ],
        gap=0.35,
    )
    forest_view
    return


@app.cell
def _(HARMS, SAE_OVERALL, SAE_RELATED, colors, mo, pill):
    # ------------------------- HARMS -------------------------
    _sae_rows = "\n".join(
        f"| {h['condition']} | {h['int_n']} ({h['int_pct']}%) | {h['std_n']} ({h['std_pct']}%) | P = {h['p']} |"
        for h in HARMS
        if h["tier"] == "Serious adverse event"
    )
    _ed_rows = "\n".join(
        f"| {h['condition']} | {h['int_n']} ({h['int_pct']}%) | {h['std_n']} ({h['std_pct']}%) | P = {h['p']} |"
        for h in HARMS
        if h["tier"] == "ED visit or SAE"
    )
    harms_md = mo.md(
        "## Harms\n"
        "_CONSORT items 15 & 27. Serious adverse events (conditions of interest) from Table 3, shown as data._\n\n"
        f"Overall, a serious adverse event occurred in **{SAE_OVERALL['int_n']:,} intensive participants "
        f"({SAE_OVERALL['int_pct']}%) vs {SAE_OVERALL['std_n']:,} ({SAE_OVERALL['std_pct']}%)** — HR "
        f"{SAE_OVERALL['hr']}, P = {SAE_OVERALL['p']}: the *net* safety balance was even. Events judged "
        f"possibly or definitely related to the intervention were higher (**{SAE_RELATED['int_n']} "
        f"({SAE_RELATED['int_pct']}%) vs {SAE_RELATED['std_n']} ({SAE_RELATED['std_pct']}%), HR "
        f"{SAE_RELATED['hr']}, P = {SAE_RELATED['p']}**). By condition:\n\n"
        "**Serious adverse event**\n\n"
        "| Condition of interest | Intensive (N = 4,678) | Standard (N = 4,683) | P |\n"
        "|:---|:---|:---|:---|\n"
        f"{_sae_rows}\n\n"
        "**Emergency-department visit or serious adverse event**\n\n"
        "| Condition of interest | Intensive | Standard | P |\n"
        "|:---|:---|:---|:---|\n"
        f"{_ed_rows}\n\n"
        "Hypotension, syncope, electrolyte abnormalities, and acute kidney injury or failure were all more "
        "common under intensive control. **Injurious falls were not** — the feared harm of aggressive "
        "treatment in older adults simply did not materialise (2.2% vs 2.3%, P = 0.71 as serious adverse "
        "events; 7.1% vs 7.1%, P = 0.97 including ED visits)."
    )

    harms_note = mo.Html(
        f"""
        <div style="background:{colors['panel2']}; border-left:4px solid {colors['warn']};
                    border-radius:8px; padding:12px 16px; font-family:Georgia, serif; color:{colors['ink']};">
            <strong>Why it matters:</strong> the kidney signal is the mechanistic tell. More diuretics,
            ACE inhibitors, and ARBs at lower pressures produced a reversible haemodynamic eGFR decline
            (HR 3.49 for ≥30% decline in those without baseline CKD), yet clinic-measured orthostatic
            hypotension was <em>less</em> frequent under intensive control (P = 0.01), and falls showed no
            increase. The harms are real, specific, and largely biochemical — {pill("reported")} against a
            mortality benefit of HR 0.73, they change the conversation from "whether" to "for whom and how
            carefully".
        </div>
        """
    )
    mo.vstack([harms_md, harms_note], gap=0.35)
    return


@app.cell
def _(TRIAL, colors, mo):
    # --------------------------- OPEN SCIENCE ---------------------------
    open_science = mo.Html(
        f"""
        <div style="font-family:Georgia, serif; color:{colors['ink']};">
            <h2 style="font-family:Georgia, serif;">Open science</h2>
            <p style="color:{colors['muted']}; margin-top:-0.4rem;">
                <em>CONSORT 2025's newest section (items 2–5) — and SPRINT's defining governance moment.</em>
            </p>
            <div style="background:#fffdf8; border:1px solid #ddd8ce; border-left:4px solid {colors['accent']};
                        border-radius:10px; padding:10px 14px; margin-bottom:12px; line-height:1.42;">
                <strong>Stopped early for benefit.</strong> On {TRIAL['stopped']} the NHLBI director accepted the
                independent DSMB's recommendation to inform investigators and participants and end the
                blood-pressure intervention, after the primary-outcome monitoring boundary was exceeded at two
                consecutive interim looks. Beneficence done right — with the honest caveat that early stops can
                exaggerate effects; SPRINT's own Fine–Gray competing-risk sensitivity analysis was virtually
                unchanged (HR 0.76, 0.64–0.89).
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:12px;">
                <div style="background:#fff; border:1px solid #e1ddd4; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Registration (item 2)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">{TRIAL['registration']}</div>
                </div>
                <div style="background:#fff; border:1px solid #e1ddd4; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Protocol & SAP (item 3)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">Protocol public; SAP not stated separately</div>
                </div>
                <div style="background:#fff; border:1px solid #e1ddd4; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Data sharing (item 4)</div>
                    <div style="color:{colors['bad']}; font-size:1.0rem;">Not addressed (2015)</div>
                </div>
                <div style="background:#fff; border:1px solid #e1ddd4; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Funding & COI (item 5)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">NIH/VA funded; donations & disclosures declared</div>
                </div>
            </div>
        </div>
        """
    )
    open_science
    return


@app.cell
def _(CHECKLIST, colors, mo, pill, section):
    # ---------------- CONSORT 2025 CHECKLIST COVERAGE ----------------
    _sel = section.value
    _rows_data = [r for r in CHECKLIST if _sel == "All sections" or r[0] == _sel]

    _counts = {"reported": 0, "partial": 0, "na": 0, "gap": 0}
    for _r in CHECKLIST:
        _counts[_r[3]] += 1
    _covered = _counts["reported"] + _counts["partial"]
    _top_level_items = len({"".join(ch for ch in row[1] if ch.isdigit()) for row in CHECKLIST})

    _table_rows = "".join(
        f"""<tr>
            <td style="padding:6px 10px; color:{colors['muted']}; white-space:nowrap;">{grp}</td>
            <td style="padding:6px 10px; font-variant-numeric:tabular-nums; color:{colors['ink']};">{num}</td>
            <td style="padding:6px 10px; color:{colors['ink']};">{topic}</td>
            <td style="padding:6px 10px;">{pill(status)}</td>
            <td style="padding:6px 10px; color:{colors['muted']}; font-size:0.85rem;">{note}</td>
        </tr>"""
        for grp, num, topic, status, note in _rows_data
    )

    checklist_html = mo.Html(
        f"""
        <div style="font-family:Georgia, serif;">
            <table style="border-collapse:collapse; width:100%; font-family:Georgia, serif;">
                <thead>
                    <tr style="border-bottom:2px solid {colors['grid']}; text-align:left;
                               font-size:0.72rem; text-transform:uppercase; letter-spacing:0.06em; color:{colors['muted']};">
                        <th style="padding:6px 10px;">Section</th>
                        <th style="padding:6px 10px;">Item</th>
                        <th style="padding:6px 10px;">Topic</th>
                        <th style="padding:6px 10px;">In SPRINT</th>
                        <th style="padding:6px 10px;">Where / note</th>
                    </tr>
                </thead>
                <tbody>{_table_rows}</tbody>
            </table>
        </div>
        """
    )

    coverage_note = mo.Html(
        f"""
        <div style="background:{colors['panel']}; border:1px solid #ddd8ce; border-radius:10px;
                    padding:14px 16px; font-family:Georgia, serif; color:{colors['ink']};">
            Of the {_top_level_items} top-level CONSORT 2025 items ({len(CHECKLIST)} checklist rows), this
            2015 paper substantively covers <strong>{_covered} of {len(CHECKLIST)} rows</strong>. What is missing is
            instructive: <strong>data sharing (item 4)</strong> and <strong>patient &amp; public involvement
            (item 8)</strong> are expectations CONSORT <em>added after</em> 2015, and the handful of
            <em>partial</em> rows — allocation concealment, sequence generation, the statistical analysis plan —
            are details SPRINT delegated to its supplementary appendix rather than omitted. Reading a landmark
            against a newer checklist is less an audit of the trial than a picture of how reporting norms moved.
        </div>
        """
    )

    checklist_view = mo.vstack(
        [
            mo.md(
                """
                ## The CONSORT 2025 checklist, item by item
                _Filter by section. Each row pairs a checklist item with where SPRINT reports it._
                """
            ),
            mo.hstack(
                [
                    section,
                    mo.md(
                        f"{pill('reported')} {_counts['reported']} &nbsp; {pill('partial')} {_counts['partial']} "
                        f"&nbsp; {pill('na')} {_counts['na']} &nbsp; {pill('gap')} {_counts['gap']}"
                    ),
                ],
                justify="start",
                gap=1.5,
                align="center",
            ),
            checklist_html,
            coverage_note,
        ],
        gap=0.4,
    )
    checklist_view
    return


@app.cell
def _(TRIAL, colors, mo):
    # ------------------------- PROVENANCE -------------------------
    provenance = mo.Html(
        f"""
        <div style="font-family:Georgia, serif; color:{colors['muted']}; font-size:0.86rem;
                    border-top:1px solid {colors['grid']}; padding-top:12px; line-height:1.5;">
            <strong style="color:{colors['ink']};">Source & provenance.</strong>
            {TRIAL['citation']} DOI <a href="https://doi.org/{TRIAL['doi']}" style="color:{colors['standard']};">{TRIAL['doi']}</a>.
            Registered as {TRIAL['registration']}.
            Checklist: Hopewell S, et al. CONSORT 2025 Statement. <em>BMJ</em> 2025;388:e081123.
            Every figure is rendered from the data literals near the top of this notebook; SPRINT printed event
            counts alongside annualised rates, so no denominator reconstruction was needed anywhere.
            The intervention ended <strong>early for benefit on the DSMB's recommendation</strong>, accepted
            {TRIAL['stopped']} at a median follow-up of {TRIAL['median_fu_years']} years; the primary-outcome
            figure therefore shows paired <strong>annualised rates and hazard ratios rather than patient-level
            icon arrays</strong>, because time-to-event endpoints with progressive censoring have no clean
            fixed denominator for a per-hundred grid (numbers needed to treat are quoted as published: NNT 61,
            90, and 172 over the median follow-up).
            Pre-randomisation screening and exclusion counts appear only in Figure 1 (image), which the
            retrieved full text does not contain; the flow diagram shows that gap rather than guessing.
            CONSORT 2025 is applied here as a modern reading lens — it postdates the 2015 trial.
        </div>
        """
    )
    provenance
    return


if __name__ == "__main__":
    app.run()
