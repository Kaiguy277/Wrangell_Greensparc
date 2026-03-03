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

from lib.config import (
    YEARS, SCENARIO_LABELS, SCENARIO_COLORS,
    C_A, C_B, C_C, C_REF,
)
from lib.financial import fmt_dollar, fmt_dollar_md, anchor_capex_coverage
from lib.model import compute_scenarios, compute_scenarios_monthly
from lib.narratives import narr_rate, narr_diesel, narr_viability, narr_community
from lib.charts import (
    chart_rate_trajectory, chart_diesel_lines, chart_energy_stacks,
    chart_diesel_cost_bars, chart_expansion_waterfall,
    chart_cumulative_coverage, chart_household_bills,
    chart_monthly_dispatch, chart_monthly_diesel_heatmap,
)
from lib.sidebar import render_sidebar
from lib.heating import (
    compute_heating_economics, chart_total_energy_cost,
    chart_oil_vs_hp_breakdown, chart_hp_savings,
)
from lib.sensitivity import run_sensitivity, chart_tornado
from lib.data_loaders import load_wrangell_actuals
from lib.pdf_export import generate_scenario_pdf

# ═════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Wrangell Energy Future | Greensparc",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    params = render_sidebar()

    # ── Run model ────────────────────────────────────────────────────────
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

    # ── Handle scenario pinning ──────────────────────────────────────────
    if st.session_state.get("_pin_trigger"):
        st.session_state["pinned_params"] = dict(params)
        st.session_state["pinned_scenarios"] = {
            k: df.copy() for k, df in scenarios.items()
        }
        st.session_state.pop("_pin_trigger", None)

    pinned = st.session_state.get("pinned_scenarios")
    pinned_label = st.session_state.get("pinned_label", "Pinned")

    # ── Compute heating economics ────────────────────────────────────────
    scenario_rates = {
        key: scenarios[key]["rate_kwh"].tolist() for key in ["A", "B", "C"]
    }
    heating_data = compute_heating_economics(
        hh_oil_gal=params["hh_oil_gal"],
        heating_oil_price=params["heating_oil_price"],
        oil_escalation=params["oil_escalation"],
        heat_pump_cop=params["heat_pump_cop"],
        hp_conversion_rate=params["hp_conversion_rate"],
        pct_oil_heat_2023=params["pct_oil_heat_2023"],
        hh_kwh_base=params["hh_kwh"],
        scenario_rates=scenario_rates,
    )

    # ── Compute monthly dispatch ────────────────────────────────────────
    monthly_data = compute_scenarios_monthly(
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
        anchor_mwh_yr=params["anchor_mwh_yr"],
        anchor_tariff_mwh=params["anchor_tariff_mwh"],
    )

    # Shorthand lookups
    base_rate    = params["base_rate"]
    expansion_yr = params["expansion_yr"]
    hh_kwh       = params["hh_kwh"]
    n_hh         = params["n_hh"]

    def rate(sc, yr): return scenarios[sc].loc[yr, "rate_kwh"]
    def bill(sc, yr): return rate(sc, yr) * hh_kwh

    community_name = params.get("community_name", "Wrangell")

    # ── Header ───────────────────────────────────────────────────────────
    st.title(f"{community_name}, Alaska: The Anchor Customer Expansion Case")
    st.markdown(
        f"A Greensparc data-center anchor customer can make hydropower expansion "
        f"financeable while driving **{community_name}** community rates **below today's level**."
    )

    # ── PDF Export ────────────────────────────────────────────────────────
    pdf_bytes = generate_scenario_pdf(params, scenarios, community_name)
    st.download_button(
        label="📄 Download Scenario PDF",
        data=pdf_bytes,
        file_name=f"{community_name.lower()}_scenario_{params['anchor_mw']:.1f}MW.pdf",
        mime="application/pdf",
    )

    # ── 2030 rate outlook cards ──────────────────────────────────────────
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

    # ── Executive summary ────────────────────────────────────────────────
    cov = params["anchor_coverage"]
    avoided_mwh = scenarios["A"]["diesel_mwh"].sum() - scenarios["C"]["diesel_mwh"].sum()
    cum_hh_savings = sum(
        (rate("A", y) - rate("C", y)) * hh_kwh for y in range(2027, 2036)
    )
    rate_c_2030 = rate("C", 2030)
    if rate_c_2030 < base_rate:
        verdict = f"rates **{abs(rate_c_2030 - base_rate)*100:.1f}¢ below** today's level"
    else:
        verdict = f"rates **{abs(rate_c_2030 - base_rate)*100:.1f}¢ above** today's level"

    st.markdown(
        f"A **{params['anchor_mw']:.1f} MW** Greensparc anchor at "
        f"**\\${params['anchor_tariff_kwh']:.3f}/kWh** covers "
        f"**{min(cov, 1.0):.0%}** of Wrangell's expansion debt "
        f"and delivers {verdict} by 2030. "
        f"Over 2027–2035, this saves the average household "
        f"**{fmt_dollar_md(cum_hh_savings)}** vs the Status Quo "
        f"and avoids **{avoided_mwh:,.0f} MWh** of diesel generation."
    )

    if pinned:
        st.caption(f"📌 Comparing against: **{pinned_label}**")

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Rate Trajectory",
        "🔥 Total Energy Cost",
        "💧 Diesel Displacement",
        "🏗️ Expansion Viability",
        "🎯 Optimizer",
        "🏘️ Community Impact",
    ])

    # ── TAB 1: Rate Trajectory ───────────────────────────────────────────
    with tab1:
        st.subheader("Retail Rate Trajectory — 2023 to 2035")
        st.plotly_chart(
            chart_rate_trajectory(scenarios, base_rate, expansion_yr,
                                 pinned=pinned, pinned_label=pinned_label),
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

        # ── Backtest Against Actuals ─────────────────────────────────────
        with st.expander("Model Validation: Backtest vs Actuals (2019–2024)"):
            try:
                actuals = load_wrangell_actuals()
                diesel_actual = actuals["diesel_annual"]

                if not diesel_actual.empty:
                    import plotly.graph_objects as go

                    # Run model from 2019 baseline (34,166 MWh) to compare
                    # Using Scenario A (no expansion) since that's the historical reality
                    actual_years = diesel_actual["year"].tolist()
                    actual_diesel = diesel_actual["diesel_mwh"].tolist()

                    # Model predicted diesel for same years
                    model_diesel = []
                    for y in actual_years:
                        if y in scenarios["A"].index:
                            model_diesel.append(scenarios["A"].loc[y, "diesel_mwh"])
                        else:
                            model_diesel.append(None)

                    # Only compare overlapping years
                    overlap_years = [y for y, m in zip(actual_years, model_diesel) if m is not None and 2023 <= y <= 2035]

                    if overlap_years:
                        fig_bt = go.Figure()

                        # Actual data points (all available years)
                        fig_bt.add_trace(go.Scatter(
                            x=actual_years, y=actual_diesel,
                            mode="markers",
                            name="Actual (EIA-923 / AEDG)",
                            marker=dict(symbol="diamond", size=10, color="#6b7280",
                                       line=dict(color="black", width=1)),
                        ))

                        # Model prediction line
                        fig_bt.add_trace(go.Scatter(
                            x=YEARS,
                            y=scenarios["A"]["diesel_mwh"].tolist(),
                            mode="lines",
                            name="Model (Status Quo)",
                            line=dict(color=C_A, width=2),
                        ))

                        fig_bt.update_layout(
                            title="Diesel Generation: Model vs Actuals",
                            xaxis_title="Year",
                            yaxis_title="Diesel (MWh/yr)",
                            height=360,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            margin=dict(t=60, b=40, l=80, r=40),
                        )
                        st.plotly_chart(fig_bt, use_container_width=True)

                        st.caption(
                            "Diamond markers show actual diesel generation from EIA-923 (2019-2024) "
                            "and AEDG (pre-2019). The model line shows the Status Quo projection. "
                            "Note: the model starts from 2023 baseline, so pre-2023 actuals are reference only."
                        )
                    else:
                        st.caption("No overlapping years found between model and actuals.")
                else:
                    st.caption("No diesel generation actuals available for Wrangell.")
            except Exception as e:
                st.caption(f"Could not load actuals: {e}")

    # ── TAB 2: Total Energy Cost ─────────────────────────────────────────
    with tab2:
        st.subheader("Total Household Energy Cost: Electricity + Heating")
        st.markdown(
            "The electricity rate is only part of the story. Wrangell households switching "
            "from heating oil to heat pumps **dramatically reduce their total energy cost** — "
            "even if electricity rates rise. This tab shows the full picture."
        )

        # Hero metrics
        oil_today = heating_data["A"].loc[2023, "oil_home_total"]
        hp_c_2030 = heating_data["C"].loc[2030, "hp_home_total"]
        savings_2030 = heating_data["C"].loc[2030, "hp_savings_vs_oil"]

        e1, e2, e3 = st.columns(3)
        e1.metric(
            "Oil-heated home (2023)",
            f"${oil_today:,.0f}/yr",
            help="Electricity + heating oil at current prices",
        )
        e2.metric(
            "Heat pump home — Scenario C (2030)",
            f"${hp_c_2030:,.0f}/yr",
            help="All-electric (base + heating) at Scenario C rate",
        )
        e3.metric(
            "Annual savings (HP vs Oil, 2030)",
            f"${savings_2030:,.0f}/yr",
            delta=f"{savings_2030/oil_today*100:.0f}% lower total cost",
            delta_color="normal",
        )

        st.plotly_chart(
            chart_total_energy_cost(heating_data, oil_today),
            use_container_width=True,
        )

        col_left, col_right = st.columns(2)
        with col_left:
            st.plotly_chart(
                chart_oil_vs_hp_breakdown(heating_data, "C"),
                use_container_width=True,
            )
        with col_right:
            st.plotly_chart(
                chart_hp_savings(heating_data),
                use_container_width=True,
            )

        st.markdown("#### Narrative")
        hp_kwh = heating_data["C"].loc[2023, "heating_kwh"]
        st.info(
            f"A typical Wrangell household using **{params['hh_oil_gal']:,} gallons/yr** "
            f"of heating oil at **\\${params['heating_oil_price']:.2f}/gal** spends "
            f"**\\${oil_today:,.0f}/yr** on total energy (electricity + heat). "
            f"Switching to a heat pump (COP {params['heat_pump_cop']:.1f}) replaces that oil "
            f"with **{hp_kwh:,.0f} kWh** of electricity — saving "
            f"**\\${savings_2030:,.0f}/yr** by 2030 under Scenario C. "
            f"Even under the Status Quo, heat pump households save "
            f"**\\${heating_data['A'].loc[2030, 'hp_savings_vs_oil']:,.0f}/yr** — the conversion "
            f"is a win regardless of which scenario plays out. The expansion just makes it better."
        )

    # ── TAB 3: Diesel Displacement ───────────────────────────────────────
    with tab3:
        diesel_view = st.radio("View", ["Annual", "Monthly"], horizontal=True, key="diesel_view")

        if diesel_view == "Annual":
            st.subheader("Diesel Backup Usage Trajectory")
            st.plotly_chart(
                chart_diesel_lines(scenarios, expansion_yr,
                                  pinned=pinned, pinned_label=pinned_label),
                use_container_width=True,
            )

            st.subheader("Annual Diesel Cost")
            st.plotly_chart(chart_diesel_cost_bars(scenarios), use_container_width=True)

            st.subheader("Energy Mix by Scenario")
            st.plotly_chart(chart_energy_stacks(scenarios, expansion_yr), use_container_width=True)
        else:
            st.subheader("Monthly Energy Dispatch")
            st.markdown(
                "Winter months show the highest diesel exposure — load peaks from heating "
                "while hydro availability drops. This is what caused the **2022 capacity crisis**."
            )
            monthly_scenario = st.radio(
                "Scenario", ["A", "B", "C"],
                format_func=lambda k: SCENARIO_LABELS[k],
                horizontal=True, index=2, key="monthly_sc",
            )
            st.plotly_chart(
                chart_monthly_dispatch(monthly_data, monthly_scenario, expansion_yr),
                use_container_width=True,
            )

            st.subheader("Diesel Seasonality Heatmap")
            st.plotly_chart(
                chart_monthly_diesel_heatmap(monthly_data, monthly_scenario),
                use_container_width=True,
            )

        # Aggregate displacement metrics (always shown)
        st.markdown("---")
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

    # ── TAB 4: Expansion Viability ───────────────────────────────────────
    with tab4:
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

        # ── Sensitivity / Tornado Chart ──────────────────────────────────
        st.markdown("---")
        st.subheader("Parameter Sensitivity")
        st.markdown(
            "Which inputs move the needle most? Each parameter is perturbed +/- from its "
            "current value. The bars show the resulting change in Scenario C retail rate."
        )

        sens_target_year = st.selectbox(
            "Sensitivity target year", [2030, 2035], index=1, key="sens_yr"
        )

        sens_df = run_sensitivity(
            base_mwh=params["base_mwh"], r1=params["r1"],
            phase1_end=params["phase1_end"], r2=params["r2"],
            seapa_cap=params["seapa_cap"], seapa_rate=params["seapa_rate"],
            expansion_yr=params["expansion_yr"],
            expansion_new_mwh=params["expansion_new_mwh"],
            diesel_floor=params["diesel_floor"],
            diesel_base_cost=params["diesel_base_cost"],
            diesel_escalation=params["diesel_escalation"],
            fixed_cost=params["fixed_cost"],
            debt_service_yr=params["debt_service_yr"],
            anchor_mw=params["anchor_mw"], anchor_cf=params["anchor_cf"],
            anchor_tariff_kwh=params["anchor_tariff_kwh"],
            target_year=sens_target_year,
        )

        base_rate_sens = scenarios["C"].loc[sens_target_year, "rate_kwh"]
        st.plotly_chart(
            chart_tornado(sens_df, base_rate_sens),
            use_container_width=True,
        )

        # Top driver callout
        top = sens_df.iloc[-1]  # highest swing (sorted ascending)
        st.info(
            f"The most sensitive parameter is **{top['parameter']}** — "
            f"varying it swings the {sens_target_year} rate by "
            f"**{top['swing']*100:.2f}¢/kWh** ({top['swing']/base_rate_sens*100:.1f}% of base rate)."
        )

    # ── TAB 5: Optimizer ─────────────────────────────────────────────────
    with tab5:
        _render_optimizer_tab(params, scenarios)

    # ── TAB 6: Community Impact ──────────────────────────────────────────
    with tab6:
        st.subheader("Household Bill Impact")
        st.plotly_chart(
            chart_household_bills(scenarios, base_rate, hh_kwh,
                                 pinned=pinned, pinned_label=pinned_label),
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

    # ── Footer ───────────────────────────────────────────────────────────
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


# ═════════════════════════════════════════════════════════════════════════════
# OPTIMIZER TAB
# ═════════════════════════════════════════════════════════════════════════════

def _render_optimizer_tab(params, scenarios):
    """Optimizer: find anchor configurations that meet a target goal."""
    import numpy as np
    import plotly.graph_objects as go

    st.subheader("Anchor Configuration Optimizer")
    st.markdown(
        "Find the combinations of anchor size and tariff that achieve your goal. "
        "The heatmap shows the feasible region — adjust the target and search space below."
    )

    # ── Goal selection ───────────────────────────────────────────────────
    goal = st.radio(
        "Optimization goal",
        ["Rate below target", "Coverage above target", "Household savings above target"],
        horizontal=True,
    )

    g1, g2 = st.columns(2)
    with g1:
        if goal == "Rate below target":
            target_rate = st.number_input("Target rate ($/kWh)", 0.08, 0.16, 0.12, 0.005, format="%.3f")
        elif goal == "Coverage above target":
            target_cov = st.number_input("Target coverage (%)", 50, 150, 100, 5)
        else:
            target_savings = st.number_input("Target savings ($/yr per household)", 50, 500, 150, 25)
    with g2:
        target_year = st.selectbox("Target year", [2028, 2029, 2030, 2031, 2032, 2035], index=2)

    # ── Search space ─────────────────────────────────────────────────────
    st.markdown("**Search space**")
    s1, s2 = st.columns(2)
    with s1:
        mw_range = st.slider("Anchor MW range", 0.5, 5.0, (1.0, 4.0), 0.25)
    with s2:
        tariff_range = st.slider("Anchor tariff range ($/kWh)", 0.07, 0.20, (0.08, 0.16), 0.005, format="%.3f")

    # ── Grid search ──────────────────────────────────────────────────────
    resolution = 30
    mw_grid = np.linspace(mw_range[0], mw_range[1], resolution)
    tariff_grid = np.linspace(tariff_range[0], tariff_range[1], resolution)

    # Build result matrix
    rate_matrix = np.zeros((resolution, resolution))
    cov_matrix = np.zeros((resolution, resolution))
    savings_matrix = np.zeros((resolution, resolution))

    for i, tariff_kwh in enumerate(tariff_grid):
        for j, mw in enumerate(mw_grid):
            a_mwh = mw * params["anchor_cf"] * 8_760
            a_tariff_mwh = tariff_kwh * 1_000

            # Recompute debt service (uses same financing terms)
            ds = params["debt_service_yr"]

            sc = compute_scenarios(
                base_mwh=params["base_mwh"], r1=params["r1"],
                phase1_end=params["phase1_end"], r2=params["r2"],
                seapa_cap=params["seapa_cap"], seapa_rate=params["seapa_rate"],
                expansion_year=params["expansion_yr"],
                expansion_new_mwh=params["expansion_new_mwh"],
                diesel_floor=params["diesel_floor"],
                diesel_base_cost=params["diesel_base_cost"],
                diesel_escalation=params["diesel_escalation"],
                fixed_cost=params["fixed_cost"],
                debt_service_yr=ds,
                anchor_mwh_yr=a_mwh,
                anchor_tariff_mwh=a_tariff_mwh,
            )

            rate_val = sc["C"].loc[target_year, "rate_kwh"]
            rate_a_val = sc["A"].loc[target_year, "rate_kwh"]
            cov_val = anchor_capex_coverage(a_mwh, a_tariff_mwh, params["seapa_rate"], ds)
            savings_val = (rate_a_val - rate_val) * params["hh_kwh"]

            rate_matrix[i, j] = rate_val
            cov_matrix[i, j] = cov_val * 100
            savings_matrix[i, j] = savings_val

    # ── Pick the right matrix and threshold ──────────────────────────────
    if goal == "Rate below target":
        z = rate_matrix
        colorbar_title = "Rate ($/kWh)"
        threshold = target_rate
        contour_label = f"${target_rate:.3f}/kWh"
        colorscale = [[0, C_C], [0.5, "#fbbf24"], [1.0, C_A]]
    elif goal == "Coverage above target":
        z = cov_matrix
        colorbar_title = "Coverage (%)"
        threshold = target_cov
        contour_label = f"{target_cov}%"
        colorscale = [[0, C_A], [0.5, "#fbbf24"], [1.0, C_C]]
    else:
        z = savings_matrix
        colorbar_title = "Savings ($/yr)"
        threshold = target_savings
        contour_label = f"${target_savings}/yr"
        colorscale = [[0, C_A], [0.5, "#fbbf24"], [1.0, C_C]]

    # ── Heatmap ──────────────────────────────────────────────────────────
    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        x=np.round(mw_grid, 2),
        y=np.round(tariff_grid, 3),
        z=z,
        colorscale=colorscale,
        colorbar=dict(title=colorbar_title),
        hovertemplate="MW: %{x:.2f}<br>Tariff: $%{y:.3f}/kWh<br>Value: %{z:.3f}<extra></extra>",
    ))

    # Contour at threshold
    fig.add_trace(go.Contour(
        x=np.round(mw_grid, 2),
        y=np.round(tariff_grid, 3),
        z=z,
        contours=dict(
            start=threshold, end=threshold, size=0,
            coloring="none",
            showlabels=True,
            labelfont=dict(size=12, color="white"),
        ),
        line=dict(color="white", width=2.5, dash="dash"),
        showscale=False,
        hoverinfo="skip",
        name=f"Target: {contour_label}",
    ))

    # Mark current configuration
    fig.add_trace(go.Scatter(
        x=[params["anchor_mw"]],
        y=[params["anchor_tariff_kwh"]],
        mode="markers+text",
        marker=dict(symbol="star", size=16, color="white", line=dict(color="black", width=1.5)),
        text=["Current"],
        textposition="top center",
        textfont=dict(color="white", size=12),
        showlegend=False,
    ))

    fig.update_layout(
        title=f"Feasible Region — {goal} ({target_year})",
        xaxis_title="Anchor Nameplate (MW)",
        yaxis_title="Anchor Tariff ($/kWh)",
        yaxis_tickformat="$.3f",
        height=520,
        margin=dict(t=60, b=60, l=80, r=40),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Insight text ─────────────────────────────────────────────────────
    if goal == "Rate below target":
        # Find minimum MW at each tariff that meets target
        feasible_count = np.sum(z <= threshold)
        total_count = z.size
        st.markdown(
            f"**{feasible_count}** of {total_count} configurations ({feasible_count/total_count:.0%}) "
            f"achieve rates below **${target_rate:.3f}/kWh** by {target_year}. "
            f"The white dashed line shows the boundary of the feasible region."
        )
    elif goal == "Coverage above target":
        feasible_count = np.sum(z >= threshold)
        total_count = z.size
        st.markdown(
            f"**{feasible_count}** of {total_count} configurations ({feasible_count/total_count:.0%}) "
            f"achieve coverage above **{target_cov}%**. "
            f"The white dashed line shows the boundary of the feasible region."
        )
    else:
        feasible_count = np.sum(z >= threshold)
        total_count = z.size
        st.markdown(
            f"**{feasible_count}** of {total_count} configurations ({feasible_count/total_count:.0%}) "
            f"achieve household savings above **${target_savings}/yr** by {target_year}. "
            f"The white dashed line shows the boundary of the feasible region."
        )


if __name__ == "__main__":
    main()
