# ─────────────────────────────────────────────────────────────────────────────
# Wrangell Energy Future | Greensparc Anchor Customer Explorer
#
# Story: SEAPA's Tyee Lake hydro is maxed out. Wrangell load is growing fast
# from heat pump adoption. The system needs a $20M 3rd turbine. A Greensparc
# data-center anchor customer can make that expansion financeable — and drive
# community rates below today's level. This tool shows how.
#
# Run:  streamlit run streamlit_app.py
# Deps: pip install streamlit pandas plotly
#
# Data sources:
#   • 2023 load / rate: EIA-861 Short Form (City of Wrangell, utility 21015)
#   • SEAPA capacity: FERC filings + Ketchikan Daily News / Frontier Media (2024)
#   • Diesel capacity: EIA-860 (Plant 95, 2025)
#   • Wholesale rate: back-calculated from 2023 EIA-861 actuals
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ═════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & COLOR PALETTE
# ═════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Wrangell Energy Future | Greensparc",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Three-scenario palette — used consistently in every chart and callout
C_A      = "#dc2626"   # red    — Status Quo: diesel creep, rising rates
C_B      = "#d97706"   # amber  — Expansion Only: capital on ratepayers
C_C      = "#16a34a"   # green  — Expansion + Anchor: rates go down
C_HYDRO        = "#2563eb"              # blue   — SEAPA hydropower in stacked charts
C_DIESEL       = "#f97316"              # orange — diesel in stacked charts
C_HYDRO_FILL   = "rgba(37,99,235,0.75)"   # semi-transparent for stacked areas
C_DIESEL_FILL  = "rgba(249,115,22,0.75)"  # semi-transparent for stacked areas
C_REF    = "#6b7280"   # gray   — reference lines (today's rate, expansion date)

SCENARIO_LABELS = {
    "A": "🔴 Status Quo",
    "B": "🟡 Expansion Only",
    "C": "🟢 Expansion + Anchor",
}
SCENARIO_COLORS = {"A": C_A, "B": C_B, "C": C_C}

YEARS = list(range(2023, 2036))   # 2023 through 2035 inclusive


# ═════════════════════════════════════════════════════════════════════════════
# 2. FINANCIAL HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def fmt_dollar(v: float, signed: bool = False) -> str:
    """Format a dollar value cleanly, handling negatives."""
    if signed:
        return f"+${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"
    return f"${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"


def fmt_dollar_md(v: float, signed: bool = False) -> str:
    """Format a dollar value for Streamlit markdown (escaped $ to avoid LaTeX)."""
    if signed:
        return f"+\\${v:,.0f}" if v >= 0 else f"-\\${abs(v):,.0f}"
    return f"\\${v:,.0f}" if v >= 0 else f"-\\${abs(v):,.0f}"


def annual_debt_service(capex: float, wrangell_share: float,
                         rate: float, term: int) -> float:
    """
    Standard annuity PMT formula.
    capex × wrangell_share = principal Wrangell must service.
    """
    pv = capex * wrangell_share
    r  = rate
    n  = term
    return pv * r * (1 + r) ** n / ((1 + r) ** n - 1)


def anchor_capex_coverage(anchor_mwh: float, anchor_tariff_mwh: float,
                           seapa_rate: float, debt_service_yr: float) -> float:
    """
    Fraction of Wrangell's annual expansion debt service covered by the anchor's
    above-cost margin.

    anchor margin/yr = anchor_mwh × (tariff − seapa_cost)
    coverage = margin / debt_service_yr
    """
    if debt_service_yr <= 0:
        return 0.0
    margin = anchor_mwh * (anchor_tariff_mwh - seapa_rate)
    return margin / debt_service_yr


# ═════════════════════════════════════════════════════════════════════════════
# 3. YEAR-BY-YEAR SCENARIO MODEL
# ═════════════════════════════════════════════════════════════════════════════

def _community_load(base_mwh, year, phase1_end, r1, r2):
    """Two-phase compound growth. Returns MWh for a single year."""
    if year <= phase1_end:
        return base_mwh * (1 + r1) ** (year - 2023)
    terminal = base_mwh * (1 + r1) ** (phase1_end - 2023)
    return terminal * (1 + r2) ** (year - phase1_end)


@st.cache_data
def compute_scenarios(
    # Load
    base_mwh, r1, phase1_end, r2,
    # SEAPA
    seapa_cap, seapa_rate,
    expansion_year, expansion_new_mwh,
    # Diesel
    diesel_floor, diesel_base_cost, diesel_escalation,
    # Fixed
    fixed_cost,
    # Expansion financing
    debt_service_yr,
    # Anchor
    anchor_mwh_yr, anchor_tariff_mwh,
) -> dict:
    """
    Compute year-by-year trajectories for all three scenarios.

    Scenario A: no expansion, no anchor. Diesel fills growing gap.
    Scenario B: expansion comes online in expansion_year; full capital on ratepayers.
    Scenario C: expansion + anchor; anchor margin offsets most of the capital cost.

    Returns a dict keyed by scenario letter, each containing lists indexed by YEARS.
    """
    results = {}

    for scenario in ["A", "B", "C"]:
        has_expansion = scenario in ("B", "C")
        has_anchor    = scenario == "C"

        rows = []
        for year in YEARS:
            yrs_from_base = year - 2023

            # ── community load (existing ratepayers) ──────────────────────
            comm_mwh = _community_load(base_mwh, year, phase1_end, r1, r2)

            # ── SEAPA energy cap this year ────────────────────────────────
            cap = seapa_cap
            if has_expansion and year >= expansion_year:
                cap = seapa_cap + expansion_new_mwh

            # ── anchor energy this year (only post-expansion) ─────────────
            anchor = anchor_mwh_yr if (has_anchor and year >= expansion_year) else 0.0

            # ── total system demand ───────────────────────────────────────
            total_mwh = comm_mwh + anchor

            # ── dispatch: hydro first, diesel fills the gap ───────────────
            diesel_mwh = max(diesel_floor, total_mwh - cap)
            hydro_mwh  = total_mwh - diesel_mwh

            # ── unit costs ────────────────────────────────────────────────
            diesel_rate = diesel_base_cost * (1 + diesel_escalation) ** yrs_from_base

            # ── annual costs ──────────────────────────────────────────────
            seapa_cost   = seapa_rate * hydro_mwh
            diesel_cost  = diesel_rate * diesel_mwh
            debt_svc     = debt_service_yr if (has_expansion and year >= expansion_year) else 0.0
            anchor_rev   = anchor * anchor_tariff_mwh   # $ from anchor customer

            total_cost   = fixed_cost + seapa_cost + diesel_cost + debt_svc

            # ── rate for existing community customers ─────────────────────
            # Anchor revenue offsets total cost; remainder borne by community
            community_cost = total_cost - anchor_rev
            rate_kwh = max(0.05, community_cost / (comm_mwh * 1_000))   # clamp floor

            rows.append(dict(
                year=year,
                community_mwh=comm_mwh,
                anchor_mwh=anchor,
                total_mwh=total_mwh,
                seapa_cap=cap,
                hydro_mwh=hydro_mwh,
                diesel_mwh=diesel_mwh,
                seapa_cost=seapa_cost,
                diesel_cost=diesel_cost,
                diesel_rate=diesel_rate,
                debt_service=debt_svc,
                anchor_revenue=anchor_rev,
                total_cost=total_cost,
                community_cost=community_cost,
                rate_kwh=rate_kwh,
            ))

        results[scenario] = pd.DataFrame(rows).set_index("year")

    return results


# ═════════════════════════════════════════════════════════════════════════════
# 4. NARRATIVE GENERATORS
# ═════════════════════════════════════════════════════════════════════════════

def narr_rate(scenarios, params, target_yr=2030):
    sc = scenarios
    yr = target_yr
    ra = sc["A"].loc[yr, "rate_kwh"]
    rb = sc["B"].loc[yr, "rate_kwh"]
    rc = sc["C"].loc[yr, "rate_kwh"]
    base = params["base_rate"]
    da   = (ra - base) / base * 100
    dc   = (rc - base) / base * 100
    cov  = anchor_capex_coverage(
        params["anchor_mwh_yr"], params["anchor_tariff_mwh"],
        params["seapa_rate"], params["debt_service_yr"]
    ) * 100
    margin_yr = params["anchor_mwh_yr"] * (params["anchor_tariff_mwh"] - params["seapa_rate"])
    dir_c = "below" if rc < base else "above"
    return (
        f"Without action, Wrangell's growing reliance on **\\${params['diesel_base_cost']:.0f}/MWh diesel** "
        f"— versus **\\${params['seapa_rate']:.0f}/MWh SEAPA hydro** — pushes rates "
        f"**{da:+.1f}%** by {yr} under the Status Quo. "
        f"The expansion alone provides rate stability but adds **{fmt_dollar_md(params['debt_service_yr'])}/year** "
        f"in capital charges to Wrangell ratepayers. "
        f"Greensparc's anchor tariff generates **{fmt_dollar_md(margin_yr)}/year** above SEAPA cost, "
        f"covering **{cov:.0f}%** of that debt service. "
        f"By {yr}, Wrangell residents under Scenario C pay "
        f"**{rc*100:.2f}¢/kWh** — "
        f"**{abs(rc-base)*100:.2f}¢ {dir_c}** today's rate."
    )


def narr_diesel(scenarios, params):
    total_a = scenarios["A"]["diesel_mwh"].sum()
    total_c = scenarios["C"]["diesel_mwh"].sum()
    avoided = total_a - total_c
    cost_a  = scenarios["A"]["diesel_cost"].sum()
    cost_c  = scenarios["C"]["diesel_cost"].sum()
    cost_saved = cost_a - cost_c
    co2 = avoided * 0.7   # ~0.7 tonnes CO2 per MWh diesel
    bbls = avoided / 0.01709  # MWh per barrel diesel
    yr_a35 = scenarios["A"].loc[2035, "diesel_mwh"]
    return (
        f"Today Wrangell runs **~{int(scenarios['A'].loc[2023,'diesel_mwh']):,} MWh/yr** of diesel backup. "
        f"Without the SEAPA expansion, load growth forces diesel use to "
        f"**{yr_a35:,.0f} MWh/yr by 2035** — "
        f"roughly **{yr_a35/scenarios['A'].loc[2035,'total_mwh']*100:.0f}%** of all power on expensive diesel. "
        f"Scenarios B and C eliminate that structural gap when the 3rd turbine comes online. "
        f"Compared to the Status Quo through 2035: "
        f"**{avoided:,.0f} MWh of diesel avoided**, saving roughly "
        f"**{fmt_dollar_md(cost_saved)}** and **{co2:,.0f} tonnes of CO₂** ({bbls:,.0f} barrels avoided)."
    )


def narr_viability(cov_pct, margin_yr, debt_svc, anchor_mw):
    if cov_pct >= 0.90:
        msg = (
            f"The anchor customer's above-cost tariff **fully covers** Wrangell's expansion debt share "
            f"and generates a surplus that flows back as lower rates. The expansion essentially "
            f"pays for itself through the anchor relationship."
        )
    elif cov_pct >= 0.60:
        msg = (
            f"The anchor covers **{cov_pct:.0%}** of Wrangell's **{fmt_dollar_md(debt_svc)}/year** expansion "
            f"debt share — a substantial reduction. Ratepayers absorb only the remaining "
            f"**{fmt_dollar_md(debt_svc - margin_yr)}/year**, a small fraction of the full capital cost."
        )
    else:
        msg = (
            f"At this anchor size and tariff, the anchor covers **{cov_pct:.0%}** of expansion costs. "
            f"Ratepayers still carry most of the capital. "
            f"Consider increasing anchor load or tariff to improve community outcomes."
        )
    return msg


def narr_community(scenarios, params, n_hh, hh_kwh):
    yr = 2030
    bill_base = params["base_rate"] * hh_kwh
    bill_a = scenarios["A"].loc[yr, "rate_kwh"] * hh_kwh
    bill_c = scenarios["C"].loc[yr, "rate_kwh"] * hh_kwh
    savings_vs_a = bill_a - bill_c
    savings_vs_base = bill_base - bill_c
    cum_savings = sum(
        (scenarios["A"].loc[y, "rate_kwh"] - scenarios["C"].loc[y, "rate_kwh"]) * hh_kwh
        for y in range(2027, 2036)
    )
    return (
        f"For Wrangell's **{n_hh:,} households** (avg **{hh_kwh:,} kWh/yr**), "
        f"the difference between Status Quo and Expansion + Anchor is "
        f"roughly **{fmt_dollar_md(savings_vs_a)}/household/year** by {yr}. "
        f"Compared to today's bill, Scenario C households save about "
        f"**{fmt_dollar_md(savings_vs_base)}/year**. "
        f"Cumulative household savings (Scenario C vs A, 2027–2035): "
        f"**{fmt_dollar_md(cum_savings)}/household** — or "
        f"**{fmt_dollar_md(cum_savings * n_hh)}** community-wide. "
        f"The anchor customer doesn't just share costs — it inverts the expansion economics, "
        f"turning a **\\$20M infrastructure liability** into a long-term community benefit."
    )


# ═════════════════════════════════════════════════════════════════════════════
# 5. CHART BUILDERS
# ═════════════════════════════════════════════════════════════════════════════

def _vline(fig, x, label, row=None, col=None):
    """Add a dashed vertical reference line at year x."""
    kwargs = dict(row=row, col=col) if row else {}
    fig.add_vline(
        x=x, line_dash="dot", line_color=C_REF, line_width=1.5,
        annotation_text=label, annotation_position="top right",
        annotation_font_size=11, annotation_font_color=C_REF,
        **kwargs,
    )


def chart_rate_trajectory(scenarios, base_rate, expansion_yr):
    """Three-line rate trajectory — the hero chart."""
    fig = go.Figure()

    # Baseline reference
    fig.add_hline(
        y=base_rate, line_dash="dot", line_color=C_REF, line_width=1.5,
        annotation_text=f"2023 rate: {base_rate*100:.1f}¢/kWh",
        annotation_position="bottom right",
        annotation_font_color=C_REF,
    )

    dashes = {"A": "dash", "B": "solid", "C": "solid"}
    widths = {"A": 2, "B": 2, "C": 3}

    # Draw C first, A last so Status Quo line stays visible until scenarios split
    for key in ["C", "B", "A"]:
        df  = scenarios[key]
        fig.add_trace(go.Scatter(
            x=YEARS,
            y=df["rate_kwh"].tolist(),
            mode="lines+markers",
            name=SCENARIO_LABELS[key],
            line=dict(color=SCENARIO_COLORS[key], dash=dashes[key], width=widths[key]),
            marker=dict(size=6 if key != "C" else 8),
            hovertemplate="%{x}: %{y:.4f} $/kWh<extra>" + SCENARIO_LABELS[key] + "</extra>",
        ))

    # Scenario C "below today" annotation
    rate_c_2030 = scenarios["C"].loc[2030, "rate_kwh"]
    if rate_c_2030 < base_rate:
        fig.add_annotation(
            x=2030, y=rate_c_2030,
            text=f"↓ {abs(rate_c_2030 - base_rate)*100:.1f}¢ below today",
            showarrow=True, arrowhead=2, arrowcolor=C_C,
            font=dict(color=C_C, size=12, family="Arial"),
            ax=60, ay=-30,
        )

    _vline(fig, expansion_yr, "Expansion online")

    fig.update_layout(
        title="Retail Rate Trajectory — Three Scenarios ($/kWh)",
        xaxis=dict(title="Year", tickmode="linear", tick0=2023, dtick=1, tickangle=-45),
        yaxis=dict(title="Retail Rate ($/kWh)", tickformat="$.3f",
                   range=[0.09, 0.17]),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=480,
        margin=dict(t=80, b=60, l=80, r=40),
    )
    return fig


def chart_diesel_lines(scenarios, expansion_yr):
    """Three lines of diesel MWh/yr by year."""
    fig = go.Figure()
    dashes = {"A": "solid", "B": "dash", "C": "dot"}
    for key in ["A", "B", "C"]:
        df = scenarios[key]
        fig.add_trace(go.Scatter(
            x=YEARS,
            y=df["diesel_mwh"].tolist(),
            mode="lines+markers",
            name=SCENARIO_LABELS[key],
            line=dict(color=SCENARIO_COLORS[key], dash=dashes[key], width=2),
            marker=dict(size=6),
            hovertemplate="%{x}: %{y:,.0f} MWh<extra>" + SCENARIO_LABELS[key] + "</extra>",
        ))
    _vline(fig, expansion_yr, "Expansion online")
    fig.update_layout(
        title="Annual Diesel Backup Usage (MWh/yr)",
        xaxis=dict(title="Year", tickmode="linear", tick0=2023, dtick=1, tickangle=-45),
        yaxis=dict(title="Diesel (MWh/yr)"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=340,
        margin=dict(t=70, b=60, l=80, r=40),
    )
    return fig


def chart_energy_stacks(scenarios, expansion_yr):
    """3-row stacked area chart: hydro + diesel by year, one row per scenario."""
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        subplot_titles=[SCENARIO_LABELS[k] for k in ["A", "B", "C"]],
        vertical_spacing=0.08,
    )
    for i, key in enumerate(["A", "B", "C"], start=1):
        df = scenarios[key]
        # Hydro area
        fig.add_trace(go.Scatter(
            x=YEARS, y=df["hydro_mwh"].tolist(),
            name="SEAPA Hydro" if i == 1 else None,
            showlegend=(i == 1),
            stackgroup="one",
            mode="none",
            fillcolor=C_HYDRO_FILL,
            hovertemplate="%{x}: %{y:,.0f} MWh hydro<extra></extra>",
        ), row=i, col=1)
        # Diesel area
        fig.add_trace(go.Scatter(
            x=YEARS, y=df["diesel_mwh"].tolist(),
            name="Diesel" if i == 1 else None,
            showlegend=(i == 1),
            stackgroup="one",
            mode="none",
            fillcolor=C_DIESEL_FILL,
            hovertemplate="%{x}: %{y:,.0f} MWh diesel<extra></extra>",
        ), row=i, col=1)

    # Expansion line on each subplot
    for i in range(1, 4):
        fig.add_vline(
            x=expansion_yr, line_dash="dot", line_color=C_REF,
            line_width=1, row=i, col=1,
        )

    fig.update_layout(
        title="Energy Mix — SEAPA Hydro vs Diesel (MWh/yr)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=620,
        margin=dict(t=100, b=60, l=80, r=40),
    )
    fig.update_yaxes(title_text="MWh/yr")
    fig.update_xaxes(title_text="Year", row=3, col=1,
                     tickmode="linear", tick0=2023, dtick=1, tickangle=-45)
    return fig


def chart_diesel_cost_bars(scenarios):
    """Grouped bar chart: diesel cost by year, three scenarios."""
    display_yrs = [2023, 2025, 2027, 2029, 2031, 2033, 2035]
    fig = go.Figure()
    for key in ["A", "B", "C"]:
        df = scenarios[key]
        vals = [df.loc[y, "diesel_cost"] for y in display_yrs]
        fig.add_trace(go.Bar(
            name=SCENARIO_LABELS[key],
            x=[str(y) for y in display_yrs],
            y=vals,
            marker_color=SCENARIO_COLORS[key],
            text=[f"${v/1e3:.0f}K" for v in vals],
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        title="Annual Diesel Cost ($/yr)",
        yaxis_title="$/year",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320,
        margin=dict(t=70, b=40, r=40),
    )
    return fig


def chart_expansion_waterfall(debt_svc, anchor_margin):
    """Waterfall: expansion debt → anchor offsets → residual on community."""
    residual = max(0.0, debt_svc - anchor_margin)
    over     = max(0.0, anchor_margin - debt_svc)
    measures = ["absolute", "relative", "total"] if over == 0 else ["absolute", "relative", "relative", "total"]
    xs       = ["Expansion\ndebt service", "Anchor\nmargin offset", "Residual\nfor ratepayers"] if over == 0 else \
               ["Expansion\ndebt service", "Anchor covers\nfull cost", "Rate reduction\nsurplus", "Net community\nimpact"]
    ys       = [-debt_svc, anchor_margin, 0] if over == 0 else [-debt_svc, debt_svc, over, 0]
    texts    = [fmt_dollar(debt_svc), fmt_dollar(anchor_margin),
                fmt_dollar(residual)] if over == 0 else \
               [fmt_dollar(debt_svc), fmt_dollar(debt_svc),
                fmt_dollar(over), fmt_dollar(over)]

    fig = go.Figure(go.Waterfall(
        measure=measures,
        x=xs,
        y=ys,
        text=texts,
        textposition="outside",
        connector={"line": {"color": "#9ca3af"}},
        increasing={"marker": {"color": C_C}},
        decreasing={"marker": {"color": C_A}},
        totals={"marker": {"color": C_B}},
    ))
    fig.update_layout(
        title="Annual Expansion Cost Allocation (representative year)",
        yaxis_title="$/year",
        yaxis_tickformat="$,.0f",
        height=360,
        margin=dict(t=70, b=40, r=40),
    )
    return fig


def chart_cumulative_coverage(debt_svc, anchor_margin, expansion_yr):
    """Cumulative debt vs anchor margin from expansion year → 2035."""
    post_yrs = [y for y in YEARS if y >= expansion_yr]
    cum_debt   = [debt_svc * (y - expansion_yr + 1) for y in post_yrs]
    cum_anchor = [anchor_margin * (y - expansion_yr + 1) for y in post_yrs]

    fig = go.Figure()
    # Shaded area between lines
    fig.add_trace(go.Scatter(
        x=post_yrs + post_yrs[::-1],
        y=cum_anchor + cum_debt[::-1],
        fill="toself",
        fillcolor="rgba(22,163,74,0.15)" if anchor_margin >= debt_svc else "rgba(220,38,38,0.10)",
        line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=post_yrs, y=cum_debt,
        name="Cumulative debt owed",
        line=dict(color=C_A, dash="dash", width=2),
        hovertemplate="%{x}: %{y:$,.0f}<extra>Debt owed</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=post_yrs, y=cum_anchor,
        name="Anchor margin contributed",
        line=dict(color=C_C, width=2.5),
        hovertemplate="%{x}: %{y:$,.0f}<extra>Anchor margin</extra>",
    ))
    fig.update_layout(
        title="Cumulative Expansion Cost vs Anchor Contribution (2027–2035)",
        xaxis=dict(title="Year", tickmode="linear", tick0=expansion_yr, dtick=1),
        yaxis=dict(title="Cumulative $", tickformat="$,.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320,
        margin=dict(t=70, b=40, l=80, r=40),
    )
    return fig


def chart_household_bills(scenarios, base_rate, hh_kwh):
    """Grouped bar: annual household bill by year, three scenarios."""
    display_yrs = [2023, 2025, 2027, 2029, 2031, 2033, 2035]
    fig = go.Figure()
    for key in ["A", "B", "C"]:
        df = scenarios[key]
        bills = [df.loc[y, "rate_kwh"] * hh_kwh for y in display_yrs]
        fig.add_trace(go.Bar(
            name=SCENARIO_LABELS[key],
            x=[str(y) for y in display_yrs],
            y=bills,
            marker_color=SCENARIO_COLORS[key],
            text=[f"${b:,.0f}" for b in bills],
            textposition="outside",
        ))
    # Reference line: today's bill
    today_bill = base_rate * hh_kwh
    fig.add_hline(
        y=today_bill, line_dash="dot", line_color=C_REF,
        annotation_text=f"2023 bill: ${today_bill:,.0f}",
        annotation_position="top left",
        annotation_font_color=C_REF,
    )
    fig.update_layout(
        barmode="group",
        title=f"Annual Household Bill ({hh_kwh:,} kWh/yr)",
        yaxis_title="$/year",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(t=70, b=40, r=40),
    )
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# 6. SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> dict:
    """All sidebar widgets. Returns a complete params dict for compute_scenarios."""

    st.sidebar.title("⚡ Model Parameters")
    st.sidebar.caption(
        "Wrangell defaults sourced from **EIA-861 2023**, **EIA-860 2025**, "
        "and **SEAPA public sources**. SEAPA wholesale rate back-calculated "
        "from 2023 utility financials."
    )

    # ── Wrangell System ──────────────────────────────────────────────────────
    with st.sidebar.expander("Wrangell System (EIA actuals)", expanded=False):
        base_mwh = st.number_input(
            "2023 baseline load (MWh/yr)", 20_000, 80_000, 40_708, 500,
            help="DEFAULT SOURCE: EIA-861 2023 Short Form, utility 21015 — 40,708 MWh/yr "
                 "sold to Wrangell customers.\n\n"
                 "MODEL EFFECT: Starting point for all load projections. Higher values increase "
                 "future demand in every year, accelerate diesel reliance under Status Quo, "
                 "and raise rates in every scenario.",
        )
        seapa_cap = st.number_input(
            "Current SEAPA energy cap (MWh/yr)", 20_000, 60_000, 40_200, 500,
            help="DEFAULT SOURCE: Back-calculated from observed diesel usage — "
                 "40,708 total minus 508 diesel = 40,200 MWh hydro.\n\n"
                 "MODEL EFFECT: Ceiling of cheap hydropower. Any demand above this cap is "
                 "served by diesel. Lowering it accelerates diesel dependency; raising it delays it.",
        )
        seapa_rate = st.number_input(
            "SEAPA wholesale rate ($/MWh)", 50.0, 150.0, 93.0, 1.0,
            help="DEFAULT SOURCE: Back-calculated from 2023 EIA-861 revenue — "
                 "(revenue - fixed - diesel cost) / hydro MWh = ~$93/MWh. "
                 "Not a published tariff.\n\n"
                 "MODEL EFFECT: Cost of every hydro MWh. Directly scales total system cost. "
                 "Also sets the floor for anchor margin — the anchor only contributes to "
                 "expansion debt if its tariff exceeds this rate.",
        )
        fixed_cost = st.number_input(
            "Wrangell Electric fixed costs ($/yr)", 500_000, 5_000_000, 1_200_000, 50_000,
            help="DEFAULT SOURCE: Estimate — 5 FT staff + infrastructure overhead for "
                 "Wrangell Municipal Light & Power. Pending audit confirmation.\n\n"
                 "MODEL EFFECT: Flat annual cost added to every scenario in every year. "
                 "Higher fixed costs raise the baseline retail rate equally across all scenarios. "
                 "Does not interact with diesel/hydro dispatch.",
        )
        diesel_base = st.number_input(
            "Diesel all-in cost ($/MWh)", 80.0, 300.0, 150.0, 5.0,
            help="DEFAULT SOURCE: Fully-loaded estimate including remote fuel delivery, "
                 "O&M, and air permit management for Wrangell's location.\n\n"
                 "MODEL EFFECT: Year-zero diesel unit cost. Higher values widen the cost "
                 "penalty of the Status Quo and increase the savings from expansion.",
        )
        diesel_esc = st.slider(
            "Diesel cost escalation (%/yr)", 0.0, 6.0, 3.0, 0.5,
            help="DEFAULT SOURCE: Fuel price inflation assumption.\n\n"
                 "MODEL EFFECT: Compounds annually on the diesel base cost. At 3%/yr, diesel "
                 "cost roughly doubles over 24 years. Higher escalation makes the Status Quo "
                 "progressively worse and strengthens the case for expansion.",
        ) / 100
        diesel_floor = st.number_input(
            "Diesel operational floor (MWh/yr)", 0, 2_000, 200, 50,
            help="DEFAULT SOURCE: Minimum run hours for generator testing, maintenance, "
                 "and peak spikes.\n\n"
                 "MODEL EFFECT: Minimum diesel generation even when hydro capacity is ample. "
                 "Prevents Scenarios B and C from showing zero diesel. Small effect unless set high.",
        )

    # ── Load Growth ──────────────────────────────────────────────────────────
    with st.sidebar.expander("Load Growth Assumptions", expanded=False):
        st.caption(
            "Wrangell load grew **+19% in 4 years** (2019→2023) driven by "
            "oil-heat → heat pump conversion. ~75% oil heat in 2016 → ~50% in 2023."
        )
        r1 = st.slider(
            "Heat pump adoption growth (2023–2027, %/yr)",
            1.0, 10.0, 5.0, 0.5,
            help="DEFAULT SOURCE: Historical — Wrangell load grew +19% over 2019-2023 "
                 "(~4.5% CAGR) from oil-to-heat-pump conversion.\n\n"
                 "MODEL EFFECT: Compound growth during rapid adoption phase. Higher values "
                 "accelerate load, worsen Status Quo diesel reliance, and increase expansion urgency.",
        ) / 100
        phase1_end = st.selectbox("Phase 1 ends", [2026, 2027, 2028], index=1,
            help="DEFAULT SOURCE: Assumption — heat pump adoption saturates ~4 years out.\n\n"
                 "MODEL EFFECT: When growth transitions from fast rate to steady-state. "
                 "Later end years mean more years of fast growth, higher peak loads, "
                 "and more diesel in the Status Quo.",
        )
        r2 = st.slider(
            "Steady-state growth (post-Phase 1, %/yr)",
            0.5, 5.0, 2.0, 0.5,
            help="DEFAULT SOURCE: Post-saturation baseline growth assumption.\n\n"
                 "MODEL EFFECT: Long-term load trajectory. Even small changes compound "
                 "significantly over the 2028-2035 window.",
        ) / 100

    # ── Expansion Financing ──────────────────────────────────────────────────
    with st.sidebar.expander("SEAPA Expansion (3rd Turbine)", expanded=False):
        st.caption("SEAPA confirmed need for 3rd turbine at Tyee Lake. Target online: Dec 2027.")
        expansion_yr  = st.selectbox("Target online year", [2026, 2027, 2028, 2029], index=1,
            help="DEFAULT SOURCE: SEAPA confirmed target — December 2027.\n\n"
                 "MODEL EFFECT: When new hydro capacity and anchor load come online. "
                 "Delaying extends the period of diesel reliance (higher Status Quo costs) "
                 "and shifts all expansion/anchor benefits later.",
        )
        expansion_new = st.number_input(
            "New SEAPA energy for Wrangell (MWh/yr)", 10_000, 60_000, 37_000, 1_000,
            help="DEFAULT SOURCE: Calculated — 5 MW x 8,760 hr x 0.845 CF = ~37,000 MWh "
                 "(Wrangell's share of the 3rd turbine).\n\n"
                 "MODEL EFFECT: Additional hydro capacity from expansion. Must exceed "
                 "community load growth + anchor demand to eliminate structural diesel use.",
        )
        capex = st.number_input(
            "Total expansion capex ($)", 10_000_000, 50_000_000, 20_000_000, 500_000,
            help="DEFAULT SOURCE: SEAPA 3rd turbine engineering estimate (~$20M).\n\n"
                 "MODEL EFFECT: Flows through the PMT formula to annual debt service. "
                 "Higher capex means larger debt payments that ratepayers (or the anchor) must cover.",
        )
        w_share = st.slider(
            "Wrangell's share of SEAPA debt (%)", 20, 60, 40, 5,
            help="DEFAULT SOURCE: Proportional to Wrangell's load vs total SEAPA membership "
                 "(estimate).\n\n"
                 "MODEL EFFECT: Fraction of total capex that Wrangell finances. "
                 "At 40% of $20M, Wrangell finances $8M principal.",
        ) / 100
        fin_rate = st.slider("Financing rate (%)", 3.0, 8.0, 5.0, 0.25,
            help="DEFAULT SOURCE: Municipal bond rate assumption.\n\n"
                 "MODEL EFFECT: Interest rate on expansion debt. Higher rates increase "
                 "annual debt service payments, making anchor coverage more critical "
                 "and raising Scenario B rates.",
        ) / 100
        fin_term = st.radio("Bond term (years)", [20, 25, 30], index=1, horizontal=True,
            help="DEFAULT SOURCE: Standard municipal bond terms.\n\n"
                 "MODEL EFFECT: Longer terms reduce annual payments but increase total "
                 "interest paid over the life of the bond.",
        )
        debt_svc = annual_debt_service(capex, w_share, fin_rate, fin_term)
        st.metric("Wrangell annual debt service", f"${debt_svc:,.0f}/yr",
                  help="This is what Wrangell ratepayers must cover absent an anchor.")

    # ── Anchor Customer ──────────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏭 Greensparc Anchor Customer")
    st.sidebar.caption("Scenario C only. Anchor comes online with the expansion (same year).")

    anchor_mw = st.sidebar.slider(
        "Anchor nameplate load (MW)", 0.5, 5.0, 2.0, 0.1,
        help="DEFAULT SOURCE: Greensparc data-center sizing assumption.\n\n"
             "MODEL EFFECT: Combined with capacity factor, determines annual anchor "
             "energy demand and revenue. Larger anchors generate more tariff revenue "
             "but consume more of the new hydro capacity.",
    )
    anchor_cf = st.sidebar.slider(
        "Anchor capacity factor", 0.70, 0.99, 0.90, 0.01,
        help="DEFAULT SOURCE: Data center industry typical — 0.85 to 0.95.\n\n"
             "MODEL EFFECT: Fraction of time at full load. Nameplate x CF x 8,760 = "
             "annual MWh. Higher CF means more energy consumed and more tariff revenue generated.",
    )
    anchor_mwh_yr = anchor_mw * anchor_cf * 8_760
    st.sidebar.caption(f"→ **{anchor_mwh_yr:,.0f} MWh/yr** ({anchor_mw:.1f} MW avg effective load)")

    anchor_tariff_kwh = st.sidebar.number_input(
        "Anchor tariff ($/kWh)", 0.07, 0.20, 0.12, 0.005, format="%.3f",
        help="DEFAULT SOURCE: Proposed rate — above SEAPA cost ($0.093/kWh) but below "
             "current retail ($0.123/kWh).\n\n"
             "MODEL EFFECT: MOST SENSITIVE LEVER in the model. The margin above SEAPA cost "
             "(tariff - $0.093) x anchor MWh = annual debt coverage. Small changes swing "
             "Scenario C from partial debt coverage to full coverage with surplus. "
             "Determines whether community rates end up above or below today's level.",
    )
    anchor_tariff_mwh = anchor_tariff_kwh * 1_000

    # Live coverage callout
    cov = anchor_capex_coverage(anchor_mwh_yr, anchor_tariff_mwh, seapa_rate, debt_svc)
    margin_yr = anchor_mwh_yr * (anchor_tariff_mwh - seapa_rate)
    if cov >= 0.90:
        st.sidebar.success(
            f"Anchor covers **{min(cov, 1.0):.0%}** of Wrangell's expansion debt "
            f"(**{fmt_dollar_md(margin_yr)}/yr margin**)"
            + ("  \n⭐ Surplus → rate reduction" if cov > 1.0 else "")
        )
    elif cov >= 0.50:
        st.sidebar.warning(
            f"Anchor covers **{cov:.0%}** of debt service (**{fmt_dollar_md(margin_yr)}/yr**). "
            f"Ratepayers absorb **{fmt_dollar_md(max(0, debt_svc - margin_yr))}/yr**."
        )
    else:
        st.sidebar.error(
            f"Anchor covers only **{cov:.0%}** of debt service. "
            f"Consider higher tariff or larger anchor load."
        )
    if anchor_tariff_mwh < seapa_rate:
        st.sidebar.error("⚠️ Tariff is below SEAPA cost — not financially viable for the utility.")

    # ── Community baseline ────────────────────────────────────────────────────
    with st.sidebar.expander("Community Baseline", expanded=False):
        n_hh    = st.number_input("Residential accounts", 500, 3_000, 1_174, 50,
            help="DEFAULT SOURCE: EIA-861 2023 customer count.\n\n"
                 "MODEL EFFECT: Display only — scales per-household savings and "
                 "community-wide totals. Does not affect rates or system economics.",
        )
        hh_kwh  = st.number_input("Avg household kWh/yr", 3_000, 20_000, 9_000, 500,
            help="DEFAULT SOURCE: Estimate for Wrangell residential usage.\n\n"
                 "MODEL EFFECT: Converts $/kWh rates into annual dollar bills per household. "
                 "Display only — does not affect system-level economics.",
        )
        econ_mult = st.slider("Local spending multiplier", 1.0, 2.5, 1.7, 0.1,
            help="DEFAULT SOURCE: Standard rural economic multiplier assumption.\n\n"
                 "MODEL EFFECT: Display only — scales economic impact estimates on the "
                 "Community Impact tab. Does not affect rates or energy dispatch.",
        )
        jobs_per_mw = st.slider("Data center jobs per MW (operating)", 0.5, 5.0, 1.5, 0.5,
            help="DEFAULT SOURCE: Industry estimate for operating data centers.\n\n"
                 "MODEL EFFECT: Display only — multiplied by anchor MW to estimate ongoing "
                 "jobs on the Community Impact tab. Does not affect financial model.",
        )

    base_rate = (fixed_cost + seapa_rate * seapa_cap + diesel_base * 500) / (base_mwh * 1_000)
    # Use actual 2023 observed rate directly (more reliable than back-calc)
    base_rate = 0.1232   # EIA-861 2023: $5,010,000 / 40,708,000 kWh

    return dict(
        base_mwh=base_mwh, r1=r1, phase1_end=phase1_end, r2=r2,
        seapa_cap=seapa_cap, seapa_rate=seapa_rate,
        expansion_yr=expansion_yr, expansion_new_mwh=expansion_new,
        diesel_floor=diesel_floor, diesel_base_cost=diesel_base, diesel_escalation=diesel_esc,
        fixed_cost=fixed_cost,
        debt_service_yr=debt_svc,
        anchor_mwh_yr=anchor_mwh_yr, anchor_tariff_mwh=anchor_tariff_mwh,
        anchor_mw=anchor_mw, anchor_cf=anchor_cf, anchor_tariff_kwh=anchor_tariff_kwh,
        n_hh=n_hh, hh_kwh=hh_kwh, econ_mult=econ_mult, jobs_per_mw=jobs_per_mw,
        base_rate=base_rate,
        capex=capex, w_share=w_share,
        anchor_coverage=cov, anchor_margin_yr=margin_yr,
    )


# ═════════════════════════════════════════════════════════════════════════════
# 7. MAIN UI
# ═════════════════════════════════════════════════════════════════════════════

def main():
    params = render_sidebar()

    # ── Run model ────────────────────────────────────────────────────────────
    scenarios = compute_scenarios(
        base_mwh          = params["base_mwh"],
        r1                = params["r1"],
        phase1_end        = params["phase1_end"],
        r2                = params["r2"],
        seapa_cap         = params["seapa_cap"],
        seapa_rate        = params["seapa_rate"],
        expansion_year    = params["expansion_yr"],
        expansion_new_mwh = params["expansion_new_mwh"],
        diesel_floor      = params["diesel_floor"],
        diesel_base_cost  = params["diesel_base_cost"],
        diesel_escalation = params["diesel_escalation"],
        fixed_cost        = params["fixed_cost"],
        debt_service_yr   = params["debt_service_yr"],
        anchor_mwh_yr     = params["anchor_mwh_yr"],
        anchor_tariff_mwh = params["anchor_tariff_mwh"],
    )

    # Shorthand lookups
    base_rate    = params["base_rate"]
    expansion_yr = params["expansion_yr"]
    hh_kwh       = params["hh_kwh"]
    n_hh         = params["n_hh"]

    def rate(sc, yr): return scenarios[sc].loc[yr, "rate_kwh"]
    def bill(sc, yr): return rate(sc, yr) * hh_kwh

    # ── Header ───────────────────────────────────────────────────────────────
    st.title("Wrangell, Alaska: The Anchor Customer Expansion Case")
    st.markdown(
        "**SEAPA's Tyee Lake hydro is maxed out.** Wrangell's load grew +19% in four years "
        "from heat pump adoption and has no more cheap hydro headroom. The fix — a third "
        "turbine — costs ~$20M. A Greensparc data-center anchor customer can make that "
        "expansion financeable while driving community rates **below today's level**."
    )

    # ── 2030 rate outlook cards ──────────────────────────────────────────────
    st.markdown("#### 2030 Rate Outlook by Scenario")
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🔴 Status Quo",
        f"${rate('A',2030):.4f}/kWh",
        delta=f"{(rate('A',2030)-base_rate)*100:+.2f}¢ vs today",
        delta_color="inverse",
    )
    c2.metric(
        "🟡 Expansion Only",
        f"${rate('B',2030):.4f}/kWh",
        delta=f"{(rate('B',2030)-base_rate)*100:+.2f}¢ vs today",
        delta_color="inverse",
    )
    c3.metric(
        "🟢 Expansion + Anchor",
        f"${rate('C',2030):.4f}/kWh",
        delta=f"{(rate('C',2030)-base_rate)*100:+.2f}¢ vs today",
        delta_color="inverse",
    )

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Rate Trajectory",
        "💧 Diesel Displacement",
        "🏗️ Expansion Viability",
        "🏘️ Community Impact",
    ])

    # ── TAB 1: Rate Trajectory ───────────────────────────────────────────────
    with tab1:
        st.subheader("Retail Rate Trajectory — 2023 to 2035")
        st.plotly_chart(
            chart_rate_trajectory(scenarios, base_rate, expansion_yr),
            use_container_width=True,
        )

        # Per-scenario metric row
        m1, m2, m3 = st.columns(3)
        for col, key in zip([m1, m2, m3], ["A", "B", "C"]):
            r30 = rate(key, 2030)
            r35 = rate(key, 2035)
            col.metric(
                SCENARIO_LABELS[key] + " — 2030",
                f"${r30:.4f}/kWh",
                delta=f"{(r30-base_rate)*100:+.2f}¢ vs today",
                delta_color="inverse",
            )
            col.metric(
                SCENARIO_LABELS[key] + " — 2035",
                f"${r35:.4f}/kWh",
                delta=f"{(r35-base_rate)*100:+.2f}¢ vs today",
                delta_color="inverse",
            )

        # Data table
        with st.expander("Full rate table ($/kWh)"):
            tbl = pd.DataFrame({
                "Year": YEARS,
                "Status Quo": [rate("A", y) for y in YEARS],
                "Expansion Only": [rate("B", y) for y in YEARS],
                "Expansion + Anchor": [rate("C", y) for y in YEARS],
            }).set_index("Year")
            st.dataframe(tbl.style.format("${:.4f}"), use_container_width=True)

        st.markdown("#### Narrative")
        st.info(narr_rate(scenarios, params, target_yr=2030))

    # ── TAB 2: Diesel Displacement ───────────────────────────────────────────
    with tab2:
        st.subheader("Diesel Backup Usage Trajectory")
        st.plotly_chart(chart_diesel_lines(scenarios, expansion_yr), use_container_width=True)

        st.subheader("Annual Diesel Cost")
        st.plotly_chart(chart_diesel_cost_bars(scenarios), use_container_width=True)

        st.subheader("Energy Mix by Scenario")
        st.plotly_chart(chart_energy_stacks(scenarios, expansion_yr), use_container_width=True)

        # Aggregate displacement metrics
        total_a   = scenarios["A"]["diesel_mwh"].sum()
        total_c   = scenarios["C"]["diesel_mwh"].sum()
        avoided   = total_a - total_c
        cost_a    = scenarios["A"]["diesel_cost"].sum()
        cost_c    = scenarios["C"]["diesel_cost"].sum()
        cost_sav  = cost_a - cost_c
        co2       = avoided * 0.7
        bbls      = avoided / 0.01709

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Total diesel avoided (C vs A)", f"{avoided:,.0f} MWh")
        d2.metric("Diesel cost savings (C vs A)",  fmt_dollar(cost_sav))
        d3.metric("CO₂ avoided",                   f"{co2:,.0f} tonnes")
        d4.metric("Barrels of diesel avoided",     f"{bbls:,.0f} bbl")

        st.markdown("#### Narrative")
        st.info(narr_diesel(scenarios, params))

    # ── TAB 3: Expansion Viability ───────────────────────────────────────────
    with tab3:
        cov        = params["anchor_coverage"]
        margin_yr  = params["anchor_margin_yr"]
        debt_svc   = params["debt_service_yr"]

        # Big coverage number
        cov_display = min(cov, 1.0)
        color = C_C if cov >= 0.75 else (C_B if cov >= 0.50 else C_A)
        st.markdown(
            f"<div style='text-align:center; padding:12px 0 4px 0;'>"
            f"<div style='font-size:13px; color:#6b7280; font-weight:600; text-transform:uppercase; "
            f"letter-spacing:0.08em;'>Anchor covers</div>"
            f"<div style='font-size:80px; font-weight:800; color:{color}; line-height:1.1;'>"
            f"{cov_display:.0%}</div>"
            f"<div style='font-size:15px; color:#374151;'>"
            f"of Wrangell's <b>{fmt_dollar(debt_svc)}/year</b> expansion debt share"
            + (" — <b style='color:" + C_C + "'>over-covers, surplus lowers rates</b>" if cov > 1.0 else "") +
            f"</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("")  # spacer

        col_l, col_r = st.columns(2)
        with col_l:
            st.plotly_chart(
                chart_expansion_waterfall(debt_svc, margin_yr),
                use_container_width=True,
            )
        with col_r:
            st.plotly_chart(
                chart_cumulative_coverage(debt_svc, margin_yr, expansion_yr),
                use_container_width=True,
            )

        # Key numbers breakdown
        st.markdown("#### Expansion Finance Breakdown")
        fin_df = pd.DataFrame({
            "Item": [
                "Total expansion capex",
                "Wrangell's share",
                "Financing rate / term",
                "Annual debt service (Wrangell)",
                "Anchor annual gross revenue",
                "SEAPA cost to serve anchor",
                "Anchor margin above SEAPA cost",
                "Debt service covered by anchor",
                "Residual on Wrangell ratepayers",
            ],
            "Value": [
                fmt_dollar(params["capex"]),
                f"{params['w_share']:.0%}",
                f"{params['debt_service_yr'] / (params['capex'] * params['w_share']):.1%} / {int(round(debt_svc / (params['capex'] * params['w_share'] * 0.05 * 1.05**25 / (1.05**25-1)) * 25))} yrs",
                fmt_dollar(debt_svc),
                fmt_dollar(params["anchor_mwh_yr"] * params["anchor_tariff_mwh"]),
                fmt_dollar(params["anchor_mwh_yr"] * params["seapa_rate"]),
                fmt_dollar(margin_yr),
                f"{min(cov, 1.0):.0%}  ({fmt_dollar(min(margin_yr, debt_svc))})",
                fmt_dollar(max(0.0, debt_svc - margin_yr)),
            ]
        }).set_index("Item")
        st.dataframe(fin_df, use_container_width=True)

        st.markdown("#### Narrative")
        st.info(narr_viability(cov, margin_yr, debt_svc, params["anchor_mw"]))

    # ── TAB 4: Community Impact ──────────────────────────────────────────────
    with tab4:
        st.subheader("Household Bill Impact")
        st.plotly_chart(
            chart_household_bills(scenarios, base_rate, hh_kwh),
            use_container_width=True,
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### Household Bill Comparison")
            today_bill = base_rate * hh_kwh
            hh_df = pd.DataFrame({
                "Year": [2023, 2027, 2030, 2035],
                "Status Quo": [bill("A", y) for y in [2023, 2027, 2030, 2035]],
                "Expansion Only": [bill("B", y) for y in [2023, 2027, 2030, 2035]],
                "Expansion + Anchor": [bill("C", y) for y in [2023, 2027, 2030, 2035]],
            }).set_index("Year")
            st.dataframe(hh_df.style.format("${:,.0f}"), use_container_width=True)

            # Savings vs status quo
            st.markdown("**Annual savings vs Status Quo (Exp + Anchor)**")
            sav_df = pd.DataFrame({
                "Year": [2027, 2030, 2035],
                "Savings / household": [
                    bill("A", y) - bill("C", y) for y in [2027, 2030, 2035]
                ],
                "Community-wide savings": [
                    (bill("A", y) - bill("C", y)) * n_hh for y in [2027, 2030, 2035]
                ],
            }).set_index("Year")
            st.dataframe(
                sav_df.style.format({"Savings / household": "${:,.0f}",
                                      "Community-wide savings": "${:,.0f}"}),
                use_container_width=True,
            )

        with col_b:
            st.markdown("#### Anchor Customer Economic Impact")
            anchor_mw     = params["anchor_mw"]
            jobs_op       = anchor_mw * params["jobs_per_mw"]
            jobs_constr   = anchor_mw * 6          # rough construction jobs/MW
            payroll_op    = jobs_op * 75_000
            payroll_con   = jobs_constr * 65_000
            local_econ    = (payroll_op + payroll_con) * params["econ_mult"]
            annual_tariff = params["anchor_mwh_yr"] * params["anchor_tariff_mwh"]

            econ_df = pd.DataFrame({
                "Metric": [
                    "Anchor nameplate load",
                    "Construction jobs (est.)",
                    "Ongoing operating jobs (est.)",
                    "Annual operating payroll",
                    "Total local economic activity",
                    "Annual anchor tariff revenue",
                    "Anchor margin above SEAPA cost",
                ],
                "Value": [
                    f"{anchor_mw:.1f} MW",
                    f"{jobs_constr:.0f}",
                    f"{jobs_op:.1f}",
                    fmt_dollar(payroll_op) + "/yr",
                    fmt_dollar(local_econ) + "/yr",
                    fmt_dollar(annual_tariff) + "/yr",
                    fmt_dollar(params["anchor_margin_yr"]) + "/yr",
                ]
            }).set_index("Metric")
            st.dataframe(econ_df, use_container_width=True)
            st.caption(f"Local spending multiplier: {params['econ_mult']:.1f}×")

        st.markdown("#### Narrative")
        st.info(narr_community(scenarios, params, n_hh, hh_kwh))

    # ── Footer ───────────────────────────────────────────────────────────────
    st.divider()
    st.caption(
        "**Model caveats:** Illustrative projections — not a rate-case or regulatory filing. "
        "SEAPA wholesale rate (\\$93/MWh) is back-calculated from 2023 EIA-861 actuals, not a published tariff. "
        "Wrangell's 40% SEAPA debt share is proportional-load estimate; actual contract terms differ. "
        "Diesel costs use fully-loaded estimates including remote fuel delivery; actual costs may vary. "
        "Two-phase load growth is assumption-based; actual heat pump adoption may differ. "
        "Fixed costs (~\\$1.2M/yr) are estimates pending Wrangell Electric audit confirmation. "
        "Data sources: EIA-861 2023, EIA-860 2025, SEAPA public sources, Ketchikan Daily News/Frontier Media (2024)."
    )


if __name__ == "__main__":
    main()
