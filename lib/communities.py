# ─────────────────────────────────────────────────────────────────────────────
# Multi-community support — config dicts for each supported community
# ─────────────────────────────────────────────────────────────────────────────

COMMUNITY_CONFIGS = {
    "wrangell": {
        "name": "Wrangell",
        "fips": "0286380",
        "eia_plant_id": 95,
        "eia_utility_id": 21015,
        "grid": "SEAPA Grid",
        "base_year": 2023,
        "description": (
            "SEAPA's Tyee Lake hydro is maxed out. Wrangell load is growing fast "
            "from heat pump adoption. The system needs a $20M 3rd turbine."
        ),
        "defaults": {
            "base_mwh": 40_708,
            "seapa_cap": 40_200,
            "seapa_rate": 93.0,
            "fixed_cost": 1_200_000,
            "diesel_base_cost": 150.0,
            "diesel_escalation": 0.03,
            "diesel_floor": 200,
            "r1": 0.05,
            "phase1_end": 2027,
            "r2": 0.02,
            "expansion_year": 2027,
            "expansion_new_mwh": 37_000,
            "capex": 20_000_000,
            "w_share": 0.40,
            "fin_rate": 0.05,
            "fin_term": 25,
            "n_hh": 1_174,
            "hh_kwh": 9_000,
            "base_rate": 0.1232,
            "anchor_mw": 2.0,
            "anchor_cf": 0.90,
            "anchor_tariff_kwh": 0.12,
            # Heating
            "hh_oil_gal": 800,
            "heating_oil_price": 5.00,
            "oil_escalation": 0.03,
            "heat_pump_cop": 2.5,
            "hp_conversion_rate": 0.05,
            "pct_oil_heat_2023": 0.50,
        },
        "load_shape": (1.20, 1.15, 1.10, 1.00, 0.90, 0.80,
                       0.80, 0.85, 0.95, 1.05, 1.10, 1.15),
        "hydro_shape": (0.70, 0.65, 0.75, 0.95, 1.20, 1.35,
                        1.35, 1.25, 1.05, 0.85, 0.75, 0.70),
    },
}


def get_community_names() -> dict:
    """Return {key: display_name} for all communities."""
    return {k: v["name"] for k, v in COMMUNITY_CONFIGS.items()}
