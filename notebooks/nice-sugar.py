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
        "intensive": "#FA4616",   # intervention arm -> UF orange
        "conventional": "#0021A5",  # reference arm -> UF blue
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
    # The NICE-SUGAR Study Investigators. Intensive versus Conventional
    # Glucose Control in Critically Ill Patients.
    # N Engl J Med 2009;360:1283-1297.  DOI 10.1056/NEJMoa0810625
    # Every figure below is rendered from these literals. Where the paper
    # reported only percentages, denominators were reconstructed so the
    # arithmetic reproduces the published rates (noted in the provenance).
    # =====================================================================

    TRIAL = {
        "name": "NICE-SUGAR",
        "title": "Intensive versus Conventional Glucose Control in Critically Ill Patients",
        "citation": "The NICE-SUGAR Study Investigators. N Engl J Med 2009;360:1283-1297.",
        "doi": "10.1056/NEJMoa0810625",
        "registration": "NCT00220987",
        "recruitment": "Dec 2004 – Nov 2008",
        "centers": 42,
        "geography": "38 academic + 4 community ICUs, Australia / New Zealand & North America",
    }

    # Participant flow (item 22). Analysed denominators reconstructed to match
    # published rates: 829/3010 = 27.5%, 751/3012 = 24.9%.
    FLOW = {
        "screened": 40171,
        "randomized": 6104,
        "int_assigned": 3054,
        "conv_assigned": 3050,
        "int_analyzed": 3010,
        "conv_analyzed": 3012,
    }
    FLOW["excluded_before"] = FLOW["screened"] - FLOW["randomized"]
    FLOW["int_excluded"] = FLOW["int_assigned"] - FLOW["int_analyzed"]
    FLOW["conv_excluded"] = FLOW["conv_assigned"] - FLOW["conv_analyzed"]

    # Arms: glucose targets (mg/dL), time-weighted achieved mean, insulin use,
    # primary-outcome deaths, and severe hypoglycaemia (<=40 mg/dL).
    ARMS = [
        {
            "arm": "Intensive",
            "target_lo": 81, "target_hi": 108, "achieved": 115,
            "insulin_pct": 97.2,
            "deaths": 829, "n": 3010,
            "hypo": 206, "hypo_n": 3016, "hypo_pct": 6.8,
        },
        {
            "arm": "Conventional",
            "target_lo": 144, "target_hi": 180, "achieved": 144,
            "insulin_pct": 69.0,
            "deaths": 751, "n": 3012,
            "hypo": 15, "hypo_n": 3014, "hypo_pct": 0.5,
        },
    ]

    # Effect estimates with 95% CI (odds ratios).
    EFFECTS = [
        {"outcome": "90-day mortality (primary)", "or": 1.14, "lo": 1.02, "hi": 1.28, "kind": "harm"},
        {"outcome": "90-day mortality (adjusted)", "or": 1.14, "lo": 1.01, "hi": 1.29, "kind": "harm"},
        {"outcome": "Severe hypoglycaemia (≤40 mg/dL)", "or": 14.7, "lo": 9.0, "hi": 25.9, "kind": "harm"},
    ]

    # Baseline (item 25) — overall cohort; the paper reported groups were balanced.
    BASELINE = [
        ("Age — mean", "60 years"),
        ("Female sex", "37%"),
        ("Body-mass index — mean", "28 kg/m²"),
        ("Diabetes", "20%"),
        ("Mechanical ventilation", "94%"),
        ("Renal-replacement therapy", "6%"),
        ("Severe sepsis", "22%"),
        ("Trauma admission", "14%"),
        ("APACHE II — mean", "21"),
        ("APACHE II ≥ 25", "31%"),
    ]

    # Secondary outcomes (item 26) — reported without a significant difference.
    SECONDARY = [
        "28-day mortality",
        "ICU length of stay",
        "hospital length of stay",
        "days of mechanical ventilation",
        "days of renal-replacement therapy",
        "new single/multi-organ failure",
    ]
    return ARMS, BASELINE, EFFECTS, FLOW, SECONDARY, TRIAL

@app.cell
def _():
    # ------------------------------------------------------------------
    # CONSORT 2025 checklist (Hopewell S, et al. BMJ 2025;388:e081123),
    # each item paired with how NICE-SUGAR (2009) reports it.
    # status: reported | partial | na | gap
    # group is the visible top-level CONSORT chapter used by the inline reader.
    # ------------------------------------------------------------------
    CHECKLIST = [
        ("Title and abstract", "1a", "Identification as a randomised trial", "reported", "“Randomised” stated in title & abstract"),
        ("Title and abstract", "1b", "Structured summary", "reported", "NEJM structured abstract"),
        ("Open science", "2", "Trial registration", "reported", "ClinicalTrials.gov NCT00220987"),
        ("Open science", "3", "Protocol & statistical analysis plan", "reported", "SAP published (Crit Care Resusc 2009)"),
        ("Open science", "4", "Data sharing (de-identified IPD, code)", "gap", "Predates routine IPD sharing (2009)"),
        ("Open science", "5a", "Funding & role of funders", "reported", "NHMRC & others; funders had no role"),
        ("Open science", "5b", "Conflicts of interest", "reported", "Author disclosures published"),
        ("Introduction", "6", "Background & rationale", "reported", "Earlier single-centre trials suggested benefit"),
        ("Introduction", "7", "Objectives (benefits & harms)", "reported", "Effect of intensive control on 90-day death"),
        ("Methods", "8", "Patient & public involvement", "gap", "Not reported — item new in 2025"),
        ("Methods", "9", "Trial design", "reported", "Parallel-group, 1:1, superiority"),
        ("Methods", "10", "Changes to trial protocol", "reported", "No major changes reported"),
        ("Methods", "11", "Trial setting", "reported", "42 ICUs across ANZ & North America"),
        ("Methods", "12a", "Eligibility — participants", "reported", "Expected ≥3 ICU days + arterial line"),
        ("Methods", "12b", "Eligibility — sites / deliverers", "na", "No special deliverer criteria"),
        ("Methods", "13", "Intervention & comparator", "reported", "81–108 vs ≤180 mg/dL via IV insulin"),
        ("Methods", "14", "Outcomes", "reported", "Primary 90-day mortality + secondaries"),
        ("Methods", "15", "Harms — definition & assessment", "reported", "Severe hypoglycaemia ≤40 mg/dL"),
        ("Methods", "16a", "Sample size", "reported", "Powered for an absolute mortality difference"),
        ("Methods", "16b", "Interim analyses & stopping", "reported", "Independent DSMB interim looks"),
        ("Methods", "17a", "Sequence generation", "reported", "Central computer-generated sequence"),
        ("Methods", "17b", "Randomisation type / restriction", "reported", "Minimisation: region & admission type"),
        ("Methods", "18", "Allocation concealment", "reported", "Central web-based allocation"),
        ("Methods", "19", "Implementation", "reported", "Central randomisation service"),
        ("Methods", "20a", "Blinding — who", "partial", "Open-label; death is an objective outcome"),
        ("Methods", "20b", "Blinding — how", "na", "Not applicable (open-label)"),
        ("Methods", "21a", "Statistical methods", "reported", "χ² / logistic regression, intention-to-treat"),
        ("Methods", "21b", "Who is in each analysis", "reported", "All randomised, as assigned"),
        ("Methods", "21c", "Missing data", "partial", "Consent-withdrawn excluded; little missing"),
        ("Methods", "21d", "Additional analyses", "reported", "Prespecified subgroups"),
        ("Results", "22a", "Participant flow", "reported", "Flow diagram; 3,010 & 3,012 analysed"),
        ("Results", "22b", "Losses & exclusions", "reported", "Withdrawals/exclusions with reasons"),
        ("Results", "23a", "Recruitment & follow-up dates", "reported", "Dec 2004 – Nov 2008"),
        ("Results", "23b", "Why the trial ended", "reported", "Target enrolment reached"),
        ("Results", "24a", "Intervention delivery / fidelity", "reported", "97% vs 69% insulin; achieved means reported"),
        ("Results", "24b", "Concomitant care", "reported", "Common nutrition / glucose co-protocol"),
        ("Results", "25", "Baseline data", "reported", "Table 1 — groups balanced"),
        ("Results", "26", "Numbers analysed, outcomes, estimation", "reported", "OR 1.14; absolute + relative effect"),
        ("Results", "27", "Harms", "reported", "Severe hypoglycaemia 6.8% vs 0.5%"),
        ("Results", "28", "Ancillary analyses", "reported", "Subgroup & sensitivity analyses"),
        ("Discussion", "29", "Interpretation", "reported", "Intensive control increased mortality"),
        ("Discussion", "30", "Limitations", "reported", "Open-label; single algorithm; generalisability"),
    ]
    return (CHECKLIST,)

@app.cell
def _(mo):
    # Interactive control used by the intervention-delivery figure.
    units = mo.ui.radio(
        options=["mg/dL", "mmol/L"],
        value="mg/dL",
        label="Glucose units",
        inline=True,
    )
    return (units,)

@app.cell
def _(ARMS, FLOW, FONT, TRIAL, colors, card, mo):
    # ---------------------------- HERO ----------------------------
    import math

    _int = ARMS[0]
    _conv = ARMS[1]
    _int_rate = 100 * _int["deaths"] / _int["n"]
    _conv_rate = 100 * _conv["deaths"] / _conv["n"]
    _ard = _int_rate - _conv_rate
    # NNH is conventionally rounded up: a fractional patient cannot be harmed.
    _nnh = math.ceil(1 / (_ard / 100))

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
                Intensive glucose control reached the lower glucose target but increased 90-day mortality.
                This notebook uses CONSORT 2025 to show how the trial was designed, delivered, analysed,
                and reported.
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:8px;">
                {card("Randomised population", f"{FLOW['randomized']:,}", "critically ill adults, 42 ICUs", colors["ink"])}
                {card("Intervention: intensive control", f"{_int_rate:.1f}%", f"{_int['deaths']:,} of {_int['n']:,} with 90-day outcome · target 81–108 mg/dL", colors["intensive"])}
                {card("Reference: conventional control", f"{_conv_rate:.1f}%", f"{_conv['deaths']:,} of {_conv['n']:,} with 90-day outcome · target ≤180 mg/dL", colors["conventional"])}
                {card("Main contrast", f"+{_ard:.1f} pts", f"1 extra death per {_nnh} treated (NNH)", colors["bad"])}
            </div>
        </div>
        """
    )
    hero
    return

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
        return mo.Html(
            f"""
            <div style="font-family:{FONT}; border-top:1px solid {colors['grid']}; padding-top:16px; color:{colors['ink']}; line-height:1.5;">
                <h3 style="font-family:{FONT}; margin:0 0 6px; color:{colors['dark']};">Coverage summary</h3>
                <div style="color:{colors['muted']}; margin-bottom:6px;">
                    {counts['reported']} reported · {counts['partial']} partial · {counts['na']} not applicable · {counts['gap']} not addressed
                </div>
                <div>
                    Of the <strong>{top_level} top-level CONSORT 2025 items ({len(CHECKLIST)} reporting rows)</strong>,
                    the 2009 report substantively covers <strong>{covered} rows</strong>. The gaps are
                    <strong>{' and '.join(gaps)}</strong>. Both expectations became standard after this trial was published.
                    See <a href="#open-science">Open science</a> for item 4 and <a href="#methods">Methods</a> for item 8.
                </div>
            </div>
            """
        )

    return chapter_header, consort_items, coverage_summary, section_nav

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
                "Can a reader identify the study as randomised and understand its design, participants, interventions, and main result from the title and abstract?",
            ),
            consort_items(["1a", "1b"]),
        ],
        gap=0.35,
    )
    title_abstract_view
    return

@app.cell
def _(TRIAL, chapter_header, colors, consort_items, mo):
    # --------------------------- OPEN SCIENCE ---------------------------
    open_science_cards = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:12px;">
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Registration (item 2)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">{TRIAL['registration']}</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Protocol & SAP (item 3)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">Published separately</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Data sharing (item 4)</div>
                    <div style="color:{colors['bad']}; font-size:1.0rem;">Not addressed (2009)</div>
                </div>
                <div style="background:#fff; border:1px solid #D8D4D7; border-radius:10px; padding:12px 14px;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.08em; color:{colors['muted']};">Funding & COI (item 5)</div>
                    <div style="color:{colors['good']}; font-size:1.0rem;">Disclosed; no funder role</div>
                </div>
            </div>
        </div>
        """
    )
    open_science_view = mo.vstack(
        [
            chapter_header(
                "Open science",
                "Registration, protocol access, data availability, funding, and conflicts determine whether readers can audit and reuse the trial.",
            ),
            consort_items(["2", "3", "4", "5a", "5b"]),
            open_science_cards,
        ],
        gap=0.35,
    )
    open_science_view
    return

@app.cell
def _(chapter_header, consort_items, mo):
    introduction_view = mo.vstack(
        [
            chapter_header(
                "Introduction",
                "Why was the trial needed, and which benefit and harm question did the investigators test?",
            ),
            consort_items(["6", "7"]),
        ],
        gap=0.35,
    )
    introduction_view
    return

@app.cell
def _(TRIAL, chapter_header, consort_items, mo):
    design = mo.md(
        f"""
        ### Trial design in one paragraph

        **{TRIAL['name']}** was a multicentre, parallel-group, **open-label** randomised controlled trial with
        blinded, objective outcome ascertainment (all-cause death). Adults expected to need **≥3 days** of intensive
        care were allocated 1:1 by central, concealed **minimisation** (stratified by region and operative status) to
        *intensive* glucose control (target **81–108 mg/dL**) or *conventional* control (target **≤180 mg/dL**), both
        delivered by intravenous insulin. The analysis was **intention-to-treat**. Recruitment ran {TRIAL['recruitment']}
        across {TRIAL['centers']} ICUs ({TRIAL['geography']}).
        """
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
        gap=0.45,
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
def _(FLOW, box, colors, consort_items, mo):
    # ----------------------- CONSORT FLOW DIAGRAM -----------------------
    arrow = f'<div style="text-align:center; color:{colors["muted"]}; font-size:1.1rem; line-height:1;">↓</div>'

    flow_html = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; max-width:720px; margin:0 auto;">
            {box("Assessed for eligibility", FLOW["screened"], colors["dark"])}
            <div style="display:grid; grid-template-columns:1fr 1fr; align-items:center; gap:8px; margin:2px 0;">
                <div style="text-align:center; color:{colors['muted']}; font-size:1.1rem;">↓</div>
                <div style="border-left:2px dashed {colors['grid']}; padding-left:12px;">
                    {box("Excluded", FLOW["excluded_before"], colors["muted"], "not eligible or no consent")}
                </div>
            </div>
            {box("Randomised", FLOW["randomized"], colors["accent"])}
            {arrow}
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                <div style="display:grid; gap:6px;">
                    {box("Allocated: intensive control", FLOW["int_assigned"], colors["intensive"])}
                    {arrow}
                    {box("Excluded from analysis", FLOW["int_excluded"], colors["muted"], "withdrew consent / no primary data")}
                    {arrow}
                    {box("Analysed for primary outcome", FLOW["int_analyzed"], colors["intensive"])}
                </div>
                <div style="display:grid; gap:6px;">
                    {box("Allocated: conventional control", FLOW["conv_assigned"], colors["conventional"])}
                    {arrow}
                    {box("Excluded from analysis", FLOW["conv_excluded"], colors["muted"], "withdrew consent / no primary data")}
                    {arrow}
                    {box("Analysed for primary outcome", FLOW["conv_analyzed"], colors["conventional"])}
                </div>
            </div>
        </div>
        """
    )

    flow_view = mo.vstack(
        [
            consort_items(["22a", "22b", "23a", "23b"], "Participant flow and recruitment"),
            mo.md(
                """
                ### Participant flow
                _The diagram reconstructs participant flow from the reported counts._
                """
            ),
            flow_html,
        ],
        gap=0.35,
    )
    flow_view
    return

@app.cell
def _(ARMS, CHART_W, alt, colors, consort_items, mo, pl, style, units):
    # ------------- INTERVENTIONS: target bands + achieved mean -------------
    factor = 1.0 if units.value == "mg/dL" else 1 / 18.0
    unit = units.value

    def _c(v):
        return round(v * factor, 2 if unit == "mmol/L" else 0)

    band_rows = []
    point_rows = []
    for a in ARMS:
        band_rows.append(
            {
                "arm": a["arm"],
                "lo": _c(a["target_lo"]),
                "hi": _c(a["target_hi"]),
                "label": f'{a["target_lo"]}–{a["target_hi"]} mg/dL',
            }
        )
        point_rows.append(
            {"arm": a["arm"], "achieved": _c(a["achieved"]), "raw": a["achieved"]}
        )
    bands = pl.DataFrame(band_rows)
    points = pl.DataFrame(point_rows)

    arm_scale = alt.Scale(
        domain=["Intensive", "Conventional"],
        range=[colors["intensive"], colors["conventional"]],
    )

    _band = alt.Chart(bands).mark_bar(height=26, opacity=0.35, cornerRadius=3).encode(
        y=alt.Y("arm:N", title=None, sort=["Intensive", "Conventional"]),
        x=alt.X("lo:Q", title=f"Blood glucose ({unit})", scale=alt.Scale(zero=False)),
        x2="hi:Q",
        color=alt.Color("arm:N", scale=arm_scale, legend=None),
        tooltip=[alt.Tooltip("arm:N"), alt.Tooltip("label:N", title="Target range")],
    )
    _achieved = alt.Chart(points).mark_point(
        size=170, filled=True, opacity=1.0
    ).encode(
        y=alt.Y("arm:N", sort=["Intensive", "Conventional"]),
        x=alt.X("achieved:Q"),
        color=alt.Color("arm:N", scale=arm_scale, legend=None),
        tooltip=[alt.Tooltip("arm:N"), alt.Tooltip("raw:Q", title="Achieved mean (mg/dL)")],
    )
    interventions = style(
        (_band + _achieved).properties(
            width=CHART_W,
            height=170,
            title=alt.TitleParams(
                "The assigned targets produced different glucose levels",
                subtitle="The shaded bar shows the protocol target. The dot shows the time-weighted achieved mean.",
            ),
        )
    )

    interventions_view = mo.vstack(
        [
            consort_items(["24a", "24b"], "Intervention delivery and concomitant care"),
            mo.md(
                """
                ### Intervention delivery
                _The chart compares the protocol targets with achieved glucose._
                """
            ),
            units,
            mo.ui.altair_chart(interventions),
            mo.md(
                "Insulin was given to **97%** of the intensive arm versus **69%** of the conventional arm. "
                "The achieved means (115 vs 144 mg/dL) show that treatment delivery produced different "
                "glucose levels in the two groups."
            ),
        ],
        gap=0.35,
    )
    interventions_view
    return

@app.cell
def _(BASELINE, CHART_W, FLOW, alt, colors, consort_items, mo, pl, style):
    # --------------------------- BASELINE ---------------------------
    _profile_labels = [
        "Mechanical ventilation",
        "APACHE II ≥ 25",
        "Severe sepsis",
        "Diabetes",
        "Renal-replacement therapy",
    ]
    _baseline_lookup = dict(BASELINE)
    _profile = pl.DataFrame(
        {
            "characteristic": _profile_labels,
            "percent": [float(_baseline_lookup[label].rstrip("%")) for label in _profile_labels],
            "label": [_baseline_lookup[label] for label in _profile_labels],
        }
    )
    _bars = alt.Chart(_profile).mark_bar(
        color=colors["muted"], opacity=0.72, cornerRadiusEnd=4, size=18
    ).encode(
        y=alt.Y("characteristic:N", sort=_profile_labels, title=None),
        x=alt.X(
            "percent:Q",
            scale=alt.Scale(domain=[0, 105]),
            title="Participants (%)",
        ),
        tooltip=[
            alt.Tooltip("characteristic:N", title="Characteristic"),
            alt.Tooltip("percent:Q", title="Participants", format=".0f"),
        ],
    )
    _labels = alt.Chart(_profile).mark_text(
        align="left", dx=6, color=colors["dark"], fontWeight=600
    ).encode(
        y=alt.Y("characteristic:N", sort=_profile_labels),
        x="percent:Q",
        text="label:N",
    )
    profile_chart = style(
        (_bars + _labels).properties(
            width=CHART_W,
            height=155,
            title=alt.TitleParams(
                "A highly supported ICU population",
                subtitle="Overall cohort; labels show the percentage with each characteristic.",
            ),
        )
    )

    _rows = "\n".join(f"| {label} | {value} |" for label, value in BASELINE)
    _baseline_table = mo.md(
        "| Characteristic | Value |\n"
        "|:---|:---|\n"
        f"{_rows}"
    )
    baseline_view = mo.vstack(
        [
            consort_items(["25"], "Baseline data"),
            mo.md(
                f"### Baseline profile\n"
                f"The overall cohort included **{FLOW['randomized']:,} participants**. "
                "The randomized groups were well balanced."
            ),
            mo.ui.altair_chart(profile_chart),
            mo.md(
                "Most participants received mechanical ventilation, so the result applies most directly to a highly supported ICU population."
            ),
            mo.accordion({"Full reported baseline summary": _baseline_table}),
        ],
        gap=0.45,
    )
    baseline_view
    return

@app.cell
def _(ARMS, CHART_W, alt, colors, consort_items, mo, pl, style):
    # ---------- PRIMARY OUTCOME: absolute risk as an icon array ----------
    # Each square = one patient per 100. Died squares are filled first.
    def _waffle_df(arm, rate, color_key):
        died = round(rate)
        rows = []
        for i in range(100):
            r, c = divmod(i, 10)
            rows.append(
                {
                    "arm": arm,
                    "row": r,
                    "col": c,
                    "status": "Died by 90 days" if i < died else "Survived",
                }
            )
        return pl.DataFrame(rows), died

    def _waffle_chart(arm, rate, color_key):
        df, died = _waffle_df(arm, rate, color_key)
        status_scale = alt.Scale(
            domain=["Died by 90 days", "Survived"],
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
                f"{arm}",
                subtitle=f"{rate:.1f}% died  ·  ≈ {died} of every 100",
                color=colors[color_key],
            ),
        )
        return style(chart)

    _int, _conv = ARMS[0], ARMS[1]
    _int_rate = 100 * _int["deaths"] / _int["n"]
    _conv_rate = 100 * _conv["deaths"] / _conv["n"]

    waffle_view = mo.vstack(
        [
            consort_items(["26"], "Numbers analysed, outcomes, and estimation"),
            mo.md(
                """
                ### Primary outcome: 90-day mortality
                **Read it as:** Each square represents one patient per 100. Filled squares represent death.

                **Why this geometry:** The trial reports 90-day mortality with fixed group denominators, so a
                10×10 array gives a valid absolute-risk comparison.
                """
            ),
            mo.hstack(
                [
                    mo.ui.altair_chart(_waffle_chart("Intensive", _int_rate, "intensive")),
                    mo.ui.altair_chart(_waffle_chart("Conventional", _conv_rate, "conventional")),
                ],
                justify="center",
                gap=0.6,
            ),
            mo.md(
                f"**What it says:** **{_int['deaths']:,}/{_int['n']:,} ({_int_rate:.1f}%)** died with intensive control versus "
                f"**{_conv['deaths']:,}/{_conv['n']:,} ({_conv_rate:.1f}%)** with conventional control. The absolute "
                f"increase of **{_int_rate - _conv_rate:.1f} percentage points** (P = 0.02)."
            ),
        ],
        gap=0.35,
    )
    waffle_view
    return

@app.cell
def _(CHART_W, EFFECTS, alt, colors, mo, pl, style):
    # --------------- EFFECT ESTIMATES: forest plot (log OR) ---------------
    ef = pl.DataFrame(EFFECTS)
    order = [e["outcome"] for e in EFFECTS]

    _rule = alt.Chart(ef).mark_rule(strokeWidth=2, color=colors["bad"]).encode(
        y=alt.Y("outcome:N", sort=order, title=None),
        x=alt.X("lo:Q", scale=alt.Scale(type="log", domain=[0.9, 30]),
                title="Odds ratio (log scale) — intensive vs conventional"),
        x2="hi:Q",
    )
    _pt = alt.Chart(ef).mark_point(size=110, filled=True, color=colors["bad"]).encode(
        y=alt.Y("outcome:N", sort=order),
        x="or:Q",
        tooltip=[
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("or:Q", title="OR"),
            alt.Tooltip("lo:Q", title="95% CI low"),
            alt.Tooltip("hi:Q", title="95% CI high"),
        ],
    )
    _null = alt.Chart(pl.DataFrame({"x": [1.0]})).mark_rule(
        strokeDash=[5, 4], color=colors["muted"]
    ).encode(x="x:Q")

    forest = style(
        (_null + _rule + _pt).properties(
            width=CHART_W,
            height=170,
            title=alt.TitleParams(
                "Intensive control increased mortality and severe hypoglycaemia",
                subtitle="Points show odds ratios; rules show 95% CIs. The dashed line marks OR = 1.",
            ),
        )
    )

    forest_view = mo.vstack(
        [
            mo.md(
                """
                ### Relative effect estimates
                _The 95% CIs for mortality and severe hypoglycaemia exclude OR = 1._
                """
            ),
            mo.ui.altair_chart(forest),
        ],
        gap=0.35,
    )
    forest_view
    return

@app.cell
def _(ARMS, CHART_W, SECONDARY, alt, colors, consort_items, mo, pl, style):
    # ------------------------- HARMS + SECONDARY -------------------------
    _outcome_order = ["90-day mortality", "Severe hypoglycaemia"]
    _arm_names = [arm["arm"] for arm in ARMS]
    _risk_rows = []
    for _arm in ARMS:
        _mortality_risk = 100 * _arm["deaths"] / _arm["n"]
        _risk_rows.extend(
            [
                {
                    "outcome": _outcome_order[0],
                    "arm": _arm["arm"],
                    "events": _arm["deaths"],
                    "n": _arm["n"],
                    "risk": _mortality_risk,
                    "label": f"{_mortality_risk:.1f}%",
                },
                {
                    "outcome": _outcome_order[1],
                    "arm": _arm["arm"],
                    "events": _arm["hypo"],
                    "n": _arm["hypo_n"],
                    "risk": _arm["hypo_pct"],
                    "label": f"{_arm['hypo_pct']:.1f}%",
                },
            ]
        )
    _risks = pl.DataFrame(_risk_rows)
    _ranges = _risks.group_by("outcome").agg(
        pl.col("risk").min().alias("lo"),
        pl.col("risk").max().alias("hi"),
    )
    _links = alt.Chart(_ranges).mark_rule(
        color=colors["muted"], opacity=0.48, strokeWidth=4
    ).encode(
        y=alt.Y("outcome:N", sort=_outcome_order, title=None),
        x=alt.X("lo:Q", scale=alt.Scale(domain=[0, 31]), title="Participants with outcome (%)"),
        x2="hi:Q",
    )
    _points = alt.Chart(_risks).mark_point(size=150, filled=True).encode(
        y=alt.Y("outcome:N", sort=_outcome_order),
        x=alt.X("risk:Q", scale=alt.Scale(domain=[0, 31])),
        color=alt.Color(
            "arm:N",
            scale=alt.Scale(
                domain=_arm_names,
                range=[colors["intensive"], colors["conventional"]],
            ),
            title=None,
        ),
        tooltip=[
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("arm:N", title="Arm"),
            alt.Tooltip("events:Q", title="Events", format=","),
            alt.Tooltip("n:Q", title="Denominator", format=","),
            alt.Tooltip("risk:Q", title="Risk (%)", format=".1f"),
        ],
    )
    _intensive_labels = alt.Chart(_risks).transform_filter(
        alt.datum.arm == _arm_names[0]
    ).mark_text(dy=-12, color=colors["intensive"], fontWeight=600).encode(
        y=alt.Y("outcome:N", sort=_outcome_order),
        x="risk:Q",
        text="label:N",
    )
    _conventional_labels = alt.Chart(_risks).transform_filter(
        alt.datum.arm == _arm_names[1]
    ).mark_text(dy=13, color=colors["conventional"], fontWeight=600).encode(
        y=alt.Y("outcome:N", sort=_outcome_order),
        x="risk:Q",
        text="label:N",
    )
    harms_chart = style(
        (_links + _points + _intensive_labels + _conventional_labels).properties(
            width=CHART_W,
            height=125,
            title=alt.TitleParams(
                "Absolute harm profile",
                subtitle="Points show observed risks; each gray line joins the randomized arms.",
            ),
        )
    )

    _int, _conv = ARMS[0], ARMS[1]
    harms_view = mo.vstack(
        [
            consort_items(["27", "28"], "Harms and ancillary analyses"),
            mo.md("### Harms and secondary outcomes"),
            mo.ui.altair_chart(harms_chart),
            mo.md(
                f"Severe hypoglycaemia (≤40 mg/dL) occurred in **{_int['hypo']:,}/{_int['hypo_n']:,} "
                f"({_int['hypo_pct']:.1f}%)** participants on intensive control and **{_conv['hypo']:,}/{_conv['hypo_n']:,} "
                f"({_conv['hypo_pct']:.1f}%)** on conventional control. No prespecified secondary outcome differed "
                f"significantly: {', '.join(SECONDARY[:-1])}, and {SECONDARY[-1].lower()}."
            ),
        ],
        gap=0.5,
    )
    harms_view
    return

@app.cell
def _(chapter_header, consort_items, mo):
    discussion_note = mo.md(
        """
        ### Interpretation and limits

        Intensive glucose control lowered blood glucose but increased mortality. The trial therefore supports
        conventional rather than intensive control for this population.

        The open-label design, use of a single glucose-control algorithm, and participating ICU settings limit
        how broadly the result can be generalized.
        """
    )
    discussion_view = mo.vstack(
        [
            chapter_header(
                "Discussion",
                "How should the result be interpreted, and which limitations affect its application?",
            ),
            consort_items(["29", "30"]),
            discussion_note,
        ],
        gap=0.55,
    )
    discussion_view
    return

@app.cell
def _(coverage_summary):
    coverage = coverage_summary()
    coverage
    return

@app.cell
def _(TRIAL, colors, mo):
    # ------------------------- PROVENANCE -------------------------
    provenance = mo.Html(
        f"""
        <div style="font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['muted']}; font-size:0.86rem;
                    border-top:1px solid {colors['grid']}; padding-top:12px; line-height:1.5;">
            <strong style="color:{colors['ink']};">Source & provenance.</strong>
            {TRIAL['citation']} DOI <a href="https://doi.org/{TRIAL['doi']}" style="color:{colors['conventional']};">{TRIAL['doi']}</a>.
            Checklist: Hopewell S, et al. CONSORT 2025 Statement. <em>BMJ</em> 2025;388:e081123.
            Every figure is rendered from the data literals near the top of this notebook. Where the paper
            reported only percentages, denominators were reconstructed so the arithmetic reproduces the
            published rates (e.g. 829/3,010 = 27.5%); the icon array rounds each rate to the nearest whole
            square. This audit applies CONSORT 2025 retrospectively; the checklist postdates the trial.
        </div>
        """
    )
    provenance
    return

if __name__ == "__main__":
    app.run()
