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
def _(CHECKLIST, ENDPOINTS, mo):
    # Interactive controls — always shown (works in script/run/edit modes).
    section = mo.ui.dropdown(
        options=["All sections"] + list(dict.fromkeys(row[0] for row in CHECKLIST)),
        value="All sections",
        label="CONSORT section",
    )
    endpoint = mo.ui.radio(
        options=list(ENDPOINTS.keys()),
        value=next(iter(ENDPOINTS.keys())),
        label="Endpoint for the time-to-event figure",
        inline=True,
    )
    return endpoint, section


@app.cell
def _(ARMS, CURVES_PRIMARY, EFFECTS, FLOW, FONT, TRIAL, card, colors, mo):
    # ---------------------------- HERO ----------------------------
    _eff = EFFECTS[0]
    _hr_txt = f"{_eff['hr']:.2f} (95% CI {_eff['lo']:.2f}–{_eff['hi']:.2f}), P = {_eff['p']:.2f}"
    _card_small_hr = (
        f"of {ARMS[0]['n']:,} randomized · HR {_hr_txt}"
    )
    _early_card = CURVES_PRIMARY[0]["diff"]
    _late_card = CURVES_PRIMARY[-1]["diff"]

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
            <div style="max-width:820px; font-size:0.96rem; line-height:1.42; color:#343741; margin-bottom:0.85rem;">
                An initial invasive strategy caused more early events and fewer later events than a conservative
                strategy. The cumulative rates crossed, and the trial found no significant overall difference.
                The estimated direction also changed when the investigators used a broader definition of
                myocardial infarction.
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
                {card("Randomised population", f"{FLOW['randomized']:,}", f"stable CAD + moderate/severe ischemia · {TRIAL['sites']} sites, {TRIAL['countries']} countries", colors["ink"])}
                {card("Intervention: invasive strategy", f"{ARMS[0]['primary_events']}", _card_small_hr, colors["invasive"])}
                {card("Reference: conservative strategy", f"{ARMS[1]['primary_events']}", f"of {ARMS[1]['n']:,} randomised · median follow-up {TRIAL['median_followup_years']} years", colors["conservative"])}
                {card("Main contrast over time", f"{_early_card:+.1f} → {_late_card:+.1f} pts", f"difference in cumulative rates, {CURVES_PRIMARY[0]['label'].lower()} vs {CURVES_PRIMARY[-1]['label'].lower()} (95% CI {CURVES_PRIMARY[0]['ci']} / {CURVES_PRIMARY[-1]['ci']})", colors["accent"])}
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
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']}; line-height:1.42;
                    border:1px solid #D8D4D7; border-left:4px solid {colors['accent']};
                    border-radius:10px; padding:10px 14px; background:#FFF4EF;">
            <strong>CONSORT map.</strong>
            Each section names the checklist items it addresses:
            design and eligibility (items 9, 11, 12), strategy specification and delivery (13, 24),
            participant flow (22), baseline balance (25), absolute and relative effects (26), harms (15, 27),
            open-science expectations (2–5), and interpretation/limitations (29–30).
            The final table separates reported, partial, not-applicable, and missing items.
        </div>
        """
    )
    consort_blurb
    return


@app.cell
def _(EXCLUSIONS, FLOW, TRIAL, mo):
    design = mo.md(
        f"""
        ## The design in one paragraph

        **{TRIAL['name']}** was an international, multicentre, parallel-group, **open-label** strategy trial.
        Patients with stable coronary disease and **moderate or severe ischemia** on clinically indicated stress
        testing entered the trial after coronary CT angiography excluded left main or nonobstructive disease.
        A central **interactive voice/Web response system** allocated them 1:1 with randomly permuted blocks of
        varying size, **stratified by site**. The *initial invasive strategy* added angiography within 30 days and
        revascularisation when feasible. The *initial conservative strategy* used medical therapy and reserved
        angiography for failure of medical therapy. Guideline-directed medical
        therapy was protocolized **equally in both arms** with treat-to-target algorithms. Clinical outcomes were
        adjudicated by a committee **unaware of assignments**; the primary analysis was **intention-to-treat**,
        time-to-first-event. Recruitment ran {TRIAL['recruitment']}, {FLOW['enrolled']:,} patients were enrolled,
        and {FLOW['randomized']:,} were randomised at {TRIAL['sites']} sites in {TRIAL['countries']} countries.
        Patients were followed until {TRIAL['followup_end']} (median {TRIAL['median_followup_years']} years).
        Key exclusions: {"; ".join(EXCLUSIONS[:-1])}; and {EXCLUSIONS[-1]}.

        _CONSORT items 1, 9, 11, 12, 17–21._
        """
    )
    design
    return


@app.cell
def _(CHART_W, FIDELITY, FIDELITY_DETAIL, FONT, STATS_EXTRA, colors, mo):
    # ------------- INTERVENTIONS: strategy delivery (items 13 & 24) -------------
    _rows = []
    for row in FIDELITY:
        _color = colors["invasive"] if row["arm"] == "Invasive" else colors["conservative"]
        _rows.append(
            f"""
            <div style="display:grid; grid-template-columns:210px minmax(180px,1fr) 48px; gap:10px; align-items:center;">
                <div style="font-size:0.78rem; color:{colors['ink']};">{row['arm']}: {row['procedure']}</div>
                <div style="height:18px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                    <div style="width:{row['pct']}%; height:100%; background:{_color}; border-radius:3px;"></div>
                </div>
                <div style="font-size:0.8rem; font-weight:700; color:{_color}; text-align:right;">{row['pct']}%</div>
            </div>
            """
        )

    _fidelity_panel = mo.Html(
        f"""
        <div role="img" aria-label="Procedure use by randomized strategy" style="font-family:{FONT}; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">Procedure use differed by randomised strategy</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 12px;">Orange and blue identify the randomised arms. Each row shows the reported proportion.</div>
            <div style="display:grid; gap:9px;">{''.join(_rows)}</div>
        </div>
        """
    )

    fidelity_view = mo.vstack(
        [
            mo.md(
                """
                ## Strategy delivery
                _CONSORT items 13 and 24. The chart compares procedure use in the randomised groups._
                """
            ),
            _fidelity_panel,
            mo.md(
                f"""
                Procedure use differed between the groups: **{FIDELITY[0]['pct']}%** of the invasive arm
                underwent angiography and **{FIDELITY[1]['pct']}%** revascularization (PCI
                **{FIDELITY_DETAIL['inv_pci_pct']}%**, CABG **{FIDELITY_DETAIL['inv_cabg_pct']}%** of the arm),
                compared with **{FIDELITY[2]['pct']}%** and **{FIDELITY[3]['pct']}%** in the conservative arm.
                Before any primary event, **{FIDELITY_DETAIL['con_angio_before_event_pct']}%** of the conservative
                group underwent angiography and **{FIDELITY_DETAIL['con_revasc_before_event_pct']}%** underwent
                revascularisation. Counting repeat procedures, the totals were
                **{FIDELITY_DETAIL['total_procedures_inv']:,} vs {FIDELITY_DETAIL['total_procedures_con']:,}**.
                The trial compared *initial* strategies; it did not prohibit later angiography in the conservative
                group. Medical therapy was protocolised identically
                (treat-to-target); median LDL cholesterol fell from
                **{STATS_EXTRA['ldl_baseline_mgdl']} to {STATS_EXTRA['ldl_last_mgdl']} mg/dL** by the last visit.
                Per the paper's Figure 1 footnote, these crude proportions differ from censoring-adjusted
                cumulative-incidence rates.
                """
            ),
        ],
        gap=0.35,
    )
    fidelity_view
    return


@app.cell
def _(FLOW, box, colors, mo):
    # ----------------------- CONSORT FLOW DIAGRAM -----------------------
    arrow = f'<div style="text-align:center; color:{colors["muted"]}; font-size:1.1rem; line-height:1;">↓</div>'

    flow_html = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; max-width:720px; margin:0 auto;">
            {box("Enrolled (stress test + CCTA screening)", FLOW["enrolled"], colors["dark"])}
            <div style="display:grid; grid-template-columns:1fr 1fr; align-items:center; gap:8px; margin:2px 0;">
                <div style="text-align:center; color:{colors['muted']}; font-size:1.1rem;">↓</div>
                <div style="border-left:2px dashed {colors['grid']}; padding-left:12px;">
                    {box("Not randomised", FLOW["not_randomized"], colors["muted"], "failed anatomical / ischemia eligibility or other criteria")}
                </div>
            </div>
            {box("Randomised", FLOW["randomized"], colors["accent"])}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div style="display:grid; gap:6px;">
                    {box("Allocated: initial invasive strategy", FLOW["inv_assigned"], colors["invasive"])}
                    {arrow}
                    {box("Analysed (intention-to-treat)", FLOW["inv_analyzed"], colors["invasive"], "no post-randomisation exclusions reported")}
                </div>
                <div style="display:grid; gap:6px;">
                    {box("Allocated: initial conservative strategy", FLOW["con_assigned"], colors["conservative"])}
                    {arrow}
                    {box("Analysed (intention-to-treat)", FLOW["con_analyzed"], colors["conservative"], "no post-randomisation exclusions reported")}
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
                _CONSORT item 22. The diagram reconstructs participant flow from the reported counts._
                """
            ),
            flow_html,
        ],
        gap=0.35,
    )
    flow_view
    return


@app.cell
def _(BASELINE, FLOW, mo):
    # --------------------------- BASELINE ---------------------------
    _rows = "\n".join(f"| {label} | {value} |" for label, value in BASELINE)
    baseline_text = (
        "## Baseline characteristics\n"
        f"_CONSORT item 25. Overall cohort (n = {FLOW['randomized']:,}); the trial reported the two "
        "groups were well balanced (Table 1). Row denominators vary slightly, as printed._\n\n"
        "| Characteristic | Value |\n"
        "|:---|:---|\n"
        f"{_rows}"
    )
    baseline_view = mo.md(baseline_text)
    baseline_view
    return


@app.cell
def _(CHART_W, ENDPOINTS, alt, colors, endpoint, math, mo, pl, style):
    # ---------- PRIMARY OUTCOME: cumulative rates over time ----------
    # The signature figure. ISCHEMIA's proportional-hazards assumption was
    # violated (P < 0.001 for time-by-treatment interaction), so the paper's
    # SAP emphasizes nonparametric cumulative event rates at fixed timepoints.
    # We plot those tabulated estimates for both arms, plus the between-arm
    # difference with its 95% CI in a lower panel. An icon array would imply
    # a constant, competing-risk-free risk — see the caption.
    import math

    curves = ENDPOINTS[endpoint.value]
    _is_primary = curves is ENDPOINTS[next(iter(ENDPOINTS.keys()))]
    _ep_short = "primary composite" if _is_primary else "key secondary (CV death or MI)"

    _rows = []
    for _c in curves:
        _rows.append({"t": _c["t"], "arm": "Invasive", "rate": _c["inv"]})
        _rows.append({"t": _c["t"], "arm": "Conservative", "rate": _c["con"]})
    rates = pl.DataFrame(_rows)

    _diff_rows = []
    for _c in curves:
        _diff_rows.append(
            {
                "t": _c["t"],
                "diff": _c["diff"],
                "lo": _c["lo"],
                "hi": _c["hi"],
                "label": _c["label"],
                "side": "Invasive higher" if _c["diff"] > 0 else "Conservative higher",
                "tip": f'{_c["label"]}: {_c["diff"]:+.1f} pts (95% CI {_c["ci"]})',
            }
        )
    diffs = pl.DataFrame(_diff_rows)

    _x_domain = [0.25, 5.3]
    _ticks = sorted({c["t"] for c in curves})

    def _x(hidden_labels):
        ax = alt.Axis(values=_ticks)
        if hidden_labels:
            ax = alt.Axis(values=_ticks, labels=False, domain=False, ticks=False)
        return alt.X("t:Q", title=None if hidden_labels else "Years since randomisation",
                     scale=alt.Scale(domain=_x_domain), axis=ax)

    _arm_scale = alt.Scale(
        domain=["Invasive", "Conservative"],
        range=[colors["invasive"], colors["conservative"]],
    )
    _side_scale = alt.Scale(
        domain=["Invasive higher", "Conservative higher"],
        range=[colors["invasive"], colors["conservative"]],
    )

    _lines = (
        alt.Chart(rates)
        .mark_line(strokeWidth=2.5)
        .encode(
            x=_x(True),
            y=alt.Y("rate:Q", title=f"Cumulative {_ep_short} rate (%)", scale=alt.Scale(zero=False)),
            color=alt.Color("arm:N", scale=_arm_scale, title=None),
        )
    )
    _points = (
        alt.Chart(rates)
        .mark_circle(size=100, filled=True, opacity=1.0)
        .encode(
            x=_x(True),
            y=alt.Y("rate:Q"),
            color=alt.Color("arm:N", scale=_arm_scale, legend=None),
            tooltip=[
                alt.Tooltip("arm:N", title="Arm"),
                alt.Tooltip("t:Q", title="Years"),
                alt.Tooltip("rate:Q", title="Cumulative rate (%)", format=".1f"),
            ],
        )
    )
    top = (_lines + _points).properties(
        width=CHART_W,
        height=290,
        title=alt.TitleParams(
            "Cumulative event rates crossed over time",
            subtitle=(
                f"The upper panel shows cumulative {_ep_short} event rates at reported timepoints. "
                "The lower panel shows the between-group difference and its 95% CI."
            ),
        ),
    )

    _err = (
        alt.Chart(diffs)
        .mark_rule(opacity=0.65, strokeWidth=2)
        .encode(
            x=_x(False),
            y=alt.Y("lo:Q", title="Difference (percentage points)"),
            y2="hi:Q",
            color=alt.Color("side:N", scale=_side_scale, legend=None),
        )
    )
    _dpts = (
        alt.Chart(diffs)
        .mark_circle(size=120, filled=True, opacity=1.0)
        .encode(
            x=_x(False),
            y=alt.Y("diff:Q"),
            color=alt.Color("side:N", scale=_side_scale, legend=None),
            tooltip=[alt.Tooltip("tip:N", title="Difference, invasive − conservative")],
        )
    )
    _null = (
        alt.Chart(pl.DataFrame({"y": [0.0]}))
        .mark_rule(strokeDash=[5, 4], color=colors["muted"])
        .encode(y="y:Q")
    )
    _lo_bound = min(min(c["lo"] for c in curves), 0.0) - 0.6
    _hi_bound = max(c["hi"] for c in curves) + 0.6
    bottom = (_err + _dpts + _null).properties(
        width=CHART_W,
        height=180,
    ).resolve_scale(y="independent")

    signature = style(alt.vconcat(top, bottom))

    # Absolute-effect bookkeeping (CONSORT item 26): NNH/NNT from the printed
    # point estimates, rounded away from zero. CIs cross zero — say so.
    _early = curves[0]
    _late = curves[-1]
    _nnh_early = math.ceil(1 / (abs(_early["diff"]) / 100))
    _nnt_late = math.ceil(1 / (abs(_late["diff"]) / 100))

    caption = mo.md(
        f"""
        **Read it as:** The upper panel shows cumulative event rates. The lower panel shows the invasive-minus-
        conservative difference and its 95% CI at each reported timepoint.

        **Why this geometry:** This is a time-to-event endpoint whose proportional-hazards
        assumption fails (P < 0.001 for time-by-treatment interaction), estimated as a competing-risk
        cumulative-incidence function with censoring. A 100-square grid fixes a denominator and implies a
        constant risk. These data require time-indexed cumulative estimates and differences instead.

        **What it says:** At {_early['label'].lower()}, the cumulative {_ep_short} rate was
        **{_early['inv']}% invasive vs {_early['con']}% conservative** (difference
        **{_early['diff']:+.1f} pts; 95% CI {_early['ci']}**), driven mainly by procedural infarctions. By
        {_late['label'].lower()} it was **{_late['inv']}% vs {_late['con']}%**
        (**{_late['diff']:+.1f} pts; 95% CI {_late['ci']}**). Taken at face value, this is roughly one extra
        event per {_nnh_early} patients treated invasively early and one fewer per {_nnt_late} late.
        Both confidence intervals cross zero, so neither difference is definitive.
        """
    )

    signature_view = mo.vstack(
        [
            mo.md(
                """
                ## The primary outcome, over time
                _CONSORT item 26. Because hazards were non-proportional, the absolute effect changes over time._
                """
            ),
            endpoint,
            mo.ui.altair_chart(signature),
            caption,
        ],
        gap=0.35,
    )
    signature_view
    return


@app.cell
def _(ARMS, CHART_W, EFFECTS, STATS_EXTRA, alt, colors, mo, pl, style):
    # --------------- EFFECT ESTIMATES: forest plot (log HR) ---------------
    ef = pl.DataFrame(EFFECTS)
    order = [e["outcome"] for e in EFFECTS]
    _lo_all = min(e["lo"] for e in EFFECTS)
    _hi_all = max(e["hi"] for e in EFFECTS)

    _rule = (
        alt.Chart(ef)
        .mark_rule(strokeWidth=2, color=colors["muted"])
        .encode(
            y=alt.Y("outcome:N", sort=order, title=None),
            x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=[round(_lo_all - 0.12, 2), round(_hi_all + 0.15, 2)]),
                    title="Hazard ratio (log scale) — invasive vs conservative"),
            x2="hi:Q",
        )
    )
    _pt = (
        alt.Chart(ef)
        .mark_point(size=110, filled=True, color=colors["muted"])
        .encode(
            y=alt.Y("outcome:N", sort=order),
            x="hr:Q",
            tooltip=[
                alt.Tooltip("outcome:N", title="Outcome"),
                alt.Tooltip("hr:Q", title="HR"),
                alt.Tooltip("lo:Q", title="95% CI low"),
                alt.Tooltip("hi:Q", title="95% CI high"),
            ],
        )
    )
    _null = (
        alt.Chart(pl.DataFrame({"x": [1.0]}))
        .mark_rule(strokeDash=[5, 4], color=colors["muted"])
        .encode(x="x:Q")
    )

    forest = style(
        (_null + _rule + _pt).properties(
            width=CHART_W,
            height=140,
            title=alt.TitleParams(
                "Both confidence intervals include HR = 1",
                subtitle="Points show covariate-adjusted hazard ratios; rules show 95% CIs. The dashed line marks HR = 1.",
            ),
        )
    )

    _prim, _death = EFFECTS
    forest_view = mo.vstack(
        [
            mo.md(
                """
                ## Effect estimates
                _CONSORT item 26. Table 2 reports hazard ratios for these two outcomes. The primary composite
                had non-proportional hazards, so the cumulative-rate view appears first._
                """
            ),
            mo.ui.altair_chart(forest),
            mo.md(
                f"""
                Primary composite: **{ARMS[0]['primary_events']} vs {ARMS[1]['primary_events']} events;
                HR {_prim['hr']:.2f} (95% CI {_prim['lo']:.2f}–{_prim['hi']:.2f}); P = {_prim['p']:.2f}**.
                Death from any cause: **{ARMS[0]['deaths']} vs {ARMS[1]['deaths']} deaths;
                HR {_death['hr']:.2f} (95% CI {_death['lo']:.2f}–{_death['hi']:.2f})**. This was the only outcome
                with proportional hazards. Over five years the restricted mean event-free time differed by
                **{STATS_EXTRA['rmst_days']} days (95% CI {STATS_EXTRA['rmst_ci']})**, and the prespecified
                Bayesian analysis estimated the probability of a >3-point 5-year benefit at
                **{STATS_EXTRA['bayes_benefit_pct']}%** versus **{STATS_EXTRA['bayes_harm_str']}** for a
                >3-point harm. These estimates were close to the null, although the event timing differed.
                """
            ),
        ],
        gap=0.35,
    )
    forest_view
    return


@app.cell
def _(ARMS, DEF_SENS, STATS_EXTRA, TRIAL, CHART_W, alt, colors, mo, pl, style):
    # ------------------------- HARMS + DEFINITION SENSITIVITY -------------------------
    ds = pl.DataFrame(DEF_SENS)
    _arm_scale = alt.Scale(
        domain=["Invasive", "Conservative"],
        range=[colors["invasive"], colors["conservative"]],
    )

    _slope = (
        alt.Chart(ds)
        .mark_line(point={"size": 110, "filled": True})
        .encode(
            x=alt.X("definition:N", title=None, sort=["Trial definition", "Secondary MI definition"]),
            y=alt.Y("rate:Q", title="Cumulative primary-outcome rate (%)", scale=alt.Scale(domain=[0, 24])),
            color=alt.Color("arm:N", scale=_arm_scale, title=None),
            detail="panel:N",
            tooltip=[
                alt.Tooltip("panel:N", title="Timepoint"),
                alt.Tooltip("arm:N", title="Arm"),
                alt.Tooltip("rate:Q", title="Rate (%)", format=".1f"),
                alt.Tooltip("tip:N", title="Difference (invasive − conservative)"),
            ],
        )
    )
    def_sens_chart = style(
        _slope.properties(width=260, height=220).facet(
            column=alt.Column("panel:N", sort=["At 6 months", "At 5 years"], title=None),
        ).properties(
            title=alt.TitleParams(
                "The MI definition changes the estimated effect",
                subtitle="Each slope pair compares the trial MI definition with the broader secondary definition.",
            ),
        )
    )

    harms_md = mo.md(
        f"""
        ## Harms, and the definition problem
        _CONSORT items 15 & 27 (harms) and 26 (secondary outcomes)._

        The early excess in the invasive arm was **procedural**: more infarctions during early follow-up,
        offset later by *fewer* nonprocedural infarctions (**{ARMS[0]['mi_events']} vs {ARMS[1]['mi_events']}
        MIs overall**). Deaths were balanced: **{ARMS[0]['deaths']} vs {ARMS[1]['deaths']}**. The invasive
        strategy produced **more hospitalizations for heart failure and fewer for unstable angina**.
        The key secondary (CV death or MI: **{ARMS[0]['secondary_events']} vs {ARMS[1]['secondary_events']}**
        events) mirrored the primary composite.

        Under the **secondary (broader) MI definition**, which counts more procedural infarctions, the
        six-month primary-outcome difference increased from +1.9 to +6.5 percentage points. The five-year
        difference changed from favouring invasive care to numerically favouring conservative care.
        The authors described the additional procedural infarctions as being "of uncertain clinical importance."
        """
    )

    harms_note = mo.Html(
        f"""
        <div style="background:{colors['panel2']}; border-left:4px solid {colors['bad']};
                    border-radius:8px; padding:12px 16px; font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            <strong>Interpretation:</strong> the MI definition changed the direction of the early estimate and the
            sign of the five-year difference, although neither definition produced a significant overall
            treatment effect. The sensitivity analysis shows how procedural events affect this composite
            endpoint. Reported limitations also include reduced power (planned
            {STATS_EXTRA['planned_n']:,} → randomised {ARMS[0]['n'] + ARMS[1]['n']:,}; {STATS_EXTRA['power_pct']}% power
 for a {STATS_EXTRA['relative_reduction_pct']}% relative reduction), lower-than-expected event rates,
 growing uncertainty past the {TRIAL['median_followup_years']}-year median follow-up, limited generalisability outside the
            eligible population, core-lab inability to confirm qualifying ischemia in
            {STATS_EXTRA['ischemia_unconfirmed_pct']}% of randomised patients (subgroup-neutral), and
            quality-of-life outcomes reported separately.
        </div>
        """
    )

    harms_view = mo.vstack([harms_md, mo.ui.altair_chart(def_sens_chart), harms_note], gap=0.35)
    harms_view
    return


@app.cell
def _(TRIAL, colors, mo):
    # --------------------------- OPEN SCIENCE ---------------------------
    open_science = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            <h2 style="font-family:Inter, ui-sans-serif, system-ui, sans-serif;">Open science</h2>
            <p style="color:{colors['muted']}; margin-top:-0.4rem;">
                <em>CONSORT 2025 items 2–5 cover registration, protocol access, data sharing, funding, and conflicts.</em>
            </p>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:12px;">
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Registration (item 2)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">{TRIAL['registration']}</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Protocol & SAP (item 3)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">Protocol posted at NEJM.org</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Data sharing (item 4)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">Statement in the full text</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Funding & COI (item 5)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">NHLBI + industry; sponsors had no data access or analytic role; disclosures published</div>
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
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif;">
            <table style="border-collapse:collapse; width:100%; font-family:Inter, ui-sans-serif, system-ui, sans-serif;">
                <thead>
                    <tr style="border-bottom:2px solid {colors['grid']}; text-align:left;
                               font-size:0.72rem; text-transform:uppercase; letter-spacing:0.06em; color:{colors['muted']};">
                        <th style="padding:6px 10px;">Section</th>
                        <th style="padding:6px 10px;">Item</th>
                        <th style="padding:6px 10px;">Topic</th>
                        <th style="padding:6px 10px;">In ISCHEMIA</th>
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
        <div style="background:{colors['panel']}; border:1px solid #D8D4D7; border-radius:10px;
                    padding:14px 16px; font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            Of the {_top_level_items} top-level CONSORT 2025 items ({len(CHECKLIST)} checklist rows), this
            2020 paper substantively covers <strong>{_covered} of {len(CHECKLIST)} rows</strong>. The only gap is
            <strong>patient and public involvement (item 8)</strong>, which CONSORT added in 2025. The trial already
            reports prospective registration, a posted protocol, a data-sharing statement, and protocol changes.
        </div>
        """
    )

    checklist_view = mo.vstack(
        [
            mo.md(
                """
                ## The CONSORT 2025 checklist, item by item
                _Filter by section. Each row pairs a checklist item with where ISCHEMIA reports it._
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
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['muted']}; font-size:0.86rem;
                    border-top:1px solid {colors['grid']}; padding-top:12px; line-height:1.5;">
            <strong style="color:{colors['ink']};">Source &amp; provenance.</strong>
            {TRIAL['citation']} DOI <a href="https://doi.org/{TRIAL['doi']}" style="color:{colors['conservative']};">{TRIAL['doi']}</a>;
            registered as {TRIAL['registration']}.
            Checklist: Hopewell S, et al. CONSORT 2025 Statement. <em>BMJ</em> 2025;388:e081123.
            Worked from the published full text (NIH Public Access author manuscript, extracted verbatim to
            papers/ischemia-text.txt). Every value in this notebook is transcribed from that text. No denominator
            was reconstructed from a percentage. Notes on transcription: (i) the
            4-year primary-outcome CI upper limit is printed as "0" in Table 2 and is shown as 0.0 here;
            (ii) printed differences in cumulative rates can differ from differences of the printed rates by up
            to 0.1 pp because the underlying estimates are rounded for publication; (iii) angiography /
            revascularization figures are crude proportions of each arm (the paper notes they differ from
            censoring-adjusted cumulative-incidence rates), and PCI/CABG shares are percentages of the invasive
            arm. The signature figure deliberately omits icon arrays: the endpoint is time-to-event with a
            violated proportional-hazards assumption (P &lt; 0.001), estimated by competing-risk
            cumulative-incidence functions, so fixed-denominator grids would imply false precision.
            This audit applies CONSORT 2025 retrospectively; the checklist postdates the trial.
        </div>
        """
    )
    provenance
    return


if __name__ == "__main__":
    app.run()
