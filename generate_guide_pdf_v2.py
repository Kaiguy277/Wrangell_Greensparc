#!/usr/bin/env python3
"""
Generate a readable PDF user guide for the Wrangell Energy Future model (v2).
Run:  python3 generate_guide_pdf_v2.py
Out:  Wrangell_Energy_Model_Guide.pdf
"""

from fpdf import FPDF

# ─── Colours ────────────────────────────────────────────────────────────────
NAVY   = (17, 44, 81)
DARK   = (30, 30, 30)
GRAY   = (100, 100, 100)
WHITE  = (255, 255, 255)
LTGRAY = (240, 240, 245)
ACCENT = (22, 163, 74)     # green
RED    = (220, 38, 38)
AMBER  = (217, 119, 6)
BLUE   = (37, 99, 235)
TEAL   = (20, 184, 166)
HDRBLUE = (230, 240, 255)

FONT      = "DejaVu"
FONT_MONO = "DejaVuMono"

FONT_DIR  = "/usr/share/fonts/truetype/dejavu"

class PDF(FPDF):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.add_font(FONT, "",  f"{FONT_DIR}/DejaVuSans.ttf")
        self.add_font(FONT, "B", f"{FONT_DIR}/DejaVuSans-Bold.ttf")
        self.add_font(FONT, "I", f"{FONT_DIR}/DejaVuSans.ttf")
        self.add_font(FONT_MONO, "", f"{FONT_DIR}/DejaVuSansMono.ttf")
        self.add_font(FONT_MONO, "B", f"{FONT_DIR}/DejaVuSansMono-Bold.ttf")

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font(FONT, "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 6, "Wrangell Energy Future v2  |  Model User Guide", align="L")
        self.cell(0, 6, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT, "I", 7)
        self.set_text_color(*GRAY)
        self.cell(0, 10, "Illustrative model \u2014 not a rate-case or regulatory filing.  |  Data: EIA-861 2023, EIA-860 2025, SEAPA public sources", align="C")

    def section_title(self, num, title):
        self.ln(6)
        self.set_font(FONT, "B", 16)
        self.set_text_color(*NAVY)
        self.cell(0, 10, f"{num}.  {title}", new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.8)
        self.line(self.l_margin, y, self.l_margin + 60, y)
        self.set_line_width(0.2)
        self.ln(4)

    def sub_title(self, title):
        self.ln(3)
        self.set_font(FONT, "B", 12)
        self.set_text_color(*NAVY)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def sub_sub_title(self, title):
        self.ln(2)
        self.set_font(FONT, "B", 10)
        self.set_text_color(*ACCENT)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, txt):
        self.set_font(FONT, "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, txt)
        self.ln(1)

    def formula_block(self, txt):
        self.set_fill_color(*LTGRAY)
        self.set_font(FONT_MONO, "", 9)
        self.set_text_color(*DARK)
        x0 = self.l_margin + 4
        w  = self.w - self.l_margin - self.r_margin - 8
        self.set_x(x0)
        self.multi_cell(w, 5, txt, fill=True)
        self.ln(2)

    def inputs_line(self, txt):
        self.set_font(FONT, "I", 9)
        self.set_text_color(*GRAY)
        self.cell(0, 5, f"Inputs: {txt}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def feature_badge(self, label, color):
        self.set_font(FONT, "B", 7)
        self.set_fill_color(*color)
        self.set_text_color(*WHITE)
        w = self.get_string_width(label) + 6
        self.cell(w, 5, f" {label} ", fill=True)
        self.cell(3, 5, "")  # spacer


def build_pdf():
    pdf = PDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=True, margin=20)
    pw = pdf.w - pdf.l_margin - pdf.r_margin

    # ═══════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font(FONT, "B", 32)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 14, "Wrangell Energy Future", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font(FONT, "", 18)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 10, "Greensparc Anchor Customer Explorer", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font(FONT, "B", 14)
    pdf.set_text_color(*AMBER)
    pdf.cell(0, 8, "Version 2  \u2014  Model User Guide", align="C", new_x="LMARGIN", new_y="NEXT")

    # Divider
    pdf.ln(8)
    cx = pdf.w / 2
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.6)
    pdf.line(cx - 40, pdf.get_y(), cx + 40, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(8)

    # Summary block
    pdf.set_font(FONT, "", 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 5.5,
        "SEAPA's Tyee Lake hydropower is at capacity. Community load is growing fast from "
        "heat-pump adoption, forcing increasing reliance on expensive diesel. A third turbine "
        "(~$20M) is needed. This interactive model explores whether a Greensparc data-center "
        "anchor customer can make that expansion financeable \u2014 and drive community rates "
        "below today's level.\n\n"
        "Version 2 adds: total energy cost analysis (electricity + heating oil), seasonal/monthly "
        "dispatch, sensitivity analysis, an optimizer, scenario comparison, multi-community "
        "support (Wrangell + Cordova), in-app PDF export, and model backtesting against actuals.",
        align="C",
    )
    pdf.ln(10)

    # Scenario legend
    for label, color in [("Status Quo \u2014 diesel creep, rising rates", RED),
                         ("Expansion Only \u2014 capital burden on ratepayers", AMBER),
                         ("Expansion + Anchor \u2014 rates go down", ACCENT)]:
        pdf.set_fill_color(*color)
        pdf.rect(pdf.w/2 - 55, pdf.get_y() + 1, 5, 5, style="F")
        pdf.set_x(pdf.w/2 - 47)
        pdf.set_font(FONT, "", 10)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 7, label, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    # v2 feature badges
    pdf.set_font(FONT, "B", 10)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 7, "New in v2:", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    badges = [
        ("Total Energy Cost", TEAL), ("Monthly Dispatch", BLUE),
        ("Sensitivity", AMBER), ("Optimizer", ACCENT),
        ("Scenario Snapshots", NAVY), ("Multi-Community", RED),
        ("PDF Export", GRAY), ("Backtest", DARK),
    ]
    for label, color in badges:
        pdf.feature_badge(label, color)
    pdf.ln(8)

    pdf.set_font(FONT, "I", 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "Data: EIA-861 (2023), EIA-860 (2025), EIA-923 (2019-2024), AEDG, SEAPA public sources", align="C")

    # ═══════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.set_font(FONT, "B", 18)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 12, "Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    toc = [
        ("1", "How to Use the App"),
        ("2", "App Structure: Tabs & Features"),
        ("3", "Sidebar Controls Reference"),
        ("4", "Backend Calculations"),
        ("5", "New in v2: Feature Guide"),
        ("6", "Multi-Community Support"),
        ("7", "Data Sources & Caveats"),
    ]
    for num, title in toc:
        pdf.set_font(FONT, "B", 11)
        pdf.set_text_color(*NAVY)
        pdf.cell(10, 7, num + ".")
        pdf.set_font(FONT, "", 11)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1: HOW TO USE
    # ═══════════════════════════════════════════════════════════════════════
    pdf.section_title("1", "How to Use the App")

    pdf.body_text(
        "Launch:  streamlit run streamlit_app.py\n"
        "Requirements:  pip install streamlit pandas plotly numpy fpdf2\n\n"
        "The interface has two areas:"
    )
    pdf.sub_title("Sidebar (left)")
    pdf.body_text(
        "Quick Controls at top: the three parameters that matter most \u2014 anchor MW, anchor "
        "tariff, and diesel escalation. These are always visible without opening any expander.\n\n"
        "Advanced Settings (collapsed): all remaining parameters organized by category \u2014 "
        "System, Load Growth, Expansion Financing, Anchor Details, Community Baseline, and "
        "Heating Fuel Analysis.\n\n"
        "Community Selector: switch between Wrangell and Cordova (or future communities). "
        "All sidebar defaults update automatically.\n\n"
        "Pin/Clear Scenario: save the current configuration for side-by-side comparison. "
        "Pinned scenarios appear as dotted overlay lines on charts.\n\n"
        "PDF Export: download button at top of main panel generates a scenario report."
    )
    pdf.sub_title("Main Panel (right)")
    pdf.body_text(
        "Executive Summary banner at the top: a single dynamic paragraph summarizing anchor "
        "size, coverage %, rate outlook, household savings, and diesel avoided.\n\n"
        "Below that, six tabs with results (see Section 2)."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 2: APP STRUCTURE
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("2", "App Structure: Tabs & Features")

    tabs = [
        ("Rate Trajectory", "[1]",
         "The hero chart: three lines showing $/kWh from 2023 to 2035. A dashed gray "
         "reference marks today's rate. The green line dropping below it is the core value "
         "proposition. Per-scenario metrics show 2030 and 2035 rates.\n\n"
         "Model Validation (expandable): overlays actual diesel generation data from EIA-923 "
         "(2019-2024) as diamond markers, letting you see how well the model tracks reality."),

        ("Total Energy Cost", "[2]",
         "NEW in v2. The electricity rate is only part of the story. This tab shows total "
         "household energy cost: electricity + heating oil. Three metric cards compare an "
         "oil-heated home today vs a heat pump home under Scenario C.\n\n"
         "Key insight: a household using 800 gal/yr of heating oil at $5/gal = $4,000/yr. "
         "A heat pump at COP 2.5 replaces that with ~12,950 kWh at $0.12 = $1,554. "
         "Net savings ~$2,446/yr \u2014 even if electricity rates rise.\n\n"
         "Charts: average total energy cost by scenario, oil vs HP cost breakdown "
         "(stacked bars), and annual HP savings vs oil-heated home."),

        ("Diesel Displacement", "[3]",
         "Annual/Monthly toggle.\n\n"
         "Annual view: diesel usage trajectory (three lines), annual diesel cost (grouped bars), "
         "and energy mix stacked areas (hydro + diesel for each scenario).\n\n"
         "Monthly view (NEW in v2): stacked area chart showing hydro + diesel by month. "
         "Winter diesel spikes become visible \u2014 this is what caused the 2022 capacity crisis. "
         "A diesel heatmap (months vs years) reveals the seasonal concentration.\n\n"
         "Aggregate metrics always shown: total diesel avoided, cost savings, CO2, barrels."),

        ("Expansion Viability", "[4]",
         "Large coverage percentage display at top. Waterfall chart showing annual cost flow "
         "(debt \u2192 anchor offset \u2192 residual). Cumulative debt vs anchor contribution chart.\n\n"
         "Finance breakdown table: capex, debt share, rate/term, debt service, anchor revenue, "
         "margin, coverage %, residual.\n\n"
         "Sensitivity Analysis (NEW in v2): tornado chart showing which of 8 key parameters "
         "moves the Scenario C rate the most. Parameters are perturbed +/- 20-50% from current "
         "values. Sorted by impact magnitude."),

        ("Optimizer", "[5]",
         "NEW in v2. Find anchor configurations that achieve a specific goal.\n\n"
         "Three goal types: rate below target, coverage above target, or household savings "
         "above target. Set a target year (default 2030).\n\n"
         "Search space: anchor MW range and tariff range (adjustable sliders).\n\n"
         "Output: heatmap with MW on x-axis, tariff on y-axis, colored by the target metric. "
         "A white dashed contour line marks the feasibility boundary. A star marks the current "
         "configuration. The 'green zone' shows all configurations that meet the goal.\n\n"
         "Uses a 30x30 grid search (900 scenario evaluations, <2 sec with caching)."),

        ("Community Impact", "[6]",
         "Household bill grouped bars, bill comparison table, savings vs Status Quo table.\n\n"
         "Anchor economic impact: nameplate load, construction/operating jobs, payroll, "
         "local economic activity (scaled by spending multiplier), tariff revenue, margin."),
    ]

    for name, icon, desc in tabs:
        if pdf.get_y() > 200:
            pdf.add_page()
        pdf.sub_title(f"Tab {icon}  {name}")
        pdf.body_text(desc)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 3: SIDEBAR CONTROLS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("3", "Sidebar Controls Reference")
    pdf.body_text(
        "Parameters are organized into Quick Controls (always visible) and Advanced Settings. "
        "Defaults change based on the selected community."
    )

    controls = [
        ("Quick Controls", "Anchor Nameplate (MW)", "2.0 MW", "0.5-5.0",
         "Greensparc sizing", "Determines annual anchor energy demand and revenue."),

        ("Quick Controls", "Anchor Tariff ($/kWh)", "$0.12", "$0.07-0.20",
         "Above SEAPA, below retail", "MOST SENSITIVE. Margin above SEAPA cost = debt coverage."),

        ("Quick Controls", "Diesel Escalation (%/yr)", "3.0%", "0-6%",
         "Fuel inflation assumption", "Compounds annually. Higher = stronger expansion case."),

        ("System", "Baseline Load", "40,708 MWh/yr", "10k-80k",
         "EIA-861 2023", "Starting point for all load projections."),

        ("System", "Hydro Energy Cap", "40,200 MWh/yr", "10k-80k",
         "Back-calculated", "Ceiling of cheap hydro. Demand above = diesel."),

        ("System", "Wholesale Hydro Rate", "$93/MWh", "$50-150",
         "Back-calculated from EIA-861", "Cost of every hydro MWh. Floor for anchor margin."),

        ("System", "Fixed Costs", "$1,200,000/yr", "$500k-5M",
         "Estimate (pending audit)", "Flat annual cost in every scenario/year."),

        ("System", "Diesel All-in Cost", "$150/MWh", "$80-300",
         "Fully-loaded estimate", "Year-zero diesel unit cost."),

        ("System", "Diesel Floor", "200 MWh/yr", "0-2,000",
         "Minimum run hours", "Minimum diesel even when hydro is ample."),

        ("Load Growth", "Phase 1 Growth", "5.0%/yr", "1-10%",
         "Historical: +19% in 4 years", "Compound growth during rapid adoption."),

        ("Load Growth", "Phase 1 End", "2027", "2026-2028",
         "Assumption", "When growth transitions to steady-state."),

        ("Load Growth", "Phase 2 Growth", "2.0%/yr", "0.5-5%",
         "Assumption", "Long-term load trajectory."),

        ("Expansion", "Online Year", "2027", "2026-2029",
         "SEAPA target", "When new hydro + anchor come online."),

        ("Expansion", "New Energy (MWh/yr)", "37,000", "5k-60k",
         "5 MW x 8,760 x 0.845 CF", "Additional hydro from expansion."),

        ("Expansion", "Total Capex", "$20,000,000", "$5M-50M",
         "Engineering estimate", "Flows through PMT to annual debt."),

        ("Expansion", "Debt Share", "40%", "20-100%",
         "Proportional to load", "Fraction of capex community finances."),

        ("Expansion", "Financing Rate", "5.0%", "3-8%",
         "Municipal bond rate", "Interest rate on expansion debt."),

        ("Expansion", "Bond Term", "25 years", "20/25/30",
         "Standard terms", "Longer = lower annual, higher total interest."),

        ("Anchor", "Capacity Factor", "0.90", "0.70-0.99",
         "DC industry typical", "Nameplate x CF x 8,760 = annual MWh."),

        ("Community", "Residential Accounts", "1,174", "200-5,000",
         "EIA-861 2023", "Display only \u2014 scales household savings."),

        ("Community", "Household kWh/yr", "9,000", "3k-20k",
         "Estimate", "Converts rates to bills. Display only."),

        ("Community", "Spending Multiplier", "1.7x", "1.0-2.5",
         "Rural standard", "Display only \u2014 scales economic impact."),

        ("Community", "Jobs per MW", "1.5", "0.5-5.0",
         "Industry estimate", "Display only \u2014 estimates anchor jobs."),

        ("Heating Fuel", "Heating Oil (gal/yr)", "800", "200-1,500",
         "Typical Wrangell household", "Annual oil consumption for space heating."),

        ("Heating Fuel", "Oil Price ($/gal)", "$5.00", "$2-8",
         "DCRA 2024-2025", "Current heating oil price."),

        ("Heating Fuel", "Oil Escalation (%/yr)", "3.0%", "0-6%",
         "Assumption", "Annual oil price inflation."),

        ("Heating Fuel", "Heat Pump COP", "2.5", "1.5-4.0",
         "Cold-climate units", "Efficiency of heat pump conversion."),

        ("Heating Fuel", "HP Conversion (%/yr)", "5%", "0-20%",
         "Assumption", "Percent of oil homes converting per year."),

        ("Heating Fuel", "% Homes on Oil (2023)", "50%", "20-80%",
         "~50% as of 2023", "Starting fraction for conversion trajectory."),
    ]

    # Table rendering
    col_widths = [pw * 0.22, pw * 0.13, pw * 0.25, pw * 0.40]
    headers = ["Parameter", "Default", "Source", "Effect on Model"]

    current_group = ""
    for group, name, default, rng, source, effect in controls:
        if pdf.get_y() > 230:
            pdf.add_page()

        if group != current_group:
            current_group = group
            if pdf.get_y() > 220:
                pdf.add_page()
            pdf.ln(3)
            pdf.set_font(FONT, "B", 11)
            pdf.set_text_color(*NAVY)
            pdf.set_fill_color(*HDRBLUE)
            pdf.cell(sum(col_widths), 7, f"  {group}", fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

            pdf.set_font(FONT, "B", 8)
            pdf.set_text_color(*WHITE)
            pdf.set_fill_color(*NAVY)
            x0 = pdf.get_x()
            for i, h in enumerate(headers):
                pdf.set_x(x0 + sum(col_widths[:i]))
                pdf.cell(col_widths[i], 6, f" {h}", fill=True)
            pdf.ln(6)

        pdf.set_font(FONT, "", 7.5)
        pdf.set_text_color(*DARK)

        texts = [f"{name}\n({rng})", default, source, effect]
        y0 = pdf.get_y()
        x0 = pdf.get_x()
        for i, txt in enumerate(texts):
            pdf.set_x(x0 + sum(col_widths[:i]))
            pdf.set_font(FONT, "B" if i == 0 else "", 7.5)
            pdf.multi_cell(col_widths[i], 3.8, f" {txt}", max_line_height=3.8)
            pdf.set_y(y0)

        actual_heights = []
        for i, txt in enumerate(texts):
            pdf.set_x(x0 + sum(col_widths[:i]))
            n = pdf.multi_cell(col_widths[i], 3.8, f" {txt}", max_line_height=3.8, dry_run=True, output="LINES")
            actual_heights.append(len(n) * 3.8)

        pdf.set_y(y0 + max(actual_heights) + 1)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + sum(col_widths), pdf.get_y())
        pdf.ln(1)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 4: BACKEND CALCULATIONS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("4", "Backend Calculations")
    pdf.body_text(
        "The model runs calculations for each year (2023-2035) across three scenarios. "
        "v2 adds monthly dispatch and heating economics alongside the original annual model."
    )

    calcs = [
        ("1", "Community Load (two-phase growth)",
         "if year <= phase1_end:\n"
         "  load = base_mwh x (1 + r1)^(year - 2023)\n"
         "else:\n"
         "  terminal = base_mwh x (1 + r1)^(phase1_end - 2023)\n"
         "  load = terminal x (1 + r2)^(year - phase1_end)",
         "base_mwh, r1, phase1_end, r2"),

        ("2", "SEAPA Energy Cap",
         "if expansion AND year >= expansion_year:\n"
         "  cap = seapa_cap + expansion_new_mwh\n"
         "else:\n"
         "  cap = seapa_cap",
         "seapa_cap, expansion_new_mwh, expansion_year"),

        ("3", "Anchor Energy Demand",
         "anchor_mwh = anchor_mw x anchor_cf x 8,760\n"
         "(Scenario C only, year >= expansion_year)",
         "anchor_mw, anchor_cf"),

        ("4", "Diesel Dispatch",
         "diesel_mwh = max(diesel_floor, total_mwh - cap)",
         "diesel_floor, total demand, cap"),

        ("5", "Hydro Dispatch",
         "hydro_mwh = total_mwh - diesel_mwh",
         "total demand, diesel dispatch"),

        ("6", "Diesel Cost Escalation",
         "diesel_rate = diesel_base x (1 + escalation)^(year - 2023)",
         "diesel_base_cost, diesel_escalation"),

        ("7", "Total Annual Cost",
         "total = fixed + (seapa_rate x hydro) + (diesel_rate x diesel) + debt_service",
         "fixed_cost, seapa_rate, debt_service_yr"),

        ("8", "Retail Rate",
         "rate = max($0.05, (total_cost - anchor_revenue) / (community_mwh x 1000))",
         "total cost, anchor revenue, community load"),

        ("9", "PMT (Debt Service)",
         "principal = capex x share\n"
         "payment = principal x r x (1+r)^n / ((1+r)^n - 1)",
         "capex, share, financing_rate, bond_term"),

        ("10", "Anchor Capex Coverage",
         "margin = anchor_mwh x (tariff - seapa_rate)\n"
         "coverage = margin / debt_service_yr",
         "anchor_tariff, seapa_rate, debt_service"),

        ("11", "Monthly Dispatch (v2)",
         "month_load = annual_load x load_shape[m] / 12\n"
         "month_cap = annual_cap x hydro_shape[m] / 12\n"
         "month_diesel = max(floor/12, month_load - month_cap)\n"
         "month_hydro = month_load - month_diesel",
         "load_shape (12 weights), hydro_shape (12 weights)"),

        ("12", "Heating Economics (v2)",
         "heating_kwh = oil_gal x 138,500 BTU / (COP x 3,412 BTU/kWh)\n"
         "oil_home_total = base_elec_bill + (oil_gal x oil_price)\n"
         "hp_home_total = (base_kwh + heating_kwh) x electric_rate\n"
         "savings = oil_home_total - hp_home_total",
         "hh_oil_gal, oil_price, heat_pump_cop, electric_rate"),

        ("13", "Sensitivity Analysis (v2)",
         "For each of 8 parameters:\n"
         "  perturb +/- 20-50% from current value\n"
         "  recompute Scenario C rate at target year\n"
         "  swing = |high_rate - low_rate|\n"
         "Sort by swing descending for tornado chart",
         "8 key parameters, target year"),

        ("14", "Optimizer Grid Search (v2)",
         "For each (MW, tariff) in 30x30 grid:\n"
         "  compute_scenarios(anchor_mw=MW, tariff=tariff)\n"
         "  check if target constraint met\n"
         "  store rate, coverage, savings\n"
         "Display as heatmap with feasibility contour",
         "MW range, tariff range, target goal, target year"),
    ]

    for num, title, formula, inputs in calcs:
        if pdf.get_y() > 220:
            pdf.add_page()

        pdf.set_font(FONT, "B", 11)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 7, f"Calculation {num}:  {title}", new_x="LMARGIN", new_y="NEXT")
        pdf.formula_block(formula)
        pdf.inputs_line(inputs)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 5: v2 FEATURE GUIDE
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("5", "New in v2: Feature Guide")

    features = [
        ("Progressive Disclosure",
         "The sidebar now has three Quick Controls at the top \u2014 anchor MW, anchor tariff, "
         "and diesel escalation. These are the parameters that move the needle most. Everything "
         "else is collapsed in 'Advanced Settings'. Most stakeholders never need to open it."),

        ("Executive Summary Banner",
         "A dynamic paragraph above the tabs summarizes the current scenario: anchor size, "
         "coverage %, rate outlook, cumulative savings, and diesel avoided. Updates instantly "
         "when sliders change."),

        ("Total Energy Cost Tab",
         "Shows electricity + heating oil together. Reframes the narrative: even if electricity "
         "rates rise modestly, households switching from oil to heat pumps save thousands per year "
         "on total energy. Includes cost breakdown charts and conversion trajectory."),

        ("Monthly Dispatch",
         "Seasonal load shape (winter peak ~1.2x, summer trough ~0.8x) and hydro availability "
         "(inverse \u2014 runoff high in summer, low in winter). Reveals that diesel exposure is "
         "worst in winter months, exactly when heat pump loads are highest. Toggle between annual "
         "and monthly views in the Diesel Displacement tab. Heatmap shows diesel concentration."),

        ("Sensitivity / Tornado Chart",
         "Perturbs 8 key parameters by +/- 20-50%. Measures the swing in Scenario C rate. "
         "Horizontal bar chart sorted by impact magnitude. Answers 'which parameters matter most?' "
         "at a glance. Anchor tariff and diesel escalation typically dominate."),

        ("Scenario Snapshots",
         "Pin the current configuration with one click. Adjust sliders to explore alternatives. "
         "Pinned scenarios appear as dotted overlay lines on rate trajectory, diesel, and household "
         "bill charts. Clear pin to reset. Essential for live stakeholder meetings."),

        ("Optimizer",
         "Find anchor configurations meeting a specific goal. Three goal types: rate below target, "
         "coverage above target, or household savings above target. Search over an MW x tariff grid. "
         "Heatmap visualization with contour line at the target threshold. Star marks current config. "
         "Insight text summarizes the feasible region."),

        ("Backtest vs Actuals",
         "Loads actual diesel generation from EIA-923 (2019-2024) and AEDG (pre-2019). Overlays "
         "diamond markers on the diesel chart. Collapsible section in the Rate Trajectory tab. "
         "Builds credibility: 'the model tracks historical data'."),

        ("PDF Export",
         "Download button generates a branded scenario report with executive summary, parameter "
         "table, rate projections, key outcomes, and caveats. Takes current slider values."),
    ]

    for name, desc in features:
        if pdf.get_y() > 220:
            pdf.add_page()
        pdf.sub_title(name)
        pdf.body_text(desc)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 6: MULTI-COMMUNITY
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("6", "Multi-Community Support")

    pdf.body_text(
        "v2 supports multiple Alaska communities. Each community has its own configuration "
        "dict with customized defaults for all parameters, seasonal load/hydro shapes, and "
        "grid information. Switching communities in the sidebar updates all defaults."
    )

    pdf.sub_title("Wrangell (default)")
    pdf.body_text(
        "Grid: SEAPA Grid (Southeast). Hydro: SEAPA Tyee Lake. Diesel: Plant 95 (12 MW). "
        "Base load: 40,708 MWh/yr (EIA-861 2023). Rate: $0.1232/kWh. Load growing at ~4.5%/yr "
        "from heat pump adoption. Expansion: 3rd turbine at Tyee Lake, ~$20M, target Dec 2027. "
        "Wrangell's share: 40%."
    )

    pdf.sub_title("Cordova")
    pdf.body_text(
        "Grid: Cordova Grid (isolated \u2014 not connected to any other grid). "
        "Hydro: Power Creek (6 MW) + Humpback Creek (1.2 MW). Diesel: Orca plant (7.7 MW). "
        "Battery: Eyak Service Center BESS (1 MW, added ~2019). "
        "Base load: ~24,000 MWh/yr. Hydro share: ~85-90%. "
        "Different seasonal patterns: stronger spring runoff, steeper winter diesel reliance. "
        "Expansion opportunity: additional hydro or battery storage."
    )

    pdf.sub_title("Adding New Communities")
    pdf.body_text(
        "To add a community, create a new entry in lib/communities.py with:\n"
        "- FIPS code, EIA plant IDs, grid name\n"
        "- Default values for all sidebar parameters\n"
        "- 12-month load shape (winter peak / summer trough weights)\n"
        "- 12-month hydro shape (runoff-driven availability weights)\n\n"
        "The AEDG dataset covers 355 Alaska communities with fuel prices, generation, "
        "and infrastructure data. Any community with sufficient data can be added."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 7: DATA SOURCES & CAVEATS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("7", "Data Sources & Caveats")

    pdf.sub_title("Data Sources")
    pdf.body_text(
        "EIA-861 Short Form (2023): Baseline load, revenue, customer counts. Utility ID 21015.\n\n"
        "EIA-860 (2025): Diesel plant capacity and generator specifications.\n\n"
        "EIA-923 (2019-2024): Monthly plant-level generation and fuel consumption. "
        "Used for backtest actuals and monthly dispatch calibration.\n\n"
        "Alaska Energy Data Gateway (AEDG): Community-level data for 355 communities \u2014 "
        "fuel prices (2005-2025), monthly generation (2001-2021), rates, capacity, employment, "
        "population, transportation. Published by ACEP/UAF under CC-BY-4.0.\n\n"
        "EIA API v2: Statewide monthly generation, retail sales, and generator capacity "
        "(2019-2025). Used for cross-validation.\n\n"
        "SEAPA/FERC Filings: Tyee Lake capacity, utilization, 3rd turbine need.\n\n"
        "Ketchikan Daily News / Frontier Media (2024): SEAPA capacity constraints, heat pump "
        "adoption data, 3rd turbine cost estimates."
    )

    pdf.sub_title("Model Caveats")
    pdf.body_text(
        "This is an illustrative projection tool, not a rate-case or regulatory filing.\n\n"
        "- SEAPA wholesale rate ($93/MWh) is back-calculated, not a published tariff.\n\n"
        "- Wrangell's 40% SEAPA debt share is a proportional-load estimate.\n\n"
        "- Diesel costs use fully-loaded estimates; actual costs vary with oil markets.\n\n"
        "- Two-phase load growth is assumption-driven.\n\n"
        "- Fixed costs (~$1.2M/yr) are estimates pending audit.\n\n"
        "- Monthly dispatch uses parameterized seasonal shapes, not historical hourly data.\n\n"
        "- Heating economics assume uniform oil consumption across households.\n\n"
        "- Cordova defaults are estimates \u2014 not yet validated against utility filings.\n\n"
        "- The optimizer uses grid search (finite resolution); boundary cases may be missed."
    )

    pdf.sub_title("Technical Stack")
    pdf.body_text(
        "Streamlit (app framework) + Plotly (charts) + Pandas (data) + NumPy (optimizer grid) + "
        "fpdf2 (PDF export). Python 3.12.\n\n"
        "Codebase: ~2,600 lines across 13 modules in lib/ + streamlit_app.py orchestrator.\n\n"
        "All computation is cached with @st.cache_data. The optimizer's 900-point grid search "
        "completes in <2 seconds."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # OUTPUT
    # ═══════════════════════════════════════════════════════════════════════
    out = "/home/kai/Documents/AKEnergy/Wrangell_Energy_Model_Guide.pdf"
    pdf.output(out)
    print(f"PDF written to: {out}")


if __name__ == "__main__":
    build_pdf()
