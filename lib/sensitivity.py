# ─────────────────────────────────────────────────────────────────────────────
# Sensitivity analysis — tornado chart and confidence bands
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from lib.config import YEARS, C_A, C_B, C_C, C_REF
from lib.model import compute_scenarios
from lib.financial import annual_debt_service


# Parameters to perturb and their display names
SENSITIVITY_PARAMS = [
    ("anchor_tariff_kwh", "Anchor tariff", 0.25),
    ("anchor_mw", "Anchor size (MW)", 0.25),
    ("diesel_base_cost", "Diesel base cost", 0.25),
    ("diesel_escalation", "Diesel escalation", 0.50),
    ("seapa_rate", "SEAPA wholesale rate", 0.20),
    ("r1", "Phase 1 growth rate", 0.30),
    ("expansion_new_mwh", "New SEAPA energy", 0.25),
    ("fixed_cost", "Fixed costs", 0.25),
]


def _build_compute_args(params, anchor_mw_override=None, anchor_tariff_override=None):
    """Build keyword args for compute_scenarios from params dict."""
    mw = anchor_mw_override if anchor_mw_override is not None else params["anchor_mw"]
    cf = params["anchor_cf"]
    tariff_kwh = anchor_tariff_override if anchor_tariff_override is not None else params["anchor_tariff_kwh"]

    return dict(
        base_mwh=params["base_mwh"], r1=params["r1"],
        phase1_end=params["phase1_end"], r2=params["r2"],
        seapa_cap=params["seapa_cap"], seapa_rate=params["seapa_rate"],
        expansion_year=params["expansion_yr"],
        expansion_new_mwh=params["expansion_new_mwh"],
        diesel_floor=params["diesel_floor"],
        diesel_base_cost=params["diesel_base_cost"],
        diesel_escalation=params["diesel_escalation"],
        fixed_cost=params["fixed_cost"],
        debt_service_yr=params["debt_service_yr"],
        anchor_mwh_yr=mw * cf * 8_760,
        anchor_tariff_mwh=tariff_kwh * 1_000,
    )


@st.cache_data
def run_sensitivity(
    base_mwh, r1, phase1_end, r2,
    seapa_cap, seapa_rate,
    expansion_yr, expansion_new_mwh,
    diesel_floor, diesel_base_cost, diesel_escalation,
    fixed_cost, debt_service_yr,
    anchor_mw, anchor_cf, anchor_tariff_kwh,
    target_year=2035,
):
    """
    Perturb each key parameter by +/- a fraction. Measure Scenario C rate at target_year.
    Returns DataFrame sorted by swing (descending).
    """
    # Build base params dict for helper
    params = dict(
        base_mwh=base_mwh, r1=r1, phase1_end=phase1_end, r2=r2,
        seapa_cap=seapa_cap, seapa_rate=seapa_rate,
        expansion_yr=expansion_yr, expansion_new_mwh=expansion_new_mwh,
        diesel_floor=diesel_floor, diesel_base_cost=diesel_base_cost,
        diesel_escalation=diesel_escalation, fixed_cost=fixed_cost,
        debt_service_yr=debt_service_yr,
        anchor_mw=anchor_mw, anchor_cf=anchor_cf,
        anchor_tariff_kwh=anchor_tariff_kwh,
    )

    # Base case rate
    base_args = _build_compute_args(params)
    base_sc = compute_scenarios(**base_args)
    base_rate = base_sc["C"].loc[target_year, "rate_kwh"]

    rows = []
    for param_key, display_name, pct in SENSITIVITY_PARAMS:
        for direction in ["low", "high"]:
            mult = (1 - pct) if direction == "low" else (1 + pct)
            tweaked = dict(params)
            tweaked[param_key] = params[param_key] * mult

            # Recompute derived values if needed
            if param_key in ("anchor_mw", "anchor_tariff_kwh"):
                args = _build_compute_args(
                    tweaked,
                    anchor_mw_override=tweaked["anchor_mw"],
                    anchor_tariff_override=tweaked["anchor_tariff_kwh"],
                )
            else:
                args = _build_compute_args(tweaked)

            sc = compute_scenarios(**args)
            rate_val = sc["C"].loc[target_year, "rate_kwh"]

            rows.append(dict(
                parameter=display_name,
                direction=direction,
                param_value=tweaked[param_key],
                rate=rate_val,
            ))

    df = pd.DataFrame(rows)

    # Pivot to get low/high per parameter
    result = []
    for param_name in df["parameter"].unique():
        sub = df[df["parameter"] == param_name]
        low_rate = sub[sub["direction"] == "low"]["rate"].values[0]
        high_rate = sub[sub["direction"] == "high"]["rate"].values[0]
        swing = abs(high_rate - low_rate)
        result.append(dict(
            parameter=param_name,
            low_rate=low_rate,
            high_rate=high_rate,
            base_rate=base_rate,
            swing=swing,
        ))

    return pd.DataFrame(result).sort_values("swing", ascending=True)  # ascending for horizontal bar


def chart_tornado(sensitivity_df, base_rate):
    """Horizontal tornado chart showing parameter sensitivity."""
    fig = go.Figure()

    params = sensitivity_df["parameter"].tolist()
    low_deltas = [(r - base_rate) * 100 for r in sensitivity_df["low_rate"]]
    high_deltas = [(r - base_rate) * 100 for r in sensitivity_df["high_rate"]]

    # Low perturbation bars
    fig.add_trace(go.Bar(
        y=params,
        x=low_deltas,
        orientation="h",
        name="Parameter low",
        marker_color=C_C,
        hovertemplate="%{y}: %{x:+.2f}¢ from base<extra>Low</extra>",
    ))

    # High perturbation bars
    fig.add_trace(go.Bar(
        y=params,
        x=high_deltas,
        orientation="h",
        name="Parameter high",
        marker_color=C_A,
        hovertemplate="%{y}: %{x:+.2f}¢ from base<extra>High</extra>",
    ))

    # Base rate line
    fig.add_vline(x=0, line_dash="solid", line_color=C_REF, line_width=1.5)

    fig.update_layout(
        title=f"Sensitivity: Impact on Scenario C Rate (¢/kWh change from {base_rate*100:.2f}¢)",
        xaxis_title="Change in rate (¢/kWh)",
        barmode="overlay",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=max(320, 40 * len(params) + 120),
        margin=dict(t=80, b=40, l=180, r=40),
    )
    return fig
