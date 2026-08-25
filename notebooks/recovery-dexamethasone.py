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
        "dex": "#FA4616",     # intervention arm -> UF orange
        "usual": "#0021A5",   # reference arm -> UF blue
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
    # The RECOVERY Collaborative Group. Dexamethasone in Hospitalized
    # Patients with Covid-19 — Preliminary Report.
    # N Engl J Med 2020;384:693-704.  DOI 10.1056/NEJMoa2021436
    # Registrations: NCT04381936 · ISRCTN50189673
    # Platform trial: this notebook reads ONLY the dexamethasone-vs-usual-
    # care comparison. Every value below comes from the pre-extracted full
    # text (papers/recovery-text.txt). No denominator was reconstructed:
    # the paper prints counts and totals for every rate shown, and each
    # published percentage (22.9%, 41.4%, ...) reproduces from those counts
    # to within 0.05 percentage points.
    # =====================================================================

    TRIAL = {
        "name": "RECOVERY · Dexamethasone",
        "comparison": "Dexamethasone versus usual care (within the RECOVERY platform trial)",
        "title": "Dexamethasone in Hospitalized Patients with Covid-19 — Preliminary Report",
        "citation": "The RECOVERY Collaborative Group. N Engl J Med 2020;384:693-704.",
        "doi": "10.1056/NEJMoa2021436",
        "registrations": "NCT04381936 · ISRCTN50189673",
        "recruitment": "Mar 19 – Jun 8, 2020",
        "centers": 176,
        "geography": "National Health Service organizations, United Kingdom",
    }

    # Participant flow (item 22), from Figure 1. The platform screened-in
    # cohort precedes this comparison: 11,303 patients were randomised across
    # all RECOVERY domains; 1,948 were excluded from the dexamethasone
    # comparison for stated reasons (may have >1 reason); the rest entered
    # dexamethasone-vs-other-treatment allocations, of whom 2,930 went to
    # another active treatment and 6,425 formed the dexamethasone-vs-usual-
    # care contrast analysed here.
    FLOW = {
        "recruited_platform": 11303,
        "excluded_comparison": 1948,
        "excluded_no_drug": 357,
        "excluded_unsuitable": 1707,
        "randomized_dex_or_other": 9355,
        "other_active_treatment": 2930,
        "randomized": 6425,
        "dex_assigned": 2104,
        "usual_assigned": 4321,
        "dex_received": 1975,
        "dex_received_den": 2079,
        "usual_crossover": 336,
        "usual_crossover_den": 4278,
        "dex_withdrew": 6,
        "usual_withdrew": 1,
        "dex_analyzed": 2104,
        "usual_analyzed": 4321,
        "dex_second_randomization": 95,
        "usual_second_randomization": 276,
    }

    # Arms: exposure fidelity and primary-outcome deaths at 28 days.
    ARMS = [
        {
            "arm": "Dexamethasone",
            "n": 2104,
            "deaths": 482,
            "received": 1975,
            "received_n": 2079,
            "median_days": 7,
            "iqr_lo": 3,
            "iqr_hi": 10,
        },
        {
            "arm": "Usual care",
            "n": 4321,
            "deaths": 1110,
            "crossover": 336,
            "crossover_n": 4278,
        },
    ]

    # Mortality rate ratios (age-adjusted, Cox regression) — overall and by
    # level of respiratory support at randomization (paper Figures 2 & 3;
    # event counts from Figure 3 annotations).
    EFFECTS = [
        {
            "group": "All patients",
            "n": 6425,
            "dex_events": 482, "dex_n": 2104,
            "uc_events": 1110, "uc_n": 4321,
            "rr": 0.83, "lo": 0.75, "hi": 0.93,
        },
        {
            "group": "Invasive mechanical ventilation",
            "n": 1007,
            "dex_events": 95, "dex_n": 324,
            "uc_events": 283, "uc_n": 683,
            "rr": 0.64, "lo": 0.51, "hi": 0.81,
        },
        {
            "group": "Oxygen only",
            "n": 3883,
            "dex_events": 298, "dex_n": 1279,
            "uc_events": 682, "uc_n": 2604,
            "rr": 0.82, "lo": 0.72, "hi": 0.94,
        },
        {
            "group": "No respiratory support",
            "n": 1535,
            "dex_events": 89, "dex_n": 501,
            "uc_events": 145, "uc_n": 1034,
            "rr": 1.19, "lo": 0.91, "hi": 1.55,
        },
    ]

    # Age-adjusted ABSOLUTE mortality reductions the paper reports for the
    # two supported strata (Results section). No adjusted overall absolute
    # difference is printed; the notebook derives the crude one from counts.
    ABS_REDUCTION = [
        ("Invasive mechanical ventilation", 12.3, 6.3, 17.6),
        ("Oxygen only", 4.2, 1.4, 6.7),
    ]

    # Secondary outcomes (Table 2). Ratios are age-adjusted rate ratios
    # (discharge, 28-day mortality) or risk ratios (ventilation outcomes);
    # * = among patients NOT on invasive mechanical ventilation at entry.
    SECONDARY = [
        {
            "outcome": "Discharged alive within 28 days",
            "dex": "1413/2104 (67.2%)", "usual": "2745/4321 (63.5%)",
            "ratio": "1.10 (1.03–1.17)", "reading": "favours dexamethasone",
        },
        {
            "outcome": "Ventilation or death*",
            "dex": "456/1780 (25.6%)", "usual": "994/3638 (27.3%)",
            "ratio": "0.92 (0.84–1.01)", "reading": "CI includes 1 — uncertain",
        },
        {
            "outcome": "Progression to ventilation*",
            "dex": "102/1780 (5.7%)", "usual": "285/3638 (7.8%)",
            "ratio": "0.77 (0.62–0.95)", "reading": "favours dexamethasone",
        },
        {
            "outcome": "Death*",
            "dex": "387/1780 (21.7%)", "usual": "827/3638 (22.7%)",
            "ratio": "0.93 (0.84–1.03)", "reading": "CI includes 1 — uncertain",
        },
    ]

    # Baseline (item 25), Table 1 — per arm. Groups were balanced on every
    # characteristic except mean age (P = 0.01), which motivated the
    # age-adjusted rate ratios used throughout the paper.
    BASELINE = [
        ("Age — mean (SD), yr", "66.9 (15.4)", "65.8 (15.8)"),
        ("Age < 70 yr", "1141 (54%)", "2504 (58%)"),
        ("Male sex", "1338 (64%)", "2749 (64%)"),
        ("Days since symptom onset — median (IQR)", "8 (5–13)", "9 (5–13)"),
        ("Days in hospital — median (IQR)", "2 (1–5)", "2 (1–5)"),
        ("Respiratory support: none", "501 (24%)", "1034 (24%)"),
        ("Respiratory support: oxygen only", "1279 (61%)", "2604 (60%)"),
        ("Respiratory support: invasive mechanical ventilation", "324 (15%)", "683 (16%)"),
        ("Any major coexisting illness", "1174 (56%)", "2417 (56%)"),
        ("Diabetes", "521 (25%)", "1025 (24%)"),
        ("Heart disease", "586 (28%)", "1171 (27%)"),
        ("Chronic lung disease", "415 (20%)", "931 (22%)"),
        ("Laboratory-confirmed SARS-CoV-2", "1850 (88%)", "3848 (89%)"),
    ]

    # Context facts used in prose (all from the full text).
    CONTEXT = {
        "dose": "oral or intravenous dexamethasone, 6 mg once daily, up to 10 days (or until discharge)",
        "allocation_ratio": "2:1 toward usual care",
        "power_target": "≥2000 dexamethasone + ≥4000 usual-care patients gave ≥90% power at a two-sided P value of 0.01 to detect a 20% proportional (4-point absolute) mortality reduction if 28-day mortality were 20%",
        "announcement": "June 16, 2020 — nearly 100 days after the protocol was first drafted; U.K. practice changed the same day",
        "trend_chi2": "11.5",
    }
    return ABS_REDUCTION, ARMS, BASELINE, CONTEXT, EFFECTS, FLOW, SECONDARY, TRIAL


@app.cell
def _():
    # ------------------------------------------------------------------
    # CONSORT 2025 checklist (Hopewell S, et al. BMJ 2025;388:e081123),
    # each item paired with how the RECOVERY dexamethasone report (2020)
    # presents it. 30 top-level items, 42 reporting rows.
    # status: reported | partial | na | gap
    # ------------------------------------------------------------------
    CHECKLIST = [
        ("Title and abstract", "1a", "Identification as a randomised trial", "partial", "Randomisation stated in abstract; title omits “randomised”"),
        ("Title and abstract", "1b", "Structured summary", "reported", "NEJM structured abstract"),
        ("Open science", "2", "Trial registration", "reported", "Dual registration: NCT04381936 · ISRCTN50189673"),
        ("Open science", "3", "Protocol & statistical analysis plan", "reported", "Available at NEJM.org and recoverytrial.net"),
        ("Open science", "4", "Data sharing (de-identified IPD, code)", "reported", "Data sharing statement published with the article"),
        ("Open science", "5a", "Funding & role of funders", "reported", "UKRI/NIHR grant + core funders; funders had no role"),
        ("Open science", "5b", "Conflicts of interest", "reported", "Author disclosure forms with the article"),
        ("Introduction", "6", "Background & rationale", "reported", "Glucocorticoids debated; inflammation-driven lung injury"),
        ("Introduction", "7", "Objectives (benefits & harms)", "reported", "Effect of dexamethasone on 28-day mortality"),
        ("Methods", "8", "Patient & public involvement", "gap", "Not reported — item new in 2025"),
        ("Methods", "9", "Trial design", "reported", "Open-label platform RCT; 2:1 allocation to usual care"),
        ("Methods", "10", "Changes to trial protocol", "reported", "Age cap removed May 9, 2020; SAP amended for age adjustment"),
        ("Methods", "11", "Trial setting", "reported", "176 NHS organizations across the UK"),
        ("Methods", "12a", "Eligibility — participants", "reported", "Hospitalised, suspected/lab-confirmed SARS-CoV-2"),
        ("Methods", "12b", "Eligibility — sites / deliverers", "na", "Any participating NHS organization; no extra criteria"),
        ("Methods", "13", "Intervention & comparator", "reported", "6 mg once daily ≤10 days vs usual care alone"),
        ("Methods", "14", "Outcomes", "reported", "Primary 28-day mortality; prespecified secondaries"),
        ("Methods", "15", "Harms — definition & assessment", "partial", "Death is the primary outcome; no AE definitions in this report"),
        ("Methods", "16a", "Sample size", "reported", "Steering-committee sizing: ≥2000 + ≥4000, 90% power, α=0.01"),
        ("Methods", "16b", "Interim analyses & stopping", "partial", "Independent DMC named; boundaries not detailed here"),
        ("Methods", "17a", "Sequence generation", "reported", "Web-based randomisation system"),
        ("Methods", "17b", "Randomisation type / restriction", "reported", "Unstratified, 2:1 fixed allocation"),
        ("Methods", "18", "Allocation concealment", "reported", "Concealed within the web-based system"),
        ("Methods", "19", "Implementation", "reported", "Central web-based entry; treating clinician prescribed"),
        ("Methods", "20a", "Blinding — who", "partial", "Open label: patients and local staff aware; objective endpoint"),
        ("Methods", "20b", "Blinding — how", "na", "Not applicable (open-label)"),
        ("Methods", "21a", "Statistical methods", "reported", "Cox regression; KM curves; log-binomial for composites"),
        ("Methods", "21b", "Who is in each analysis", "reported", "All randomised, as assigned (intention-to-treat)"),
        ("Methods", "21c", "Missing data", "reported", "99.9% complete; explicit censoring rule for 0.1%"),
        ("Methods", "21d", "Additional analyses", "reported", "Prespecified subgroups; sensitivity without age adjustment"),
        ("Results", "22a", "Participant flow", "reported", "Figure 1 spans platform → this comparison"),
        ("Results", "22b", "Losses & exclusions", "reported", "Reasons given at each exclusion; 6 vs 1 withdrawals"),
        ("Results", "23a", "Recruitment & follow-up dates", "reported", "Mar 19 – Jun 8, 2020; data cutoff Jul 6, 2020"),
        ("Results", "23b", "Why the trial ended", "reported", "Dexamethasone enrolment closed on exceeding target"),
        ("Results", "24a", "Intervention delivery / fidelity", "reported", "95% received ≥1 dose; median 7 days (IQR 3–10)"),
        ("Results", "24b", "Concomitant care", "reported", "Other treatments tracked (azithromycin 24% vs 25%)"),
        ("Results", "25", "Baseline data", "reported", "Table 1 by arm AND by respiratory-support stratum"),
        ("Results", "26", "Numbers analysed, outcomes, estimation", "reported", "Counts, %, rate ratios with CI; absolute gains in strata"),
        ("Results", "27", "Harms", "partial", "No adverse-event table in this preliminary report"),
        ("Results", "28", "Ancillary analyses", "reported", "Subgroup figures; post hoc positive-test sensitivity"),
        ("Discussion", "29", "Interpretation", "reported", "Benefit with respiratory support; none without"),
        ("Discussion", "30", "Limitations", "partial", "Constraints discussed in text; no dedicated section"),
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
    return (section,)


@app.cell
def _(ARMS, FLOW, FONT, TRIAL, colors, card, mo):
    # ---------------------------- HERO ----------------------------
    import math

    _dex = ARMS[0]
    _uc = ARMS[1]
    _dex_rate = 100 * _dex["deaths"] / _dex["n"]
    _uc_rate = 100 * _uc["deaths"] / _uc["n"]
    _ard = _uc_rate - _dex_rate
    # NNT is conventionally rounded up: a fractional patient cannot be saved.
    _nnt = math.ceil(1 / (_ard / 100))

    hero = mo.Html(
        f"""
        <div style="background:{colors['panel']}; border:1px solid #D8D4D7; border-radius:14px;
                    padding:18px 20px; font-family:{FONT}; color:{colors['ink']};">
            <div style="text-transform:uppercase; letter-spacing:0.15em; font-size:0.72rem;
                        color:{colors['muted']}; margin-bottom:0.5rem;">
                A randomised trial, read through CONSORT 2025 · {TRIAL["comparison"]}
            </div>
            <div style="font-size:1.82rem; line-height:1.12; margin-bottom:0.25rem;">{TRIAL['name']}</div>
            <div style="font-size:1.0rem; color:#343741; margin-bottom:0.35rem;">{TRIAL['title']}</div>
            <div style="max-width:820px; font-size:0.96rem; line-height:1.42; color:#343741; margin-bottom:0.85rem;">
                Dexamethasone reduced 28-day mortality in hospitalised patients who needed oxygen or invasive
                ventilation. The trial did not show benefit in patients who needed no respiratory support.
                This notebook covers only dexamethasone versus usual care within the RECOVERY platform trial.
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
                {card("Randomised population", f"{FLOW['randomized']:,}", "2:1 toward usual care · 176 UK NHS organisations", colors["ink"])}
                {card("Intervention: dexamethasone", f"{_dex_rate:.1f}%", f"{_dex['deaths']:,} of {_dex['n']:,} died by 28 days", colors["dex"])}
                {card("Reference: usual care", f"{_uc_rate:.1f}%", f"{_uc['deaths']:,} of {_uc['n']:,} died by 28 days", colors["usual"])}
                {card("Main contrast", f"–{_ard:.1f} pts", f"RR 0.83 (95% CI 0.75–0.93) · ≈1 death prevented per {_nnt} treated", colors["good"])}
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
            design and eligibility (items 9, 11, 12), intervention specification and delivery (13, 24),
            participant flow (22), baseline balance (25), absolute and relative effects (26), harms (15, 27),
            open-science expectations (2–5), and interpretation/limitations (29–30).
            The final table separates reported, partial, not-applicable, and missing items.
        </div>
        """
    )
    consort_blurb
    return


@app.cell
def _(CONTEXT, TRIAL, mo):
    design = mo.md(
        "**The design in one paragraph**\n\n"
        f"**RECOVERY** was a controlled, **open-label platform randomised trial** across {TRIAL['centers']} NHS "
        "organisations in the United Kingdom. The platform evaluated several Covid-19 treatments at the same time. "
        "Eligible patients had suspected or laboratory-confirmed SARS-CoV-2 infection and no clinician-judged "
        "substantial risk from participation (pregnant or breastfeeding women were eligible). Within each domain, "
        f"patients were allocated by a concealed web-based system, {CONTEXT['allocation_ratio']}. "
        "This notebook covers the dexamethasone domain only. It compares oral or intravenous **dexamethasone 6 mg "
        "once daily for up to 10 days** with **usual care alone**. There was no placebo or masking, but death was "
        "an objective endpoint. The primary outcome was all-cause mortality within 28 days. The intention-to-treat "
        "analysis used age-adjusted Cox-regression rate ratios because the dexamethasone group was 1.1 years older "
        f"on average. Recruitment ran {TRIAL['recruitment']} and stopped after enrolment exceeded the target.\n\n"
        "_CONSORT items 9, 11, 12, 17–21._"
    )
    design
    return


@app.cell
def _(ARMS, CHART_W, FONT, colors, mo):
    # ------------- INTERVENTION DELIVERY: prescribed vs received -------------
    # A drug trial's fidelity display is exposure, not an achieved-vs-target band.
    dex = ARMS[0]
    uc = ARMS[1]
    fidelity_rows = [
        {
            "arm": dex["arm"],
            "kind": "Received ≥1 dose",
            "pct": 100 * dex["received"] / dex["received_n"],
            "label": f'{dex["received"]:,} of {dex["received_n"]:,} with completed follow-up form',
        },
        {
            "arm": uc["arm"],
            "kind": "Received dexamethasone anyway",
            "pct": 100 * uc["crossover"] / uc["crossover_n"],
            "label": f'{uc["crossover"]:,} of {uc["crossover_n"]:,}; crossover reduced between-arm separation',
        },
    ]
    _rows = []
    for row in fidelity_rows:
        _color = colors["dex"] if row["arm"] == "Dexamethasone" else colors["usual"]
        _rows.append(
            f"""
            <div style="display:grid; grid-template-columns:220px minmax(180px,1fr) 52px; gap:10px; align-items:center;">
                <div style="font-size:0.78rem; color:{colors['ink']};">{row['arm']}: {row['kind']}</div>
                <div style="height:18px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                    <div style="width:{row['pct']}%; height:100%; background:{_color}; border-radius:3px;"></div>
                </div>
                <div style="font-size:0.8rem; font-weight:700; color:{_color}; text-align:right;">{row['pct']:.1f}%</div>
            </div>
            """
        )

    _fidelity_panel = mo.Html(
        f"""
        <div role="img" aria-label="Dexamethasone exposure by randomized arm" style="font-family:{FONT}; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">Assigned treatment produced different dexamethasone exposure</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 12px;">Orange and blue identify the randomised arms. Each row shows exposure to dexamethasone.</div>
            <div style="display:grid; gap:9px;">{''.join(_rows)}</div>
        </div>
        """
    )

    fidelity_view = mo.vstack(
        [
            mo.md(
                """
                ## Intervention delivery
                _CONSORT items 13 and 24. The chart compares assigned treatment with treatment received._
                """
            ),
            _fidelity_panel,
            mo.md(
                f"""Among patients with a completed follow-up form, **95%** of the dexamethasone arm received at least
                one dose ({dex['received']:,}/{dex['received_n']:,}), with a median treatment duration of
                **{dex['median_days']} days (IQR {dex['iqr_lo']}–{dex['iqr_hi']})**. In the usual-care arm,
                **{uc['crossover']} of {uc['crossover_n']:,} (8%)** received dexamethasone as part of routine clinical
                care. This crossover reduced the separation between the randomised groups."""
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

    def _excl(n, label):
        return (
            f'<div style="border-left:2px dashed {colors["grid"]}; padding-left:12px;">'
            f'{box("Excluded", n, colors["muted"], label)}</div>'
        )

    flow_html = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; max-width:720px; margin:0 auto;">
            {box("Recruited into the RECOVERY platform", FLOW["recruited_platform"], colors["dark"],
                 "hospitalised Covid-19, all treatment domains")}
            <div style="display:grid; grid-template-columns:1fr 1fr; align-items:center; gap:8px; margin:2px 0;">
                <div style="text-align:center; color:{colors['muted']}; font-size:1.1rem;">↓</div>
                {_excl(FLOW["excluded_comparison"], f'could not enter the dexamethasone comparison ({FLOW["excluded_no_drug"]} drug unavailable · {FLOW["excluded_unsuitable"]} clinically unsuitable)')}
            </div>
            {box("Randomised within the dexamethasone domain (dex vs other treatments)", FLOW["randomized_dex_or_other"], colors["dark"])}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; align-items:center; gap:8px; margin:2px 0;">
                <div style="text-align:center; color:{colors['muted']}; font-size:1.1rem;">↓</div>
                {box("Allocated to another active treatment — outside this notebook's scope", FLOW["other_active_treatment"], colors["muted"])}
            </div>
            {box("This comparison: randomised dexamethasone vs usual care", FLOW["randomized"], colors["accent"])}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div style="display:grid; gap:6px;">
                    {box("Allocated: dexamethasone", FLOW["dex_assigned"], colors["dex"])}
                    {arrow}
                    {_excl(FLOW["dex_withdrew"], "withdrew consent before follow-up")}
                    {arrow}
                    {box("Analysed for 28-day mortality", FLOW["dex_analyzed"], colors["dex"],
                         f'{FLOW["dex_second_randomization"]} later re-randomised in another domain; analysed here as assigned')}
                </div>
                <div style="display:grid; gap:6px;">
                    {box("Allocated: usual care alone", FLOW["usual_assigned"], colors["usual"])}
                    {arrow}
                    {_excl(FLOW["usual_withdrew"], "withdrew consent before follow-up")}
                    {arrow}
                    {box("Analysed for 28-day mortality", FLOW["usual_analyzed"], colors["usual"],
                         f'{FLOW["usual_second_randomization"]} later re-randomised in another domain; analysed here as assigned')}
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
                _CONSORT item 22. The diagram reconstructs the dexamethasone comparison from Figure 1._
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
    _rows = "\n".join(f"| {label} | {v_dex} | {v_uc} |" for label, v_dex, v_uc in BASELINE)
    baseline_text = (
        "## Baseline characteristics\n"
        "_CONSORT item 25. Table 1 of the paper reports by arm and by respiratory-support stratum; "
        "every characteristic was balanced except mean age (P = 0.01), which is why all rate ratios "
        "in this notebook are age-adjusted._\n\n"
        "| Characteristic | Dexamethasone (N = 2,104) | Usual care (N = 4,321) |\n"
        "|:---|:---|:---|\n"
        f"{_rows}"
    )
    baseline_view = mo.md(baseline_text)
    baseline_view
    return


@app.cell
def _(CHART_W, EFFECTS, alt, colors, mo, pl, style):
    # -------- OVERALL PRIMARY OUTCOME: absolute risk icon arrays --------
    # Clean fixed denominators exist for the overall comparison (482/2104 vs
    # 1110/4321), so a 10x10 waffle per arm is appropriate here.
    overall = EFFECTS[0]

    def _waffle_chart(arm_name, events, denom, rate_pct, color_key):
        died = round(rate_pct)
        rows = []
        for i in range(100):
            r, c = divmod(i, 10)
            rows.append(
                {
                    "arm": arm_name,
                    "row": r,
                    "col": c,
                    "status": "Died by 28 days" if i < died else "Alive at day 28",
                }
            )
        df = pl.DataFrame(rows)
        status_scale = alt.Scale(
            domain=["Died by 28 days", "Alive at day 28"],
            range=[colors[color_key], colors["neutral_bg"]],
        )
        chart = alt.Chart(df).mark_square(size=150, cornerRadius=2).encode(
            x=alt.X("col:O", axis=None),
            y=alt.Y("row:O", axis=None, sort="descending"),
            color=alt.Color("status:N", scale=status_scale, legend=None),
            tooltip=[alt.Tooltip("status:N", title="Outcome")],
        ).properties(
            width=CHART_W // 2 - 30,
            height=CHART_W // 2 - 30,
            title=alt.TitleParams(
                arm_name,
                subtitle=f"{rate_pct:.1f}% died  ·  ≈ {died} of every 100",
                color=colors[color_key],
            ),
        )
        return style(chart)

    dex_rate = 100 * overall["dex_events"] / overall["dex_n"]
    uc_rate = 100 * overall["uc_events"] / overall["uc_n"]

    waffle_view = mo.vstack(
        [
            mo.md(
                """
                ## Primary outcome: 28-day mortality
                _CONSORT item 26. Each square represents one patient per 100. The dexamethasone array has about
                two fewer death squares than the usual-care array._
                """
            ),
            mo.hstack(
                [
                    mo.ui.altair_chart(_waffle_chart("Dexamethasone", overall["dex_events"], overall["dex_n"], dex_rate, "dex")),
                    mo.ui.altair_chart(_waffle_chart("Usual care", overall["uc_events"], overall["uc_n"], uc_rate, "usual")),
                ],
                justify="center",
                gap=0.6,
            ),
            mo.md(
                f"""**{overall['dex_events']}/{overall['dex_n']:,} ({dex_rate:.1f}%)** died with dexamethasone versus
                **{overall['uc_events']:,}/{overall['uc_n']:,} ({uc_rate:.1f}%)** with usual care. The absolute reduction
                of **{uc_rate - dex_rate:.1f} percentage points** (age-adjusted rate ratio {overall['rr']},
                95% CI {overall['lo']}–{overall['hi']}; P&lt;0.001)."""
            ),
        ],
        gap=0.35,
    )
    waffle_view
    return


@app.cell
def _(ABS_REDUCTION, CHART_W, CONTEXT, EFFECTS, alt, colors, mo, pl, style):
    # -------- SIGNATURE FIGURE: respiratory-support subgroup panel --------
    # Paired dot-and-CI charts per stratum: absolute risk (left) and the
    # age-adjusted rate ratio with its CI (right). The two views are kept
    # side by side on purpose: the risk panel shows WHERE benefit lives,
    # the ratio panel shows WHICH intervals exclude 1.
    subgroups = EFFECTS[1:]
    sub_order = [s["group"] for s in subgroups]

    def _risk_rows(s):
        out = []
        for arm_key, ev_key, n_key in (("Dexamethasone", "dex_events", "dex_n"), ("Usual care", "uc_events", "uc_n")):
            events = s[ev_key]
            denom = s[n_key]
            pct = 100 * events / denom
            out.append(
                {
                    "group": s["group"],
                    "arm": arm_key,
                    "pct": pct,
                    "events": f"{events:,}/{denom:,}",
                }
            )
        return out

    risk_df = pl.DataFrame([row for s in subgroups for row in _risk_rows(s)])
    rr_df = pl.DataFrame(subgroups).with_columns((pl.col("lo") + pl.col("hi")).alias("_sum"))

    arm_scale = alt.Scale(domain=["Dexamethasone", "Usual care"], range=[colors["dex"], colors["usual"]])

    _risk_pts = (
        alt.Chart(risk_df)
        .mark_point(size=120, filled=True)
        .encode(
            y=alt.Y("group:N", sort=sub_order, title=None),
            x=alt.X("pct:Q", scale=alt.Scale(domain=[0, 45]), title="28-day mortality (%)"),
            color=alt.Color("arm:N", scale=arm_scale, legend=None),
            xOffset="arm:N",
            tooltip=[
                alt.Tooltip("group:N", title="Respiratory support at entry"),
                alt.Tooltip("arm:N", title="Arm"),
                alt.Tooltip("events:N", title="Deaths"),
                alt.Tooltip("pct:Q", title="Mortality", format=".1f"),
            ],
        )
    )
    _risk_connect = (
        alt.Chart(rr_df)
        .mark_rule(strokeDash=[2, 3], color=colors["muted"])
        .encode(y=alt.Y("group:N", sort=sub_order), detail="group:N")
    )

    _rr_rule = (
        alt.Chart(rr_df)
        .mark_rule(strokeWidth=2)
        .encode(
            y=alt.Y("group:N", sort=sub_order, title=None),
            x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=[0.4, 1.8]), title="Rate ratio (log scale) — dexamethasone vs usual care"),
            x2="hi:Q",
            color=alt.Color(
                "crosses_null:N",
                scale=alt.Scale(domain=["yes", "no"], range=[colors["muted"], colors["good"]]),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("group:N", title="Respiratory support at entry"),
                alt.Tooltip("rr:Q", title="Rate ratio"),
                alt.Tooltip("lo:Q", title="95% CI low"),
                alt.Tooltip("hi:Q", title="95% CI high"),
            ],
        )
    )
    _rr_pt = (
        alt.Chart(rr_df)
        .mark_point(size=130, filled=True)
        .encode(
            y=alt.Y("group:N", sort=sub_order),
            x="rr:Q",
            color=alt.Color(
                "crosses_null:N",
                scale=alt.Scale(domain=["yes", "no"], range=[colors["muted"], colors["good"]]),
                legend=None,
            ),
        )
    )
    _null = (
        alt.Chart(pl.DataFrame({"x": [1.0]}))
        .mark_rule(strokeDash=[5, 4], color=colors["ink"])
        .encode(x="x:Q")
    )

    _risk_panel = _risk_pts + _risk_connect
    _rr_panel = (_null + _rr_rule + _rr_pt)

    subgroup_view = mo.vstack(
        [
            mo.md(
                """
                ## Mortality by respiratory support at randomisation
                _CONSORT items 26 and 28._

                **Read it as:** The left panel shows absolute mortality in each randomised group. The right panel
                shows age-adjusted rate ratios and 95% CIs. Green marks identify CIs that exclude 1.

                **Why this geometry:** The paired panels show both the absolute risk within each respiratory-support
                stratum and the precision of the relative effect.
                """
            ),
            mo.hstack(
                [
                    mo.ui.altair_chart(
                        style(
                            _risk_panel.properties(
                                width=CHART_W // 2 - 40,
                                height=190,
                                title=alt.TitleParams(
                                    "Absolute mortality by stratum",
                                    subtitle="Each dot shows an arm's death rate. The dotted line links the two arms.",
                                ),
                            )
                        ),
                    ),
                    mo.ui.altair_chart(
                        style(
                            _rr_panel.properties(
                                width=CHART_W // 2 + 40,
                                height=190,
                                title=alt.TitleParams(
                                    "Rate ratios by respiratory support",
                                    subtitle="Green marks show CIs that exclude 1. Grey marks show CIs that include 1.",
                                ),
                            )
                        ),
                    ),
                ],
                justify="center",
                gap=0.5,
            ),
            mo.md(
                f"""**What it says:** Treatment effect differed by respiratory support at entry. Among patients already on **invasive mechanical
                ventilation**, mortality fell from **{EFFECTS[1]['uc_events']}/{EFFECTS[1]['uc_n']} ({100 * EFFECTS[1]['uc_events'] / EFFECTS[1]['uc_n']:.1f}%)**
                to **{EFFECTS[1]['dex_events']}/{EFFECTS[1]['dex_n']} ({100 * EFFECTS[1]['dex_events'] / EFFECTS[1]['dex_n']:.1f}%)**. The rate ratio was {EFFECTS[1]['rr']}
                (95% CI {EFFECTS[1]['lo']}–{EFFECTS[1]['hi']}), an age-adjusted **{ABS_REDUCTION[0][1]} percentage-point**
                reduction (95% CI {ABS_REDUCTION[0][2]}–{ABS_REDUCTION[0][3]}). With **oxygen only**, the fall was smaller:
                {EFFECTS[2]['dex_events']}/{EFFECTS[2]['dex_n']} ({100 * EFFECTS[2]['dex_events'] / EFFECTS[2]['dex_n']:.1f}%)
                vs {EFFECTS[2]['uc_events']}/{EFFECTS[2]['uc_n']} ({100 * EFFECTS[2]['uc_events'] / EFFECTS[2]['uc_n']:.1f}%). The rate ratio was {EFFECTS[2]['rr']}
                (95% CI {EFFECTS[2]['lo']}–{EFFECTS[2]['hi']}), a {ABS_REDUCTION[1][1]}-point reduction
                (95% CI {ABS_REDUCTION[1][2]}–{ABS_REDUCTION[1][3]}). But among patients needing **no respiratory
                support**, the point estimate was {EFFECTS[3]['dex_events']}/{EFFECTS[3]['dex_n']} ({100 * EFFECTS[3]['dex_events'] / EFFECTS[3]['dex_n']:.1f}%)
                vs {EFFECTS[3]['uc_events']}/{EFFECTS[3]['uc_n']} ({100 * EFFECTS[3]['uc_events'] / EFFECTS[3]['uc_n']:.1f}%). The rate ratio was {EFFECTS[3]['rr']}
                (95% CI {EFFECTS[3]['lo']}–{EFFECTS[3]['hi']}). This CI includes 1, so the data were compatible
                with no effect or possible harm. The chi-square test for trend
                across the three strata was {CONTEXT["trend_chi2"]}."""
            ),
        ],
        gap=0.35,
    )
    subgroup_view
    return


@app.cell
def _(CHART_W, EFFECTS, SECONDARY, alt, colors, mo, pl, style):
    # ------------------- FOREST PLOT: all effect estimates -------------------
    forest_rows = [
        {
            "outcome": "28-day mortality — all patients (primary)",
            "rr": EFFECTS[0]["rr"], "lo": EFFECTS[0]["lo"], "hi": EFFECTS[0]["hi"],
            "kind": "benefit",
        },
        {
            "outcome": "— on invasive ventilation",
            "rr": EFFECTS[1]["rr"], "lo": EFFECTS[1]["lo"], "hi": EFFECTS[1]["hi"],
            "kind": "benefit",
        },
        {
            "outcome": "— oxygen only",
            "rr": EFFECTS[2]["rr"], "lo": EFFECTS[2]["lo"], "hi": EFFECTS[2]["hi"],
            "kind": "benefit",
        },
        {
            "outcome": "— no respiratory support",
            "rr": EFFECTS[3]["rr"], "lo": EFFECTS[3]["lo"], "hi": EFFECTS[3]["hi"],
            "kind": "uncertain",
        },
        {
            "outcome": "Discharged alive within 28 days",
            "rr": 1.10, "lo": 1.03, "hi": 1.17,
            "kind": "benefit",
        },
        {
            "outcome": "Ventilation or death (no vent at entry)",
            "rr": 0.92, "lo": 0.84, "hi": 1.01,
            "kind": "uncertain",
        },
        {
            "outcome": "Progression to ventilation (no vent at entry)",
            "rr": 0.77, "lo": 0.62, "hi": 0.95,
            "kind": "benefit",
        },
    ]
    ef = pl.DataFrame(forest_rows)
    order = [r["outcome"] for r in forest_rows]
    x_domain = [0.55, 1.25]

    _rule = alt.Chart(ef).mark_rule(strokeWidth=2).encode(
        y=alt.Y("outcome:N", sort=order, title=None),
        x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=x_domain),
                title="Rate / risk ratio (log scale) — dexamethasone vs usual care"),
        x2="hi:Q",
        color=alt.Color(
            "kind:N",
            scale=alt.Scale(domain=["benefit", "uncertain"], range=[colors["good"], colors["muted"]]),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("rr:Q", title="Ratio"),
            alt.Tooltip("lo:Q", title="95% CI low"),
            alt.Tooltip("hi:Q", title="95% CI high"),
        ],
    )
    _pt = alt.Chart(ef).mark_point(size=110, filled=True).encode(
        y=alt.Y("outcome:N", sort=order),
        x="rr:Q",
        color=alt.Color("kind:N", scale=alt.Scale(domain=["benefit", "uncertain"], range=[colors["good"], colors["muted"]]), legend=None),
        tooltip=[
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("rr:Q", title="Ratio"),
        ],
    )
    _null = alt.Chart(pl.DataFrame({"x": [1.0]})).mark_rule(
        strokeDash=[5, 4], color=colors["muted"]
    ).encode(x="x:Q")

    forest = style(
        (_null + _rule + _pt).properties(
            width=CHART_W,
            height=230,
            title=alt.TitleParams(
                "Benefit varied by respiratory support",
                subtitle="Green marks show CIs that exclude 1. Grey marks show CIs that include 1. Ratios are age-adjusted.",
            ),
        )
    )

    forest_view = mo.vstack(
        [
            mo.md(
                """
                ## Effect estimates across outcomes
                _CONSORT item 26. Primary outcome and its respiratory-support subgroups, plus the Table 2
                secondary outcomes with usable intervals. For discharge, a ratio above 1 means that more
                patients were home by day 28. Grey rows have CIs that include 1._
                """
            ),
            mo.ui.altair_chart(forest),
        ],
        gap=0.35,
    )
    forest_view
    return


@app.cell
def _(SECONDARY, colors, mo):
    # ------------------------- HARMS + SECONDARY -------------------------
    _sec_lines = "\n".join(
        f"| {s['outcome']} | {s['dex']} | {s['usual']} | {s['ratio']} |" for s in SECONDARY
    )
    harms_md = mo.md(
        "## Harms, secondary outcomes, and what this preliminary report does not say\n"
        "_CONSORT items 15 &amp; 27 (harms) and 26 (secondary outcomes)._\n\n"
        "**Death was the primary outcome**, so fatal harms were part of the primary analysis. The report found "
        "no excess non-fatal harm and a shorter hospital stay. However, this **preliminary report** did not include "
        "an adverse-event table or counts for secondary infection and hyperglycaemia. Later reports provided "
        "additional safety detail.\n\n"
        "**Secondary outcomes** (Table 2):\n\n"
        "| Outcome | Dexamethasone | Usual care | Ratio (95% CI) |\n"
        "|:---|:---|:---|:---|\n"
        f"{_sec_lines}\n\n"
        "*Ratios are age-adjusted rate ratios (discharge, mortality) or risk ratios (ventilation outcomes); "
        "rows marked * exclude patients already on invasive mechanical ventilation at entry.*\n\n"
        "Concomitant treatment stayed balanced: azithromycin 24% vs 25%, and 0–3% received any other "
        "trial drug during follow-up."
    )

    harms_note = mo.Html(
        f"""
        <div style="background:{colors['panel2']}; border-left:4px solid {colors['good']};
                    border-radius:8px; padding:12px 16px; font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            <strong>Clinical interpretation:</strong> benefit was concentrated in patients who needed invasive
            ventilation or oxygen. The trial did not show benefit in patients who needed no respiratory support.
            The findings support dexamethasone for hypoxaemic Covid-19, not for patients without an oxygen need.
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
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            <h2 style="font-family:Inter, ui-sans-serif, system-ui, sans-serif;">Open science</h2>
            <p style="color:{colors['muted']}; margin-top:-0.4rem;">
                <em>CONSORT 2025 items 2–5 cover registration, protocol access, data sharing, funding, and conflicts.</em>
            </p>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:12px;">
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Registration (item 2)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">{TRIAL['registrations']}</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Protocol &amp; SAP (item 3)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">NEJM.org + recoverytrial.net</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Data sharing (item 4)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">Statement published with article</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Funding &amp; COI (item 5)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">UKRI/NIHR grant; no funder role; disclosures filed</div>
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
    _top_level_items = len({row[1].split("a")[0].split("b")[0].split("c")[0].split("d")[0] for row in CHECKLIST})

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
                        <th style="padding:6px 10px;">In RECOVERY (dex report)</th>
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
            Of the <strong>{_top_level_items} top-level CONSORT 2025 items ({len(CHECKLIST)} checklist rows)</strong>,
            this 2020 report substantively covers <strong>{_covered} of {len(CHECKLIST)} rows</strong>. The only gap is
            <strong>patient and public involvement (item 8)</strong>, which CONSORT added after the trial. Partial
            items reflect limited adverse-event detail in the preliminary report and the absence of blinding in
            the open-label design.
        </div>
        """
    )

    checklist_view = mo.vstack(
        [
            mo.md(
                """
                ## The CONSORT 2025 checklist, item by item
                _Filter by section. Each row pairs a checklist item with where the RECOVERY dexamethasone report
                addresses it._
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
            The RECOVERY Collaborative Group. Dexamethasone in Hospitalized Patients with Covid-19 —
            Preliminary Report. <em>N Engl J Med</em> 2020;384:693-704. DOI
            <a href="https://doi.org/{TRIAL['doi']}" style="color:{colors['usual']};">{TRIAL['doi']}</a>.
            Registered as {TRIAL['registrations']}. Checklist: Hopewell S, et al. CONSORT 2025 Statement.
            <em>BMJ</em> 2025;388:e081123. Every figure is rendered from the data literals near the top of this
            notebook, and every rate shown reproduces from counts printed in the paper — no denominator was
            reconstructed. Icon arrays round each rate to the nearest whole square (23 of 100 for the 22.9%
            dexamethasone arm, 26 for the 25.7% usual-care arm). Absolute differences in the hero and waffle
            captions are crude (unadjusted) differences computed from counts; the paper's age-adjusted absolute
            reductions (12.3 and 4.2 points) are shown separately and labelled as such. CONSORT 2025 is applied
            here retrospectively; it postdates this 2020 report. RECOVERY is a platform trial: this
            notebook reads only the dexamethasone-vs-usual-care comparison and visualises no other domain's arms.
        </div>
        """
    )
    provenance
    return


if __name__ == "__main__":
    app.run()
