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
        "ink": "#002657",
        "muted": "#5B6472",
        "paper": "#ffffff",
        "panel": "#F5F7FC",
        "panel2": "#FFF4EF",
        "grid": "#C7C9C8",
        "intensive": "#FA4616",  # intervention arm -> UF orange
        "standard": "#0021A5",   # reference arm -> UF blue
        "accent": "#F2A900",
        "good": "#22884C",
        "warn": "#F2A900",
        "bad": "#D32737",
        "good_bg": "#EAF6EE",
        "warn_bg": "#FFF4D6",
        "bad_bg": "#FCEAEC",
        "neutral_bg": "#F0F1F3",
        "dark": "#002657",
    }
    FONT = "Inter, ui-sans-serif, system-ui, sans-serif"
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
        <div style="background:#ffffff; border:1px solid #D8D4D7; border-radius:10px; padding:10px 12px;">
            <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.1em; color:{colors['muted']};">{kicker}</div>
            <div style="font-size:1.42rem; color:{color}; margin:1px 0;">{big}</div>
            <div style="font-size:0.86rem; color:{colors['muted']}; line-height:1.28;">{small}</div>
        </div>"""

    def box(title, n, color, sub=""):
        sub_html = f'<div style="font-size:0.78rem; color:{colors["muted"]}; margin-top:2px;">{sub}</div>' if sub else ""
        return f"""
        <div style="background:{colors['paper']}; border:1px solid #D8D4D7; border-left:4px solid {color};
                    border-radius:8px; padding:8px 10px; text-align:center;">
            <div style="font-size:0.92rem; color:{colors['ink']};">{title}</div>
            <div style="font-size:1.25rem; color:{color}; font-weight:600;">n = {n:,}</div>
            {sub_html}
        </div>"""

    def pill(status):
        spec = {
            "reported": (colors["good"], colors["good_bg"], "Reported"),
            "partial": (colors["warn"], colors["warn_bg"], "Partial"),
            "na": (colors["muted"], colors["neutral_bg"], "N/A"),
            "gap": (colors["bad"], colors["bad_bg"], "Not addressed"),
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
def _(CHECKLIST, FONT, colors, mo, pill):
    # Shared inline CONSORT reader. The checklist guides the visible notebook.
    _section_order = [
        "Title and abstract",
        "Open science",
        "Introduction",
        "Methods",
        "Results",
        "Discussion",
    ]

    def _slug(section_name):
        return section_name.lower().replace(" ", "-").replace("&", "and")

    def _section_rows(section_name):
        return [row for row in CHECKLIST if row[0] == section_name]

    def _status_counts(rows):
        counts = {"reported": 0, "partial": 0, "na": 0, "gap": 0}
        for row in rows:
            counts[row[3]] += 1
        return counts

    def chapter_header(section_name, intro):
        rows = _section_rows(section_name)
        counts = _status_counts(rows)
        status_html = " ".join(
            f"{pill(status)} <span style='color:{colors['muted']}; font-size:0.78rem; margin-right:8px;'>{count}</span>"
            for status, count in counts.items()
            if count
        )
        return mo.Html(
            f"""
            <div id="{_slug(section_name)}" style="scroll-margin-top:24px; border-top:1px solid {colors['grid']}; padding-top:18px; font-family:{FONT};">
                <div style="display:flex; justify-content:space-between; gap:16px; align-items:flex-start; flex-wrap:wrap;">
                    <div>
                        <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.12em; color:{colors['muted']};">CONSORT 2025 chapter</div>
                        <h2 style="font-family:{FONT}; color:{colors['dark']}; margin:2px 0 4px;">{section_name}</h2>
                        <div style="color:{colors['muted']}; max-width:760px; line-height:1.42;">{intro}</div>
                    </div>
                    <div style="display:flex; align-items:center; flex-wrap:wrap; gap:4px; padding-top:4px;">{status_html}</div>
                </div>
            </div>
            """
        )

    def consort_items(item_ids, title=""):
        wanted = set(item_ids)
        rows = [row for row in CHECKLIST if row[1] in wanted]
        counts = _status_counts(rows)
        status_names = {
            "reported": "reported",
            "partial": "partial",
            "na": "not applicable",
            "gap": "not addressed",
        }
        status_summary = " · ".join(
            f"{count} {status_names[status]}"
            for status, count in counts.items()
            if count
        )
        item_word = "item" if len(rows) == 1 else "items"
        fold_title = f"{title or 'Checklist items'} · {len(rows)} {item_word} · {status_summary}"
        rows_html = "".join(
            f"""
            <div style="display:grid; grid-template-columns:minmax(42px,auto) minmax(0,1fr) auto; gap:10px; align-items:start;
                        padding:9px 0; border-top:1px solid {colors['grid']};">
                <div style="font-size:0.78rem; font-weight:700; color:{colors['dark']}; padding-top:2px;">{item}</div>
                <div>
                    <div style="font-size:0.88rem; font-weight:650; color:{colors['ink']};">{topic}</div>
                    <div style="font-size:0.82rem; color:{colors['muted']}; line-height:1.38; margin-top:2px;">{note}</div>
                </div>
                <div>{pill(status)}</div>
            </div>
            """
            for _section, item, topic, status, note in rows
        )
        item_rows = mo.Html(
            f"""
            <div style="font-family:{FONT}; color:{colors['ink']}; padding:0 6px 4px;">{rows_html}</div>
            """
        )
        return mo.accordion({fold_title: item_rows})

    def section_nav():
        nav_items = []
        for section_name in _section_order:
            rows = _section_rows(section_name)
            counts = _status_counts(rows)
            covered = counts["reported"] + counts["partial"]
            gap_text = f", {counts['gap']} gap" if counts["gap"] else ""
            nav_items.append(
                f"[{section_name}](#{_slug(section_name)}) ({covered}/{len(rows)} covered{gap_text})"
            )
        return mo.md("**Read the trial by CONSORT section**\n\n" + " · ".join(nav_items))

    def coverage_summary():
        counts = _status_counts(CHECKLIST)
        covered = counts["reported"] + counts["partial"]
        top_level = len({"".join(ch for ch in row[1] if ch.isdigit()) for row in CHECKLIST})
        gaps = [f"item {row[1]} ({row[2].lower()})" for row in CHECKLIST if row[3] == "gap"]
        not_applicable = [f"item {row[1]} ({row[2].lower()})" for row in CHECKLIST if row[3] == "na"]
        gap_text = ", ".join(gaps) if gaps else "none"
        na_text = ", ".join(not_applicable) if not_applicable else "none"
        return mo.Html(
            f"""
            <div style="font-family:{FONT}; border-top:1px solid {colors['grid']}; padding-top:16px; color:{colors['ink']}; line-height:1.5;">
                <h3 style="font-family:{FONT}; margin:0 0 6px; color:{colors['dark']};">Coverage summary</h3>
                <div style="color:{colors['muted']}; margin-bottom:6px;">
                    {counts['reported']} reported · {counts['partial']} partial · {counts['na']} not applicable · {counts['gap']} not addressed
                </div>
                <div>
                    Of the <strong>{top_level} top-level CONSORT 2025 items ({len(CHECKLIST)} reporting rows)</strong>,
                    the report substantively covers <strong>{covered} rows</strong>. The gaps are
                    <strong>{gap_text}</strong>. Not-applicable rows are <strong>{na_text}</strong>.
                    The gap pattern shows which reporting expectations became standard after this 2015 trial.
                    See <a href="#open-science">Open science</a> and <a href="#methods">Methods</a> for the inline evidence.
                </div>
            </div>
            """
        )

    return chapter_header, consort_items, coverage_summary, section_nav


@app.cell
def _(mo):
    # Interactive primary-outcome view. It changes the unit shown in the chart.
    rate_mode = mo.ui.radio(
        options=["Annualised rate (%/yr)", "Events during trial (n)"],
        value="Annualised rate (%/yr)",
        label="Primary-outcome view",
        inline=True,
    )
    return (rate_mode,)


@app.cell
def _(ARMS, FLOW, NNT, OUTCOMES, TRIAL, card, colors, mo):
    # ---------------------------- HERO ----------------------------
    _primary = next(outcome for outcome in OUTCOMES if outcome["short"] == "Primary composite")
    _rate_difference = _primary["std_rate"] - _primary["int_rate"]
    hero = mo.Html(
        f"""
        <div style="background:{colors['panel']}; border:1px solid #D8D4D7; border-radius:14px;
                    padding:18px 20px; font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            <div style="text-transform:uppercase; letter-spacing:0.15em; font-size:0.72rem;
                        color:{colors['muted']}; margin-bottom:0.5rem;">
                A randomised trial, read through CONSORT 2025
            </div>
            <div style="font-size:1.82rem; line-height:1.12; margin-bottom:0.25rem;">{TRIAL['name']}</div>
            <div style="font-size:1.0rem; color:#343741; margin-bottom:0.35rem;">{TRIAL['title']}</div>
            <div style="max-width:820px; font-size:0.96rem; line-height:1.42; color:#343741; margin-bottom:0.85rem;">
                SPRINT compared systolic blood-pressure targets {ARMS[0]['target_label']} and {ARMS[1]['target_label']} in adults at high
                cardiovascular risk without diabetes. Intensive control reduced the primary cardiovascular outcome
                and all-cause mortality, but some serious adverse events were more common. The intervention stopped
                early for benefit.
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
                {card("Randomised population", f"{FLOW['randomized']:,}", f"{FLOW['int_assigned']:,} intensive · {FLOW['std_assigned']:,} standard · {TRIAL['centers']} sites", colors["ink"])}
                {card("Intervention: intensive target", f"{_primary['int_rate']}%/yr", f"{_primary['int_n']} events · HR {_primary['hr']} ({_primary['lo']}–{_primary['hi']}), P {_primary['p']}", colors["intensive"])}
                {card("Reference: standard target", f"{_primary['std_rate']}%/yr", f"{_primary['std_n']} events · median follow-up {TRIAL['median_fu_years']} years", colors["standard"])}
                {card("Main contrast", f"−{_rate_difference:.2f} pts/yr", f"Published NNT {NNT['primary']} over median follow-up · HR {_primary['hr']} ({_primary['lo']}–{_primary['hi']})", colors["good"])}
            </div>
        </div>
        """
    )
    hero
    return


@app.cell
def _(section_nav):
    navigator = section_nav()
    navigator
    return


@app.cell
def _(chapter_header, consort_items, mo):
    title_abstract_view = mo.vstack(
        [
            chapter_header(
                "Title and abstract",
                "Can a reader identify the study as randomised and understand its design, participants, interventions, and main result?",
            ),
            consort_items(["1a", "1b"]),
        ],
        gap=0.35,
    )
    title_abstract_view
    return


@app.cell
def _(CHECKLIST, TRIAL, card, chapter_header, colors, consort_items, mo):
    # --------------------------- OPEN SCIENCE ---------------------------
    _notes = {row[1]: row[4] for row in CHECKLIST}
    open_science_cards = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:12px;">
                {card("Registration · item 2", TRIAL["registration"], _notes["2"], colors["good"])}
                {card("Protocol & SAP · item 3", "Protocol public", _notes["3"], colors["good"])}
                {card("Data sharing · item 4", "Not addressed", _notes["4"], colors["bad"])}
                {card("Funding & COI · item 5", "Disclosed", f"{_notes['5a']} {_notes['5b']}", colors["good"])}
            </div>
        </div>
        """
    )
    open_science_view = mo.vstack(
        [
            chapter_header(
                "Open science",
                "Registration, protocol access, data availability, funding, and conflicts determine whether readers can audit the trial.",
            ),
            consort_items(["2", "3", "4", "5a", "5b"], "Registration, protocol, sharing, and funding"),
            open_science_cards,
        ],
        gap=0.4,
    )
    open_science_view
    return


@app.cell
def _(CHECKLIST, chapter_header, consort_items, mo):
    # --------------------------- INTRODUCTION ---------------------------
    _rationale = next(row[4] for row in CHECKLIST if row[1] == "6")
    _objective = next(row[4] for row in CHECKLIST if row[1] == "7")
    introduction_view = mo.vstack(
        [
            chapter_header(
                "Introduction",
                "Why was the trial needed, and which benefit and harm question did the investigators test?",
            ),
            consort_items(["6", "7"], "Rationale and objectives"),
            mo.md(
                f"**Rationale.** {_rationale}.\n\n"
                f"**Clinical question.** {_objective}. SPRINT tested whether a lower systolic-pressure target "
                "reduced cardiovascular events without an unacceptable increase in treatment-related harm."
            ),
        ],
        gap=0.4,
    )
    introduction_view
    return


@app.cell
def _(CHECKLIST, TRIAL, chapter_header, consort_items, mo):
    # ----------------------------- METHODS -----------------------------
    _notes = {row[1]: row[4] for row in CHECKLIST}
    design = mo.md(
        "### Trial design in one paragraph\n\n"
        f"**{TRIAL['name']}** was a multicentre, parallel-group, **open-label randomised trial** at "
        f"{TRIAL['centers']} sites in {TRIAL['networks']} networks in {TRIAL['geography']}. Adults with elevated "
        "systolic blood pressure and increased cardiovascular risk were allocated 1:1, stratified by clinical site, "
        "to an intensive or standard systolic-pressure target. Participants and treatment personnel knew the "
        "assignment, but outcome adjudicators were masked. The primary analysis included all randomly assigned "
        "participants as assigned and used clinic-stratified Cox regression. The prespecified intervention stopped "
        f"early on {TRIAL['stopped']} after the monitoring boundary was crossed; median follow-up was "
        f"{TRIAL['median_fu_years']} years. The report states the eligibility criteria as **{_notes['12a']}** and "
        f"the intervention contrast as **{_notes['13']}**. Recruitment ran {TRIAL['recruitment']}."
    )
    methods_view = mo.vstack(
        [
            chapter_header(
                "Methods",
                "How was the trial planned, who was eligible, what care was assigned, and how were bias and uncertainty handled?",
            ),
            consort_items(["8", "9", "10", "11", "12a", "12b"], "Design, setting, and participants"),
            design,
            consort_items(["13", "14", "15"], "Interventions, outcomes, and harms assessment"),
            consort_items(
                ["16a", "16b", "17a", "17b", "18", "19", "20a", "20b", "21a", "21b", "21c", "21d"],
                "Sample size, randomisation, masking, and analysis",
            ),
        ],
        gap=0.5,
    )
    methods_view
    return


@app.cell
def _(chapter_header):
    results_header = chapter_header(
        "Results",
        "Who entered the trial, what treatment they received, and what benefits, harms, and uncertainties were observed?",
    )
    results_header
    return


@app.cell
def _(ARMS, CHART_W, alt, colors, consort_items, mo, pl, style):
    # ------------- INTERVENTION DELIVERY: target and achieved pressure -------------
    _arm_names = [arm["arm"] for arm in ARMS]
    _arm_colors = [colors["intensive"], colors["standard"]]
    _view_floor = min(
        value
        for arm in ARMS
        for value in (arm["achieved_1yr"], arm["achieved_mean"], arm["target_ceiling"])
    ) - 8
    _view_ceiling = max(
        value
        for arm in ARMS
        for value in (arm["achieved_1yr"], arm["achieved_mean"], arm["target_ceiling"])
    ) + 4
    _band_rows = []
    _point_rows = []
    for arm in ARMS:
        _band_rows.append(
            {
                "arm": arm["arm"],
                "lo": _view_floor,
                "hi": arm["target_ceiling"],
                "label": f'Target {arm["target_label"]} (no protocol lower bound)',
            }
        )
        _point_rows.extend(
            [
                {"arm": arm["arm"], "kind": "Achieved mean at 1 year", "value": arm["achieved_1yr"]},
                {"arm": arm["arm"], "kind": "Mean over median follow-up", "value": arm["achieved_mean"]},
            ]
        )
    _bands = pl.DataFrame(_band_rows)
    _points = pl.DataFrame(_point_rows)
    _arm_scale = alt.Scale(domain=_arm_names, range=_arm_colors)
    _band = alt.Chart(_bands).mark_bar(height=26, opacity=0.35, cornerRadius=3).encode(
        y=alt.Y("arm:N", title=None, sort=_arm_names),
        x=alt.X("lo:Q", title="Systolic blood pressure (mm Hg)", scale=alt.Scale(domain=[_view_floor, _view_ceiling])),
        x2="hi:Q",
        color=alt.Color("arm:N", scale=_arm_scale, legend=None),
        tooltip=[alt.Tooltip("arm:N"), alt.Tooltip("label:N", title="Protocol target")],
    )
    _achieved = alt.Chart(_points).mark_point(size=170, filled=True).encode(
        y=alt.Y("arm:N", sort=_arm_names),
        x=alt.X("value:Q"),
        color=alt.Color("arm:N", scale=_arm_scale, legend=None),
        shape=alt.Shape(
            "kind:N",
            scale=alt.Scale(
                domain=["Achieved mean at 1 year", "Mean over median follow-up"],
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
                "The assigned targets produced sustained blood-pressure separation",
                subtitle="The shaded band ends at the target ceiling; the circle shows the 1-year mean and the diamond the trial mean.",
            ),
        )
    )
    _intensive, _standard = ARMS[0], ARMS[1]
    fidelity_view = mo.vstack(
        [
            consort_items(["24a", "24b"], "Intervention delivery and concomitant care"),
            mo.md("### Intervention delivery\n_The chart compares protocol targets with achieved systolic pressure._"),
            mo.ui.altair_chart(interventions),
            mo.md(
                f"At 1 year, mean systolic pressure was **{_intensive['achieved_1yr']} mm Hg** under intensive control "
                f"versus **{_standard['achieved_1yr']} mm Hg** under standard care. The difference persisted across "
                f"follow-up (**{_intensive['achieved_mean']} vs {_standard['achieved_mean']} mm Hg**). Participants used "
                f"**{_intensive['meds']} vs {_standard['meds']}** antihypertensive agents per patient on average."
            ),
        ],
        gap=0.4,
    )
    fidelity_view
    return


@app.cell
def _(ARMS, FLOW, TRIAL, box, colors, consort_items, mo):
    # ----------------------- CONSORT FLOW DIAGRAM -----------------------
    def _note_box(title, sub):
        return f"""
        <div style="background:{colors['panel']}; border:1px dashed {colors['grid']};
                    border-radius:8px; padding:8px 10px; text-align:center;">
            <div style="font-size:0.92rem; color:{colors['ink']};">{title}</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin-top:2px;">{sub}</div>
        </div>"""

    _screened = (
        box("Assessed for eligibility", FLOW["screened"], colors["dark"])
        if FLOW["screened"] is not None
        else _note_box("Assessed for eligibility", "count appears only in Figure 1 — not in the retrieved full text")
    )
    arrow = f'<div style="text-align:center; color:{colors["muted"]}; font-size:1.1rem; line-height:1;">↓</div>'
    flow_html = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; max-width:720px; margin:0 auto;">
            {_screened}
            {arrow}
            {box("Randomised", FLOW["randomized"], colors["accent"], TRIAL["recruitment"])}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div style="display:grid; gap:6px;">
                    {box("Allocated: intensive target", FLOW["int_assigned"], colors["intensive"], f"target {ARMS[0]['target_label']}")}
                    {arrow}
                    {box("Analysed (intention-to-treat)", FLOW["int_analyzed"], colors["intensive"], "primary outcome; no post-randomisation exclusions reported")}
                </div>
                <div style="display:grid; gap:6px;">
                    {box("Allocated: standard target", FLOW["std_assigned"], colors["standard"], f"target {ARMS[1]['target_label']}")}
                    {arrow}
                    {box("Analysed (intention-to-treat)", FLOW["std_analyzed"], colors["standard"], "primary outcome; no post-randomisation exclusions reported")}
                </div>
            </div>
        </div>
        """
    )
    flow_view = mo.vstack(
        [
            consort_items(["22a", "22b", "23a", "23b"], "Participant flow and recruitment"),
            mo.md(
                "### Participant flow\n_The reported randomised and analysed counts close at each arm. "
                "The pre-randomisation screening count is left visibly empty because it appears only in the retrieved figure._"
            ),
            flow_html,
        ],
        gap=0.4,
    )
    flow_view
    return


@app.cell
def _(ARMS, BASELINE, CHART_W, FLOW, FONT, colors, consort_items, mo):
    # --------------------------- BASELINE ---------------------------
    import re as _re_sprint_baseline

    _profile_rows = []
    for _label, _int_value, _std_value in BASELINE:
        if any(
            token in _label
            for token in (
                "Age ≥ 75",
                "Female sex",
                "Chronic kidney disease",
                "Cardiovascular disease",
                "Framingham 10-yr risk",
            )
        ):
            _int_match = _re_sprint_baseline.search(r"([\d.]+)%", _int_value)
            _std_match = _re_sprint_baseline.search(r"([\d.]+)%", _std_value)
            if _int_match and _std_match:
                _profile_rows.append(
                    {
                        "label": _label,
                        "int_pct": float(_int_match.group(1)),
                        "std_pct": float(_std_match.group(1)),
                    }
                )
    _bars = []
    for _row in _profile_rows:
        _bars.append(
            f"""
            <div style="display:grid; grid-template-columns:245px minmax(150px,1fr) 48px; gap:9px; align-items:center; margin:7px 0;">
                <div style="font-size:0.78rem; color:{colors['ink']};">{_row['label']} · {ARMS[0]['arm']}</div>
                <div style="height:15px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                    <div style="width:{_row['int_pct']}%; height:100%; background:{colors['intensive']}; border-radius:3px;"></div>
                </div>
                <div style="font-size:0.78rem; font-weight:700; color:{colors['intensive']}; text-align:right;">{_row['int_pct']:g}%</div>
            </div>
            <div style="display:grid; grid-template-columns:245px minmax(150px,1fr) 48px; gap:9px; align-items:center; margin:7px 0 12px;">
                <div style="font-size:0.78rem; color:{colors['ink']};">{_row['label']} · {ARMS[1]['arm']}</div>
                <div style="height:15px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                    <div style="width:{_row['std_pct']}%; height:100%; background:{colors['standard']}; border-radius:3px;"></div>
                </div>
                <div style="font-size:0.78rem; font-weight:700; color:{colors['standard']}; text-align:right;">{_row['std_pct']:g}%</div>
            </div>
            """
        )
    profile_panel = mo.Html(
        f"""
        <div role="img" aria-label="Selected baseline characteristics by randomised arm" style="font-family:{FONT}; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">The randomised groups had similar baseline profiles</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 12px;">Bars show selected percentages printed in Table 1. Orange and blue retain the randomised-arm mapping.</div>
            {''.join(_bars)}
        </div>
        """
    )
    _rows = "\n".join(f"| {label} | {value_int} | {value_std} |" for label, value_int, value_std in BASELINE)
    baseline_table = mo.md(
        "| Characteristic | " + ARMS[0]["arm"] + " | " + ARMS[1]["arm"] + " |\n"
        "|:---|:---|:---|\n"
        f"{_rows}"
    )
    baseline_view = mo.vstack(
        [
            consort_items(["25"], "Baseline data"),
            mo.md(
                f"### Baseline profile\nThe trial randomised **{FLOW['randomized']:,} participants**. "
                "The source report describes the groups as balanced except for statin use."
            ),
            profile_panel,
            mo.accordion({"Full reported baseline summary": baseline_table}),
        ],
        gap=0.5,
    )
    baseline_view
    return


@app.cell
def _(ARMS, CHART_W, NNT, OUTCOMES, alt, colors, consort_items, mo, pl, rate_mode, style):
    # ---------- PRIMARY OUTCOME: paired annualised rates / counts ----------
    # SPRINT reports time-to-event endpoints with unequal follow-up. A fixed
    # denominator icon array would imply a common follow-up period, so this
    # view uses the paper's annualised rates or raw event counts.
    _arm_names = [arm["arm"] for arm in ARMS]
    _chart_outcomes = [outcome for outcome in OUTCOMES if "renal" not in outcome["short"].lower()]
    _order = [outcome["short"] for outcome in sorted(_chart_outcomes, key=lambda row: -row["std_rate"])]
    _by_rate = rate_mode.value == "Annualised rate (%/yr)"
    _int_field, _std_field = (("int_rate", "std_rate") if _by_rate else ("int_n", "std_n"))
    _unit = "% per year" if _by_rate else "events"
    _pair_rows = [
        {
            "short": outcome["short"],
            "int_v": outcome[_int_field],
            "std_v": outcome[_std_field],
            "effect": f'HR {outcome["hr"]} ({outcome["lo"]}–{outcome["hi"]})',
        }
        for outcome in _chart_outcomes
    ]
    _dot_rows = []
    for outcome in _chart_outcomes:
        _dot_rows.extend(
            [
                {"short": outcome["short"], "arm": _arm_names[0], "v": outcome[_int_field]},
                {"short": outcome["short"], "arm": _arm_names[1], "v": outcome[_std_field]},
            ]
        )
    _pairs = pl.DataFrame(_pair_rows)
    _dots = pl.DataFrame(_dot_rows)
    _arm_scale = alt.Scale(domain=_arm_names, range=[colors["intensive"], colors["standard"]])
    _rule = alt.Chart(_pairs).mark_rule(strokeWidth=3, color=colors["grid"]).encode(
        y=alt.Y("short:N", sort=_order, title=None),
        x=alt.X("int_v:Q", title=f"Annualised rate ({_unit})" if _by_rate else "Events during trial (n)", scale=alt.Scale(zero=False)),
        x2="std_v:Q",
        tooltip=[
            alt.Tooltip("short:N", title="Outcome"),
            alt.Tooltip("int_v:Q", title="Intensive"),
            alt.Tooltip("std_v:Q", title="Standard"),
            alt.Tooltip("effect:N", title="Effect estimate"),
        ],
    )
    _points = alt.Chart(_dots).mark_point(size=150, filled=True).encode(
        y=alt.Y("short:N", sort=_order),
        x=alt.X("v:Q"),
        color=alt.Color("arm:N", scale=_arm_scale, legend=alt.Legend(title="Arm")),
        tooltip=[alt.Tooltip("short:N", title="Outcome"), alt.Tooltip("arm:N", title="Arm"), alt.Tooltip("v:Q", title=_unit)],
    )
    rates_chart = style(
        (_rule + _points).properties(
            width=CHART_W,
            height=260,
            title=alt.TitleParams(
                "Annualised event rates were lower with intensive control",
                subtitle=(
                    "Paired annualised rates from Table 2. The renal endpoint uses different denominators and is shown in the forest plot."
                    if _by_rate
                    else "Raw event counts from Table 2. Counts do not adjust for unequal person-time; the annualised-rate view is the appropriate comparison."
                ),
            ),
        )
    )
    _primary = next(outcome for outcome in OUTCOMES if outcome["short"] == "Primary composite")
    primary_view = mo.vstack(
        [
            consort_items(["26"], "Numbers analysed, outcomes, and estimation"),
            mo.md(
                "### Primary outcome, in its native units\n"
                "**Read it as:** Each pair of dots compares an outcome value in the intensive and standard groups; the "
                "grey rule joins the two values.\n\n"
                "**Why this geometry:** SPRINT reports time-to-event outcomes as annualised rates and hazard ratios. "
                "Participants had unequal follow-up, so a fixed-denominator icon array would be misleading."
            ),
            rate_mode,
            mo.ui.altair_chart(rates_chart),
            mo.md(
                f"**What it says:** The primary composite occurred in **{_primary['int_n']} vs {_primary['std_n']} participants**, "
                f"with annualised rates of **{_primary['int_rate']}% vs {_primary['std_rate']}% per year**. The absolute "
                f"difference was **{_primary['std_rate'] - _primary['int_rate']:.2f} percentage points per year**. The hazard "
                f"ratio was **{_primary['hr']} (95% CI {_primary['lo']}–{_primary['hi']}; P {_primary['p']})**. The paper "
                f"reported NNT **{NNT['primary']}** over the median follow-up."
            ),
        ],
        gap=0.4,
    )
    primary_view
    return


@app.cell
def _(CHART_W, HARMS, OUTCOMES, SAE_OVERALL, alt, colors, mo, pl, style):
    # --------------- EFFECT ESTIMATES: forest plot (log HR) ---------------
    _effect_table = pl.DataFrame(OUTCOMES)
    _order = [outcome["short"] for outcome in OUTCOMES]
    _lo_all = min(outcome["lo"] for outcome in OUTCOMES)
    _hi_all = max(outcome["hi"] for outcome in OUTCOMES)
    _x_domain = [max(0.25, _lo_all * 0.8), _hi_all * 1.2]
    _kind_scale = alt.Scale(
        domain=["benefit", "harm", "ns"],
        range=[colors["good"], colors["bad"], colors["muted"]],
    )
    _rules = alt.Chart(_effect_table).mark_rule(strokeWidth=2).encode(
        y=alt.Y("short:N", sort=_order, title=None),
        x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=_x_domain), title="Hazard ratio (log scale) — intensive vs standard"),
        x2="hi:Q",
        color=alt.Color("kind:N", scale=_kind_scale, legend=None),
    )
    _points = alt.Chart(_effect_table).mark_point(size=110, filled=True).encode(
        y=alt.Y("short:N", sort=_order),
        x="hr:Q",
        color=alt.Color("kind:N", scale=_kind_scale, legend=alt.Legend(title="Direction")),
        tooltip=[
            alt.Tooltip("short:N", title="Outcome"),
            alt.Tooltip("hr:Q", title="HR"),
            alt.Tooltip("lo:Q", title="95% CI low"),
            alt.Tooltip("hi:Q", title="95% CI high"),
            alt.Tooltip("p:N", title="P"),
        ],
    )
    _null = alt.Chart(pl.DataFrame({"x": [1.0]})).mark_rule(strokeDash=[5, 4], color=colors["muted"]).encode(x="x:Q")
    forest = style(
        (_null + _rules + _points).properties(
            width=CHART_W,
            height=320,
            title=alt.TitleParams(
                "Intensive control reduced cardiovascular outcomes and increased renal injury",
                subtitle="Points show hazard ratios from Table 2; rules show 95% CIs. The dashed line marks HR = 1. The renal estimate uses the subgroup without baseline CKD.",
            ),
        )
    )
    forest_view = mo.vstack(
        [
            mo.md("### Relative effect estimates\n_The forest plot shows the primary, key secondary, and renal estimates with their uncertainty._"),
            mo.ui.altair_chart(forest),
        ],
        gap=0.4,
    )
    forest_view
    return


@app.cell
def _(ARMS, CHART_W, FONT, HARMS, SAE_OVERALL, SAE_RELATED, colors, consort_items, mo):
    # ------------------------- HARMS + SECONDARY -------------------------
    _serious = [harm for harm in HARMS if harm["tier"] == "Serious adverse event"]
    _arm_specs = [(ARMS[0]["arm"], colors["intensive"]), (ARMS[1]["arm"], colors["standard"])]
    _blocks = []
    for harm in _serious:
        _blocks.append(
            f"""
            <div style="padding:8px 0 10px; border-top:1px solid {colors['grid']};">
                <div style="font-size:0.82rem; font-weight:700; color:{colors['dark']};">{harm['condition']} <span style="font-size:0.76rem; font-weight:400; color:{colors['muted']};">P = {harm['p']}</span></div>
                <div style="display:grid; gap:5px; margin-top:6px;">
                    <div style="display:grid; grid-template-columns:150px minmax(120px,1fr) 110px; gap:8px; align-items:center;">
                        <span style="font-size:0.76rem; color:{colors['ink']};">{_arm_specs[0][0]}</span>
                        <span style="height:14px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;"><span style="display:block; width:{harm['int_pct']}%; height:100%; background:{_arm_specs[0][1]};"></span></span>
                        <span style="font-size:0.75rem; color:{_arm_specs[0][1]}; text-align:right;">{harm['int_n']:,} ({harm['int_pct']}%)</span>
                    </div>
                    <div style="display:grid; grid-template-columns:150px minmax(120px,1fr) 110px; gap:8px; align-items:center;">
                        <span style="font-size:0.76rem; color:{colors['ink']};">{_arm_specs[1][0]}</span>
                        <span style="height:14px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;"><span style="display:block; width:{harm['std_pct']}%; height:100%; background:{_arm_specs[1][1]};"></span></span>
                        <span style="font-size:0.75rem; color:{_arm_specs[1][1]}; text-align:right;">{harm['std_n']:,} ({harm['std_pct']}%)</span>
                    </div>
                </div>
            </div>
            """
        )
    harms_panel = mo.Html(
        f"""
        <div role="img" aria-label="Serious adverse event conditions by randomised arm" style="font-family:{FONT}; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">Conditions of interest were not equally distributed</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 8px;">Bars show serious-adverse-event percentages from Table 3. Labels retain counts and P values.</div>
            {''.join(_blocks)}
        </div>
        """
    )
    _all_harms = "\n".join(
        f"| {harm['tier']} | {harm['condition']} | {harm['int_n']} ({harm['int_pct']}%) | {harm['std_n']} ({harm['std_pct']}%) | P = {harm['p']} |"
        for harm in HARMS
    )
    harms_table = mo.md(
        "| Tier | Condition | " + ARMS[0]["arm"] + " | " + ARMS[1]["arm"] + " | P |\n"
        "|:---|:---|:---|:---|:---|\n"
        f"{_all_harms}"
    )
    harms_view = mo.vstack(
        [
            consort_items(["27", "28"], "Harms and ancillary analyses"),
            mo.md("### Harms and secondary outcomes"),
            harms_panel,
            mo.md(
                f"Overall serious adverse events occurred in **{SAE_OVERALL['int_n']:,} ({SAE_OVERALL['int_pct']}%)** "
                f"intensive participants versus **{SAE_OVERALL['std_n']:,} ({SAE_OVERALL['std_pct']}%)** standard participants "
                f"(HR {SAE_OVERALL['hr']}, P {SAE_OVERALL['p']}). Events judged possibly or definitely related to the "
                f"intervention were higher (**{SAE_RELATED['int_n']} ({SAE_RELATED['int_pct']}%) vs {SAE_RELATED['std_n']} "
                f"({SAE_RELATED['std_pct']}%), HR {SAE_RELATED['hr']}, P {SAE_RELATED['p']}**). Hypotension, syncope, "
                "electrolyte abnormality, and acute kidney injury were more common with intensive control; injurious "
                "falls and bradycardia were not significantly different."
            ),
            mo.accordion({"Full reported harms table": harms_table}),
        ],
        gap=0.65,
    )
    harms_view
    return


@app.cell
def _(CHECKLIST, TRIAL, chapter_header, consort_items, mo):
    # --------------------------- DISCUSSION ---------------------------
    _interpretation = next(row[4] for row in CHECKLIST if row[1] == "29")
    _limitations = next(row[4] for row in CHECKLIST if row[1] == "30")
    discussion_view = mo.vstack(
        [
            chapter_header(
                "Discussion",
                "How should the result be interpreted, and which limitations affect its application?",
            ),
            consort_items(["29", "30"], "Interpretation and limitations"),
            mo.md(
                f"### Interpretation\n\n{_interpretation}. Intensive control reduced major cardiovascular outcomes and all-cause mortality "
                "in the enrolled population, but the treatment burden included hypotension, electrolyte abnormalities, "
                "and acute kidney injury.\n\n"
                f"### Limits\n\n{_limitations}. The trial stopped early for benefit, was open-label, and excluded people with diabetes, "
                "prior stroke, or other conditions outside its eligibility criteria. Apply the result to similar high-risk "
                f"adults rather than to every patient with hypertension. Recruitment ran {TRIAL['recruitment']}."
            ),
        ],
        gap=0.7,
    )
    discussion_view
    return


@app.cell
def _(coverage_summary):
    coverage = coverage_summary()
    coverage
    return


@app.cell
def _(NNT, OUTCOMES, TRIAL, colors, mo):
    # ------------------------- PROVENANCE -------------------------
    _primary = next(outcome for outcome in OUTCOMES if outcome["short"] == "Primary composite")
    provenance = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['muted']}; font-size:0.86rem;
                    border-top:1px solid {colors['grid']}; padding-top:12px; line-height:1.5;">
            <strong style="color:{colors['ink']};">Source & provenance.</strong>
            {TRIAL['citation']} DOI <a href="https://doi.org/{TRIAL['doi']}" style="color:{colors['standard']};">{TRIAL['doi']}</a>.
            Registered as {TRIAL['registration']}. Checklist: Hopewell S, et al. CONSORT 2025 Statement.
            <em>BMJ</em> 2025;388:e081123. The source-data cell near the top transcribes values from the paper's
            main text, Tables 1–3, and Figures 1–2. SPRINT printed event counts beside annualised rates, so no
            denominator was reconstructed. The primary endpoint is time-to-event with unequal follow-up; this
            notebook therefore uses paired annualised rates and hazard ratios rather than fixed-denominator icon
            arrays. The paper's published NNTs are retained ({NNT['primary']}, {NNT['any_death']}, and {NNT['cv_death']} over
            the median follow-up). The screening count is not in the retrieved full text and remains visibly empty in
            the flow diagram. CONSORT 2025 is applied retrospectively; the checklist postdates this 2015 report.
        </div>
        """
    )
    provenance
    return


if __name__ == "__main__":
    app.run()
