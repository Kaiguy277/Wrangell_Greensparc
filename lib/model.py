# ─────────────────────────────────────────────────────────────────────────────
# Core scenario computation — pure Python, no Streamlit dependency
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
import streamlit as st

from lib.config import YEARS


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


# ─────────────────────────────────────────────────────────────────────────────
# Monthly dispatch model — seasonal resolution
# ─────────────────────────────────────────────────────────────────────────────

# Default Wrangell shapes (derived from EIA-923 diesel seasonal pattern)
# Load peaks in winter (heating), troughs in summer
WRANGELL_LOAD_SHAPE = (1.20, 1.15, 1.10, 1.00, 0.90, 0.80,
                       0.80, 0.85, 0.95, 1.05, 1.10, 1.15)

# Hydro availability: spring/summer runoff high, winter low
WRANGELL_HYDRO_SHAPE = (0.70, 0.65, 0.75, 0.95, 1.20, 1.35,
                        1.35, 1.25, 1.05, 0.85, 0.75, 0.70)

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@st.cache_data
def compute_scenarios_monthly(
    base_mwh, r1, phase1_end, r2,
    seapa_cap, seapa_rate,
    expansion_year, expansion_new_mwh,
    diesel_floor, diesel_base_cost, diesel_escalation,
    fixed_cost, debt_service_yr,
    anchor_mwh_yr, anchor_tariff_mwh,
    load_shape=WRANGELL_LOAD_SHAPE,
    hydro_shape=WRANGELL_HYDRO_SHAPE,
) -> dict:
    """
    Monthly dispatch for all three scenarios.
    Returns dict keyed by scenario, each a DataFrame with (year, month) rows.
    """
    results = {}

    for scenario in ["A", "B", "C"]:
        has_expansion = scenario in ("B", "C")
        has_anchor = scenario == "C"

        rows = []
        for year in YEARS:
            yrs_from_base = year - 2023

            # Annual values
            annual_comm = _community_load(base_mwh, year, phase1_end, r1, r2)
            annual_cap = seapa_cap + (expansion_new_mwh if has_expansion and year >= expansion_year else 0)
            annual_anchor = anchor_mwh_yr if (has_anchor and year >= expansion_year) else 0.0
            diesel_rate = diesel_base_cost * (1 + diesel_escalation) ** yrs_from_base

            for m in range(12):
                # Monthly load: annual / 12, scaled by seasonal shape
                month_comm = annual_comm * load_shape[m] / 12
                month_anchor = annual_anchor / 12  # flat data center load
                month_total = month_comm + month_anchor

                # Monthly hydro cap: annual / 12, scaled by hydro availability
                month_cap = annual_cap * hydro_shape[m] / 12

                # Dispatch
                month_diesel = max(diesel_floor / 12, month_total - month_cap)
                month_hydro = month_total - month_diesel

                rows.append(dict(
                    year=year,
                    month=m + 1,
                    month_label=MONTH_LABELS[m],
                    community_mwh=month_comm,
                    anchor_mwh=month_anchor,
                    total_mwh=month_total,
                    hydro_cap=month_cap,
                    hydro_mwh=month_hydro,
                    diesel_mwh=month_diesel,
                    diesel_rate=diesel_rate,
                    diesel_cost=diesel_rate * month_diesel,
                ))

        results[scenario] = pd.DataFrame(rows)

    return results
