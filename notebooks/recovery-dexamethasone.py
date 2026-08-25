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
                    the report substantively covers <strong>{covered} rows</strong>. The gap is
                    <strong>{gap_text}</strong>. Not-applicable rows are <strong>{na_text}</strong>.
                    The gap pattern reflects expectations that became standard after this 2020 report.
                    See <a href="#open-science">Open science</a> for registration and sharing items and
                    <a href="#methods">Methods</a> for patient and public involvement.
                </div>
            </div>
            """
        )

    return chapter_header, consort_items, coverage_summary, section_nav


@app.cell
def _(ARMS, EFFECTS, FLOW, FONT, TRIAL, card, colors, mo):
    # ---------------------------- HERO ----------------------------
    import math

    _dex = ARMS[0]
    _usual = ARMS[1]
    _primary = EFFECTS[0]
    _dex_rate = 100 * _dex["deaths"] / _dex["n"]
    _usual_rate = 100 * _usual["deaths"] / _usual["n"]
    _absolute_reduction = _usual_rate - _dex_rate
    # NNT is conventionally rounded up: a fractional patient cannot be saved.
    _nnt = math.ceil(1 / (_absolute_reduction / 100))

    hero = mo.Html(
        f"""
        <div style="background:{colors['panel']}; border:1px solid #D8D4D7; border-radius:14px;
                    padding:18px 20px; font-family:{FONT}; color:{colors['ink']};">
            <div style="text-transform:uppercase; letter-spacing:0.15em; font-size:0.72rem;
                        color:{colors['muted']}; margin-bottom:0.5rem;">
                A randomised trial, read through CONSORT 2025 · dexamethasone versus usual care within the RECOVERY platform
            </div>
            <div style="font-size:1.82rem; line-height:1.12; margin-bottom:0.25rem;">{TRIAL['name']}</div>
            <div style="font-size:1.0rem; color:#343741; margin-bottom:0.35rem;">{TRIAL['title']}</div>
            <div style="max-width:820px; font-size:0.96rem; line-height:1.42; color:#343741; margin-bottom:0.85rem;">
                Dexamethasone reduced 28-day mortality in hospitalised patients who needed oxygen or invasive
                ventilation. The trial did not show benefit in patients who needed no respiratory support.
                This notebook covers only the dexamethasone-versus-usual-care comparison within the RECOVERY
                platform trial.
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
                {card("Randomised population", f"{FLOW['randomized']:,}", f"{TRIAL['centers']} NHS organisations · {TRIAL['recruitment']}", colors["ink"])}
                {card("Intervention: dexamethasone", f"{_dex_rate:.1f}%", f"{_dex['deaths']:,} of {_dex['n']:,} died by 28 days", colors["dex"])}
                {card("Reference: usual care", f"{_usual_rate:.1f}%", f"{_usual['deaths']:,} of {_usual['n']:,} died by 28 days", colors["usual"])}
                {card("Main contrast", f"−{_absolute_reduction:.1f} pts", f"NNT {_nnt} · age-adjusted RR {_primary['rr']} ({_primary['lo']}–{_primary['hi']})", colors["good"])}
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
                "Can a reader identify the study as randomised and understand its design, participants, intervention, comparator, and main result?",
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
                {card("Registration · item 2", TRIAL["registrations"], _notes["2"], colors["good"])}
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
    introduction_text = mo.md(
        f"**Rationale.** {_rationale}.\n\n"
        f"**Clinical question.** {_objective}. The relevant benefit is survival, and the relevant harm assessment "
        "must include adverse events in addition to the primary mortality outcome."
    )
    introduction_view = mo.vstack(
        [
            chapter_header(
                "Introduction",
                "Why was the trial needed, and which benefit and harm question did the investigators test?",
            ),
            consort_items(["6", "7"], "Rationale and objectives"),
            introduction_text,
        ],
        gap=0.4,
    )
    introduction_view
    return


@app.cell
def _(CONTEXT, TRIAL, chapter_header, consort_items, mo):
    # ----------------------------- METHODS -----------------------------
    design = mo.md(
        "### Trial design in one paragraph\n\n"
        f"**RECOVERY** was a multicentre, controlled, **open-label platform randomised trial** across "
        f"{TRIAL['centers']} NHS organisations in {TRIAL['geography']}. The platform evaluated several Covid-19 "
        "treatments at the same time; this notebook covers only the dexamethasone domain. Eligible patients were "
        "hospitalised with suspected or laboratory-confirmed SARS-CoV-2 infection and had no clinician-judged "
        "substantial risk from participation. A concealed web-based system allocated patients "
        f"{CONTEXT['allocation_ratio']}. The intervention was {CONTEXT['dose']}; the comparator was usual care alone. "
        "There was no placebo or masking, but death was an objective endpoint. The primary analysis was "
        "intention-to-treat and used age-adjusted Cox regression because the dexamethasone group was older on "
        f"average. Recruitment ran {TRIAL['recruitment']} and stopped after enrolment exceeded the target."
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
def _(ARMS, CHART_W, FONT, colors, consort_items, mo):
    # ------------------- INTERVENTION DELIVERY -------------------
    _dex, _usual = ARMS[0], ARMS[1]
    _fidelity_rows = [
        {
            "arm": _dex["arm"],
            "kind": "Received ≥1 dose",
            "pct": 100 * _dex["received"] / _dex["received_n"],
            "label": f'{_dex["received"]:,} of {_dex["received_n"]:,} with completed follow-up form',
            "color": colors["dex"],
        },
        {
            "arm": _usual["arm"],
            "kind": "Received dexamethasone anyway",
            "pct": 100 * _usual["crossover"] / _usual["crossover_n"],
            "label": f'{_usual["crossover"]:,} of {_usual["crossover_n"]:,}; crossover reduced between-arm separation',
            "color": colors["usual"],
        },
    ]
    _rows = []
    for row in _fidelity_rows:
        _rows.append(
            f"""
            <div style="display:grid; grid-template-columns:220px minmax(180px,1fr) 52px; gap:10px; align-items:center;">
                <div style="font-size:0.78rem; color:{colors['ink']};">{row['arm']}: {row['kind']}</div>
                <div style="height:18px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                    <div style="width:{row['pct']}%; height:100%; background:{row['color']}; border-radius:3px;"></div>
                </div>
                <div style="font-size:0.8rem; font-weight:700; color:{row['color']}; text-align:right;">{row['pct']:.1f}%</div>
            </div>
            <div style="font-size:0.76rem; color:{colors['muted']}; margin:-5px 0 2px 230px;">{row['label']}</div>
            """
        )

    fidelity_panel = mo.Html(
        f"""
        <div role="img" aria-label="Dexamethasone exposure by randomised arm" style="font-family:{FONT}; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">Assigned treatment produced different dexamethasone exposure</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 12px;">Orange and blue identify the randomised arms. Each row shows exposure to dexamethasone.</div>
            <div style="display:grid; gap:9px;">{''.join(_rows)}</div>
        </div>
        """
    )
    _received_pct = 100 * _dex["received"] / _dex["received_n"]
    _crossover_pct = 100 * _usual["crossover"] / _usual["crossover_n"]
    fidelity_view = mo.vstack(
        [
            consort_items(["24a", "24b"], "Intervention delivery and concomitant care"),
            mo.md("### Intervention delivery\n_The figure compares assigned treatment with treatment received._"),
            fidelity_panel,
            mo.md(
                f"The dexamethasone arm received at least one dose in **{_received_pct:.1f}%** of participants with a "
                f"completed follow-up form ({_dex['received']:,}/{_dex['received_n']:,}); treatment lasted a median "
                f"of **{_dex['median_days']} days (IQR {_dex['iqr_lo']}–{_dex['iqr_hi']})**. In the usual-care arm, "
                f"**{_crossover_pct:.1f}%** received dexamethasone as part of routine care "
                f"({_usual['crossover']:,}/{_usual['crossover_n']:,}). This crossover reduced separation between the "
                "randomised groups."
            ),
        ],
        gap=0.4,
    )
    fidelity_view
    return


@app.cell
def _(FLOW, box, colors, consort_items, mo):
    # ----------------------- CONSORT FLOW DIAGRAM -----------------------
    arrow = f'<div style="text-align:center; color:{colors["muted"]}; font-size:1.1rem; line-height:1;">↓</div>'

    def _excl(n, label):
        return (
            f'<div style="border-left:2px dashed {colors["grid"]}; padding-left:12px;">'
            f'{box("Excluded", n, colors["muted"], label)}</div>'
        )

    _platform_to_domain = FLOW["recruited_platform"] - FLOW["excluded_comparison"]
    _domain_to_comparison = FLOW["randomized_dex_or_other"] - FLOW["other_active_treatment"]
    flow_html = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; max-width:720px; margin:0 auto;">
            {box("Recruited into the RECOVERY platform", FLOW["recruited_platform"], colors["dark"], "hospitalised Covid-19, all treatment domains")}
            <div style="display:grid; grid-template-columns:1fr 1fr; align-items:center; gap:8px; margin:2px 0;">
                <div style="text-align:center; color:{colors['muted']}; font-size:1.1rem;">↓</div>
                {_excl(FLOW["excluded_comparison"], f'could not enter the dexamethasone comparison ({FLOW["excluded_no_drug"]} drug unavailable · {FLOW["excluded_unsuitable"]} clinically unsuitable)')}
            </div>
            {box("Entered the dexamethasone domain", _platform_to_domain, colors["dark"], "platform cohort after comparison exclusions")}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; align-items:center; gap:8px; margin:2px 0;">
                <div style="text-align:center; color:{colors['muted']}; font-size:1.1rem;">↓</div>
                {box("Randomised to dexamethasone or another active treatment", FLOW["randomized_dex_or_other"], colors["dark"])}
            </div>
            {_excl(FLOW["other_active_treatment"], "allocated outside this notebook's dexamethasone-versus-usual-care comparison")}
            {arrow}
            {box("This comparison: randomised dexamethasone vs usual care", _domain_to_comparison, colors["accent"])}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div style="display:grid; gap:6px;">
                    {box("Allocated: dexamethasone", FLOW["dex_assigned"], colors["dex"], f'{FLOW["dex_withdrew"]} withdrew; all randomised participants retained in intention-to-treat analysis')}
                    {arrow}
                    {box("Analysed for 28-day mortality", FLOW["dex_analyzed"], colors["dex"], f'{FLOW["dex_second_randomization"]} later re-randomised in another domain; analysed here as assigned')}
                </div>
                <div style="display:grid; gap:6px;">
                    {box("Allocated: usual care alone", FLOW["usual_assigned"], colors["usual"], f'{FLOW["usual_withdrew"]} withdrew; all randomised participants retained in intention-to-treat analysis')}
                    {arrow}
                    {box("Analysed for 28-day mortality", FLOW["usual_analyzed"], colors["usual"], f'{FLOW["usual_second_randomization"]} later re-randomised in another domain; analysed here as assigned')}
                </div>
            </div>
        </div>
        """
    )

    flow_view = mo.vstack(
        [
            consort_items(["22a", "22b", "23a", "23b"], "Participant flow and recruitment"),
            mo.md(
                "### Participant flow\n_The diagram reconstructs the dexamethasone comparison from Figure 1. "
                "The platform stages remain visible so the scope of this comparison is clear._"
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
    import re as _re_baseline

    _profile_rows = []
    for _label, _dex_value, _usual_value in BASELINE:
        if (
            _label.startswith(("Respiratory support:", "Laboratory-confirmed"))
            or "coexisting illness" in _label
        ):
            _dex_match = _re_baseline.search(r"(\d+)%", _dex_value)
            _usual_match = _re_baseline.search(r"(\d+)%", _usual_value)
            if _dex_match and _usual_match:
                _profile_rows.append(
                    {
                        "label": _label.replace("Respiratory support: ", ""),
                        "dex_pct": int(_dex_match.group(1)),
                        "usual_pct": int(_usual_match.group(1)),
                        "dex_raw": _dex_value,
                        "usual_raw": _usual_value,
                    }
                )

    _bars = []
    for _row in _profile_rows:
        _bars.append(
            f"""
            <div style="display:grid; grid-template-columns:230px minmax(150px,1fr) 48px; gap:9px; align-items:center; margin:7px 0;">
                <div style="font-size:0.78rem; color:{colors['ink']};">{_row['label']} · {ARMS[0]['arm']}</div>
                <div style="height:15px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                    <div style="width:{_row['dex_pct']}%; height:100%; background:{colors['dex']}; border-radius:3px;"></div>
                </div>
                <div style="font-size:0.78rem; font-weight:700; color:{colors['dex']}; text-align:right;">{_row['dex_pct']}%</div>
            </div>
            <div style="display:grid; grid-template-columns:230px minmax(150px,1fr) 48px; gap:9px; align-items:center; margin:7px 0 12px;">
                <div style="font-size:0.78rem; color:{colors['ink']};">{_row['label']} · {ARMS[1]['arm']}</div>
                <div style="height:15px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                    <div style="width:{_row['usual_pct']}%; height:100%; background:{colors['usual']}; border-radius:3px;"></div>
                </div>
                <div style="font-size:0.78rem; font-weight:700; color:{colors['usual']}; text-align:right;">{_row['usual_pct']}%</div>
            </div>
            """
        )
    _profile_panel = mo.Html(
        f"""
        <div role="img" aria-label="Baseline respiratory support and illness profile by randomised arm" style="font-family:{FONT}; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">Respiratory support and major illness were common at entry</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 12px;">Each bar is the percentage printed for that arm in Table 1. Orange and blue retain the randomised-arm mapping.</div>
            {''.join(_bars)}
        </div>
        """
    )
    _rows = "\n".join(f"| {label} | {value_dex} | {value_usual} |" for label, value_dex, value_usual in BASELINE)
    _baseline_table = mo.md(
        "| Characteristic | " + ARMS[0]["arm"] + " | " + ARMS[1]["arm"] + " |\n"
        "|:---|:---|:---|\n"
        f"{_rows}"
    )
    baseline_view = mo.vstack(
        [
            consort_items(["25"], "Baseline data"),
            mo.md(
                f"### Baseline profile\nThe comparison included **{FLOW['randomized']:,} randomised participants**. "
                "The groups were balanced on most reported characteristics, with the paper noting an age difference."
            ),
            _profile_panel,
            mo.accordion({"Full reported baseline summary": _baseline_table}),
        ],
        gap=0.5,
    )
    baseline_view
    return


@app.cell
def _(ARMS, CHART_W, EFFECTS, alt, colors, consort_items, mo, pl, style):
    # ---------- PRIMARY OUTCOME: absolute-risk icon arrays ----------
    # The overall comparison has clean fixed denominators (482/2104 vs
    # 1110/4321), so a 10x10 waffle per arm is appropriate.
    import math as _math

    _overall = EFFECTS[0]
    _arm_names = [arm["arm"] for arm in ARMS]
    _arm_specs = [
        (_arm_names[0], _overall["dex_events"], _overall["dex_n"], "dex"),
        (_arm_names[1], _overall["uc_events"], _overall["uc_n"], "usual"),
    ]

    def _waffle_chart(arm_name, events, denom, color_key):
        rate_pct = 100 * events / denom
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

    _dex_rate = 100 * _overall["dex_events"] / _overall["dex_n"]
    _usual_rate = 100 * _overall["uc_events"] / _overall["uc_n"]
    _absolute_reduction = _usual_rate - _dex_rate
    _nnt = _math.ceil(1 / (_absolute_reduction / 100))

    waffle_view = mo.vstack(
        [
            consort_items(["26"], "Numbers analysed, outcomes, and estimation"),
            mo.md(
                "### Primary outcome: 28-day mortality\n"
                "**Read it as:** Each square represents one patient per 100. Filled squares represent death.\n\n"
                "**Why this geometry:** The paper reports a fixed-denominator overall mortality comparison, so a "
                "10×10 array gives an absolute-risk view without replacing the reported rate ratio."
            ),
            mo.hstack(
                [mo.ui.altair_chart(_waffle_chart(*spec)) for spec in _arm_specs],
                justify="center",
                gap=0.6,
            ),
            mo.md(
                f"**What it says:** **{_overall['dex_events']:,}/{_overall['dex_n']:,} ({_dex_rate:.1f}%)** died with "
                f"dexamethasone versus **{_overall['uc_events']:,}/{_overall['uc_n']:,} ({_usual_rate:.1f}%)** with usual care. "
                f"The absolute reduction was **{_absolute_reduction:.1f} percentage points**, or about one fewer death "
                f"per **{_nnt} treated** from the crude counts. The age-adjusted rate ratio was **{_overall['rr']} "
                f"(95% CI {_overall['lo']}–{_overall['hi']}; P&lt;0.001)**."
            ),
        ],
        gap=0.4,
    )
    waffle_view
    return


@app.cell
def _(ABS_REDUCTION, CHART_W, CONTEXT, EFFECTS, alt, colors, mo, pl, style):
    # -------- SIGNATURE FIGURE: respiratory-support subgroups --------
    # The paired view keeps absolute mortality next to the age-adjusted rate
    # ratio. It shows where the observed benefit was concentrated.
    subgroups = EFFECTS[1:]
    sub_order = [s["group"] for s in subgroups]

    def _risk_rows(subgroup):
        out = []
        for arm_key, event_key, n_key in (("Dexamethasone", "dex_events", "dex_n"), ("Usual care", "uc_events", "uc_n")):
            events = subgroup[event_key]
            denom = subgroup[n_key]
            out.append(
                {
                    "group": subgroup["group"],
                    "arm": arm_key,
                    "pct": 100 * events / denom,
                    "events": f"{events:,}/{denom:,}",
                }
            )
        return out

    risk_df = pl.DataFrame([row for subgroup in subgroups for row in _risk_rows(subgroup)])
    rr_df = pl.DataFrame(subgroups).with_columns(
        pl.when((pl.col("lo") <= 1.0) & (pl.col("hi") >= 1.0))
        .then(pl.lit("yes"))
        .otherwise(pl.lit("no"))
        .alias("crosses_null")
    )
    arm_names = ["Dexamethasone", "Usual care"]
    arm_scale = alt.Scale(domain=arm_names, range=[colors["dex"], colors["usual"]])

    _risk_pts = alt.Chart(risk_df).mark_point(size=120, filled=True).encode(
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
    _rr_rule = alt.Chart(rr_df).mark_rule(strokeWidth=2).encode(
        y=alt.Y("group:N", sort=sub_order, title=None),
        x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=[0.4, 1.8]), title="Rate ratio (log scale)"),
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
    _rr_pt = alt.Chart(rr_df).mark_point(size=130, filled=True).encode(
        y=alt.Y("group:N", sort=sub_order),
        x="rr:Q",
        color=alt.Color(
            "crosses_null:N",
            scale=alt.Scale(domain=["yes", "no"], range=[colors["muted"], colors["good"]]),
            legend=None,
        ),
    )
    _null = alt.Chart(pl.DataFrame({"x": [1.0]})).mark_rule(
        strokeDash=[5, 4], color=colors["ink"]
    ).encode(x="x:Q")

    _risk_chart = style(
        _risk_pts.properties(
            width=CHART_W,
            height=190,
            title=alt.TitleParams(
                "Absolute mortality by support",
                subtitle="Dots show the death rate in each randomised arm.",
            ),
        )
    )
    _rr_chart = style(
        (_null + _rr_rule + _rr_pt).properties(
            width=CHART_W,
            height=190,
            title=alt.TitleParams(
                "Rate ratios by support",
                subtitle="Green intervals exclude 1; grey intervals include 1.",
            ),
        )
    )

    _vent = subgroups[0]
    _oxygen = subgroups[1]
    _none = subgroups[2]
    subgroup_view = mo.vstack(
        [
            mo.md(
                "### Mortality by respiratory support at randomisation\n"
                "**Read it as:** The left panel shows absolute mortality within each randomised group. The right "
                "panel shows age-adjusted rate ratios and 95% confidence intervals.\n\n"
                "**Why this geometry:** The subgroup denominators are fixed within each stratum, while the relative "
                "effect is reported as an adjusted rate ratio. The paired panels preserve both views."
            ),
            mo.vstack(
                [
                    mo.ui.altair_chart(_risk_chart),
                    mo.ui.altair_chart(_rr_chart),
                ],
                gap=0.3,
            ),
            mo.md(
                f"**What it says:** Among patients on **{_vent['group'].lower()}**, mortality was "
                f"**{_vent['dex_events']}/{_vent['dex_n']} ({100 * _vent['dex_events'] / _vent['dex_n']:.1f}%)** with "
                f"dexamethasone versus **{_vent['uc_events']}/{_vent['uc_n']} ({100 * _vent['uc_events'] / _vent['uc_n']:.1f}%)** "
                f"with usual care. The rate ratio was **{_vent['rr']} (95% CI {_vent['lo']}–{_vent['hi']})**, with an "
                f"age-adjusted absolute reduction of **{ABS_REDUCTION[0][1]} points** ({ABS_REDUCTION[0][2]}–{ABS_REDUCTION[0][3]}). "
                f"The corresponding reduction among patients receiving **{_oxygen['group'].lower()}** was "
                f"**{ABS_REDUCTION[1][1]} points** ({ABS_REDUCTION[1][2]}–{ABS_REDUCTION[1][3]}). Among patients needing "
                f"**{_none['group'].lower()}**, the rate ratio was **{_none['rr']} (95% CI {_none['lo']}–{_none['hi']})**, "
                f"so the interval included no clear difference. The test for trend was **{CONTEXT['trend_chi2']}**."
            ),
        ],
        gap=0.45,
    )
    subgroup_view
    return


@app.cell
def _(CHART_W, EFFECTS, SECONDARY, alt, colors, mo, pl, style):
    # --------------- EFFECT ESTIMATES: forest plot (log rate ratio) ---------------
    import re as _re_forest

    forest_rows = [
        {
            "outcome": "28-day mortality — all patients (primary)",
            "ratio": EFFECTS[0]["rr"],
            "lo": EFFECTS[0]["lo"],
            "hi": EFFECTS[0]["hi"],
            "kind": "benefit",
            "source": "Age-adjusted Cox rate ratio",
        }
    ]
    forest_rows.extend(
        {
            "outcome": f"Mortality — {effect['group'].lower()}",
            "ratio": effect["rr"],
            "lo": effect["lo"],
            "hi": effect["hi"],
            "kind": "benefit" if effect["hi"] < 1 else "uncertain",
            "source": "Age-adjusted Cox rate ratio",
        }
        for effect in EFFECTS[1:]
    )
    for _secondary_forest in SECONDARY:
        _match = _re_forest.search(r"([0-9.]+)\s*\(([0-9.]+)[–-]([0-9.]+)\)", _secondary_forest["ratio"])
        if _match:
            _ratio, _lo, _hi = (float(value) for value in _match.groups())
            forest_rows.append(
                {
                    "outcome": _secondary_forest["outcome"],
                    "ratio": _ratio,
                    "lo": _lo,
                    "hi": _hi,
                    "kind": "benefit" if "favours" in _secondary_forest["reading"] else "uncertain",
                    "source": _secondary_forest["ratio"],
                }
            )

    ef = pl.DataFrame(forest_rows)
    order = [row["outcome"] for row in forest_rows]
    _lo_all = min(row["lo"] for row in forest_rows)
    _hi_all = max(row["hi"] for row in forest_rows)
    _x_domain = [max(0.35, _lo_all * 0.8), _hi_all * 1.2]
    kind_scale = alt.Scale(
        domain=["benefit", "uncertain"],
        range=[colors["good"], colors["muted"]],
    )

    _rule = alt.Chart(ef).mark_rule(strokeWidth=2).encode(
        y=alt.Y("outcome:N", sort=order, title=None),
        x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=_x_domain), title="Rate ratio (log scale) — dexamethasone vs usual care"),
        x2="hi:Q",
        color=alt.Color("kind:N", scale=kind_scale, legend=None),
        tooltip=[
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("ratio:Q", title="Ratio", format=".2f"),
            alt.Tooltip("lo:Q", title="95% CI low", format=".2f"),
            alt.Tooltip("hi:Q", title="95% CI high", format=".2f"),
            alt.Tooltip("source:N", title="Reported estimate"),
        ],
    )
    _pt = alt.Chart(ef).mark_point(size=110, filled=True).encode(
        y=alt.Y("outcome:N", sort=order),
        x="ratio:Q",
        color=alt.Color("kind:N", scale=kind_scale, legend=alt.Legend(title="Interpretation")),
        tooltip=[
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("ratio:Q", title="Ratio", format=".2f"),
            alt.Tooltip("lo:Q", title="95% CI low", format=".2f"),
            alt.Tooltip("hi:Q", title="95% CI high", format=".2f"),
        ],
    )
    _null = alt.Chart(pl.DataFrame({"x": [1.0]})).mark_rule(
        strokeDash=[5, 4], color=colors["muted"]
    ).encode(x="x:Q")
    forest = style(
        (_null + _rule + _pt).properties(
            width=CHART_W,
            height=300,
            title=alt.TitleParams(
                "Dexamethasone benefit was concentrated in supported patients",
                subtitle="Points show rate or risk ratios; rules show 95% CIs. The dashed line marks a ratio of 1.",
            ),
        )
    )
    forest_view = mo.vstack(
        [
            mo.md(
                "### Relative effect estimates\n"
                "The forest plot carries the adjusted primary and subgroup estimates, followed by secondary outcomes "
                "with published ratios and confidence intervals."
            ),
            mo.ui.altair_chart(forest),
        ],
        gap=0.4,
    )
    forest_view
    return


@app.cell
def _(ARMS, CHART_W, FONT, SECONDARY, colors, consort_items, mo):
    # ------------------------- HARMS + SECONDARY -------------------------
    import re as _re_harms

    _arm_specs = [
        (ARMS[0]["arm"], colors["dex"]),
        (ARMS[1]["arm"], colors["usual"]),
    ]
    _outcome_blocks = []
    for _secondary_harms in SECONDARY:
        _bars = []
        for arm_name, color, value in (
            (_arm_specs[0][0], _arm_specs[0][1], _secondary_harms["dex"]),
            (_arm_specs[1][0], _arm_specs[1][1], _secondary_harms["usual"]),
        ):
            _match = _re_harms.match(r"([\d,]+)/([\d,]+)\s*\(([\d.]+)%\)", value)
            if not _match:
                continue
            _events, _denom, _pct = _match.groups()
            _bars.append(
                f"""
                <div style="display:grid; grid-template-columns:190px minmax(150px,1fr) 130px; gap:9px; align-items:center; margin:6px 0;">
                    <div style="font-size:0.77rem; color:{colors['ink']};">{arm_name}</div>
                    <div style="height:15px; background:{colors['neutral_bg']}; border-radius:3px; overflow:hidden;">
                        <div style="width:{_pct}%; height:100%; background:{color}; border-radius:3px;"></div>
                    </div>
                    <div style="font-size:0.76rem; color:{color}; text-align:right;">{_events}/{_denom} ({_pct}%)</div>
                </div>
                """
            )
        _outcome_blocks.append(
            f"""
            <div style="padding:8px 0 10px; border-top:1px solid {colors['grid']};">
                <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;">
                    <strong style="font-size:0.82rem; color:{colors['dark']};">{_secondary_harms['outcome']}</strong>
                    <span style="font-size:0.76rem; color:{colors['muted']};">{_secondary_harms['ratio']}</span>
                </div>
                {''.join(_bars)}
            </div>
            """
        )
    secondary_panel = mo.Html(
        f"""
        <div role="img" aria-label="Secondary outcomes by randomised arm" style="font-family:{FONT}; width:min(100%, {CHART_W}px); border:1px solid {colors['grid']}; border-radius:10px; background:{colors['paper']}; padding:14px 16px; box-sizing:border-box;">
            <div style="font-size:0.95rem; font-weight:700; color:{colors['dark']};">Secondary outcomes were reported with counts and ratios</div>
            <div style="font-size:0.78rem; color:{colors['muted']}; margin:2px 0 8px;">Bar length is the printed percentage. The ratio at right is the paper's adjusted estimate.</div>
            {''.join(_outcome_blocks)}
        </div>
        """
    )
    harms_view = mo.vstack(
        [
            consort_items(["27", "28"], "Harms and ancillary analyses"),
            mo.md("### Harms and secondary outcomes"),
            secondary_panel,
            mo.md(
                "The preliminary report did not include a standalone adverse-event table, so non-fatal harms cannot "
                "be compared here beyond the information it states. Mortality was the primary safety-relevant "
                "endpoint. The secondary outcomes show benefit for discharge and progression to ventilation, while "
                "the intervals for ventilation or death and death alone include no difference. The main limitation "
                "is that this is a platform comparison with open-label treatment and crossover in usual care."
            ),
        ],
        gap=0.65,
    )
    harms_view
    return


@app.cell
def _(CHECKLIST, chapter_header, consort_items, mo):
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
                f"### Interpretation\n\n{_interpretation}. The result supports dexamethasone for hospitalised "
                "patients who need oxygen or invasive ventilation, but it does not support routine use for patients "
                "without a need for respiratory support.\n\n"
                f"### Limits\n\n{_limitations}. The open-label platform design, treatment crossover, preliminary safety reporting, and "
                "selected hospital population limit how directly this comparison can be applied to other settings."
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
def _(ARMS, TRIAL, colors, mo):
    # ------------------------- PROVENANCE -------------------------
    _dex_rate = 100 * ARMS[0]["deaths"] / ARMS[0]["n"]
    _usual_rate = 100 * ARMS[1]["deaths"] / ARMS[1]["n"]
    _dex_squares = round(_dex_rate)
    _usual_squares = round(_usual_rate)
    provenance = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['muted']}; font-size:0.86rem;
                    border-top:1px solid {colors['grid']}; padding-top:12px; line-height:1.5;">
            <strong style="color:{colors['ink']};">Source & provenance.</strong>
            {TRIAL['citation']} DOI <a href="https://doi.org/{TRIAL['doi']}" style="color:{colors['usual']};">{TRIAL['doi']}</a>.
            Registered as {TRIAL['registrations']}. Checklist: Hopewell S, et al. CONSORT 2025 Statement.
            <em>BMJ</em> 2025;388:e081123. The full text was retrieved and extracted to
            <code>papers/recovery-text.txt</code>. The data cell near the top of this notebook records the platform
            scope, flow counts, arm counts, effect estimates, baseline values, and secondary outcomes. Every figure
            is rendered from those literals. The paper prints counts and denominators for the displayed rates, so no
            denominator was reconstructed. The waffle arrays round the computed mortality rates ({_dex_rate:.1f}% and
            {_usual_rate:.1f}%) to {_dex_squares} and {_usual_squares} event squares per 100; the captions retain the
            exact counts and rates. The crude absolute difference is shown beside the age-adjusted rate ratio from
            the paper. This audit applies CONSORT 2025 retrospectively; the checklist postdates this 2020 report.
            RECOVERY is a platform trial: this notebook reads only the dexamethasone-versus-usual-care comparison and
            does not visualise other domains' arms.
        </div>
        """
    )
    provenance
    return


if __name__ == "__main__":
    app.run()
