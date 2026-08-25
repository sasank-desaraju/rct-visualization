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
        "invasive": "#FA4616",      # intervention arm -> UF orange
        "conservative": "#0021A5",  # reference arm -> UF blue
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
    # Maron DJ, Hochman JS, Reynolds HR, et al.; ISCHEMIA Research Group.
    # Initial Invasive or Conservative Strategy for Stable Coronary Disease.
    # N Engl J Med 2020;382:1395-1407.  DOI 10.1056/NEJMoa1915922
    # Registered as NCT01471522.
    # Every figure below is rendered from these literals. All values are
    # transcribed verbatim from the published full text (author manuscript,
    # PMC, extracted at papers/ischemia-text.txt). Nothing was reconstructed;
    # no denominator was derived from a percentage.
    # =====================================================================

    TRIAL = {
        "name": "ISCHEMIA",
        "title": "Initial Invasive or Conservative Strategy for Stable Coronary Disease",
        "citation": "Maron DJ, Hochman JS, Reynolds HR, et al.; ISCHEMIA Research Group. N Engl J Med 2020;382:1395-1407.",
        "doi": "10.1056/NEJMoa1915922",
        "registration": "NCT01471522",
        "recruitment": "Jul 26, 2012 – Jan 31, 2018",
        "followup_end": "Jun 30, 2019",
        "median_followup_years": 3.2,
        "sites": 320,
        "countries": 37,
    }

    # Participant flow (item 22): enrolled -> randomized -> analysed.
    # Analysed = randomized in each arm (intention-to-treat; the paper reports
    # no post-randomization exclusions from the primary analysis).
    FLOW = {
        "enrolled": 8518,
        "randomized": 5179,
        "inv_assigned": 2588,
        "con_assigned": 2591,
        "inv_analyzed": 2588,
        "con_analyzed": 2591,
    }
    FLOW["not_randomized"] = FLOW["enrolled"] - FLOW["randomized"]

    # Arms with event counts (Table 2). Rates over time live in CURVES_*.
    ARMS = [
        {
            "arm": "Invasive",
            "n": 2588,
            "primary_events": 318,
            "secondary_events": 276,  # CV death or MI
            "mi_events": 210,
            "deaths": 145,
        },
        {
            "arm": "Conservative",
            "n": 2591,
            "primary_events": 352,
            "secondary_events": 314,
            "mi_events": 233,
            "deaths": 144,
        },
    ]

    # Effect estimates with 95% CI (covariate-adjusted hazard ratios; Table 2
    # presents HRs for these two outcomes only).
    EFFECTS = [
        {"outcome": "Primary composite", "hr": 0.93, "lo": 0.80, "hi": 1.08, "p": 0.34},
        {"outcome": "Death from any cause", "hr": 1.05, "lo": 0.83, "hi": 1.32, "p": None},
    ]

    # Other prespecified / contextual statistics quoted in prose.
    STATS_EXTRA = {
        "rmst_days": 9.5,
        "rmst_ci": "-17.8 to 36.9",
        "rmst_secondary_days": 9.4,
        "bayes_benefit_pct": 24.5,
        "bayes_harm_str": "<0.1%",
        "ldl_baseline_mgdl": 83,
        "ldl_last_mgdl": 64,
        "ischemia_unconfirmed_pct": 14,
        "planned_n": 8000,
        "power_pct": 83,
        "relative_reduction_pct": 18.5,
    }

    # Key exclusions (verbatim thresholds from METHODS / DISCUSSION).
    EXCLUSIONS = [
        "a recent acute coronary syndrome",
        "unprotected left main stenosis of at least 50%",
        "eGFR below 30 mL/min/1.73 m²",
        "LVEF below 35%",
        "NYHA class III–IV heart failure",
        "unacceptable angina despite maximal medical therapy",
    ]
    return ARMS, EFFECTS, EXCLUSIONS, FLOW, STATS_EXTRA, TRIAL


@app.cell
def _(ARMS):
    # ------------------------------------------------------------------
    # Time-to-event estimates for the primary composite (CV death, MI,
    # hospitalization for unstable angina/HF, resuscitated cardiac arrest)
    # and the key secondary (CV death or MI). Values are the tabulated
    # cumulative event rates and differences from Table 2, verbatim.
    # Printed differences may differ from differences of printed rates by
    # up to 0.1 pp because the underlying estimates are rounded for print.
    # ------------------------------------------------------------------
    _inv, _con = ARMS[0]["n"], ARMS[1]["n"]

    CURVES_PRIMARY = [
        {"label": "6 months", "t": 0.5, "inv": 5.3, "con": 3.4, "diff": 1.9, "lo": 0.8, "hi": 3.0, "ci": "0.8 to 3.0"},
        {"label": "1 year", "t": 1, "inv": 7.0, "con": 5.4, "diff": 1.5, "lo": 0.2, "hi": 2.9, "ci": "0.2 to 2.9"},
        {"label": "2 years", "t": 2, "inv": 9.0, "con": 9.5, "diff": -0.5, "lo": -2.1, "hi": 1.1, "ci": "-2.1 to 1.1"},
        {"label": "3 years", "t": 3, "inv": 11.3, "con": 12.7, "diff": -1.3, "lo": -3.2, "hi": 0.6, "ci": "-3.2 to 0.6"},
        {"label": "4 years", "t": 4, "inv": 13.3, "con": 15.5, "diff": -2.2, "lo": -4.4, "hi": 0.0, "ci": "-4.4 to 0"},
        {"label": "5 years", "t": 5, "inv": 16.4, "con": 18.2, "diff": -1.8, "lo": -4.7, "hi": 1.0, "ci": "-4.7 to 1.0"},
    ]

    CURVES_SECONDARY = [
        {"label": "6 months", "t": 0.5, "inv": 4.8, "con": 2.9, "diff": 1.9, "lo": 0.9, "hi": 3.0, "ci": "0.9 to 3.0"},
        {"label": "1 year", "t": 1, "inv": 6.2, "con": 4.6, "diff": 1.6, "lo": 0.4, "hi": 2.8, "ci": "0.4 to 2.8"},
        {"label": "2 years", "t": 2, "inv": 7.9, "con": 8.2, "diff": -0.3, "lo": -1.8, "hi": 1.2, "ci": "-1.8 to 1.2"},
        {"label": "3 years", "t": 3, "inv": 9.7, "con": 11.0, "diff": -1.3, "lo": -3.1, "hi": 0.5, "ci": "-3.1 to 0.5"},
        {"label": "4 years", "t": 4, "inv": 11.7, "con": 13.9, "diff": -2.2, "lo": -4.4, "hi": -0.1, "ci": "-4.4 to -0.1"},
        {"label": "5 years", "t": 5, "inv": 14.2, "con": 16.5, "diff": -2.3, "lo": -5.0, "hi": 0.4, "ci": "-5.0 to 0.4"},
    ]

    ENDPOINTS = {
        "Primary composite (CV death, MI, UA/HF hospitalisation, resuscitated arrest)": CURVES_PRIMARY,
        "Key secondary (CV death or MI)": CURVES_SECONDARY,
    }
    return CURVES_PRIMARY, CURVES_SECONDARY, ENDPOINTS


@app.cell
def _():
    # Delivery of each strategy (item 24a): crude proportions of randomized
    # patients, as printed in RESULTS. The paper's Figure 1 footnote notes
    # these proportions differ from censoring-adjusted cumulative-incidence
    # rates. PCI/CABG shares are percentages of the invasive-strategy arm.
    FIDELITY = [
        {"arm": "Invasive", "procedure": "Angiography", "pct": 96},
        {"arm": "Invasive", "procedure": "Revascularization", "pct": 79},
        {"arm": "Conservative", "procedure": "Angiography", "pct": 26},
        {"arm": "Conservative", "procedure": "Revascularization", "pct": 21},
    ]
    FIDELITY_DETAIL = {
        "inv_pci_pct": 74,
        "inv_cabg_pct": 26,
        "con_angio_before_event_pct": 19,
        "con_revasc_before_event_pct": 15,
        "total_procedures_inv": 5337,
        "total_procedures_con": 1506,
    }

    # Sensitivity of the primary composite to the MI definition (RESULTS +
    # DISCUSSION). The "trial definition" required higher biomarker thresholds
    # for procedural infarctions; the "secondary MI definition" used thresholds
    # similar to the universal definition and adjudicated more procedural MIs.
    DEF_SENS = [
        {"panel": "At 6 months", "definition": "Trial definition", "arm": "Invasive", "rate": 5.3, "tip": "+1.9 pts (95% CI 0.8 to 3.0)"},
        {"panel": "At 6 months", "definition": "Trial definition", "arm": "Conservative", "rate": 3.4, "tip": "+1.9 pts (95% CI 0.8 to 3.0)"},
        {"panel": "At 6 months", "definition": "Secondary MI definition", "arm": "Invasive", "rate": 10.2, "tip": "+6.5 pts (95% CI 5.2 to 7.9)"},
        {"panel": "At 6 months", "definition": "Secondary MI definition", "arm": "Conservative", "rate": 3.7, "tip": "+6.5 pts (95% CI 5.2 to 7.9)"},
        {"panel": "At 5 years", "definition": "Trial definition", "arm": "Invasive", "rate": 16.4, "tip": "-1.8 pts (95% CI -4.7 to 1.0)"},
        {"panel": "At 5 years", "definition": "Trial definition", "arm": "Conservative", "rate": 18.2, "tip": "-1.8 pts (95% CI -4.7 to 1.0)"},
        {"panel": "At 5 years", "definition": "Secondary MI definition", "arm": "Invasive", "rate": 21.2, "tip": "+2.2 pts (95% CI -0.7 to 5.2)"},
        {"panel": "At 5 years", "definition": "Secondary MI definition", "arm": "Conservative", "rate": 19.0, "tip": "+2.2 pts (95% CI -0.7 to 5.2)"},
    ]
    return DEF_SENS, FIDELITY, FIDELITY_DETAIL


@app.cell
def _():
    # Baseline characteristics (item 25), Total column of Table 1, verbatim.
    BASELINE = [
        ("Age — median (IQR)", "64 yr (58–70)"),
        ("Male sex", "77.4%"),
        ("White / Asian / Black race", "66.3% / 29.0% / 4.0%"),
        ("Hispanic or Latino ethnicity", "15.8%"),
        ("Hypertension", "73.4%"),
        ("Diabetes (insulin-treated)", "41.8% (9.5%)"),
        ("Current smoking", "12.4%"),
        ("Previous myocardial infarction", "19.2%"),
        ("Previous PCI / previous CABG", "20.3% / 3.9%"),
        ("History of angina", "89.6%"),
        ("Daily or weekly angina", "20.3%"),
        ("LVEF — median (IQR)", "60% (55–65)"),
    ]
    return (BASELINE,)


@app.cell
def _():
    # ------------------------------------------------------------------
    # CONSORT 2025 checklist (Hopewell S, et al. BMJ 2025;388:e081123),
    # each item paired with how ISCHEMIA (2020) reports it.
    # status: reported | partial | na | gap
    # group is the top-level CONSORT section used by the section filter.
    # ------------------------------------------------------------------
    CHECKLIST = [
        ("Title and abstract", "1a", "Identification as a randomised trial", "reported", "Abstract: “We randomly assigned 5179 patients”"),
        ("Title and abstract", "1b", "Structured summary", "reported", "NEJM structured abstract (Background–Conclusions)"),
        ("Open science", "2", "Trial registration", "reported", "ClinicalTrials.gov NCT01471522"),
        ("Open science", "3", "Protocol & statistical analysis plan", "reported", "Protocol posted at NEJM.org; SAP elements prespecified"),
        ("Open science", "4", "Data sharing (de-identified IPD, code)", "reported", "Explicit data sharing statement in the full text"),
        ("Open science", "5a", "Funding & role of funders", "reported", "NHLBI + industry; sponsors had no data access or analytic role"),
        ("Open science", "5b", "Conflicts of interest", "reported", "Disclosure forms published with the article"),
        ("Introduction", "6", "Background & rationale", "reported", "Prior strategy trials found no reduction in death or MI"),
        ("Introduction", "7", "Objectives (benefits & harms)", "reported", "Effect of adding angiography + revascularization to medical therapy"),
        ("Methods", "8", "Patient & public involvement", "gap", "Not reported — item new in 2025"),
        ("Methods", "9", "Trial design", "reported", "Two-group, parallel, 1:1 superiority strategy trial"),
        ("Methods", "10", "Changes to trial protocol", "reported", "Outcome switch + prespecified revert; 2014 stress-test addendum documented"),
        ("Methods", "11", "Trial setting", "reported", "320 sites in 37 countries; Jul 2012 – Jan 2018"),
        ("Methods", "12a", "Eligibility — participants", "reported", "Stable CAD + moderate/severe ischemia; exclusion list given"),
        ("Methods", "12b", "Eligibility — sites / deliverers", "reported", "Sites had to meet protocol quality metrics"),
        ("Methods", "13", "Intervention & comparator", "reported", "Angiography ≤30 d + revascularization if feasible vs medical therapy alone"),
        ("Methods", "14", "Outcomes", "reported", "Five-component composite; blinded adjudication; MI definitions specified"),
        ("Methods", "15", "Harms — definition & assessment", "partial", "Procedural MI defined by biomarker thresholds; no standalone harms battery"),
        ("Methods", "16a", "Sample size", "reported", "≥83% power for an 18–18.5% relative reduction; blinded re-estimation"),
        ("Methods", "16b", "Interim analyses & stopping", "partial", "DSMB safety oversight described; interim rules not detailed"),
        ("Methods", "17a", "Sequence generation", "reported", "Randomly permuted blocks of varying sizes"),
        ("Methods", "17b", "Randomisation type / restriction", "reported", "Central IVR/Web system, stratified by enrollment site"),
        ("Methods", "18", "Allocation concealment", "reported", "Randomisation only after CCTA-based eligibility confirmed"),
        ("Methods", "19", "Implementation", "reported", "Central system; local heart team chose PCI vs CABG"),
        ("Methods", "20a", "Blinding — who", "partial", "Open-label strategies; event adjudicators & core labs masked"),
        ("Methods", "20b", "Blinding — how", "reported", "Clinical-event committee unaware of assignments; independent core labs"),
        ("Methods", "21a", "Statistical methods", "reported", "ITT time-to-first-event; adjusted Cox; prespecified nonparametric emphasis"),
        ("Methods", "21b", "Who is in each analysis", "reported", "All randomised analysed as assigned (2,588 vs 2,591)"),
        ("Methods", "21c", "Missing data", "partial", "Follow-up completeness shown in flow figure; handling not detailed in text"),
        ("Methods", "21d", "Additional analyses", "reported", "Subgroups, Bayesian, kernel-smoothed hazards, RMST"),
        ("Results", "22a", "Participant flow", "reported", "8,518 enrolled → 5,179 randomised (2,588 vs 2,591)"),
        ("Results", "22b", "Losses & exclusions", "partial", "Pre-randomisation exclusions clear; post-randomisation losses in supplement"),
        ("Results", "23a", "Recruitment & follow-up dates", "reported", "Jul 26, 2012 – Jan 31, 2018; followed until Jun 30, 2019"),
        ("Results", "23b", "Why the trial ended", "partial", "Slow recruitment reported; formal stop reason not stated"),
        ("Results", "24a", "Intervention delivery / fidelity", "reported", "96%/79% vs 26%/21% angiography/revascularization"),
        ("Results", "24b", "Concomitant care", "reported", "Treat-to-target medical therapy in both arms; LDL 83 → 64 mg/dL"),
        ("Results", "25", "Baseline data", "reported", "Table 1 — groups well balanced"),
        ("Results", "26", "Numbers analysed, outcomes, estimation", "reported", "Counts, cumulative rates with CIs at 6 mo–5 yr, adjusted HRs"),
        ("Results", "27", "Harms", "reported", "Deaths 145 vs 144; procedural-MI excess; more HF hospitalisations"),
        ("Results", "28", "Ancillary analyses", "reported", "Null heterogeneity analyses; MI-definition sensitivity quantified"),
        ("Discussion", "29", "Interpretation", "reported", "No evidence of reduced ischemic events or death; definition-sensitive"),
        ("Discussion", "30", "Limitations", "reported", "Explicit paragraph: power, event rates, follow-up, generalisability"),
    ]
    return (CHECKLIST,)



@app.cell
def _(CHECKLIST, FONT, colors, mo, pill):
    # Shared inline CONSORT reader. The checklist appears beside the evidence.
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
                    <strong>{', '.join(gaps) if gaps else 'none'}</strong>. Not-applicable rows are
                    <strong>{', '.join(not_applicable) if not_applicable else 'none'}</strong>.
                    CONSORT 2025 is a retrospective reporting lens, so a gap can reflect the reporting era rather than
                    a flaw in trial conduct. See <a href="#open-science">Open science</a> and <a href="#methods">Methods</a> for the evidence.
                </div>
            </div>
            """
        )

    return chapter_header, consort_items, coverage_summary, section_nav


@app.cell
def _(ENDPOINTS, mo):
    # This control changes the time-to-event endpoint plotted in Results.
    endpoint = mo.ui.radio(
        options=list(ENDPOINTS.keys()),
        value=next(iter(ENDPOINTS.keys())),
        label="Endpoint for the time-to-event figure",
        inline=True,
    )
    return (endpoint,)


@app.cell
def _(ARMS, CURVES_PRIMARY, EFFECTS, FLOW, FONT, STATS_EXTRA, TRIAL, card, colors, mo):
    # ---------------------------- HERO ----------------------------
    _primary = CURVES_PRIMARY[-1]
    _invasive = ARMS[0]
    _conservative = ARMS[1]
    _rate_difference = _primary["con"] - _primary["inv"]
    _primary_effect = EFFECTS[0]
    _event_n = _invasive["primary_events"] + _conservative["primary_events"]
    hero = mo.Html(
        f"""
        <div style="background:{colors['panel']}; border:1px solid #D8D4D7; border-radius:14px;
                    padding:18px 20px; font-family:{FONT}; color:{colors['ink']};">
            <div style="text-transform:uppercase; letter-spacing:0.15em; font-size:0.72rem;
                        color:{colors['muted']}; margin-bottom:0.5rem;">
                A randomised trial, read through CONSORT 2025
            </div>
            <div style="font-size:1.82rem; line-height:1.12; margin-bottom:0.25rem;">{TRIAL['name']}</div>
            <div style="font-size:1.0rem; color:#343741; margin-bottom:0.35rem;">{TRIAL['title']}</div>
            <div style="max-width:840px; font-size:0.96rem; line-height:1.42; color:#343741; margin-bottom:0.85rem;">
                ISCHEMIA compared an initial invasive strategy with a conservative strategy in patients with stable
                coronary disease and moderate or severe ischemia. The strategies did not reduce the primary composite
                or death over follow-up. Invasive care caused an early procedural-event excess, followed by fewer
                events later. The primary endpoint showed non-proportional hazards, so cumulative rates are the clearest
                first view.
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
                {card("Randomised population", f"{FLOW['randomized']:,}", f"{FLOW['inv_assigned']:,} invasive · {FLOW['con_assigned']:,} conservative · {TRIAL['sites']} sites", colors["ink"])}
                {card("Invasive strategy", f"{_invasive['primary_events']:,} events", f"{_primary['inv']}% at {_primary['label']} · {TRIAL['median_followup_years']}-year median follow-up", colors["invasive"])}
                {card("Conservative strategy", f"{_conservative['primary_events']:,} events", f"{_primary['con']}% at {_primary['label']} · {_event_n:,} primary events overall", colors["conservative"])}
                {card("Main contrast", f"{_rate_difference:+.1f} pts", f"{_primary['label']} cumulative rate: conservative minus invasive · HR {_primary_effect['hr']:.2f} ({_primary_effect['lo']:.2f}–{_primary_effect['hi']:.2f})", colors["muted"])}
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
                {card("Protocol & SAP · item 3", "Available", _notes["3"], colors["good"])}
                {card("Data sharing · item 4", "Statement published", _notes["4"], colors["good"])}
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
            mo.md(f"**Rationale.** {_rationale}.\n\n**Clinical question.** {_objective}."),
        ],
        gap=0.4,
    )
    introduction_view
    return


@app.cell
def _(CHECKLIST, EXCLUSIONS, STATS_EXTRA, TRIAL, chapter_header, consort_items, mo):
    # ----------------------------- METHODS -----------------------------
    _notes = {row[1]: row[4] for row in CHECKLIST}
    _exclusion_text = "; ".join(EXCLUSIONS)
    design = mo.md(
        "### Trial design in one paragraph\n\n"
        f"**{TRIAL['name']}** was a multicentre, parallel-group, open-label, superiority strategy trial at "
        f"**{TRIAL['sites']} sites in {TRIAL['countries']} countries**. Adults with stable coronary disease and "
        "moderate or severe ischemia were randomly assigned to an initial invasive or conservative strategy. "
        f"The report states the eligibility criteria as **{_notes['12a']}**, with exclusions including **{_exclusion_text}**. "
        f"The invasive strategy used angiography within the protocol window and revascularization when feasible; the comparator "
        f"used medical therapy alone. The primary analysis was intention-to-treat and used adjusted Cox models, but the "
        f"primary hazard ratio did not describe the changing effect over time. Recruitment ran {TRIAL['recruitment']}, "
        f"with follow-up through {TRIAL['followup_end']}. The sample-size target was {STATS_EXTRA['planned_n']:,} with "
        f"{STATS_EXTRA['power_pct']}% power for an approximately {STATS_EXTRA['relative_reduction_pct']}% relative reduction."
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
        "Who entered the trial, how the strategies were delivered, and what happened to outcomes and harms over time?",
    )
    results_header
    return


@app.cell
def _(ARMS, CHART_W, FIDELITY, FIDELITY_DETAIL, alt, colors, consort_items, mo, pl, style):
    # ------------------- INTERVENTION DELIVERY / FIDELITY -------------------
    _arm_names = [arm["arm"] for arm in ARMS]
    _arm_scale = alt.Scale(domain=_arm_names, range=[colors["invasive"], colors["conservative"]])
    _inv_angio = next(row["pct"] for row in FIDELITY if row["arm"] == _arm_names[0] and row["procedure"] == "Angiography")
    _con_angio = next(row["pct"] for row in FIDELITY if row["arm"] == _arm_names[1] and row["procedure"] == "Angiography")
    _fidelity = pl.DataFrame(FIDELITY)
    fidelity_chart = style(
        alt.Chart(_fidelity)
        .mark_bar(size=24)
        .encode(
            y=alt.Y("procedure:N", title=None, sort=["Angiography", "Revascularization"]),
            x=alt.X("pct:Q", title="Patients receiving the procedure (%)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("arm:N", scale=_arm_scale, legend=alt.Legend(title="Randomised arm")),
            yOffset="arm:N",
            tooltip=[alt.Tooltip("arm:N", title="Arm"), alt.Tooltip("procedure:N", title="Procedure"), alt.Tooltip("pct:Q", title="Percent")],
        )
        .properties(
            width=CHART_W,
            height=150,
            title=alt.TitleParams(
                "The assigned strategies created a clear procedural separation",
                subtitle="Bars show crude proportions of randomised patients. PCI and CABG shares are percentages of the invasive arm.",
            ),
        )
    )
    fidelity_view = mo.vstack(
        [
            consort_items(["24a", "24b"], "Intervention delivery and concomitant care"),
            mo.ui.altair_chart(fidelity_chart),
            mo.md(
                f"Angiography occurred in **{_inv_angio}%** of invasive-strategy patients.\n\n"
                f"It occurred in **{_con_angio}%** of conservative-strategy patients.\n\n"
                f"Among invasive patients, revascularization used PCI in **{FIDELITY_DETAIL['inv_pci_pct']}%** and CABG in **{FIDELITY_DETAIL['inv_cabg_pct']}%**. "
                f"The recorded procedure counts were **{FIDELITY_DETAIL['total_procedures_inv']:,} vs {FIDELITY_DETAIL['total_procedures_con']:,}**."
            ),
        ],
        gap=0.4,
    )
    fidelity_view
    return


@app.cell
def _(FLOW, TRIAL, box, colors, consort_items, mo):
    # ----------------------- CONSORT FLOW DIAGRAM -----------------------
    arrow = f'<div style="text-align:center; color:{colors["muted"]}; font-size:1.1rem; line-height:1;">↓</div>'
    flow_html = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; max-width:720px; margin:0 auto;">
            {box("Enrolled", FLOW["enrolled"], colors["dark"], TRIAL["recruitment"])}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                {box("Not randomised", FLOW["not_randomized"], colors["muted"], "Eligibility, refusal, or other pre-randomisation reasons")}
                {box("Randomised", FLOW["randomized"], colors["accent"], TRIAL["followup_end"] + " follow-up end")}
            </div>
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div style="display:grid; gap:6px;">
                    {box("Allocated: invasive", FLOW["inv_assigned"], colors["invasive"], "Initial angiography strategy")}
                    {arrow}
                    {box("Analysed: intention-to-treat", FLOW["inv_analyzed"], colors["invasive"], "No post-randomisation exclusion from primary analysis reported")}
                </div>
                <div style="display:grid; gap:6px;">
                    {box("Allocated: conservative", FLOW["con_assigned"], colors["conservative"], "Medical therapy strategy")}
                    {arrow}
                    {box("Analysed: intention-to-treat", FLOW["con_analyzed"], colors["conservative"], "No post-randomisation exclusion from primary analysis reported")}
                </div>
            </div>
        </div>
        """
    )
    flow_view = mo.vstack(
        [
            consort_items(["22a", "22b", "23a", "23b"], "Participant flow and recruitment"),
            mo.md("### Participant flow\n_The enrolled, randomised, allocated, and analysed counts close at every reported stage._"),
            flow_html,
        ],
        gap=0.4,
    )
    flow_view
    return


@app.cell
def _(BASELINE, CHART_W, FLOW, FONT, colors, consort_items, mo):
    # --------------------------- BASELINE ---------------------------
    import re as _re_ischemia_baseline

    _profile_rows = []
    for _label, _value in BASELINE:
        if any(token in _label for token in ("Male sex", "Hypertension", "Current smoking", "Previous myocardial infarction", "History of angina", "Daily or weekly angina")):
            _match = _re_ischemia_baseline.search(r"([\d.]+)%", _value)
            if _match:
                _profile_rows.append((_label, float(_match.group(1))))
    _bars = "".join(
        f"""
        <div style="display:grid; grid-template-columns:235px minmax(150px,1fr) 52px; gap:9px; align-items:center; margin:9px 0;">
            <div style="font-size:0.78rem; color:{colors['ink']};">{label}</div>
            <div style="height:16px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                <div style="width:{value}%; height:100%; background:{colors['grid']}; border-radius:3px;"></div>
            </div>
            <div style="font-size:0.78rem; font-weight:700; color:{colors['ink']}; text-align:right;">{value:g}%</div>
        </div>
        """
        for label, value in _profile_rows
    )
    profile_panel = mo.Html(
        f"""
        <div role="img" aria-label="Selected baseline characteristics in the ISCHEMIA randomised cohort" style="font-family:{FONT}; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">The cohort had extensive stable coronary disease</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 12px;">Bars show selected total-cohort percentages from Table 1. The full reported table remains closed below.</div>
            {_bars}
        </div>
        """
    )
    _rows = "\n".join(f"| {label} | {value} |" for label, value in BASELINE)
    baseline_table = mo.md("| Characteristic | Total randomised cohort |\n|:---|:---|\n" + _rows)
    baseline_view = mo.vstack(
        [
            consort_items(["25"], "Baseline data"),
            mo.md(f"### Baseline profile\nThe trial randomised **{FLOW['randomized']:,} participants**. The source report describes the two strategy groups as well balanced."),
            profile_panel,
            mo.accordion({"Full reported baseline summary": baseline_table}),
        ],
        gap=0.5,
    )
    baseline_view
    return


@app.cell
def _(ARMS, CHART_W, ENDPOINTS, alt, colors, consort_items, endpoint, mo, pl, style):
    # ---------------- PRIMARY OUTCOME: CUMULATIVE RATES ----------------
    # The endpoint is time-to-event and the primary hazard ratio is not a
    # sufficient summary because hazards are non-proportional. A cumulative
    # rate view preserves the early procedural harm and later convergence.
    _curve = ENDPOINTS[endpoint.value]
    _long_rows = []
    for _row in _curve:
        _long_rows.extend(
            [
                {"time": _row["t"], "label": _row["label"], "arm": ARMS[0]["arm"], "rate": _row["inv"], "difference": _row["diff"], "ci": _row["ci"]},
                {"time": _row["t"], "label": _row["label"], "arm": ARMS[1]["arm"], "rate": _row["con"], "difference": _row["diff"], "ci": _row["ci"]},
            ]
        )
    _rates = pl.DataFrame(_long_rows)
    _arm_names = [arm["arm"] for arm in ARMS]
    _arm_scale = alt.Scale(domain=_arm_names, range=[colors["invasive"], colors["conservative"]])
    _lines = alt.Chart(_rates).mark_line(point={"size": 80, "filled": True}, strokeWidth=3).encode(
        x=alt.X("time:Q", title="Years since randomisation", scale=alt.Scale(domain=[0, 5])),
        y=alt.Y("rate:Q", title="Cumulative event rate (%)", scale=alt.Scale(zero=True)),
        color=alt.Color("arm:N", scale=_arm_scale, legend=alt.Legend(title="Randomised arm")),
        tooltip=[
            alt.Tooltip("label:N", title="Time"),
            alt.Tooltip("arm:N", title="Arm"),
            alt.Tooltip("rate:Q", title="Cumulative rate (%)"),
            alt.Tooltip("difference:Q", title="Invasive − conservative (points)"),
            alt.Tooltip("ci:N", title="95% CI for difference"),
        ],
    )
    cumulative_chart = style(
        _lines.properties(
            width=CHART_W,
            height=270,
            title=alt.TitleParams(
                "The strategy contrast changed over time",
                subtitle="Lines show cumulative rates for the selected endpoint. Tooltips include the invasive-minus-conservative difference and its 95% CI.",
            ),
        )
    )
    _last = _curve[-1]
    _endpoint_label = endpoint.value.split(" (")[0]
    primary_view = mo.vstack(
        [
            consort_items(["26"], "Numbers analysed, outcomes, and estimation"),
            mo.md(
                "### Primary outcome, in its native units\n"
                "**Read it as:** Each line shows cumulative event rates over time in one randomised arm.\n\n"
                "**Why this geometry:** The primary endpoint is time-to-event, and the proportional-hazards assumption was violated.\n\n"
                "A fixed-denominator icon array would hide the early procedural excess and imply false precision."
            ),
            endpoint,
            mo.ui.altair_chart(cumulative_chart),
            mo.md(
                f"**What it says:** For **{_endpoint_label}** at {_last['label']}, the cumulative rates were **{_last['inv']}% invasive** "
                f"versus **{_last['con']}% conservative**, a printed difference of **{_last['diff']:+.1f} percentage points** "
                f"(95% CI {_last['ci']}). The primary composite included **{ARMS[0]['primary_events']} vs {ARMS[1]['primary_events']} events** "
                "over the full trial. The paper did not report an NNT for this time-to-event comparison, so none is computed from rounded cumulative rates."
            ),
        ],
        gap=0.4,
    )
    primary_view
    return


@app.cell
def _(CHART_W, EFFECTS, STATS_EXTRA, alt, colors, mo, pl, style):
    # -------------------- EFFECT ESTIMATES: FOREST PLOT --------------------
    _effect_rows = []
    for _effect in EFFECTS:
        _kind = "benefit" if _effect["hi"] < 1 else "harm" if _effect["lo"] > 1 else "uncertain"
        _effect_rows.append({**_effect, "kind": _kind})
    _effects = pl.DataFrame(_effect_rows)
    _order = [effect["outcome"] for effect in EFFECTS]
    _lo_all = min(effect["lo"] for effect in EFFECTS)
    _hi_all = max(effect["hi"] for effect in EFFECTS)
    _domain = [max(0.5, _lo_all * 0.8), _hi_all * 1.2]
    _kind_scale = alt.Scale(domain=["benefit", "harm", "uncertain"], range=[colors["good"], colors["bad"], colors["muted"]])
    _rules = alt.Chart(_effects).mark_rule(strokeWidth=2).encode(
        y=alt.Y("outcome:N", sort=_order, title=None),
        x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=_domain), title="Hazard ratio (log scale) — invasive vs conservative"),
        x2="hi:Q",
        color=alt.Color("kind:N", scale=_kind_scale, legend=None),
    )
    _points = alt.Chart(_effects).mark_point(size=110, filled=True).encode(
        y=alt.Y("outcome:N", sort=_order),
        x="hr:Q",
        color=alt.Color("kind:N", scale=_kind_scale, legend=alt.Legend(title="Interpretation")),
        tooltip=[
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("hr:Q", title="HR"),
            alt.Tooltip("lo:Q", title="95% CI low"),
            alt.Tooltip("hi:Q", title="95% CI high"),
            alt.Tooltip("p:Q", title="P", format=".2f"),
        ],
    )
    _null = alt.Chart(pl.DataFrame({"x": [1.0]})).mark_rule(strokeDash=[5, 4], color=colors["muted"]).encode(x="x:Q")
    forest = style(
        (_null + _rules + _points).properties(
            width=CHART_W,
            height=150,
            title=alt.TitleParams(
                "The reported hazard ratios were compatible with no overall benefit",
                subtitle="Points show covariate-adjusted HRs and rules show 95% CIs. The dashed line marks HR = 1.",
            ),
        )
    )
    forest_view = mo.vstack(
        [
            mo.md("### Relative effect estimates\n_The forest plot carries the adjusted estimates and their uncertainty._"),
            mo.ui.altair_chart(forest),
            mo.md(
                f"The primary composite HR was **{EFFECTS[0]['hr']:.2f} (95% CI {EFFECTS[0]['lo']:.2f}–{EFFECTS[0]['hi']:.2f}; P = {EFFECTS[0]['p']:.2f})**.\n\n"
                f"All-cause death had HR **{EFFECTS[1]['hr']:.2f} (95% CI {EFFECTS[1]['lo']:.2f}–{EFFECTS[1]['hi']:.2f})**.\n\n"
                f"Restricted mean event-free time differed by **{STATS_EXTRA['rmst_days']} days (95% CI {STATS_EXTRA['rmst_ci']})**, which was close to the null."
            ),
        ],
        gap=0.4,
    )
    forest_view
    return


@app.cell
def _(ARMS, CHART_W, DEF_SENS, STATS_EXTRA, TRIAL, colors, consort_items, mo):
    # ------------------------- HARMS + SECONDARY -------------------------
    _arm_specs = [(ARMS[0]["arm"], colors["invasive"]), (ARMS[1]["arm"], colors["conservative"])]
    _comparison_rows = [
        ("Primary composite", "primary_events"),
        ("CV death or MI", "secondary_events"),
        ("Myocardial infarction", "mi_events"),
        ("Death from any cause", "deaths"),
    ]
    _max_count = max(arm[key] for arm in ARMS for _, key in _comparison_rows)
    _blocks = []
    for _label, _key in _comparison_rows:
        _blocks.append(
            f"""
            <div style="padding:8px 0 10px; border-top:1px solid {colors['grid']};">
                <div style="font-size:0.82rem; font-weight:700; color:{colors['dark']};">{_label}</div>
                <div style="display:grid; gap:5px; margin-top:6px;">
                    <div style="display:grid; grid-template-columns:155px minmax(120px,1fr) 96px; gap:8px; align-items:center;">
                        <span style="font-size:0.76rem; color:{colors['ink']};">{_arm_specs[0][0]}</span>
                        <span style="height:14px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;"><span style="display:block; width:{100 * ARMS[0][_key] / _max_count}%; height:100%; background:{_arm_specs[0][1]};"></span></span>
                        <span style="font-size:0.75rem; color:{_arm_specs[0][1]}; text-align:right;">{ARMS[0][_key]:,} ({100 * ARMS[0][_key] / ARMS[0]['n']:.1f}%)</span>
                    </div>
                    <div style="display:grid; grid-template-columns:155px minmax(120px,1fr) 96px; gap:8px; align-items:center;">
                        <span style="font-size:0.76rem; color:{colors['ink']};">{_arm_specs[1][0]}</span>
                        <span style="height:14px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;"><span style="display:block; width:{100 * ARMS[1][_key] / _max_count}%; height:100%; background:{_arm_specs[1][1]};"></span></span>
                        <span style="font-size:0.75rem; color:{_arm_specs[1][1]}; text-align:right;">{ARMS[1][_key]:,} ({100 * ARMS[1][_key] / ARMS[1]['n']:.1f}%)</span>
                    </div>
                </div>
            </div>
            """
        )
    comparison_panel = mo.Html(
        f"""
        <div role="img" aria-label="Selected ISCHEMIA event counts and rates by randomised arm" style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">Benefits and harms were separated in time</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 8px;">Bars show event counts; labels show counts and crude percentages of the randomised arm.</div>
            {''.join(_blocks)}
        </div>
        """
    )
    _sensitivity_rows = "\n".join(
        f"| {row['panel']} | {row['definition']} | {row['arm']} | {row['rate']}% | {row['tip']} |"
        for row in DEF_SENS
    )
    sensitivity_table = mo.md(
        "| Timepoint | MI definition | Arm | Rate | Printed difference |\n|:---|:---|:---|---:|:---|\n" + _sensitivity_rows
    )
    _six_month_trial = next(row for row in DEF_SENS if row["panel"] == "At 6 months" and row["definition"] == "Trial definition" and row["arm"] == ARMS[0]["arm"])
    _six_month_broad = next(row for row in DEF_SENS if row["panel"] == "At 6 months" and row["definition"] == "Secondary MI definition" and row["arm"] == ARMS[0]["arm"])
    _five_year_trial = next(row for row in DEF_SENS if row["panel"] == "At 5 years" and row["definition"] == "Trial definition" and row["arm"] == ARMS[0]["arm"])
    _five_year_broad = next(row for row in DEF_SENS if row["panel"] == "At 5 years" and row["definition"] == "Secondary MI definition" and row["arm"] == ARMS[0]["arm"])
    harms_view = mo.vstack(
        [
            consort_items(["27", "28"], "Harms and ancillary analyses"),
            mo.md("### Harms and secondary outcomes"),
            comparison_panel,
            mo.md(
                f"The invasive strategy had **{ARMS[0]['primary_events']} vs {ARMS[1]['primary_events']} primary events**, "
                f"**{ARMS[0]['mi_events']} vs {ARMS[1]['mi_events']} myocardial infarctions**, and **{ARMS[0]['deaths']} vs {ARMS[1]['deaths']} deaths**. "
                "The early excess was procedural. Later, invasive care had fewer nonprocedural infarctions and fewer unstable-angina admissions, "
                "but more heart-failure hospitalisations. The key secondary outcome, cardiovascular death or MI, was "
                f"**{ARMS[0]['secondary_events']} vs {ARMS[1]['secondary_events']} events**. Under the broader MI definition, the {_six_month_trial['panel'].lower()} difference "
                f"changed from **{_six_month_trial['tip']}** to **{_six_month_broad['tip']}**, while the {_five_year_trial['panel'].lower()} difference changed from "
                f"**{_five_year_trial['tip']}** to **{_five_year_broad['tip']}**. This sensitivity analysis shows why the composite result depends on how procedural MI is defined."
            ),
            mo.accordion({"Full MI-definition sensitivity table": sensitivity_table}),
            mo.md(
                f"Other limits included lower-than-expected event rates, a median follow-up of **{TRIAL['median_followup_years']} years**, "
                f"and **{STATS_EXTRA['ischemia_unconfirmed_pct']}%** of randomised patients without core-lab confirmation of qualifying ischemia. "
                "Quality-of-life outcomes were reported separately."
            ),
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
                f"### Interpretation\n\n{_interpretation}.\n\nThe trial does not support a routine initial invasive strategy for the enrolled stable-coronary-disease population. "
                "The decision remains sensitive to symptom burden, anatomy, procedural risk, and the definition used for myocardial infarction.\n\n"
                f"### Limits\n\n{_limitations}.\n\nThe report was open-label, recruitment was slower than planned, and the event rate was lower than expected.\n\n"
                f"Apply the result to patients resembling the eligibility population and the ischemia-confirmation process used from {TRIAL['recruitment']}."
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
def _(STATS_EXTRA, TRIAL, colors, mo):
    # ------------------------- PROVENANCE -------------------------
    provenance = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['muted']}; font-size:0.86rem;
                    border-top:1px solid {colors['grid']}; padding-top:12px; line-height:1.5;">
            <strong style="color:{colors['ink']};">Source &amp; provenance.</strong>
            {TRIAL['citation']} DOI <a href="https://doi.org/{TRIAL['doi']}" style="color:{colors['conservative']};">{TRIAL['doi']}</a>;
            registered as {TRIAL['registration']}. Checklist: Hopewell S, et al. CONSORT 2025 Statement.
            <em>BMJ</em> 2025;388:e081123. The source-data cells near the top transcribe the published full text
            from the NIH Public Access author manuscript at papers/ischemia-text.txt. Every displayed value is
            derived from those literals. No denominator was reconstructed from a percentage. The printed
            cumulative-rate differences may differ from subtraction of rounded arm rates by up to 0.1 percentage
            points. Angiography and revascularization figures are crude proportions of each randomised arm, and
            PCI/CABG shares are percentages of the invasive arm. The signature figure omits icon arrays because
            the endpoint is time-to-event with non-proportional hazards; a fixed-denominator grid would imply false
            precision. NNT is not reported and is not computed from rounded cumulative rates. CONSORT 2025 is applied
            retrospectively, so its checklist postdates this trial.
        </div>
        """
    )
    provenance
    return


if __name__ == "__main__":
    app.run()
