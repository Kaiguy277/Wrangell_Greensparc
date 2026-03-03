# ─────────────────────────────────────────────────────────────────────────────
# Dynamic narrative text generators
# ─────────────────────────────────────────────────────────────────────────────

from lib.financial import fmt_dollar_md, anchor_capex_coverage


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
