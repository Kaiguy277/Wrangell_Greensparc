# ─────────────────────────────────────────────────────────────────────────────
# Cached data loaders
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data
def load_fuel_prices(fips: str = "0286380") -> pd.DataFrame:
    """Load heating fuel prices for a community."""
    df = pd.read_csv(DATA_DIR / "public_fuel_prices.csv")
    return df[(df["fips_code"] == fips) & (df["fuel_type"] == "heating_fuel")]


@st.cache_data
def load_monthly_generation(fips: str = "0286380") -> pd.DataFrame:
    """Load monthly generation from AEDG (diesel-only for Wrangell)."""
    df = pd.read_csv(DATA_DIR / "public_monthly_generation.csv")
    return df[df["fips_code"] == fips]


@st.cache_data
def load_yearly_generation(fips: str = "0286380") -> pd.DataFrame:
    """Load yearly generation from AEDG."""
    df = pd.read_csv(DATA_DIR / "public_yearly_generation.csv")
    return df[df["fips_code"] == fips]


@st.cache_data
def load_eia923_plant(plant_id: int = 95) -> pd.DataFrame:
    """Load EIA-923 monthly diesel generation for a specific plant."""
    df = pd.read_csv(DATA_DIR / "eia923_alaska_monthly.csv")
    return df[df["plant_id"] == plant_id]


@st.cache_data
def load_rates(fips: str = "0286380") -> pd.DataFrame:
    """Load historical electricity rates from AEDG."""
    df = pd.read_csv(DATA_DIR / "public_rates.csv")
    return df[df["fips_code"] == fips]


@st.cache_data
def load_communities() -> pd.DataFrame:
    """Load all 355 community records."""
    return pd.read_csv(DATA_DIR / "public_communities.csv")


@st.cache_data
def load_wrangell_actuals() -> dict:
    """
    Load actual historical data for Wrangell backtest.
    Returns dict with diesel generation actuals and historical rates.
    """
    # EIA-923: plant 95 monthly diesel, 2019-2024
    eia923 = pd.read_csv(DATA_DIR / "eia923_alaska_monthly.csv")
    wrangell_diesel_monthly = eia923[eia923["plant_id"] == 95].copy()

    # AEDG: yearly diesel generation (2001-2021)
    yearly = pd.read_csv(DATA_DIR / "public_yearly_generation.csv")
    wrangell_yearly = yearly[yearly["fips_code"] == "0286380"].copy()

    # Aggregate EIA-923 to annual diesel for 2019-2024
    diesel_annual_eia = (
        wrangell_diesel_monthly
        .groupby("year")["net_gen_mwh"]
        .sum()
        .reset_index()
        .rename(columns={"net_gen_mwh": "diesel_mwh"})
    )

    # AEDG annual diesel (only DFO type)
    aedg_diesel = wrangell_yearly[
        wrangell_yearly["fuel_type"].str.contains("Distillate|Fuel Oil", case=False, na=False)
    ].copy()
    if "service_area_generation_mwh" in aedg_diesel.columns:
        aedg_annual = (
            aedg_diesel
            .groupby("year")["service_area_generation_mwh"]
            .sum()
            .reset_index()
            .rename(columns={"service_area_generation_mwh": "diesel_mwh"})
        )
    else:
        aedg_annual = pd.DataFrame(columns=["year", "diesel_mwh"])

    # Merge: AEDG for pre-2019, EIA-923 for 2019+
    pre_2019 = aedg_annual[aedg_annual["year"] < 2019]
    combined_diesel = pd.concat([pre_2019, diesel_annual_eia], ignore_index=True).sort_values("year")

    # Historical rates from AEDG
    rates = pd.read_csv(DATA_DIR / "public_rates.csv")
    wrangell_rates = rates[rates["fips_code"] == "0286380"].copy()

    return {
        "diesel_annual": combined_diesel,
        "diesel_monthly_eia": wrangell_diesel_monthly,
        "rates": wrangell_rates,
        "eia861_2023": {"rate": 0.1232, "total_mwh": 40_708, "revenue": 5_010_000},
    }
