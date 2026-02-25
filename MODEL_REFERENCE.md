# Wrangell Energy Future — Model Reference

## Sidebar Controls

| # | Parameter | Default | Range | Source of Default | Effect on Model |
|---|-----------|---------|-------|-------------------|-----------------|
| 1 | **2023 baseline load** (MWh/yr) | 40,708 | 20,000–80,000 | EIA-861 2023 Short Form, utility 21015 | Sets the starting point for all load growth projections. Higher values mean more energy demand in every future year, faster diesel reliance under Status Quo, and larger anchor coverage requirements. |
| 2 | **Current SEAPA energy cap** (MWh/yr) | 40,200 | 20,000–60,000 | Back-calculated: 40,708 total − 508 diesel = 40,200 hydro | Defines the ceiling of cheap hydropower available before expansion. Any demand above this cap is served by diesel. Lowering it accelerates diesel dependency; raising it delays it. |
| 3 | **SEAPA wholesale rate** ($/MWh) | 93 | 50–150 | Back-calculated from 2023 EIA-861 revenue: (revenue − fixed − diesel cost) ÷ hydro MWh | The cost of every MWh of hydropower. Directly scales total system cost for hydro portion. Also sets the floor for anchor margin — the anchor only contributes to expansion debt if its tariff exceeds this rate. |
| 4 | **Wrangell Electric fixed costs** ($/yr) | 1,200,000 | 500,000–5,000,000 | Estimate: 5 FT staff + infrastructure overhead (pending audit) | A flat annual cost added to every scenario in every year. Higher fixed costs raise the baseline retail rate for all scenarios equally. Does not interact with diesel/hydro dispatch. |
| 5 | **Diesel all-in cost** ($/MWh) | 150 | 80–300 | Fully-loaded estimate including remote fuel delivery, O&M, air permits | The year-zero unit cost for diesel generation. Directly determines how expensive diesel-served MWh are. Higher values widen the cost penalty of the Status Quo and increase the savings from expansion. |
| 6 | **Diesel cost escalation** (%/yr) | 3.0% | 0–6% | Fuel price inflation assumption | Compounds annually on the diesel base cost. At 3%/yr, diesel cost roughly doubles over 24 years. Higher escalation makes the Status Quo progressively worse and strengthens the case for expansion. |
| 7 | **Diesel operational floor** (MWh/yr) | 200 | 0–2,000 | Minimum run hours for testing, maintenance, peak spikes | The minimum diesel generation even when hydro capacity is ample. Prevents scenarios B and C from showing zero diesel. Small effect unless set very high. |
| 8 | **Heat pump adoption growth** (Phase 1, %/yr) | 5.0% | 1–10% | Historical: Wrangell load grew +19% over 2019–2023 (~4.5%/yr CAGR) from oil-to-heat-pump conversion | Compound annual growth rate for community load during the rapid adoption phase. Higher values accelerate load growth, causing earlier and larger diesel dependency under Status Quo and increasing the urgency of expansion. |
| 9 | **Phase 1 end year** | 2027 | 2026–2028 | Assumption: heat pump adoption saturates ~4 years out | The year when load growth transitions from the fast rate (r1) to the steady-state rate (r2). Later end years mean more years of fast growth, higher peak loads, and more diesel in the Status Quo. |
| 10 | **Steady-state growth** (Phase 2, %/yr) | 2.0% | 0.5–5% | Assumption: post-saturation baseline growth | Compound annual growth after heat pump adoption slows. Determines long-term load trajectory. Even small changes compound significantly over the 2028–2035 window. |
| 11 | **Expansion target online year** | 2027 | 2026–2029 | SEAPA confirmed target: Dec 2027 | The year new hydro capacity and anchor load come online. Delaying it extends the period of diesel reliance (higher Status Quo costs) and shifts all expansion/anchor benefits later. |
| 12 | **New SEAPA energy for Wrangell** (MWh/yr) | 37,000 | 10,000–60,000 | Calculated: 5 MW × 8,760 hr × 0.845 CF ≈ 37,000 MWh (Wrangell's share of 3rd turbine) | The additional hydro capacity Wrangell gains from expansion. Determines how much load can shift from diesel to hydro post-expansion. Must exceed community load growth + anchor demand to eliminate structural diesel use. |
| 13 | **Total expansion capex** ($) | 20,000,000 | 10M–50M | SEAPA 3rd turbine engineering estimate | The total capital cost of building the 3rd turbine. Flows through to annual debt service via the PMT formula. Higher capex means larger debt payments that ratepayers (or the anchor) must cover. |
| 14 | **Wrangell's share of SEAPA debt** (%) | 40% | 20–60% | Proportional to Wrangell's load vs total SEAPA membership (estimate) | The fraction of total capex that Wrangell must finance. Directly scales Wrangell's annual debt service. At 40% of $20M, Wrangell finances $8M. |
| 15 | **Financing rate** (%) | 5.0% | 3–8% | Municipal bond rate assumption | The annual interest rate on expansion debt. Higher rates increase annual debt service payments, making anchor coverage more important and raising Scenario B rates. |
| 16 | **Bond term** (years) | 25 | 20, 25, or 30 | Standard municipal bond terms | Longer terms reduce annual payments but increase total interest paid. Affects the annual debt service that appears in Scenarios B and C. |
| 17 | **Anchor nameplate load** (MW) | 2.0 | 0.5–5.0 | Greensparc data-center sizing assumption | The installed capacity of the anchor customer. Combined with capacity factor, determines annual anchor energy demand. Larger anchors generate more revenue but consume more of the new hydro capacity. |
| 18 | **Anchor capacity factor** | 0.90 | 0.70–0.99 | Data center industry typical: 0.85–0.95 | The fraction of time the anchor runs at full load. Multiplied by nameplate × 8,760 hours to get annual MWh. Higher CF means more energy consumed and more tariff revenue generated. |
| 19 | **Anchor tariff** ($/kWh) | 0.12 | 0.07–0.20 | Proposed: above SEAPA cost ($0.093) but below retail ($0.123) | The rate charged to the anchor. The margin above SEAPA cost (tariff − $0.093/kWh) times anchor MWh is the annual contribution toward expansion debt. This is the single most sensitive lever for Scenario C outcomes. |
| 20 | **Residential accounts** | 1,174 | 500–3,000 | EIA-861 2023 customer count | Number of households for per-household bill and savings calculations. Does not affect rates or system economics — only the community impact display. |
| 21 | **Avg household kWh/yr** | 9,000 | 3,000–20,000 | Estimate for Wrangell residential usage | Used to convert $/kWh rates into annual dollar bills per household. Does not affect system-level economics. |
| 22 | **Local spending multiplier** | 1.7 | 1.0–2.5 | Standard rural economic multiplier assumption | Scales payroll and spending estimates for total local economic impact. Display-only — does not affect rates or energy dispatch. |
| 23 | **Data center jobs per MW** | 1.5 | 0.5–5.0 | Industry estimate for operating data centers | Multiplied by anchor MW to estimate ongoing jobs. Display-only — affects the Community Impact tab narrative but not financial model. |


## Backend Calculations

### 1. Community Load Projection (two-phase compound growth)

```
if year <= phase1_end:
    community_mwh = base_mwh × (1 + r1)^(year − 2023)
else:
    terminal = base_mwh × (1 + r1)^(phase1_end − 2023)
    community_mwh = terminal × (1 + r2)^(year − phase1_end)
```

Models load growth in two phases: fast heat-pump adoption (r1) then steady-state (r2). This is the demand that existing Wrangell ratepayers create.

**Inputs:** base_mwh, r1, phase1_end, r2

---

### 2. SEAPA Energy Cap (annual hydro ceiling)

```
if has_expansion AND year >= expansion_year:
    cap = seapa_cap + expansion_new_mwh
else:
    cap = seapa_cap
```

The maximum MWh of cheap hydropower available. Jumps up when the 3rd turbine comes online.

**Inputs:** seapa_cap, expansion_new_mwh, expansion_year

---

### 3. Anchor Energy Demand

```
anchor_mwh = anchor_mw × anchor_cf × 8,760    (annual)

Per year:
    if Scenario C AND year >= expansion_year:
        anchor = anchor_mwh_yr
    else:
        anchor = 0
```

The anchor only exists in Scenario C and only comes online with the expansion.

**Inputs:** anchor_mw, anchor_cf

---

### 4. Total System Demand

```
total_mwh = community_mwh + anchor_mwh
```

Everything the grid must serve in a given year.

---

### 5. Diesel Dispatch (gap-filling)

```
diesel_mwh = max(diesel_floor, total_mwh − cap)
```

Hydro is dispatched first (cheapest). Diesel fills whatever the hydro cap can't cover, subject to an operational minimum floor.

**Inputs:** diesel_floor

---

### 6. Hydro Dispatch

```
hydro_mwh = total_mwh − diesel_mwh
```

The complement of diesel — everything not served by diesel comes from SEAPA hydro.

---

### 7. Diesel Unit Cost Escalation

```
diesel_rate = diesel_base_cost × (1 + diesel_escalation)^(year − 2023)
```

Diesel gets more expensive every year due to fuel price inflation.

**Inputs:** diesel_base_cost, diesel_escalation

---

### 8. SEAPA Hydro Cost

```
seapa_cost = seapa_rate × hydro_mwh
```

Total annual cost of hydropower at the wholesale rate.

**Inputs:** seapa_rate

---

### 9. Diesel Cost

```
diesel_cost = diesel_rate × diesel_mwh
```

Total annual cost of diesel generation at the escalated rate.

---

### 10. Annual Debt Service (PMT formula)

```
principal = capex × wrangell_share
debt_service = principal × r × (1 + r)^n / ((1 + r)^n − 1)

where r = financing_rate, n = bond_term
```

Standard annuity formula. Only applies in Scenarios B and C, and only from the expansion year onward.

**Inputs:** capex, wrangell_share, financing_rate, bond_term

---

### 11. Anchor Revenue

```
anchor_revenue = anchor_mwh × anchor_tariff_mwh
```

Gross revenue from the anchor customer. Only nonzero in Scenario C post-expansion.

**Inputs:** anchor_tariff_kwh (converted to $/MWh)

---

### 12. Total Annual System Cost

```
total_cost = fixed_cost + seapa_cost + diesel_cost + debt_service
```

The full cost of running Wrangell's electric system for one year.

**Inputs:** fixed_cost

---

### 13. Community Cost (what ratepayers bear)

```
community_cost = total_cost − anchor_revenue
```

Anchor revenue offsets total cost. The remainder is what existing community ratepayers must pay. In Scenarios A and B, anchor_revenue = 0 so community_cost = total_cost.

---

### 14. Retail Rate

```
rate_kwh = max(0.05, community_cost / (community_mwh × 1,000))
```

Cost per kWh for Wrangell residents. Divides community cost by community consumption (in kWh). Floored at $0.05/kWh as a regulatory minimum.

---

### 15. Anchor Margin (above SEAPA cost)

```
margin = anchor_mwh_yr × (anchor_tariff_mwh − seapa_rate)
```

The annual dollar contribution the anchor makes toward expansion debt. Only positive when the anchor tariff exceeds the SEAPA wholesale rate.

---

### 16. Anchor Capex Coverage Ratio

```
coverage = margin / debt_service_yr
```

The fraction of Wrangell's annual expansion debt covered by anchor margin. At 100%+, the anchor fully funds the expansion and surplus flows back as rate reductions.

---

### 17. Diesel Avoided (Scenario C vs A)

```
avoided_mwh = sum(diesel_A[year] − diesel_C[year]) for all years
```

Total diesel generation eliminated by having the expansion + anchor vs doing nothing.

---

### 18. CO2 and Barrels Avoided

```
co2_tonnes = avoided_mwh × 0.7
barrels = avoided_mwh / 0.01709
```

Environmental metrics using standard diesel emission and energy density factors.

---

### 19. Household Annual Bill

```
bill = rate_kwh × hh_kwh
```

Converts the per-kWh rate into an annual dollar figure for a typical household.

**Inputs:** hh_kwh

---

### 20. Cumulative Household Savings (C vs A)

```
cum_savings = sum((rate_A[year] − rate_C[year]) × hh_kwh) for year in 2027–2035
```

Total dollar savings per household over the post-expansion period from choosing Scenario C over Status Quo. Multiplied by n_hh for community-wide figure.

**Inputs:** n_hh
