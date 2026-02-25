#!/usr/bin/env python3
"""
Generate a readable PDF user guide for the Wrangell Energy Future model.
Run:  python3 generate_guide_pdf.py
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
HDRBLUE = (230, 240, 255)

FONT      = "DejaVu"
FONT_MONO = "DejaVuMono"

FONT_DIR  = "/usr/share/fonts/truetype/dejavu"

class PDF(FPDF):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.add_font(FONT, "",  f"{FONT_DIR}/DejaVuSans.ttf", uni=True)
        self.add_font(FONT, "B", f"{FONT_DIR}/DejaVuSans-Bold.ttf", uni=True)
        self.add_font(FONT, "I", f"{FONT_DIR}/DejaVuSans.ttf", uni=True)  # no italic file, use regular
        self.add_font(FONT_MONO, "", f"{FONT_DIR}/DejaVuSansMono.ttf", uni=True)
        self.add_font(FONT_MONO, "B", f"{FONT_DIR}/DejaVuSansMono-Bold.ttf", uni=True)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font(FONT, "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 6, "Wrangell Energy Future  |  Model User Guide", align="L")
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


def build_pdf():
    pdf = PDF("P", "mm", "Letter")
    pdf.set_auto_page_break(auto=True, margin=20)
    pw = pdf.w - pdf.l_margin - pdf.r_margin  # printable width

    # ═══════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font(FONT, "B", 32)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 14, "Wrangell Energy Future", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font(FONT, "", 18)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 10, "Greensparc Anchor Customer Explorer", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font(FONT, "", 13)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 8, "Model User Guide & Calculation Reference", align="C", new_x="LMARGIN", new_y="NEXT")

    # Divider
    pdf.ln(10)
    cx = pdf.w / 2
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.6)
    pdf.line(cx - 40, pdf.get_y(), cx + 40, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(10)

    # Summary block
    pdf.set_font(FONT, "", 10)
    pdf.set_text_color(*DARK)
    pdf.multi_cell(0, 5.5,
        "SEAPA's Tyee Lake hydropower is at capacity. Wrangell's electricity load is growing "
        "fast from heat-pump adoption, forcing increasing reliance on expensive diesel generation. "
        "A third turbine (~$20M) is needed. This interactive model explores whether a Greensparc "
        "data-center anchor customer can make that expansion financeable — and drive community "
        "electricity rates below today's level.\n\n"
        "This document describes every adjustable parameter in the model sidebar, where each "
        "default value comes from, and the 20 backend calculations that drive the three scenarios.",
        align="C",
    )
    pdf.ln(12)

    # Scenario legend
    for label, color in [("Status Quo — diesel creep, rising rates", RED),
                         ("Expansion Only — capital burden on ratepayers", AMBER),
                         ("Expansion + Anchor — rates go down", ACCENT)]:
        pdf.set_fill_color(*color)
        pdf.rect(pdf.w/2 - 55, pdf.get_y() + 1, 5, 5, style="F")
        pdf.set_x(pdf.w/2 - 47)
        pdf.set_font(FONT, "", 10)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 7, label, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(20)
    pdf.set_font(FONT, "I", 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "Data sources: EIA-861 (2023), EIA-860 (2025), SEAPA/FERC filings, Ketchikan Daily News (2024)", align="C", new_x="LMARGIN", new_y="NEXT")

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
        ("2", "Sidebar Controls Reference (23 Parameters)"),
        ("3", "Backend Calculations (20 Formulas)"),
        ("4", "Interpreting the Results"),
        ("5", "Data Sources & Caveats"),
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
        "Launch the app with:  streamlit run streamlit_app.py\n"
        "Requirements:  pip install streamlit pandas plotly\n\n"
        "The interface has two areas:"
    )
    pdf.sub_title("Sidebar (left)")
    pdf.body_text(
        "Contains all 23 adjustable parameters organized into collapsible sections: "
        "Wrangell System, Load Growth, SEAPA Expansion, Greensparc Anchor Customer, and Community Baseline. "
        "Change any slider or input and the model recalculates instantly."
    )
    pdf.sub_title("Main Panel (right)")
    pdf.body_text(
        "Displays results across four tabs:\n\n"
        "  1. Rate Trajectory — line chart of $/kWh through 2035 for all three scenarios\n"
        "  2. Diesel Displacement — diesel usage, cost bars, and energy-mix stacked areas\n"
        "  3. Expansion Viability — waterfall and cumulative charts showing anchor debt coverage\n"
        "  4. Community Impact — household bills, savings tables, jobs, and economic activity\n\n"
        "At the top, three metric cards show the 2030 rate outlook for each scenario compared to today's rate."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 2: SIDEBAR CONTROLS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("2", "Sidebar Controls Reference")
    pdf.body_text(
        "The table below documents every adjustable parameter. \"Source\" indicates where the "
        "default value was derived. \"Model Effect\" describes how changing the parameter "
        "propagates through the calculations."
    )

    controls = [
        # (group, name, default, range, source, effect)
        ("Wrangell System", "2023 Baseline Load", "40,708 MWh/yr", "20k-80k",
         "EIA-861 2023 Short Form, utility 21015",
         "Starting point for all load projections. Higher values increase future demand, accelerate diesel reliance, and raise rates in every scenario."),

        ("Wrangell System", "Current SEAPA Energy Cap", "40,200 MWh/yr", "20k-60k",
         "Back-calculated: 40,708 total minus 508 diesel",
         "Ceiling of cheap hydro. Demand above this cap is served by diesel. Lowering it accelerates diesel dependency."),

        ("Wrangell System", "SEAPA Wholesale Rate", "$93/MWh", "$50-150",
         "Back-calculated from 2023 EIA-861 revenue",
         "Cost of every hydro MWh. Also sets the floor for anchor margin — anchor only contributes if tariff exceeds this."),

        ("Wrangell System", "Fixed Costs", "$1,200,000/yr", "$500k-5M",
         "Estimate: 5 FT staff + overhead (pending audit)",
         "Flat annual cost in every scenario/year. Raises baseline rate equally across all scenarios."),

        ("Wrangell System", "Diesel All-in Cost", "$150/MWh", "$80-300",
         "Fully-loaded estimate incl. remote delivery, O&M, permits",
         "Year-zero diesel unit cost. Higher values widen the Status Quo cost penalty and increase expansion savings."),

        ("Wrangell System", "Diesel Escalation", "3.0%/yr", "0-6%",
         "Fuel price inflation assumption",
         "Compounds annually on diesel cost. At 3%, diesel roughly doubles in 24 years. Higher values make Status Quo progressively worse."),

        ("Wrangell System", "Diesel Floor", "200 MWh/yr", "0-2,000",
         "Minimum for testing, maintenance, peak spikes",
         "Minimum diesel even when hydro is ample. Small effect unless set high."),

        ("Load Growth", "Phase 1 Growth Rate", "5.0%/yr", "1-10%",
         "Historical: +19% over 2019-2023 (~4.5% CAGR)",
         "Compound growth during rapid heat-pump adoption. Higher values accelerate load, worsen Status Quo, increase expansion urgency."),

        ("Load Growth", "Phase 1 End Year", "2027", "2026-2028",
         "Assumption: adoption saturates ~4 years out",
         "When growth transitions from fast to steady-state. Later = more years of fast growth and higher peak loads."),

        ("Load Growth", "Phase 2 Growth Rate", "2.0%/yr", "0.5-5%",
         "Post-saturation baseline growth assumption",
         "Long-term load trajectory. Even small changes compound significantly over 2028-2035."),

        ("SEAPA Expansion", "Target Online Year", "2027", "2026-2029",
         "SEAPA confirmed target: Dec 2027",
         "When new hydro + anchor come online. Delay extends diesel reliance and shifts all benefits later."),

        ("SEAPA Expansion", "New Energy for Wrangell", "37,000 MWh/yr", "10k-60k",
         "5 MW x 8,760 hr x 0.845 CF (Wrangell share)",
         "Additional hydro capacity from expansion. Must exceed load growth + anchor to eliminate structural diesel."),

        ("SEAPA Expansion", "Total Expansion Capex", "$20,000,000", "$10M-50M",
         "SEAPA 3rd turbine engineering estimate",
         "Flows through PMT formula to annual debt service. Higher capex = larger debt payments."),

        ("SEAPA Expansion", "Wrangell Debt Share", "40%", "20-60%",
         "Proportional to load vs total SEAPA membership",
         "Fraction of capex Wrangell finances. At 40% of $20M = $8M principal."),

        ("SEAPA Expansion", "Financing Rate", "5.0%", "3-8%",
         "Municipal bond rate assumption",
         "Interest rate on debt. Higher rates increase annual payments, making anchor coverage more critical."),

        ("SEAPA Expansion", "Bond Term", "25 years", "20/25/30",
         "Standard municipal bond terms",
         "Longer terms reduce annual payments but increase total interest paid."),

        ("Anchor Customer", "Nameplate Load", "2.0 MW", "0.5-5.0",
         "Greensparc data-center sizing",
         "Combined with capacity factor, determines annual anchor demand and revenue. Larger = more revenue but more hydro consumed."),

        ("Anchor Customer", "Capacity Factor", "0.90", "0.70-0.99",
         "Data center typical: 0.85-0.95",
         "Fraction of time at full load. Nameplate x CF x 8,760 = annual MWh. Higher CF = more energy and revenue."),

        ("Anchor Customer", "Anchor Tariff", "$0.12/kWh", "$0.07-0.20",
         "Proposed: above SEAPA ($0.093) but below retail ($0.123)",
         "MOST SENSITIVE LEVER. Margin above SEAPA cost x MWh = annual debt coverage. Determines whether Scenario C beats today's rate."),

        ("Community", "Residential Accounts", "1,174", "500-3,000",
         "EIA-861 2023 customer count",
         "Display only — scales per-household savings. Does not affect rates or system economics."),

        ("Community", "Avg Household kWh/yr", "9,000", "3k-20k",
         "Estimate for Wrangell residential usage",
         "Converts $/kWh to annual bills. Display only."),

        ("Community", "Local Spending Multiplier", "1.7x", "1.0-2.5",
         "Standard rural economic multiplier",
         "Display only — scales economic impact estimates on Community tab."),

        ("Community", "Jobs per MW", "1.5", "0.5-5.0",
         "Industry estimate for operating data centers",
         "Display only — estimates ongoing jobs on Community tab."),
    ]

    # Table rendering
    col_widths = [pw * 0.22, pw * 0.13, pw * 0.25, pw * 0.40]
    headers = ["Parameter", "Default", "Source", "Effect on Model"]

    current_group = ""
    for group, name, default, rng, source, effect in controls:
        # Check space — need ~30mm for a row
        if pdf.get_y() > 230:
            pdf.add_page()

        # Group header
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

            # Column headers
            pdf.set_font(FONT, "B", 8)
            pdf.set_text_color(*WHITE)
            pdf.set_fill_color(*NAVY)
            x0 = pdf.get_x()
            for i, h in enumerate(headers):
                pdf.set_x(x0 + sum(col_widths[:i]))
                pdf.cell(col_widths[i], 6, f" {h}", fill=True)
            pdf.ln(6)

        # Data row
        pdf.set_font(FONT, "", 7.5)
        pdf.set_text_color(*DARK)

        # Calculate row height based on longest content
        texts = [f"{name}\n({rng})", default, source, effect]
        line_heights = []
        for i, txt in enumerate(texts):
            # Estimate lines needed
            chars_per_line = max(1, int(col_widths[i] / 1.8))
            n_lines = max(1, len(txt) // chars_per_line + txt.count('\n') + 1)
            line_heights.append(n_lines)
        row_h = max(line_heights) * 3.8
        row_h = max(row_h, 12)

        # Alternate row shading
        y0 = pdf.get_y()
        pdf.set_fill_color(*LTGRAY)

        x0 = pdf.get_x()
        for i, txt in enumerate(texts):
            pdf.set_x(x0 + sum(col_widths[:i]))
            pdf.set_font(FONT, "B" if i == 0 else "", 7.5)
            pdf.multi_cell(col_widths[i], 3.8, f" {txt}", max_line_height=3.8)
            pdf.set_y(y0)

        # Move past the row
        actual_heights = []
        for i, txt in enumerate(texts):
            pdf.set_x(x0 + sum(col_widths[:i]))
            n = pdf.multi_cell(col_widths[i], 3.8, f" {txt}", max_line_height=3.8, dry_run=True, output="LINES")
            actual_heights.append(len(n) * 3.8)

        pdf.set_y(y0 + max(actual_heights) + 1)

        # Separator line
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + sum(col_widths), pdf.get_y())
        pdf.ln(1)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 3: BACKEND CALCULATIONS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("3", "Backend Calculations")
    pdf.body_text(
        "The model runs 20 calculations for each year (2023-2035) across three scenarios. "
        "Hydro is dispatched first as the cheapest source; diesel fills the gap. Anchor revenue "
        "offsets total system cost, reducing the rate borne by community customers."
    )

    calcs = [
        ("1", "Community Load Projection",
         "Two-phase compound growth models Wrangell's demand from existing customers.",
         "if year <= phase1_end:\n"
         "  load = base_mwh x (1 + r1)^(year - 2023)\n"
         "else:\n"
         "  terminal = base_mwh x (1 + r1)^(phase1_end - 2023)\n"
         "  load = terminal x (1 + r2)^(year - phase1_end)",
         "base_mwh, r1, phase1_end, r2"),

        ("2", "SEAPA Energy Cap",
         "Maximum hydro energy available. Steps up when the 3rd turbine comes online.",
         "if expansion AND year >= expansion_year:\n"
         "  cap = seapa_cap + expansion_new_mwh\n"
         "else:\n"
         "  cap = seapa_cap",
         "seapa_cap, expansion_new_mwh, expansion_year"),

        ("3", "Anchor Energy Demand",
         "Annual MWh consumed by the anchor customer. Only active in Scenario C post-expansion.",
         "anchor_mwh_yr = anchor_mw x anchor_cf x 8,760\n"
         "(only in Scenario C, year >= expansion_year)",
         "anchor_mw, anchor_cf"),

        ("4", "Total System Demand",
         "Everything the grid must serve.",
         "total_mwh = community_mwh + anchor_mwh",
         "Calc #1 + Calc #3"),

        ("5", "Diesel Dispatch",
         "Diesel fills whatever hydro can't cover, subject to an operational floor.",
         "diesel_mwh = max(diesel_floor, total_mwh - cap)",
         "diesel_floor, Calc #4, Calc #2"),

        ("6", "Hydro Dispatch",
         "The complement of diesel — everything not served by diesel.",
         "hydro_mwh = total_mwh - diesel_mwh",
         "Calc #4, Calc #5"),

        ("7", "Diesel Unit Cost Escalation",
         "Diesel gets more expensive each year due to fuel inflation.",
         "diesel_rate = diesel_base_cost x (1 + escalation)^(year - 2023)",
         "diesel_base_cost, diesel_escalation"),

        ("8", "SEAPA Hydro Cost",
         "Total annual cost of hydropower at the wholesale rate.",
         "seapa_cost = seapa_rate x hydro_mwh",
         "seapa_rate, Calc #6"),

        ("9", "Diesel Cost",
         "Total annual cost of diesel generation.",
         "diesel_cost = diesel_rate x diesel_mwh",
         "Calc #7, Calc #5"),

        ("10", "Annual Debt Service (PMT)",
         "Standard annuity formula for Wrangell's share of expansion financing.",
         "principal = capex x wrangell_share\n"
         "payment = principal x r x (1+r)^n / ((1+r)^n - 1)\n"
         "(only Scenarios B & C, year >= expansion_year)",
         "capex, wrangell_share, financing_rate, bond_term"),

        ("11", "Anchor Revenue",
         "Gross annual revenue from the anchor customer's tariff payments.",
         "anchor_revenue = anchor_mwh x anchor_tariff_mwh\n"
         "(only Scenario C, year >= expansion_year)",
         "anchor_tariff, Calc #3"),

        ("12", "Total Annual System Cost",
         "Full cost of running Wrangell's electric system for one year.",
         "total_cost = fixed_cost + seapa_cost + diesel_cost + debt_service",
         "fixed_cost, Calc #8, #9, #10"),

        ("13", "Community Cost",
         "What existing ratepayers actually bear after anchor offsets.",
         "community_cost = total_cost - anchor_revenue\n"
         "(In Scenarios A & B, anchor_revenue = 0)",
         "Calc #12, Calc #11"),

        ("14", "Retail Rate",
         "Cost per kWh for Wrangell residents, with a regulatory floor.",
         "rate = max($0.05, community_cost / (community_mwh x 1,000))",
         "Calc #13, Calc #1"),

        ("15", "Anchor Margin",
         "Annual dollar contribution toward expansion debt — the key financial mechanism.",
         "margin = anchor_mwh_yr x (anchor_tariff - seapa_rate)",
         "anchor_tariff, seapa_rate, Calc #3"),

        ("16", "Anchor Capex Coverage Ratio",
         "Fraction of Wrangell's annual debt covered by anchor margin. >= 100% means anchor fully funds expansion.",
         "coverage = margin / debt_service_yr",
         "Calc #15, Calc #10"),

        ("17", "Diesel Avoided (C vs A)",
         "Total diesel generation eliminated by Expansion + Anchor vs Status Quo.",
         "avoided = SUM(diesel_A[year] - diesel_C[year])  for 2023-2035",
         "Calc #5 across scenarios"),

        ("18", "CO2 and Barrels Avoided",
         "Environmental impact using standard diesel emission and energy density factors.",
         "co2_tonnes = avoided_mwh x 0.7\n"
         "barrels = avoided_mwh / 0.01709",
         "Calc #17"),

        ("19", "Household Annual Bill",
         "Converts per-kWh rate to a yearly dollar figure for a typical household.",
         "bill = rate_kwh x hh_kwh",
         "Calc #14, hh_kwh"),

        ("20", "Cumulative Household Savings",
         "Total savings per household from choosing Scenario C over Status Quo, 2027-2035.",
         "savings = SUM((rate_A[y] - rate_C[y]) x hh_kwh)  for y in 2027-2035\n"
         "community_wide = savings x n_hh",
         "Calc #14, hh_kwh, n_hh"),
    ]

    for num, title, desc, formula, inputs in calcs:
        # Check if we need a new page (need ~45mm)
        if pdf.get_y() > 225:
            pdf.add_page()

        # Number + title
        pdf.set_font(FONT, "B", 11)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 7, f"Calculation {num}:  {title}", new_x="LMARGIN", new_y="NEXT")

        # Description
        pdf.set_font(FONT, "", 9.5)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(1)

        # Formula box
        pdf.formula_block(formula)

        # Inputs
        pdf.inputs_line(inputs)

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 4: INTERPRETING RESULTS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("4", "Interpreting the Results")

    pdf.sub_title("Rate Trajectory Tab")
    pdf.body_text(
        "The hero chart. Three lines show $/kWh from 2023 to 2035. A dashed gray line marks "
        "today's rate (12.32 cents/kWh). The green Scenario C line dropping below that reference "
        "line is the central value proposition: the anchor customer doesn't just prevent rate "
        "increases — it actively lowers rates below today's level."
    )

    pdf.sub_title("Diesel Displacement Tab")
    pdf.body_text(
        "Shows the physical consequence of each scenario. Under Status Quo, diesel usage grows "
        "from ~500 MWh/yr to thousands of MWh/yr by 2035. The stacked area charts make it "
        "visually clear how much of Wrangell's power comes from expensive diesel vs cheap hydro. "
        "The aggregate metrics (MWh avoided, cost saved, CO2 reduced) quantify the environmental "
        "and financial benefit."
    )

    pdf.sub_title("Expansion Viability Tab")
    pdf.body_text(
        "The large percentage display at the top is the single most important number: what "
        "fraction of Wrangell's expansion debt the anchor covers. The waterfall chart breaks "
        "down the annual flow: debt service in, anchor margin offsetting, residual on ratepayers. "
        "The cumulative chart shows whether anchor contributions keep pace with debt over time. "
        "Green shading between the lines = anchor is covering more than debt."
    )

    pdf.sub_title("Community Impact Tab")
    pdf.body_text(
        "Translates system-level economics into household-level outcomes. The grouped bar chart "
        "shows annual bills side by side. The savings table quantifies the per-household and "
        "community-wide benefit of Scenario C vs Status Quo. The economic impact panel estimates "
        "jobs, payroll, and local spending from the anchor customer."
    )

    pdf.sub_title("Key Sensitivities to Explore")
    pdf.body_text(
        "1. Anchor Tariff: slide from $0.10 to $0.14/kWh and watch coverage swing from "
        "partial to surplus. This is the most sensitive lever.\n\n"
        "2. Anchor Size: increasing from 2 MW to 3 MW dramatically increases margin.\n\n"
        "3. Diesel Escalation: at 5%/yr instead of 3%, the Status Quo becomes much worse, "
        "strengthening the expansion case.\n\n"
        "4. Load Growth Rate: faster Phase 1 growth accelerates the urgency — diesel costs "
        "balloon sooner.\n\n"
        "5. Wrangell Debt Share: lowering from 40% to 30% reduces annual payments and improves "
        "all expansion scenarios."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 5: DATA SOURCES & CAVEATS
    # ═══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("5", "Data Sources & Caveats")

    pdf.sub_title("Data Sources")
    pdf.body_text(
        "EIA-861 Short Form (2023): Wrangell baseline load (40,708 MWh), revenue ($5,010,000), "
        "customer count (1,174 residential). Utility ID 21015.\n\n"
        "EIA-860 (2025): Wrangell diesel plant capacity and specifications. Plant ID 95.\n\n"
        "SEAPA/FERC Filings: Tyee Lake hydro capacity, utilization, and the confirmed need "
        "for a 3rd turbine.\n\n"
        "Ketchikan Daily News / Frontier Media (2024): Local reporting on SEAPA capacity "
        "constraints and expansion planning.\n\n"
        "SEAPA Wholesale Rate ($93/MWh): Back-calculated from 2023 actuals — not a published "
        "tariff. Formula: (total revenue - fixed costs - diesel costs) / hydro MWh."
    )

    pdf.sub_title("Model Caveats")
    pdf.body_text(
        "This is an illustrative projection tool, not a rate-case or regulatory filing.\n\n"
        "- The SEAPA wholesale rate is inferred, not published. Actual contract terms "
        "may differ.\n\n"
        "- Wrangell's 40% SEAPA debt share is a proportional-load estimate. Actual allocation "
        "depends on inter-utility agreements.\n\n"
        "- Diesel costs use fully-loaded estimates including remote fuel delivery. Actual "
        "costs vary with oil markets and barge schedules.\n\n"
        "- Two-phase load growth is assumption-driven. Actual heat pump adoption rates may "
        "be faster or slower.\n\n"
        "- Fixed costs (~$1.2M/yr) are estimates pending Wrangell Electric audit.\n\n"
        "- The model uses annual averages. It does not capture hourly dispatch, seasonal "
        "hydro variability, or peak demand constraints.\n\n"
        "- CO2 factors (0.7 tonnes/MWh) and diesel energy density (0.01709 MWh/barrel) "
        "are standard industry approximations."
    )

    # ═══════════════════════════════════════════════════════════════════════
    # OUTPUT
    # ═══════════════════════════════════════════════════════════════════════
    out = "/home/kai/Documents/AKEnergy/Wrangell_Energy_Model_Guide.pdf"
    pdf.output(out)
    print(f"PDF written to: {out}")


if __name__ == "__main__":
    build_pdf()
