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
    # group is the top-level CONSORT section used by the section filter.
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
def _(CHECKLIST, mo):
    # Interactive controls — always shown (works in script/run/edit modes).
    units = mo.ui.radio(
        options=["mg/dL", "mmol/L"],
        value="mg/dL",
        label="Glucose units",
        inline=True,
    )
    section = mo.ui.dropdown(
        options=["All sections"] + list(dict.fromkeys(row[0] for row in CHECKLIST)),
        value="All sections",
        label="CONSORT section",
    )
    return section, units


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
def _(TRIAL, mo):
    design = mo.md(
        f"""
        ## The design in one paragraph

        **{TRIAL['name']}** was a multicentre, parallel-group, **open-label** randomised controlled trial with
        blinded, objective outcome ascertainment (all-cause death). Adults expected to need **≥3 days** of intensive
        care were allocated 1:1 by central, concealed **minimisation** (stratified by region and operative status) to
        *intensive* glucose control (target **81–108 mg/dL**) or *conventional* control (target **≤180 mg/dL**), both
        delivered by intravenous insulin. The analysis was **intention-to-treat**. Recruitment ran {TRIAL['recruitment']}
        across {TRIAL['centers']} ICUs ({TRIAL['geography']}).

        _CONSORT items 1, 9, 11, 12, 17–21._
        """
    )
    design
    return


@app.cell
def _(ARMS, CHART_W, alt, colors, mo, pl, style, units):
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
            mo.md(
                """
                ## Intervention delivery
                _CONSORT items 13 and 24. The chart compares the protocol targets with achieved glucose._
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
def _(FLOW, box, colors, mo):
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
def _(BASELINE, mo):
    # --------------------------- BASELINE ---------------------------
    _rows = "\n".join(f"| {label} | {value} |" for label, value in BASELINE)
    baseline_text = (
        "## Baseline characteristics\n"
        "_CONSORT item 25. Overall cohort (n = 6,104); the trial reported the two groups were well balanced._\n\n"
        "| Characteristic | Value |\n"
        "|:---|:---|\n"
        f"{_rows}"
    )
    baseline_view = mo.md(baseline_text)
    baseline_view
    return


@app.cell
def _(ARMS, CHART_W, alt, colors, mo, pl, style):
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
            mo.md(
                """
                ## Primary outcome: 90-day mortality
                _CONSORT item 26._

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
                ## Effect estimates
                _CONSORT item 26. The 95% CIs for mortality and severe hypoglycaemia exclude OR = 1._
                """
            ),
            mo.ui.altair_chart(forest),
        ],
        gap=0.35,
    )
    forest_view
    return


@app.cell
def _(ARMS, SECONDARY, colors, mo, pill):
    # ------------------------- HARMS + SECONDARY -------------------------
    _int, _conv = ARMS[0], ARMS[1]
    harms_md = mo.md(
        f"""
        ## Harms & secondary outcomes
        _CONSORT items 15 & 27 (harms) and 26 (secondary outcomes)._

        **Severe hypoglycaemia** (≤40 mg/dL) occurred in
        **{_int['hypo']} patients ({_int['hypo_pct']}%)** on intensive control versus **{_conv['hypo']}
        ({_conv['hypo_pct']}%)** on conventional control, about **15 times** as often.

        No prespecified **secondary outcome** showed a significant between-group difference:
        {", ".join(SECONDARY[:-1])}, and {SECONDARY[-1].lower()}.
        """
    )

    harms_note = mo.Html(
        f"""
        <div style="background:{colors['panel2']}; border-left:4px solid {colors['bad']};
                    border-radius:8px; padding:12px 16px; font-family:Inter, ui-sans-serif, system-ui, sans-serif; color:{colors['ink']};">
            <strong>Clinical interpretation:</strong> blood glucose is a surrogate outcome. Intensive control
            lowered glucose but increased mortality. {pill("reported")} The report also quantified severe
            hypoglycaemia.
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
                        <th style="padding:6px 10px;">In NICE-SUGAR</th>
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
            2009 paper substantively covers <strong>{_covered} of {len(CHECKLIST)} rows</strong>. The gaps are
            <strong>data sharing (item 4)</strong> and <strong>patient and public involvement (item 8)</strong>.
            CONSORT added both expectations after 2009. This retrospective audit shows how reporting
            requirements changed.
        </div>
        """
    )

    checklist_view = mo.vstack(
        [
            mo.md(
                """
                ## The CONSORT 2025 checklist, item by item
                _Filter by section. Each row pairs a checklist item with where NICE-SUGAR reports it._
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
