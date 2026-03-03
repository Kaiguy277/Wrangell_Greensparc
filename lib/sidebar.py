# ─────────────────────────────────────────────────────────────────────────────
# Sidebar widgets — returns complete params dict
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st

from lib.financial import annual_debt_service, anchor_capex_coverage, fmt_dollar_md
from lib.communities import COMMUNITY_CONFIGS, get_community_names


def render_sidebar() -> dict:
    """All sidebar widgets. Returns a complete params dict for compute_scenarios."""

    st.sidebar.title("⚡ Model Parameters")

    # ── Community selector ─────────────────────────────────────────────────
    community_names = get_community_names()
    community_key = st.sidebar.selectbox(
        "Community",
        list(community_names.keys()),
        format_func=lambda k: community_names[k],
    )
    config = COMMUNITY_CONFIGS[community_key]
    d = config["defaults"]  # shorthand for default values

    st.sidebar.caption(config["description"])

    # ── Quick Controls (always visible) ────────────────────────────────────
    st.sidebar.markdown("### Quick Controls")

    anchor_mw = st.sidebar.slider(
        "Anchor nameplate load (MW)", 0.5, 5.0, d["anchor_mw"], 0.1,
        help=(
            "The installed electrical capacity of the Greensparc data-center anchor customer.\n\n"
            "**Source:** Greensparc data-center sizing assumption.\n\n"
            "**Math:** `anchor_mwh = MW × CF × 8,760 hrs`. At 2.0 MW × 0.90 CF = 15,768 MWh/yr. "
            "Feeds into total system demand, anchor revenue, and capex coverage ratio.\n\n"
            "**Sensitivity:** HIGH — one of the top 2 levers. Larger anchors generate more "
            "revenue but consume more of the new hydro capacity."
        ),
    )
    anchor_tariff_kwh = st.sidebar.number_input(
        "Anchor tariff ($/kWh)", 0.07, 0.20, d["anchor_tariff_kwh"], 0.005, format="%.3f",
        help=(
            "The electricity rate charged to the anchor customer per kWh. The gap between this "
            "and the SEAPA wholesale cost is the margin that pays down expansion debt.\n\n"
            "**Source:** Proposed rate above SEAPA cost ($0.093) but below retail ($0.123).\n\n"
            "**Math:** `margin = anchor_mwh × (tariff − SEAPA rate)`. "
            "`coverage = margin / debt_service`. At $0.12/kWh the margin is $0.027/kWh × 15,768 MWh "
            "= ~$426K/yr toward expansion debt.\n\n"
            "**Sensitivity:** HIGHEST — the single most sensitive lever for Scenario C outcomes. "
            "Dominates the tornado chart. Every $0.01/kWh change swings coverage ~15 percentage points."
        ),
    )
    diesel_esc = st.sidebar.slider(
        "Diesel cost escalation (%/yr)", 0.0, 6.0, d["diesel_escalation"] * 100, 0.5,
        help=(
            "Annual rate at which diesel generation costs increase due to fuel price inflation.\n\n"
            "**Source:** Fuel price inflation assumption.\n\n"
            "**Math:** `diesel_rate = base_cost × (1 + escalation)^(year − 2023)`. "
            "At 3%/yr, diesel cost roughly doubles over 24 years. Compounds on the $150/MWh base.\n\n"
            "**Sensitivity:** HIGH — top 3 parameter. Higher escalation makes the Status Quo "
            "progressively worse and strengthens the case for expansion."
        ),
    ) / 100

    # ── Advanced Settings ──────────────────────────────────────────────────
    with st.sidebar.expander("Advanced Settings", expanded=False):

        # ── System ─────────────────────────────────────────────────────────
        st.markdown(f"**{config['name']} System**")
        base_mwh = st.number_input(
            "Baseline load (MWh/yr)", 10_000, 80_000, d["base_mwh"], 500,
            help=(
                "Total community electricity consumption in the base year (2023). "
                "This is the starting point from which all future load growth is projected.\n\n"
                "**Source:** EIA-861 2023 Short Form, City of Wrangell, utility ID 21015.\n\n"
                "**Math:** Starting point for all projections: "
                "`load = base_mwh × (1 + r)^(year − 2023)`. Higher values mean more demand "
                "in every future year, faster diesel reliance under Status Quo.\n\n"
                "**Sensitivity:** MEDIUM — shifts all three scenario curves up/down together."
            ),
        )
        seapa_cap = st.number_input(
            "Current hydro energy cap (MWh/yr)", 10_000, 80_000, d["seapa_cap"], 500,
            help=(
                "The maximum MWh of cheap SEAPA hydropower available to the community per year. "
                "Any demand above this ceiling must be served by expensive diesel generation.\n\n"
                "**Source:** Back-calculated from 2023 actuals: 40,708 total − 508 diesel "
                "= 40,200 MWh hydro.\n\n"
                "**Math:** `diesel_mwh = max(floor, total_demand − cap)`. "
                "Post-expansion: `cap = seapa_cap + expansion_new_mwh`.\n\n"
                "**Sensitivity:** MEDIUM — lowering it accelerates diesel dependency; "
                "raising it delays it."
            ),
        )
        seapa_rate = st.number_input(
            "Wholesale hydro rate ($/MWh)", 50.0, 150.0, d["seapa_rate"], 1.0,
            help=(
                "The per-MWh cost the community pays SEAPA for hydropower from Tyee Lake. "
                "This is the cheapest energy source and also the baseline cost the anchor must exceed.\n\n"
                "**Source:** Back-calculated from 2023 EIA-861 actuals: "
                "(revenue − fixed − diesel cost) / hydro MWh ≈ $93/MWh. "
                "Not a published SEAPA tariff.\n\n"
                "**Math:** `hydro_cost = seapa_rate × hydro_mwh`. Also sets the floor for "
                "anchor margin: `margin = anchor_mwh × (tariff − seapa_rate)`. "
                "If anchor tariff < SEAPA rate, the anchor loses money.\n\n"
                "**Sensitivity:** MEDIUM-HIGH — appears in the tornado chart. "
                "Affects both total system cost and anchor economics simultaneously."
            ),
        )
        fixed_cost = st.number_input(
            "Fixed costs ($/yr)", 500_000, 5_000_000, d["fixed_cost"], 50_000,
            help=(
                "Annual non-energy operating costs for the local utility — staff, line maintenance, "
                "billing, administration, and infrastructure overhead.\n\n"
                "**Source:** Estimate: ~5 FT staff + infrastructure overhead. "
                "Pending Wrangell Electric audit confirmation.\n\n"
                "**Math:** `total_cost = fixed_cost + hydro_cost + diesel_cost + debt_service`. "
                "Added as a flat amount every year in every scenario.\n\n"
                "**Sensitivity:** LOW — raises baseline rate equally for all three scenarios. "
                "Does not change the relative advantage of expansion or the anchor."
            ),
        )
        diesel_base = st.number_input(
            "Diesel all-in cost ($/MWh)", 80.0, 300.0, d["diesel_base_cost"], 5.0,
            help=(
                "The fully-loaded cost to generate one MWh from diesel in the base year (2023), "
                "including fuel, remote delivery, O&M, and air permits.\n\n"
                "**Source:** Fully-loaded estimate including remote fuel delivery, "
                "O&M, and air permits.\n\n"
                "**Math:** Year-zero unit cost. Escalates annually: "
                "`diesel_rate = base × (1 + escalation)^(year − 2023)`. "
                "Then `diesel_cost = diesel_rate × diesel_mwh`.\n\n"
                "**Sensitivity:** MEDIUM — higher base widens the cost penalty of Status Quo "
                "and increases savings from expansion. Appears in tornado chart."
            ),
        )
        diesel_floor = st.number_input(
            "Diesel operational floor (MWh/yr)", 0, 2_000, d["diesel_floor"], 50,
            help=(
                "The minimum amount of diesel generation that must run each year regardless of "
                "hydro availability — for generator testing, maintenance, and peak-spike coverage.\n\n"
                "**Source:** Minimum run hours required for testing, maintenance, "
                "and peak spikes.\n\n"
                "**Math:** `diesel_mwh = max(floor, total_demand − cap)`. "
                "Prevents Scenarios B and C from showing zero diesel.\n\n"
                "**Sensitivity:** LOW — negligible effect unless set very high (>1,000 MWh)."
            ),
        )

        st.markdown("---")

        # ── Load Growth ────────────────────────────────────────────────────
        st.markdown("**Load Growth Assumptions**")
        r1 = st.slider(
            "Phase 1 growth (%/yr)", 1.0, 10.0, d["r1"] * 100, 0.5,
            help=(
                "Compound annual growth rate for community electricity demand during the rapid "
                "heat-pump adoption phase (2023 to Phase 1 end year).\n\n"
                "**Source:** Historical: Wrangell load grew +19% over 2019–2023 "
                "(~4.5%/yr CAGR) from oil-to-heat-pump conversion.\n\n"
                "**Math:** `load = base_mwh × (1 + r1)^(year − 2023)` during Phase 1. "
                "Compounds annually — at 5%/yr, load grows ~22% by 2027.\n\n"
                "**Sensitivity:** MEDIUM — appears in tornado chart. Higher values "
                "accelerate diesel dependency and increase expansion urgency."
            ),
        ) / 100
        phase1_end = st.selectbox(
            "Phase 1 ends", [2026, 2027, 2028],
            index=[2026, 2027, 2028].index(d["phase1_end"]),
            help=(
                "The year when rapid heat-pump adoption tapers off and load growth transitions "
                "from the fast rate (Phase 1) to the slower steady-state rate (Phase 2).\n\n"
                "**Source:** Assumption — heat pump adoption saturates ~4 years out.\n\n"
                "**Math:** Before this year: `load = base × (1+r1)^t`. "
                "After: `load = terminal × (1+r2)^t`. Later end = more years of fast growth.\n\n"
                "**Sensitivity:** LOW-MEDIUM — shifts the kink point in the load curve "
                "by 1–2 years."
            ),
        )
        r2 = st.slider(
            "Phase 2 growth (%/yr)", 0.5, 5.0, d["r2"] * 100, 0.5,
            help=(
                "Compound annual growth rate for community electricity demand after heat-pump "
                "adoption saturates — the long-term baseline growth from population, EVs, etc.\n\n"
                "**Source:** Assumption: post-saturation baseline growth.\n\n"
                "**Math:** `load = terminal × (1 + r2)^(year − phase1_end)` "
                "where terminal is the load at the end of Phase 1. "
                "Even small changes compound significantly over the 2028–2035 window.\n\n"
                "**Sensitivity:** MEDIUM — determines the long-term load trajectory "
                "and whether diesel creep returns after expansion."
            ),
        ) / 100

        st.markdown("---")

        # ── Expansion Financing ────────────────────────────────────────────
        st.markdown("**Expansion Financing**")
        expansion_yr = st.selectbox(
            "Target online year", [2026, 2027, 2028, 2029],
            index=[2026, 2027, 2028, 2029].index(d["expansion_year"]),
            help=(
                "The year the 3rd Tyee Lake turbine comes online, adding new hydro capacity "
                "and activating the anchor customer load. Debt service also starts this year.\n\n"
                "**Source:** SEAPA confirmed target: December 2027.\n\n"
                "**Math:** Before this year, all scenarios behave identically. "
                "From this year on, Scenarios B & C get new hydro capacity and pay debt service. "
                "Scenario C also adds anchor load and revenue.\n\n"
                "**Sensitivity:** MEDIUM — delaying extends the period of diesel "
                "reliance and shifts all expansion/anchor benefits later."
            ),
        )
        expansion_new = st.number_input(
            "New hydro energy (MWh/yr)", 5_000, 60_000, d["expansion_new_mwh"], 1_000,
            help=(
                "Additional cheap hydropower (MWh/yr) the community gains from the 3rd turbine "
                "expansion. This is Wrangell's share of the new turbine output.\n\n"
                "**Source:** Calculated: 5 MW × 8,760 hrs × 0.845 CF ≈ 37,000 MWh "
                "(Wrangell's share of the 3rd Tyee Lake turbine).\n\n"
                "**Math:** `cap_post_expansion = seapa_cap + new_mwh`. "
                "Must exceed community load growth + anchor demand to eliminate "
                "structural diesel use.\n\n"
                "**Sensitivity:** MEDIUM — appears in tornado chart. "
                "Directly controls post-expansion diesel displacement."
            ),
        )
        capex = st.number_input(
            "Total expansion capex ($)", 5_000_000, 50_000_000, d["capex"], 500_000,
            help=(
                "Total capital cost to build the 3rd Tyee Lake turbine — shared across "
                "SEAPA member communities. Wrangell's share is financed as municipal debt.\n\n"
                "**Source:** SEAPA 3rd turbine engineering estimate (~$20M).\n\n"
                "**Math:** Flows through PMT: `principal = capex × share`, then "
                "`debt_service = principal × r(1+r)^n / ((1+r)^n − 1)`. "
                "At $20M × 40% share × 5%/25yr = ~$569K/yr debt service.\n\n"
                "**Sensitivity:** MEDIUM — higher capex means larger annual debt "
                "payments that ratepayers (or the anchor) must cover."
            ),
        )
        w_share = st.slider(
            "Community's share of debt (%)", 20, 100, int(d["w_share"] * 100), 5,
            help=(
                "The fraction of total expansion capex that Wrangell must finance. "
                "SEAPA costs are split among member communities (Wrangell, Petersburg, Ketchikan).\n\n"
                "**Source:** Proportional to Wrangell's load vs total SEAPA "
                "membership (estimate). Actual contract terms may differ.\n\n"
                "**Math:** `principal = capex × share`. At 40% of $20M, "
                "Wrangell finances $8M. Directly scales annual debt service.\n\n"
                "**Sensitivity:** MEDIUM — linear effect on debt service and "
                "therefore on Scenario B/C rates."
            ),
        ) / 100
        fin_rate = st.slider(
            "Financing rate (%)", 3.0, 8.0, d["fin_rate"] * 100, 0.25,
            help=(
                "Annual interest rate on the municipal bonds used to finance "
                "Wrangell's share of expansion capex.\n\n"
                "**Source:** Municipal bond rate assumption.\n\n"
                "**Math:** Used in PMT: `payment = P × r(1+r)^n / ((1+r)^n − 1)`. "
                "Higher rates increase annual debt service, making anchor coverage "
                "more important and raising Scenario B rates.\n\n"
                "**Sensitivity:** MEDIUM — a 1% rate increase adds ~$50K/yr to "
                "debt service on $8M principal."
            ),
        ) / 100
        fin_term = st.radio(
            "Bond term (years)", [20, 25, 30],
            index=[20, 25, 30].index(d["fin_term"]),
            horizontal=True,
            help=(
                "Length of the municipal bond used to finance the expansion. "
                "Longer terms spread payments out but cost more in total interest.\n\n"
                "**Source:** Standard municipal bond terms.\n\n"
                "**Math:** Longer terms reduce annual payments but increase total "
                "interest paid. 20yr → ~$641K/yr, 25yr → ~$569K/yr, 30yr → ~$520K/yr "
                "(at 5% on $8M).\n\n"
                "**Sensitivity:** LOW-MEDIUM — affects annual debt service by ~$50–120K "
                "across the range."
            ),
        )
        debt_svc = annual_debt_service(capex, w_share, fin_rate, fin_term)
        st.metric("Annual debt service", f"${debt_svc:,.0f}/yr",
                  help=(
                      "**Derived:** `PMT(capex × share, rate, term)`. "
                      "This is the annual payment Wrangell ratepayers must cover "
                      "if there is no anchor customer (Scenario B). In Scenario C, "
                      "the anchor margin offsets this amount."
                  ))

        st.markdown("---")

        # ── Anchor Details ─────────────────────────────────────────────────
        st.markdown("**Anchor Details**")
        anchor_cf = st.slider(
            "Anchor capacity factor", 0.70, 0.99, d["anchor_cf"], 0.01,
            help=(
                "The fraction of time the anchor data center runs at full nameplate load. "
                "A CF of 0.90 means the facility operates at 90% of its peak capacity on average.\n\n"
                "**Source:** Data center industry typical: 0.85–0.95.\n\n"
                "**Math:** `anchor_mwh = MW × CF × 8,760`. Multiplied by nameplate "
                "to get annual MWh. Higher CF = more energy consumed and more "
                "tariff revenue generated.\n\n"
                "**Sensitivity:** MEDIUM — at 2 MW, changing CF from 0.85 to 0.95 "
                "adds ~1,752 MWh/yr of demand and ~$47K/yr of margin."
            ),
        )

        st.markdown("---")

        # ── Community Baseline ─────────────────────────────────────────────
        st.markdown("**Community Baseline**")
        n_hh = st.number_input(
            "Residential accounts", 200, 5_000, d["n_hh"], 50,
            help=(
                "Number of residential electricity accounts (households) in the community.\n\n"
                "**Source:** EIA-861 2023 customer count.\n\n"
                "**Math:** `community_savings = per_hh_savings × n_hh`. "
                "Used for per-household bill and savings calculations.\n\n"
                "**Sensitivity:** NONE on rates/model — display only. "
                "Scales the Community Impact tab numbers."
            ),
        )
        hh_kwh = st.number_input(
            "Avg household kWh/yr", 3_000, 20_000, d["hh_kwh"], 500,
            help=(
                "Typical annual electricity consumption for one residential household, "
                "used to translate per-kWh rates into annual dollar bills.\n\n"
                "**Source:** Estimate for Wrangell residential usage.\n\n"
                "**Math:** `annual_bill = rate_kwh × hh_kwh`. Converts $/kWh rates "
                "into annual dollar bills per household.\n\n"
                "**Sensitivity:** NONE on rates/model — display only. "
                "Does not affect system-level economics."
            ),
        )
        econ_mult = st.slider(
            "Local spending multiplier", 1.0, 2.5, 1.7, 0.1,
            help=(
                "How much each dollar of direct spending (payroll, procurement) ripples through "
                "the local economy via re-spending. A 1.7× multiplier means $1 direct = $1.70 total.\n\n"
                "**Source:** Standard rural economic multiplier assumption.\n\n"
                "**Math:** `local_economic_activity = (payroll + spending) × multiplier`.\n\n"
                "**Sensitivity:** NONE on rates/model — display only. "
                "Affects the Community Impact tab narrative."
            ),
        )
        jobs_per_mw = st.slider(
            "Data center jobs per MW (operating)", 0.5, 5.0, 1.5, 0.5,
            help=(
                "Estimated number of permanent full-time jobs per MW of data center capacity "
                "once the facility is operational (excludes construction jobs).\n\n"
                "**Source:** Industry estimate for operating data centers.\n\n"
                "**Math:** `operating_jobs = anchor_mw × jobs_per_mw`. "
                "At 2 MW × 1.5 = 3 ongoing jobs.\n\n"
                "**Sensitivity:** NONE on rates/model — display only. "
                "Affects the Community Impact tab jobs estimate."
            ),
        )

        st.markdown("---")

        # ── Heating Fuel Analysis ──────────────────────────────────────────
        st.markdown("**Heating Fuel Analysis**")
        hh_oil_gal = st.number_input(
            "Avg household heating oil (gal/yr)", 200, 1500, d["hh_oil_gal"], 50,
            help=(
                "Gallons of heating oil a typical household burns per year for space heating. "
                "This is the fossil fuel consumption that heat pumps replace with electricity.\n\n"
                "**Source:** Typical Wrangell household consumption.\n\n"
                "**Math:** `heating_kwh = gal × 138,500 BTU / (COP × 3,412 BTU/kWh)`. "
                "At 800 gal × 138,500 / (2.5 × 3,412) ≈ 12,950 kWh.\n\n"
                "**Sensitivity:** Affects heating tab only — not grid rates."
            ),
        )
        heating_oil_price = st.number_input(
            "Current heating oil price ($/gal)", 2.00, 8.00, d["heating_oil_price"], 0.25,
            help=(
                "Current retail price per gallon of home heating oil delivered in the community.\n\n"
                "**Source:** DCRA Alaska fuel price survey, 2024–2025.\n\n"
                "**Math:** `oil_home_total = base_elec_bill + (gal × oil_price)`. "
                "At 800 gal × $5.00 = $4,000/yr heating oil cost.\n\n"
                "**Sensitivity:** Affects heating tab only — higher oil price "
                "makes heat pump savings larger."
            ),
        )
        oil_escalation = st.slider(
            "Heating oil escalation (%/yr)", 0.0, 6.0, d["oil_escalation"] * 100, 0.5,
            help=(
                "Annual rate at which heating oil prices increase due to fuel market inflation. "
                "Same concept as diesel escalation but for home heating fuel.\n\n"
                "**Source:** Assumption: annual oil price inflation.\n\n"
                "**Math:** `oil_price_yr = base × (1 + escalation)^(year − 2023)`. "
                "Makes heat pump savings grow over time.\n\n"
                "**Sensitivity:** Affects heating tab only — makes the case for "
                "heat pump conversion stronger over time."
            ),
        ) / 100
        heat_pump_cop = st.number_input(
            "Heat pump COP (cold climate)", 1.5, 4.0, d["heat_pump_cop"], 0.1,
            help=(
                "Coefficient of Performance — the ratio of heat output to electricity input "
                "for cold-climate heat pumps. COP 2.5 means 2.5 units of heat per unit of electricity.\n\n"
                "**Source:** Cold-climate heat pump specifications.\n\n"
                "**Math:** `heating_kwh = oil_gal × 138,500 BTU / (COP × 3,412 BTU/kWh)`. "
                "Higher COP = less electricity needed. "
                "At COP 2.5: 12,950 kWh. At COP 3.0: 10,790 kWh.\n\n"
                "**Sensitivity:** Affects heating tab only — higher COP "
                "reduces the electricity needed for heating and increases savings."
            ),
        )
        hp_conversion_rate = st.slider(
            "Homes converting to heat pumps (%/yr)", 0, 20, int(d["hp_conversion_rate"] * 100), 1,
            help=(
                "Percent of remaining oil-heated homes that install heat pumps each year. "
                "These conversions shift heating load from oil to electricity, driving load growth.\n\n"
                "**Source:** Assumption: pace of oil-to-heat-pump adoption.\n\n"
                "**Math:** At 5%/yr with 50% starting on oil: ~587 homes × 5% = ~29 homes/yr "
                "initially (declining as the pool shrinks). "
                "Drives the load growth that underpins Phase 1.\n\n"
                "**Sensitivity:** Affects heating tab trajectory. Indirectly relates to "
                "Phase 1 growth rate (r1) which drives grid load."
            ),
        ) / 100
        pct_oil_heat_2023 = st.slider(
            "% homes using oil heat (base year)", 20, 80, int(d["pct_oil_heat_2023"] * 100), 5,
            help=(
                "Fraction of households that use heating oil as their primary heat source "
                "in the base year. This is the starting pool available for heat pump conversion.\n\n"
                "**Source:** ~50% as of 2023 estimate.\n\n"
                "**Math:** Starting fraction for conversion trajectory. "
                "Combined with conversion rate, determines how many homes "
                "are switching per year and how much new electric load appears.\n\n"
                "**Sensitivity:** Affects heating tab only — sets the pool of "
                "homes available for conversion."
            ),
        ) / 100

    # ── Derived anchor values ──────────────────────────────────────────────
    anchor_mwh_yr = anchor_mw * anchor_cf * 8_760
    anchor_tariff_mwh = anchor_tariff_kwh * 1_000

    st.sidebar.caption(f"→ **{anchor_mwh_yr:,.0f} MWh/yr** ({anchor_mw:.1f} MW × {anchor_cf:.0%} CF)")

    # ── Live coverage callout ──────────────────────────────────────────────
    cov = anchor_capex_coverage(anchor_mwh_yr, anchor_tariff_mwh, seapa_rate, debt_svc)
    margin_yr = anchor_mwh_yr * (anchor_tariff_mwh - seapa_rate)
    if cov >= 0.90:
        st.sidebar.success(
            f"Anchor covers **{min(cov, 1.0):.0%}** of expansion debt "
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
        st.sidebar.error("⚠️ Tariff is below hydro cost — not financially viable.")

    # ── Scenario pin/compare ───────────────────────────────────────────────
    st.sidebar.markdown("---")
    col_pin, col_clear = st.sidebar.columns(2)
    with col_pin:
        if st.button("📌 Pin Scenario", use_container_width=True):
            st.session_state["pinned_label"] = f"Pinned: {anchor_mw:.1f}MW @ ${anchor_tariff_kwh:.3f}"
            st.session_state["_pin_trigger"] = True
    with col_clear:
        if st.button("Clear Pin", use_container_width=True):
            st.session_state.pop("pinned_params", None)
            st.session_state.pop("pinned_scenarios", None)
            st.session_state.pop("pinned_label", None)
            st.session_state.pop("_pin_trigger", None)

    base_rate = d["base_rate"]

    return dict(
        community_key=community_key,
        community_name=config["name"],
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
        # Heating fuel params
        hh_oil_gal=hh_oil_gal, heating_oil_price=heating_oil_price,
        oil_escalation=oil_escalation, heat_pump_cop=heat_pump_cop,
        hp_conversion_rate=hp_conversion_rate, pct_oil_heat_2023=pct_oil_heat_2023,
    )
