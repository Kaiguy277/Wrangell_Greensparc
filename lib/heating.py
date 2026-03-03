# ─────────────────────────────────────────────────────────────────────────────
# Total energy cost calculations (electricity + heating oil displacement)
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lib.config import YEARS, SCENARIO_LABELS, SCENARIO_COLORS, C_A, C_B, C_C, C_REF

BTU_PER_GAL = 138_500  # heating oil energy content
BTU_PER_KWH = 3_412    # electrical equivalent


@st.cache_data
def compute_heating_economics(
    hh_oil_gal: float,
    heating_oil_price: float,
    oil_escalation: float,
    heat_pump_cop: float,
    hp_conversion_rate: float,
    pct_oil_heat_2023: float,
    hh_kwh_base: float,
    scenario_rates: dict,
) -> dict:
    """
    For each scenario, compute total household energy cost trajectories.

    An oil-heated home pays: electricity + heating oil
    A heat-pump home pays: electricity + heating electricity (no oil)

    Returns dict keyed by scenario, each a DataFrame indexed by year.
    """
    # How much electricity a heat pump needs to replace the oil
    heating_kwh = hh_oil_gal * BTU_PER_GAL / (heat_pump_cop * BTU_PER_KWH)

    results = {}
    for scenario_key, rates in scenario_rates.items():
        rows = []
        for i, year in enumerate(YEARS):
            yrs = year - YEARS[0]
            oil_price = heating_oil_price * (1 + oil_escalation) ** yrs

            # Conversion trajectory: exponential decay of oil-heated fraction
            remaining_oil = pct_oil_heat_2023 * (1 - hp_conversion_rate) ** yrs
            pct_hp = 1.0 - remaining_oil

            rate = rates[i]

            # Oil home: base electricity + full oil heating
            oil_elec_cost = hh_kwh_base * rate
            oil_heating_cost = hh_oil_gal * oil_price
            oil_home_total = oil_elec_cost + oil_heating_cost

            # HP home: base electricity + heating electricity, no oil
            hp_elec_cost = (hh_kwh_base + heating_kwh) * rate
            hp_home_total = hp_elec_cost  # no oil cost

            # Community weighted average
            avg_total = remaining_oil * oil_home_total + pct_hp * hp_home_total

            rows.append(dict(
                year=year,
                pct_oil=remaining_oil,
                pct_hp=pct_hp,
                oil_price=oil_price,
                oil_home_total=oil_home_total,
                oil_elec_cost=oil_elec_cost,
                oil_heating_cost=oil_heating_cost,
                hp_home_total=hp_home_total,
                hp_elec_cost=hp_elec_cost,
                heating_kwh=heating_kwh,
                avg_total_energy_cost=avg_total,
                hp_savings_vs_oil=oil_home_total - hp_home_total,
            ))
        results[scenario_key] = pd.DataFrame(rows).set_index("year")
    return results


def chart_total_energy_cost(heating_data: dict, base_oil_total: float):
    """Line chart: average total household energy cost by scenario."""
    fig = go.Figure()

    fig.add_hline(
        y=base_oil_total, line_dash="dot", line_color=C_REF, line_width=1.5,
        annotation_text=f"2023 oil-heated home: ${base_oil_total:,.0f}/yr",
        annotation_position="bottom right",
        annotation_font_color=C_REF,
    )

    widths = {"A": 2, "B": 2, "C": 3}
    dashes = {"A": "dash", "B": "solid", "C": "solid"}

    for key in ["C", "B", "A"]:
        df = heating_data[key]
        fig.add_trace(go.Scatter(
            x=YEARS,
            y=df["avg_total_energy_cost"].tolist(),
            mode="lines+markers",
            name=SCENARIO_LABELS[key],
            line=dict(color=SCENARIO_COLORS[key], dash=dashes[key], width=widths[key]),
            marker=dict(size=6 if key != "C" else 8),
            hovertemplate="%{x}: $%{y:,.0f}/yr<extra>" + SCENARIO_LABELS[key] + "</extra>",
        ))

    fig.update_layout(
        title="Average Total Household Energy Cost (Electricity + Heating)",
        xaxis=dict(title="Year", tickmode="linear", tick0=2023, dtick=1, tickangle=-45),
        yaxis=dict(title="$/year per household", tickformat="$,.0f"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=440,
        margin=dict(t=80, b=60, l=80, r=40),
    )
    return fig


def chart_oil_vs_hp_breakdown(heating_data: dict, scenario_key: str = "C"):
    """Side-by-side stacked bars: oil home vs HP home cost breakdown for key years."""
    display_yrs = [2023, 2025, 2027, 2030, 2035]
    df = heating_data[scenario_key]

    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True,
        subplot_titles=["Oil-Heated Home", "Heat Pump Home"],
        horizontal_spacing=0.05,
    )

    # Oil home: electricity (blue) + heating oil (orange)
    oil_elec = [df.loc[y, "oil_elec_cost"] for y in display_yrs]
    oil_heat = [df.loc[y, "oil_heating_cost"] for y in display_yrs]
    fig.add_trace(go.Bar(
        name="Electricity", x=[str(y) for y in display_yrs], y=oil_elec,
        marker_color="rgba(37,99,235,0.8)", showlegend=True,
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        name="Heating Oil", x=[str(y) for y in display_yrs], y=oil_heat,
        marker_color="rgba(249,115,22,0.8)", showlegend=True,
    ), row=1, col=1)

    # HP home: base electricity (blue) + heating electricity (teal)
    hp_base = [df.loc[y, "oil_elec_cost"] for y in display_yrs]  # same base usage
    hp_heat_elec = [df.loc[y, "hp_elec_cost"] - df.loc[y, "oil_elec_cost"] for y in display_yrs]
    fig.add_trace(go.Bar(
        name="Base Electricity", x=[str(y) for y in display_yrs], y=hp_base,
        marker_color="rgba(37,99,235,0.8)", showlegend=False,
    ), row=1, col=2)
    fig.add_trace(go.Bar(
        name="Heating Electricity", x=[str(y) for y in display_yrs], y=hp_heat_elec,
        marker_color="rgba(20,184,166,0.8)", showlegend=True,
    ), row=1, col=2)

    fig.update_layout(
        barmode="stack",
        title=f"Cost Breakdown — {SCENARIO_LABELS[scenario_key]}",
        yaxis_title="$/year",
        legend=dict(orientation="h", yanchor="bottom", y=1.08, xanchor="right", x=1),
        height=380,
        margin=dict(t=100, b=40, r=40),
    )
    return fig


def chart_hp_savings(heating_data: dict):
    """Line chart: annual savings from switching to heat pump vs staying on oil."""
    fig = go.Figure()

    widths = {"A": 2, "B": 2, "C": 3}
    dashes = {"A": "dash", "B": "solid", "C": "solid"}

    for key in ["C", "B", "A"]:
        df = heating_data[key]
        fig.add_trace(go.Scatter(
            x=YEARS,
            y=df["hp_savings_vs_oil"].tolist(),
            mode="lines+markers",
            name=SCENARIO_LABELS[key],
            line=dict(color=SCENARIO_COLORS[key], dash=dashes[key], width=widths[key]),
            marker=dict(size=6 if key != "C" else 8),
            hovertemplate="%{x}: $%{y:,.0f}/yr savings<extra>" + SCENARIO_LABELS[key] + "</extra>",
        ))

    fig.update_layout(
        title="Annual Savings: Heat Pump Home vs Oil-Heated Home",
        xaxis=dict(title="Year", tickmode="linear", tick0=2023, dtick=1, tickangle=-45),
        yaxis=dict(title="Savings ($/year)", tickformat="$,.0f"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=360,
        margin=dict(t=80, b=60, l=80, r=40),
    )
    return fig
