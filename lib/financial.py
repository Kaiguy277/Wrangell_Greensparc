# ─────────────────────────────────────────────────────────────────────────────
# Financial helper functions
# ─────────────────────────────────────────────────────────────────────────────


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
