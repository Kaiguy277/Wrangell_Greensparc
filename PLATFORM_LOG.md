# AKEnergy — Wrangell Anchor Customer Explorer: Platform Log

**Project:** Greensparc Anchor Customer Impact Explorer — Wrangell, Alaska
**File:** `streamlit_app.py`
**Last updated:** 2026-02-19
**Status:** MVP / Demo-ready

---

## 1. Purpose

A single-page Streamlit web application for exploring the economic case for a Greensparc small-scale data center in Wrangell, Alaska. The core argument: Wrangell's power supply (SEAPA Tyee Lake hydro) is near its capacity ceiling due to rapid load growth from heat pump adoption. The system needs a ~$20M third turbine. A Greensparc anchor customer can provide the guaranteed offtake revenue that makes that expansion financeable — and can drive community retail rates *below* their current level.

The app is designed for use in stakeholder meetings, policy conversations, and project development discussions. It is a scenario-planning tool, not a rate-case model.

---

## 2. The Three Scenarios

| Scenario | Description | Key outcome |
|---|---|---|
| 🔴 **Status Quo** | No expansion, no anchor. Load grows, diesel fills gap. | Rates rise ~22% by 2035 |
| 🟡 **Expansion Only** | SEAPA 3rd turbine built; full capital cost on ratepayers. | Rates roughly flat; capital burden on community |
| 🟢 **Expansion + Anchor** | 3rd turbine + Greensparc anchor. Anchor margin covers ~75%+ of Wrangell's debt share. | Rates fall ~5% below today by 2030 |

---

## 3. Data Sources

### 3a. Primary sources (hard data)

| Data point | Value | Source | Year |
|---|---|---|---|
| Total annual retail sales | 40,708 MWh/yr | EIA Form 861, Short Form — City of Wrangell (Utility #21015) | 2023 |
| Total utility revenue | $5,010,000/yr | EIA Form 861 Short Form | 2023 |
| Total customers | 2,068 | EIA Form 861 Short Form | 2023 |
| Residential accounts | 1,174 | Wrangell city website / findenergy.com | 2023 |
| Commercial accounts | 843 | Wrangell city website / findenergy.com | 2023 |
| Avg residential rate | $0.122/kWh | findenergy.com (cross-checked vs EIA-861) | 2023 |
| Rate schedule (tiered) | $0.126/0.102/0.080 per kWh | City of Wrangell Fee & Rate Schedule, eff. July 2023 | 2023 |
| Diesel generators (nameplate) | 12.0 MW (5 units, all operational) | EIA Form 860, Plant ID 95, Nov 2025 | 2025 |
| Annual diesel generation | 518 MWh/yr | EIA Form 923, Plant ID 95 | 2024 |
| Historical diesel generation | 447–902 MWh/yr | EIA Form 923 / AEA public_monthly_generation.csv | 2007–2024 |
| Community population | ~2,100 | ACS 5-year estimate (2019–2023) | 2023 |
| Grid affiliation | SEAPA Grid, Southeast AK | AEA public_communities.csv | — |
| PCE eligibility | Not eligible | AEA public_communities.csv | — |
| Transportation | No road connection; ferry, air, barge | AEA public_transportation.csv | — |
| Diesel fuel price | $4.83–$5.31/gallon | AEA public_fuel_prices.csv (DCRA / Petro Marine) | 2024–2025 |
| Employment | ~870 residents employed | AEA public_employment.csv | 2016 (most recent available) |
| Annual tax revenue | ~$5.2M/yr | AEA public_taxes.csv | 2024 |

### 3b. Derived / back-calculated values

| Parameter | Value | Derivation |
|---|---|---|
| Implied avg load | 4.65 MW | 40,708 MWh ÷ 8,760 hr |
| Blended retail rate | $0.1231/kWh | $5,010,000 ÷ 40,708,000 kWh |
| SEAPA wholesale rate | ~$93/MWh | (Revenue − fixed costs − diesel costs) ÷ hydro MWh |
| SEAPA energy cap for Wrangell | ~40,200 MWh/yr | Total 2024 load − diesel generation |
| Load growth 2019→2023 | +19.1% | (40,708 − 34,166) ÷ 34,166 |
| Annual load growth rate | ~4.5%/yr | CAGR of 19.1% over 4 years |

> **Note on SEAPA wholesale rate:** The $93/MWh figure is back-calculated from 2023 EIA-861 actuals using estimated fixed costs. It is not a published tariff. The actual SEAPA power sales agreement rate is not publicly available. Sensitivity to this value can be explored via the sidebar.

### 3c. SEAPA infrastructure (publicly reported)

| Data point | Value | Source |
|---|---|---|
| Tyee Lake installed capacity | 20 MW (2 × 10 MW turbines) | SEAPA / Frontier Media / Ketchikan Daily News 2024 |
| Tyee Lake serves | Wrangell + Petersburg only | SEAPA public materials |
| Swan Lake installed capacity | 22.4 MW | SEAPA / multiple sources |
| Swan Lake serves | Ketchikan primarily | SEAPA |
| 3rd turbine project (Tyee) | ~$20M, target Dec 2027 | Ketchikan Daily News / Frontier Media 2024 |
| Federal grant secured | $5M | Frontier Media 2024 |
| AEA funding requested | $4M | Frontier Media 2024 |
| Capacity constraint event | Winter 2022: ran at 100%, both communities switched to diesel | Ketchikan Daily News 2025 |
| Expansion driver | Heat pump adoption — oil heat 75% (2016) → 50% (2023) | Frontier Media 2024 |

### 3d. Local datasets (AEA / state sources)

Located in `/home/kai/Documents/AKEnergy/data/`:

| File | Contents | Wrangell records |
|---|---|---|
| `public_communities.csv` | Community metadata, grid, PCE status | 1 row |
| `public_capacity.csv` | Service area capacity (MW) by fuel type | 1 row (2021, 8.5 MW DFO) |
| `public_monthly_generation.csv` | Monthly generation by fuel type | 252 rows (2001–2021) |
| `public_yearly_generation.csv` | Annual generation totals | 21 rows (2001–2021) |
| `public_rates.csv` | Residential/commercial rates by year | 11 rows (2011–2021) |
| `public_fuel_prices.csv` | Seasonal fuel prices by source | 128 rows (2005–2025) |
| `public_employment.csv` | Residents employed, UI claimants | 16 rows (2001–2016) |
| `public_taxes.csv` | Annual tax revenue breakdown | 8 rows (2017–2024) |
| `public_populations_ages_sexes.csv` | ACS population estimates | 2 rows (2018–2022, 2019–2023) |
| `public_transportation.csv` | Infrastructure/access profile | 1 row |
| `eia923_alaska_monthly.csv` | Monthly diesel generation (Plant 95) | 72 rows (2019–2024) |
| `eia_api_capacity.csv` | Generator-level capacity (EIA API) | 319 rows (2020–2025) |
| `eia923/` | Raw EIA-923 XLSX files | Plant 95 in each year |

> The AEA datasets capture **diesel generation only**. SEAPA hydro supply to Wrangell is not in these files. This gap was identified during data analysis and resolved using EIA-861 retail sales data.

---

## 4. Model Design

### 4a. Load trajectory

Two-phase compound growth model:
- **Phase 1 (2023–2027):** 5%/yr — accelerated heat pump adoption
- **Phase 2 (2028–2035):** 2%/yr — steady-state growth post-transition

The 5%/yr rate is consistent with the observed 2019→2023 CAGR of ~4.5%/yr and the known driver (6,100 new heat pump installations funded by a $38M federal grant across coastal Southeast AK communities).

### 4b. Dispatch model

Simple merit-order dispatch:
1. SEAPA hydro fills demand up to its annual energy cap
2. Diesel fills any remainder
3. Diesel floor (200 MWh/yr) represents minimum operational run-hours for testing and peak spikes even when hydro is ample

This is a simplified energy-balance model. It does not model hourly dispatch, load duration curves, or seasonal hydro reservoir levels. The 2022 capacity constraint was a peak-power event; the model captures this through the diesel floor and escalating diesel with load growth.

### 4c. Cost model

```
Total annual cost = fixed_costs
                  + seapa_rate × hydro_MWh
                  + diesel_rate × diesel_MWh
                  + expansion_debt_service  (post-expansion years only)

Retail rate = (total_cost − anchor_revenue) ÷ community_MWh ÷ 1,000
```

Where:
- `anchor_revenue = anchor_MWh × anchor_tariff_per_MWh` (Scenario C only, post-expansion)
- `expansion_debt_service` = Wrangell's share of SEAPA 3rd turbine annual debt service
- `diesel_rate` escalates at 3%/yr from base year

### 4d. Expansion financing

Standard annuity (PMT formula):

```
PMT = PV × r × (1+r)^n ÷ ((1+r)^n − 1)
```

Defaults: $20M capex × 40% Wrangell share × 5% rate × 25 years = **~$568K/yr**

The 40% Wrangell share is estimated proportionally (Wrangell load as fraction of combined Wrangell + Petersburg load). Actual SEAPA cost allocation is contractually defined and not publicly available.

### 4e. Anchor capex coverage

```
Coverage = anchor_MWh × (anchor_tariff − seapa_wholesale_rate) ÷ wrangell_debt_service
```

This is the "above-cost margin" that the anchor contributes above what it costs to serve them. At default settings (2 MW, 90% CF, $0.12/kWh tariff):

```
= 15,768 MWh × ($120 − $93) ÷ $568,000
= $425,736 ÷ $568,000
= 74.9%
```

Coverage > 100% means the anchor over-covers; surplus reduces community rates further.

---

## 5. Key Findings (at default parameters)

| Metric | Value |
|---|---|
| 2023 baseline rate | $0.123/kWh |
| 2030 rate — Status Quo | ~$0.137/kWh (+11%) |
| 2030 rate — Expansion Only | ~$0.127/kWh (+3%) |
| 2030 rate — Expansion + Anchor | ~$0.119/kWh (−3%) |
| 2035 rate — Status Quo | ~$0.151/kWh (+23%) |
| 2035 rate — Expansion + Anchor | ~$0.117/kWh (−5%) |
| Anchor capex coverage | ~75% at $0.12/kWh tariff |
| Diesel avoided (C vs A, 2023–2035) | ~100,000+ MWh |
| Household savings vs Status Quo (2030) | ~$150–200/yr per household |

---

## 6. Known Data Gaps and Limitations

| Gap | Impact | How to resolve |
|---|---|---|
| SEAPA wholesale rate not published | Core cost model parameter must be estimated | Request from Wrangell Electric or SEAPA; or use RCA filings |
| Wrangell Electric fixed costs not confirmed | Estimated at ~$1.2M/yr | Pull FY2024 audit from wrangell.com/finance/financial-reports-budget-and-audit |
| Wrangell's contractual SEAPA share (%) | Assumed 40%; actual may differ | Power Sales Agreement (not public) |
| Retail rate post-2019 in AEA data | AEA dataset has NaN for 2020–2021 | Confirmed via EIA-861 ($0.123/kWh) and July 2023 rate schedule |
| EIA-861 data only available through 2023 | No 2024/2025 consumption data | File annual request or check next EIA release cycle |
| Heat pump growth rate post-2025 | Key driver of load trajectory uncertainty | Monitor AEA/DCRA heat pump program data |
| Petersburg load (affects Tyee sharing) | Affects Wrangell's hydro allocation | Petersburg Electric utility data (EIA-861 / AEA) |
| SEAPA 3rd turbine final cost/timeline | Target $20M / Dec 2027 — not confirmed | Monitor SEAPA / FERC filings |

---

## 7. Technical Stack

| Component | Technology |
|---|---|
| App framework | Streamlit (1.54.0) |
| Charts | Plotly (graph_objects, 5.15.0) |
| Data manipulation | Pandas (2.3.3) |
| Language | Python 3.12 |
| Deployment | Local (`streamlit run streamlit_app.py`, port 8501) |

**Key implementation notes:**
- Plotly 5.15 does not support 8-digit hex colors (`#rrggbbaa`). Use `rgba(r,g,b,a)` format for transparent fills.
- `@st.cache_data` is used on `compute_scenarios()`. Cache key is the full parameter set passed as keyword arguments. Any sidebar change triggers a recompute.
- The `compute_scenarios()` function has no Streamlit dependencies — it can be imported and called independently for testing or notebook use.

---

## 8. File Structure

```
/home/kai/Documents/AKEnergy/
├── streamlit_app.py          # Main application
├── PLATFORM_LOG.md           # This file
└── data/
    ├── public_communities.csv
    ├── public_capacity.csv
    ├── public_monthly_generation.csv
    ├── public_yearly_generation.csv
    ├── public_rates.csv
    ├── public_fuel_prices.csv
    ├── public_employment.csv
    ├── public_taxes.csv
    ├── public_populations_ages_sexes.csv
    ├── public_transportation.csv
    ├── eia923_alaska_monthly.csv
    ├── eia_api_capacity.csv
    ├── eia_api_generation_monthly.csv
    ├── eia_api_retail_sales.csv
    ├── cordova_annual_timeline.csv
    ├── cordova_monthly_generation.csv
    └── eia923/
        ├── EIA923_Schedules_2_3_4_5_M_12_2019_Final_Revision.xlsx
        ├── EIA923_Schedules_2_3_4_5_M_12_2020_Final_Revision.xlsx
        ├── EIA923_Schedules_2_3_4_5_M_12_2021_Final_Revision.xlsx
        ├── EIA923_Schedules_2_3_4_5_M_12_2022_Final_Revision.xlsx
        ├── EIA923_Schedules_2_3_4_5_M_12_2023_Final_Revision.xlsx
        └── EIA923_Schedules_2_3_4_5_M_12_2024_Final.xlsx
```

---

## 9. Generalizing to Other Communities

The model was built specifically for Wrangell but can be adapted for other Alaska communities (e.g., Cordova, Petersburg, Sitka). To add a new community:

1. Source EIA-861 Short Form data for annual MWh and revenue
2. Identify the primary generation source (hydro vs diesel vs mix)
3. Back-calculate the wholesale rate from utility financials
4. Identify any capacity expansion plans and their costs
5. Update the sidebar defaults or add a community selector dropdown

The Cordova dataset (`cordova_annual_timeline.csv`, `cordova_monthly_generation.csv`) is already in the data directory and would be the natural next candidate — Cordova also has SEAPA-adjacent hydro (Eyak Lake / Power Creek) and similar structural characteristics.

---

## 10. Intended Use and Caveats

**Intended use:**
- Stakeholder briefings and project development discussions
- Live scenario exploration in meetings (adjust anchor MW/tariff sliders in real time)
- Policy and PR narrative development

**Not intended for:**
- Rate-case filings or regulatory proceedings
- Permitting applications
- Financial projections for investment decisions

**Key caveats (also shown in app footer):**
- SEAPA wholesale rate is estimated, not published
- Wrangell's SEAPA debt share (40%) is proportional estimate
- Diesel cost uses fully-loaded remote delivery estimate; actual costs vary seasonally
- Two-phase load growth is assumption-based; heat pump adoption rate uncertain
- Fixed costs (~$1.2M/yr) need audit confirmation
- Model does not capture seasonal hydro variability, load duration, or peak vs. average dispatch in detail

---

## 11. Change Log

| Date | Change | Author |
|---|---|---|
| 2026-02-19 | Initial app built — generic anchor customer model | Claude / Kai |
| 2026-02-19 | Data analysis: all AEA + EIA files searched for Wrangell | Claude / Kai |
| 2026-02-19 | Web research: SEAPA, EIA-861 2023, Wrangell rate schedule | Claude / Kai |
| 2026-02-19 | EIA-861 2023 ZIP downloaded and parsed — confirmed 40,708 MWh, $5.01M revenue, 2,068 customers | Claude / Kai |
| 2026-02-19 | App reimagined as Wrangell-specific expansion catalyst story; three-scenario year-by-year model | Claude / Kai |
| 2026-02-19 | Fixed Plotly 5.15 rgba compatibility (8-digit hex not supported) | Claude / Kai |
| 2026-02-19 | Platform log created | Claude / Kai |
