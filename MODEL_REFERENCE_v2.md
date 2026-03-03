# Anchor Customer Explorer — Model Reference v2

**Version:** 2.0
**Last updated:** 2026-03-02
**Predecessor:** MODEL_REFERENCE.md (v1, 23 parameters, 20 calculations)

---

## What Changed from v1

| Area | v1 | v2 |
|---|---|---|
| Architecture | Single 1,125-line file | 13 modules under `lib/` |
| Communities | Wrangell only (hardcoded) | Wrangell + Cordova (config-driven, extensible) |
| Dispatch | Annual energy balance only | Annual + monthly seasonal dispatch |
| Energy scope | Electricity rates only | Electricity + heating oil (total energy cost) |
| Sensitivity | Manual slider exploration | Automated tornado chart (8 params, ±perturbation) |
| Optimizer | None | Grid search over MW × tariff with feasible-region heatmap |
| Comparison | None | Pin/compare scenario snapshots |
| Validation | None | Backtest vs EIA-923 / AEDG actuals (2001–2024) |
| Export | Separate script (`generate_guide_pdf.py`) | In-app PDF download button |
| Parameters | 23 | 29 (6 new for heating fuel analysis) |
| Calculations | 20 | 30 (10 new) |

---

## Sidebar Controls

### Quick Controls (always visible)

| # | Parameter | Default (Wrangell) | Default (Cordova) | Range | Effect on Model |
|---|-----------|-------|---------|-------|-----------------|
| 1 | **Anchor nameplate load** (MW) | 2.0 | 1.5 | 0.5–5.0 | Combined with capacity factor, determines annual anchor energy demand. Larger anchors generate more revenue but consume more new hydro capacity. |
| 2 | **Anchor tariff** ($/kWh) | 0.12 | 0.11 | 0.07–0.20 | MOST SENSITIVE LEVER. The margin above hydro cost × anchor MWh = annual debt coverage. Small changes swing Scenario C from partial to full coverage. |
| 3 | **Diesel cost escalation** (%/yr) | 3.0% | 3.0% | 0–6% | Compounds annually on diesel base cost. At 3%/yr, diesel cost roughly doubles over 24 years. Higher escalation strengthens the case for expansion. |

### Advanced Settings

#### System

| # | Parameter | Default (Wrangell) | Default (Cordova) | Range | Source | Effect on Model |
|---|-----------|-------|---------|-------|--------|-----------------|
| 4 | **Baseline load** (MWh/yr) | 40,708 | 24,000 | 10,000–80,000 | EIA-861 2023 / estimate | Starting point for all load projections. |
| 5 | **Current hydro energy cap** (MWh/yr) | 40,200 | 22,000 | 10,000–80,000 | Back-calculated from diesel usage | Ceiling of cheap hydropower. Demand above this is served by diesel. |
| 6 | **Wholesale hydro rate** ($/MWh) | 93 | 85 | 50–150 | Back-calculated (Wrangell) / estimate (Cordova) | Cost of every hydro MWh. Sets the floor for anchor margin. |
| 7 | **Fixed costs** ($/yr) | 1,200,000 | 900,000 | 500,000–5,000,000 | Estimate | Flat annual cost added to every scenario in every year. |
| 8 | **Diesel all-in cost** ($/MWh) | 150 | 160 | 80–300 | Fully-loaded estimate | Year-zero diesel unit cost. |
| 9 | **Diesel operational floor** (MWh/yr) | 200 | 300 | 0–2,000 | Min run hours for testing/maintenance | Minimum diesel even when hydro is ample. |

#### Load Growth

| # | Parameter | Default (Wrangell) | Default (Cordova) | Range | Effect on Model |
|---|-----------|-------|---------|-------|-----------------|
| 10 | **Phase 1 growth** (%/yr) | 5.0% | 3.0% | 1–10% | Compound growth during rapid adoption phase. |
| 11 | **Phase 1 ends** | 2027 | 2027 | 2026–2028 | When growth transitions from fast to steady-state. |
| 12 | **Phase 2 growth** (%/yr) | 2.0% | 1.5% | 0.5–5% | Long-term load trajectory after saturation. |

#### Expansion Financing

| # | Parameter | Default (Wrangell) | Default (Cordova) | Range | Effect on Model |
|---|-----------|-------|---------|-------|-----------------|
| 13 | **Target online year** | 2027 | 2028 | 2026–2029 | When new hydro capacity comes online. |
| 14 | **New hydro energy** (MWh/yr) | 37,000 | 15,000 | 5,000–60,000 | Additional hydro capacity from expansion. |
| 15 | **Total expansion capex** ($) | 20,000,000 | 12,000,000 | 5M–50M | Total capital cost of expansion. |
| 16 | **Community's share of debt** (%) | 40% | 100% | 20–100% | Fraction of capex financed by this community. |
| 17 | **Financing rate** (%) | 5.0% | 5.0% | 3–8% | Interest rate on expansion debt. |
| 18 | **Bond term** (years) | 25 | 25 | 20, 25, 30 | Longer terms reduce annual payments, increase total interest. |

#### Anchor Details

| # | Parameter | Default (Wrangell) | Default (Cordova) | Range | Effect on Model |
|---|-----------|-------|---------|-------|-----------------|
| 19 | **Anchor capacity factor** | 0.90 | 0.85 | 0.70–0.99 | Fraction of time at full load. Nameplate × CF × 8,760 = annual MWh. |

#### Community Baseline

| # | Parameter | Default (Wrangell) | Default (Cordova) | Range | Effect on Model |
|---|-----------|-------|---------|-------|-----------------|
| 20 | **Residential accounts** | 1,174 | 800 | 200–5,000 | Display-only: scales per-household savings. |
| 21 | **Avg household kWh/yr** | 9,000 | 8,500 | 3,000–20,000 | Converts rates to annual bills. Display-only. |
| 22 | **Local spending multiplier** | 1.7 | 1.7 | 1.0–2.5 | Scales economic impact estimates. Display-only. |
| 23 | **Data center jobs per MW** | 1.5 | 1.5 | 0.5–5.0 | Estimates ongoing jobs. Display-only. |

#### Heating Fuel Analysis (new in v2)

| # | Parameter | Default (Wrangell) | Default (Cordova) | Range | Source | Effect on Model |
|---|-----------|-------|---------|-------|--------|-----------------|
| 24 | **Avg household heating oil** (gal/yr) | 800 | 900 | 200–1,500 | Estimate for SE Alaska | Gallons of oil a typical oil-heated home burns per year. Drives the oil-to-heat-pump savings calculation. |
| 25 | **Current heating oil price** ($/gal) | 5.00 | 5.30 | 2.00–8.00 | DCRA 2024-2025 survey | Base-year price per gallon. Escalates annually. |
| 26 | **Heating oil escalation** (%/yr) | 3.0% | 3.0% | 0–6% | Assumption | Compounds annually on oil price. Higher = bigger savings from conversion. |
| 27 | **Heat pump COP** | 2.5 | 2.3 | 1.5–4.0 | Cold-climate HP specs | Coefficient of Performance. Higher COP = less electricity needed per unit of heat. |
| 28 | **Homes converting to HP** (%/yr) | 5% | 4% | 0–20% | Historical adoption trend | Fraction of remaining oil-heated homes converting each year. |
| 29 | **% homes on oil heat (base year)** | 50% | 55% | 20–80% | DCRA / ACS estimates | Starting fraction of homes using oil heat. Decays exponentially via conversion rate. |

---

## Backend Calculations

### Calculations 1–20: Core Model (unchanged from v1)

These are identical to v1 MODEL_REFERENCE.md. Summary:

| # | Calculation | Formula |
|---|---|---|
| 1 | Community load projection | Two-phase compound growth: `base × (1+r1)^t` then `terminal × (1+r2)^t` |
| 2 | SEAPA energy cap | `seapa_cap` (+ `expansion_new_mwh` post-expansion) |
| 3 | Anchor energy demand | `anchor_mw × anchor_cf × 8,760` (Scenario C only, post-expansion) |
| 4 | Total system demand | `community_mwh + anchor_mwh` |
| 5 | Diesel dispatch | `max(diesel_floor, total_mwh − cap)` |
| 6 | Hydro dispatch | `total_mwh − diesel_mwh` |
| 7 | Diesel cost escalation | `diesel_base × (1 + escalation)^(year − 2023)` |
| 8 | SEAPA hydro cost | `seapa_rate × hydro_mwh` |
| 9 | Diesel cost | `diesel_rate × diesel_mwh` |
| 10 | Annual debt service (PMT) | `PV × r × (1+r)^n / ((1+r)^n − 1)` |
| 11 | Anchor revenue | `anchor_mwh × anchor_tariff_mwh` |
| 12 | Total annual system cost | `fixed + seapa + diesel + debt_service` |
| 13 | Community cost | `total_cost − anchor_revenue` |
| 14 | Retail rate | `max(0.05, community_cost / (community_mwh × 1,000))` |
| 15 | Anchor margin | `anchor_mwh × (tariff − seapa_rate)` |
| 16 | Anchor capex coverage | `margin / debt_service_yr` |
| 17 | Diesel avoided (C vs A) | `sum(diesel_A − diesel_C)` for all years |
| 18 | CO2 and barrels avoided | `avoided_mwh × 0.7` tonnes; `avoided_mwh / 0.01709` barrels |
| 19 | Household annual bill | `rate_kwh × hh_kwh` |
| 20 | Cumulative household savings | `sum((rate_A − rate_C) × hh_kwh)` for 2027–2035 |

---

### Calculation 21: Monthly Load Shape (new in v2)

```
month_community_mwh = annual_community_mwh × load_shape[m] / 12
```

Distributes annual load across 12 months using a seasonal weight vector. Weights sum to 12.0 so the monthly average equals the annual value divided by 12.

**Wrangell default load shape** (derived from EIA-923 diesel seasonal pattern):

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1.20 | 1.15 | 1.10 | 1.00 | 0.90 | 0.80 | 0.80 | 0.85 | 0.95 | 1.05 | 1.10 | 1.15 |

Winter peak (~1.2×) reflects heating load; summer trough (~0.8×) is the low-demand period.

---

### Calculation 22: Monthly Hydro Availability Shape (new in v2)

```
month_hydro_cap = annual_hydro_cap × hydro_shape[m] / 12
```

Hydro availability is inversely correlated with load — runoff peaks in spring/summer, drops in winter.

**Wrangell default hydro shape:**

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0.70 | 0.65 | 0.75 | 0.95 | 1.20 | 1.35 | 1.35 | 1.25 | 1.05 | 0.85 | 0.75 | 0.70 |

The mismatch between load shape (winter-heavy) and hydro shape (summer-heavy) is what drives winter diesel dependency — the seasonal dynamic that caused the 2022 capacity crisis.

---

### Calculation 23: Monthly Diesel Dispatch (new in v2)

```
month_diesel = max(diesel_floor / 12, month_total − month_hydro_cap)
month_hydro  = month_total − month_diesel
```

Same merit-order logic as the annual model, applied per-month. Anchor load is assumed flat (data center runs 24/7: `annual_anchor / 12`).

**Inputs:** load_shape, hydro_shape, diesel_floor

---

### Calculation 24: Heating kWh Equivalent (new in v2)

```
heating_kwh = hh_oil_gal × 138,500 BTU/gal / (COP × 3,412 BTU/kWh)
```

How much electricity a heat pump needs to deliver the same heat as the household's oil consumption.

At defaults (800 gal, COP 2.5): `800 × 138,500 / (2.5 × 3,412) = 12,980 kWh`

**Inputs:** hh_oil_gal, heat_pump_cop

---

### Calculation 25: Oil Home Total Energy Cost (new in v2)

```
oil_home_total = (hh_kwh_base × rate_kwh) + (hh_oil_gal × oil_price)
```

A household still on oil heat pays for both base electricity and heating oil.

Oil price escalates: `oil_price = heating_oil_price × (1 + oil_escalation)^(year − 2023)`

**Inputs:** hh_kwh_base, hh_oil_gal, heating_oil_price, oil_escalation

---

### Calculation 26: Heat Pump Home Total Energy Cost (new in v2)

```
hp_home_total = (hh_kwh_base + heating_kwh) × rate_kwh
```

A converted household pays for base electricity plus heating electricity. No oil cost.

**Inputs:** hh_kwh_base, heating_kwh (from Calc 24), rate_kwh (from Calc 14)

---

### Calculation 27: Community Average Total Energy Cost (new in v2)

```
remaining_oil = pct_oil_heat_2023 × (1 − hp_conversion_rate)^(year − 2023)
pct_hp = 1.0 − remaining_oil

avg_total = remaining_oil × oil_home_total + pct_hp × hp_home_total
```

Weighted average across the community as homes convert from oil to heat pumps over time. The conversion trajectory is exponential decay of the oil-heated fraction.

**Inputs:** pct_oil_heat_2023, hp_conversion_rate

---

### Calculation 28: Sensitivity Analysis (new in v2)

```
For each of 8 key parameters:
    low_rate  = compute_scenarios(param × (1 − perturbation))["C"].rate[target_year]
    high_rate = compute_scenarios(param × (1 + perturbation))["C"].rate[target_year]
    swing     = |high_rate − low_rate|

Sort by swing descending → tornado chart
```

Parameters perturbed and their default perturbation range:

| Parameter | Perturbation |
|---|---|
| Anchor tariff | ±25% |
| Anchor size (MW) | ±25% |
| Diesel base cost | ±25% |
| Diesel escalation | ±50% |
| SEAPA wholesale rate | ±20% |
| Phase 1 growth rate | ±30% |
| New SEAPA energy | ±25% |
| Fixed costs | ±25% |

**Outputs:** Tornado chart showing ¢/kWh change from base rate for each parameter. Identifies the single most sensitive lever at current settings.

---

### Calculation 29: Optimizer Grid Search (new in v2)

```
For each (mw, tariff) in 30×30 grid:
    anchor_mwh = mw × anchor_cf × 8,760
    scenarios  = compute_scenarios(anchor_mwh, tariff × 1000, ...)

    rate[i,j]     = scenarios["C"].rate[target_year]
    coverage[i,j] = anchor_margin / debt_service
    savings[i,j]  = (rate_A − rate_C) × hh_kwh
```

900 evaluations of `compute_scenarios` (cached, <2 sec total). Produces a heatmap over the MW × tariff space colored by the selected metric, with a contour line at the user's target threshold.

**Three optimization goals:**
- Rate below target $/kWh by target year
- Coverage above target % of expansion debt
- Household savings above target $/yr vs Status Quo

---

### Calculation 30: Backtest Comparison (new in v2)

```
actual_diesel = EIA-923 Plant 95 annual diesel (2019–2024)
               + AEDG yearly diesel (2001–2018)

model_diesel  = compute_scenarios("A")["diesel_mwh"] for overlapping years
```

Overlays actual historical diesel generation as diamond markers on the model's Status Quo projection. The model starts from the 2023 baseline, so pre-2023 actuals serve as reference context rather than direct validation targets.

**Data sources:**
- `data/eia923_alaska_monthly.csv` — Plant 95, 2019–2024
- `data/public_yearly_generation.csv` — Wrangell DFO, 2001–2021

---

## Tab Structure

| Tab | Contents | Key Charts |
|---|---|---|
| **Rate Trajectory** | 3-line rate chart, 2030/2035 metrics, rate table, narrative, backtest | `chart_rate_trajectory`, backtest overlay |
| **Total Energy Cost** | Oil vs HP home comparison, total cost trajectory, savings | `chart_total_energy_cost`, `chart_oil_vs_hp_breakdown`, `chart_hp_savings` |
| **Diesel Displacement** | Annual/Monthly toggle, diesel lines, cost bars, energy stacks, heatmap | `chart_diesel_lines`, `chart_diesel_cost_bars`, `chart_energy_stacks`, `chart_monthly_dispatch`, `chart_monthly_diesel_heatmap` |
| **Expansion Viability** | Big coverage %, waterfall, cumulative chart, finance breakdown, tornado | `chart_expansion_waterfall`, `chart_cumulative_coverage`, `chart_tornado` |
| **Optimizer** | Goal selector, MW×tariff heatmap with feasibility contour | Optimizer heatmap with contour + star marker |
| **Community Impact** | Household bills, savings tables, economic impact | `chart_household_bills` |

---

## File Structure

```
streamlit_app.py              # Main orchestrator (825 lines)
lib/
  __init__.py
  config.py                   # Colors, YEARS, scenario labels
  financial.py                # fmt_dollar, PMT, coverage
  model.py                    # compute_scenarios + compute_scenarios_monthly
  narratives.py               # 4 narrative generators
  charts.py                   # 9 chart builders
  sidebar.py                  # All widgets, community-driven defaults
  data_loaders.py             # Cached CSV loaders
  heating.py                  # Total energy cost calculations + 3 charts
  sensitivity.py              # Tornado analysis
  communities.py              # Wrangell + Cordova config dicts
  pdf_export.py               # In-app PDF generation
generate_guide_pdf.py         # Original standalone PDF generator (v1)
MODEL_REFERENCE.md            # v1 model reference (preserved)
```

---

## Community Configs

Each community is a config dict in `lib/communities.py` with:
- `name`, `fips`, `grid`, `description`
- `defaults` — all 29 parameter default values
- `load_shape` — 12 monthly load weights (sum = 12.0)
- `hydro_shape` — 12 monthly hydro availability weights (sum = 12.0)

**Currently supported:** Wrangell, Cordova

**To add a new community:**
1. Add a new entry to `COMMUNITY_CONFIGS` in `lib/communities.py`
2. Set community-specific defaults (baseline load, hydro cap, rates, etc.)
3. Derive load and hydro shapes from available monthly generation data
4. The sidebar and all calculations automatically adapt

---

## Dependencies

```
streamlit
pandas
plotly
numpy
fpdf2
```

---

## Caveats (apply to all communities)

- Illustrative projections — not a rate-case or regulatory filing
- Wholesale hydro rates are estimated, not published tariffs
- Debt shares are proportional-load estimates; actual contract terms may differ
- Diesel costs use fully-loaded estimates; actual costs vary seasonally
- Two-phase load growth is assumption-based
- Fixed costs are estimates pending audit confirmation
- Monthly shapes are approximations; actual seasonal patterns vary year to year
- The heating fuel model assumes uniform conversion across the community
- The optimizer uses a grid search, not global optimization — results depend on search range
