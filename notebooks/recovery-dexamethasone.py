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
        "dex": "#b3544c",     # the exposed arm -> clay red (kept red even though beneficial)
        "usual": "#3f7d78",   # the reference arm -> teal
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
        <div style="background:{colors['panel']}; border:1px solid #ddd8ce; border-radius:14px;
                    padding:18px 20px; font-family:{FONT}; color:{colors['ink']};">
            <div style="text-transform:uppercase; letter-spacing:0.15em; font-size:0.72rem;
                        color:{colors['muted']}; margin-bottom:0.5rem;">
                A randomised trial, read through CONSORT 2025 · {TRIAL["comparison"]}
            </div>
            <div style="font-size:1.82rem; line-height:1.12; margin-bottom:0.25rem;">{TRIAL['name']}</div>
            <div style="font-size:1.0rem; color:#45515b; margin-bottom:0.35rem;">{TRIAL['title']}</div>
            <div style="max-width:820px; font-size:0.96rem; line-height:1.42; color:#45515b; margin-bottom:0.85rem;">
                This notebook is not just a visual summary; it is a CONSORT-shaped read of one comparison inside a
                <strong>platform trial</strong>. RECOVERY randomised hospitalised Covid-19 patients across many treatment
                domains at once; here only the dexamethasone-versus-usual-care domain is analysed — other domains'
                arms are never shown. The trial found lower 28-day mortality where it mattered most (invasive
                ventilation, oxygen), honest uncertainty where it did not (no respiratory support), and became
                standard of care within a single day.
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
                {card("Randomised to this contrast", f"{FLOW['randomized']:,}", "2:1 toward usual care · 176 UK NHS organizations", colors["ink"])}
                {card("Dexamethasone death", f"{_dex_rate:.1f}%", f"{_dex['deaths']:,} of {_dex['n']:,} died by 28 days", colors["dex"])}
                {card("Usual-care death", f"{_uc_rate:.1f}%", f"{_uc['deaths']:,} of {_uc['n']:,} died by 28 days", colors["usual"])}
                {card("Absolute benefit", f"–{_ard:.1f} pts", f"RR 0.83 (95% CI 0.75–0.93) · ≈1 death prevented per {_nnt} treated", colors["good"])}
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
            The final table is the audit trail: what this remarkably fast 2020 report covers in full,
            what only partially, and what CONSORT added after the trial was run.
        </div>
        """
    )
    consort_blurb
    return


@app.cell
def _(CONTEXT, TRIAL, mo):
    design = mo.md(
        "**The design in one paragraph**\n\n"
        f"**RECOVERY** is a controlled, **open-label platform randomised trial** evaluating multiple potential "
        f"treatments for Covid-19 simultaneously across {TRIAL['centers']} NHS organizations in the United Kingdom. "
        "Eligible patients had suspected or laboratory-confirmed SARS-CoV-2 infection and no clinician-judged "
        "substantial risk from participation (pregnant or breastfeeding women were eligible). Within each domain, "
        f"patients were allocated by a concealed web-based system — {CONTEXT['allocation_ratio']} toward usual care — "
        "and this notebook reads the dexamethasone domain alone: oral or intravenous **dexamethasone 6 mg once daily "
        "for up to 10 days** versus **usual care alone**, with no placebo and no masking (patients and local staff "
        "knew the assignment; the endpoint, death, was objective). The primary outcome was all-cause mortality within "
        "28 days; analyses were intention-to-treat with Cox-regression rate ratios adjusted for age in three "
        f"categories after chance left the dexamethasone arm 1.1 years older. Recruitment ran {TRIAL['recruitment']} "
        "and closed early once enrolment exceeded target.\n\n"
        "_CONSORT items 9, 11, 12, 17–21._"
    )
    design
    return


@app.cell
def _(ARMS, CHART_W, alt, colors, mo, pl, style):
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
            "label": f'{uc["crossover"]:,} of {uc["crossover_n"]:,} — crossover contaminates the contrast slightly',
        },
    ]
    fidelity_df = pl.DataFrame(fidelity_rows)

    fidelity_chart = alt.Chart(fidelity_df).mark_bar(size=30, cornerRadius=3).encode(
        y=alt.Y("arm:N", title=None, sort=["Dexamethasone", "Usual care"]),
        x=alt.X("pct:Q", scale=alt.Scale(domain=[0, 100]), title="Patients receiving dexamethasone (%)"),
        color=alt.Color(
            "arm:N",
            scale=alt.Scale(domain=["Dexamethasone", "Usual care"], range=[colors["dex"], colors["usual"]]),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip("arm:N", title="Arm"),
            alt.Tooltip("kind:N", title="Category"),
            alt.Tooltip("pct:Q", title="Percent", format=".1f"),
            alt.Tooltip("label:N"),
        ],
    ).properties(
        width=CHART_W,
        height=140,
        title=alt.TitleParams(
            "One arm took the drug; a slice of the other did too",
            subtitle="Bar length = share of that arm exposed to dexamethasone · 8% crossover dilutes, it does not erase, the contrast.",
        ),
    )

    fidelity_view = mo.vstack(
        [
            mo.md(
                """
                ## Intervention as specified, and as delivered
                _CONSORT items 13 & 24 — what was prescribed, what was actually taken, and how clean the contrast stayed._
                """
            ),
            mo.ui.altair_chart(fidelity_chart),
            mo.md(
                f"""Among patients with a completed follow-up form, **95%** of the dexamethasone arm received at least
                one dose ({dex['received']:,}/{dex['received_n']:,}), with a median treatment duration of
                **{dex['median_days']} days (IQR {dex['iqr_lo']}–{dex['iqr_hi']})**. In the usual-care arm,
                **{uc['crossover']} of {uc['crossover_n']:,} (8%)** received dexamethasone as part of routine clinical
                care — open-label pragmatism cuts both ways."""
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
        <div style="font-family:Georgia, serif; max-width:720px; margin:0 auto;">
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
                         f'{FLOW["dex_second_randomization"]} later re-randomised in another domain — still analysed here as assigned')}
                </div>
                <div style="display:grid; gap:6px;">
                    {box("Allocated: usual care alone", FLOW["usual_assigned"], colors["usual"])}
                    {arrow}
                    {_excl(FLOW["usual_withdrew"], "withdrew consent before follow-up")}
                    {arrow}
                    {box("Analysed for 28-day mortality", FLOW["usual_analyzed"], colors["usual"],
                         f'{FLOW["usual_second_randomization"]} later re-randomised in another domain — still analysed here as assigned')}
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
                _CONSORT item 22 — rebuilt from Figure 1's counts. The platform's funnel narrows to the one
                comparison this notebook reads._
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
            range=[colors[color_key], "#e7e2d8"],
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
                ## Primary outcome — death by day 28, in absolute terms
                _CONSORT item 26 asks for the **absolute** effect first. Each square is one patient per hundred;
                the two fewer shaded squares on the left are what a 6-milligram tablet bought across the whole cohort._
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
                **{overall['uc_events']:,}/{overall['uc_n']:,} ({uc_rate:.1f}%)** with usual care — an absolute reduction
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
                scale=alt.Scale(domain=["yes", "no"], range=[colors["muted"], colors["accent"]]),
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
        .mark_point(size=130, filled=True, color=colors["accent"])
        .encode(y=alt.Y("group:N", sort=sub_order), x="rr:Q")
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
                ## The signature figure — mortality by level of respiratory support at randomization
                _CONSORT items 26 & 28. Left: paired absolute risks per stratum. Right: age-adjusted rate ratios;
                gold marks mean the interval excludes 1, grey means it crosses 1._
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
                                    subtitle="Dot = arm's death rate · dotted line links the pair.",
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
                                    "Benefit where intervals sit left of 1",
                                    subtitle="Gold = CI excludes 1 · grey = CI includes 1 (uncertain).",
                                ),
                            )
                        ),
                    ),
                ],
                justify="center",
                gap=0.5,
            ),
            mo.md(
                f"""The gradient is the trial's mechanistic heart. Among patients already on **invasive mechanical
                ventilation**, mortality fell from **{EFFECTS[1]['uc_events']}/{EFFECTS[1]['uc_n']} ({100 * EFFECTS[1]['uc_events'] / EFFECTS[1]['uc_n']:.1f}%)**
                to **{EFFECTS[1]['dex_events']}/{EFFECTS[1]['dex_n']} ({100 * EFFECTS[1]['dex_events'] / EFFECTS[1]['dex_n']:.1f}%)** — rate ratio {EFFECTS[1]['rr']}
                (95% CI {EFFECTS[1]['lo']}–{EFFECTS[1]['hi']}), an age-adjusted **{ABS_REDUCTION[0][1]} percentage-point**
                reduction (95% CI {ABS_REDUCTION[0][2]}–{ABS_REDUCTION[0][3]}). With **oxygen only**, the fall was smaller:
                {EFFECTS[2]['dex_events']}/{EFFECTS[2]['dex_n']} ({100 * EFFECTS[2]['dex_events'] / EFFECTS[2]['dex_n']:.1f}%)
                vs {EFFECTS[2]['uc_events']}/{EFFECTS[2]['uc_n']} ({100 * EFFECTS[2]['uc_events'] / EFFECTS[2]['uc_n']:.1f}%) — RR {EFFECTS[2]['rr']}
                (95% CI {EFFECTS[2]['lo']}–{EFFECTS[2]['hi']}), a {ABS_REDUCTION[1][1]}-point reduction
                (95% CI {ABS_REDUCTION[1][2]}–{ABS_REDUCTION[1][3]}). But among patients needing **no respiratory
                support**, the point estimate flips: {EFFECTS[3]['dex_events']}/{EFFECTS[3]['dex_n']} ({100 * EFFECTS[3]['dex_events'] / EFFECTS[3]['dex_n']:.1f}%)
                vs {EFFECTS[3]['uc_events']}/{EFFECTS[3]['uc_n']} ({100 * EFFECTS[3]['uc_events'] / EFFECTS[3]['uc_n']:.1f}%) — RR {EFFECTS[3]['rr']},
                95% CI {EFFECTS[3]['lo']}–{EFFECTS[3]['hi']}. That interval **includes 1**: consistent with no effect,
                            and the paper notes results were compatible with possible harm here. The chi-square test for trend
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
            scale=alt.Scale(domain=["benefit", "uncertain"], range=[colors["dex"], colors["muted"]]),
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
        color=alt.Color("kind:N", scale=alt.Scale(domain=["benefit", "uncertain"], range=[colors["dex"], colors["muted"]]), legend=None),
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
                "Every mortality interval favours dexamethasone except the stratum that didn't need oxygen",
                subtitle="Clay = CI excludes 1 · grey = CI includes 1. Ratios are age-adjusted; <1 favours dexamethasone for every row shown.",
            ),
        )
    )

    forest_view = mo.vstack(
        [
            mo.md(
                """
                ## Effect estimates across outcomes
                _CONSORT item 26. Primary outcome and its respiratory-support subgroups, plus the Table 2
                secondary outcomes with usable intervals. Discharge &gt; 1 also favours dexamethasone (more
                patients home by day 28); the two grey rows keep the trial honest._
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
        "**Death was the primary outcome**, so the harm ledger is partly built into the endpoint itself: "
        "no signal of excess non-fatal harm emerged, and the drug shortened hospital stay. But this is a "
        "**preliminary report** written at pandemic speed, and its harm reporting is thin — there is no "
        "adverse-event table, no secondary-infection count, no hyperglycaemia tally despite dexamethasone's "
        "known metabolic effects. Later follow-up papers had to fill that space.\n\n"
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
                    border-radius:8px; padding:12px 16px; font-family:Georgia, serif; color:{colors['ink']};">
            <strong>Why it matters:</strong> dexamethasone reversed a decade of guideline pessimism about
            corticosteroids in viral pneumonia within a single day of announcement. The mechanism reads straight
            off the subgroup gradient: benefit concentrates exactly where Covid-19 is dominated by
            inflammatory lung injury (ventilation, oxygen), and disappears where early viral replication,
            which steroids can prolong, is the main event. The right drug for the right stage of the disease.
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
                <em>CONSORT 2025's open-science section (items 2–5) — where a 2020 pandemic trial scores better
                than most of its predecessors.</em>
            </p>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:12px;">
                <div style="background:#fff; border:1px solid #e1ddd4; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Registration (item 2)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">{TRIAL['registrations']}</div>
                </div>
                <div style="background:#fff; border:1px solid #e1ddd4; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Protocol &amp; SAP (item 3)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">NEJM.org + recoverytrial.net</div>
                </div>
                <div style="background:#fff; border:1px solid #e1ddd4; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Data sharing (item 4)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">Statement published with article</div>
                </div>
                <div style="background:#fff; border:1px solid #e1ddd4; border-radius:10px; padding:12px 14px;">
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
        <div style="font-family:Georgia, serif;">
            <table style="border-collapse:collapse; width:100%; font-family:Georgia, serif;">
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
        <div style="background:{colors['panel']}; border:1px solid #ddd8ce; border-radius:10px;
                    padding:14px 16px; font-family:Georgia, serif; color:{colors['ink']};">
            Of the <strong>{_top_level_items} top-level CONSORT 2025 items ({len(CHECKLIST)} checklist rows)</strong>,
            this 2020 report substantively covers <strong>{_covered} of {len(CHECKLIST)} rows</strong>. The one outright
            gap — <strong>patient &amp; public involvement (item 8)</strong> — is an expectation CONSORT added after the
            trial ran; the partials cluster where a preliminary report written in 100 days had to defer detail
            (adverse-event definitions and tables to later follow-up papers) or where openness was structural
            (an unmasked design has no blinding mechanics to describe). Reading this landmark against the new
            checklist is less an audit of the trial than a snapshot of how reporting norms moved.
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
        <div style="font-family:Georgia, serif; color:{colors['muted']}; font-size:0.86rem;
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
            here as a modern reading lens — it postdates this 2020 report. RECOVERY is a platform trial: this
            notebook reads only the dexamethasone-vs-usual-care comparison and visualises no other domain's arms.
        </div>
        """
    )
    provenance
    return


if __name__ == "__main__":
    app.run()
