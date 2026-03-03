# ─────────────────────────────────────────────────────────────────────────────
# In-app PDF export — generates scenario report from current params
# ─────────────────────────────────────────────────────────────────────────────

import io
from pathlib import Path

from fpdf import FPDF

from lib.config import YEARS
from lib.financial import fmt_dollar


class ScenarioPDF(FPDF):
    """PDF with Greensparc branding."""

    def __init__(self, community_name="Wrangell"):
        super().__init__("P", "mm", "Letter")
        self.community_name = community_name
        self._setup_fonts()

    def _setup_fonts(self):
        """Try to use DejaVu, fall back to Helvetica."""
        dejavu_path = Path("/usr/share/fonts/truetype/dejavu")
        if (dejavu_path / "DejaVuSans.ttf").exists():
            self.add_font("DejaVu", "", str(dejavu_path / "DejaVuSans.ttf"), uni=True)
            self.add_font("DejaVu", "B", str(dejavu_path / "DejaVuSans-Bold.ttf"), uni=True)
            self._font_family = "DejaVu"
        else:
            self._font_family = "Helvetica"

    def header(self):
        if self.page_no() > 1:
            self.set_font(self._font_family, "B", 9)
            self.set_text_color(107, 114, 128)
            self.cell(0, 8, f"{self.community_name} Energy Future | Greensparc", align="L")
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font(self._font_family, "", 8)
        self.set_text_color(156, 163, 175)
        self.cell(0, 10, f"Page {self.page_no()} | Illustrative projections - not a rate-case filing", align="C")

    def section_title(self, title):
        self.set_font(self._font_family, "B", 14)
        self.set_text_color(22, 163, 74)  # green accent
        self.cell(0, 10, title, ln=True)
        self.set_draw_color(22, 163, 74)
        self.line(self.get_x(), self.get_y(), self.get_x() + 60, self.get_y())
        self.ln(4)

    def body_text(self, txt):
        self.set_font(self._font_family, "", 10)
        self.set_text_color(55, 65, 81)
        self.multi_cell(0, 5, txt)
        self.ln(2)

    def key_value(self, key, value):
        self.set_font(self._font_family, "B", 10)
        self.set_text_color(55, 65, 81)
        w = self.get_string_width(key + ":  ")
        self.cell(w, 5, key + ":  ")
        self.set_font(self._font_family, "", 10)
        self.cell(0, 5, str(value), ln=True)


def generate_scenario_pdf(params: dict, scenarios: dict, community_name: str = "Wrangell") -> bytes:
    """
    Generate a PDF report for the current scenario configuration.
    Returns PDF as bytes.
    """
    pdf = ScenarioPDF(community_name)
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Cover Page ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font(pdf._font_family, "B", 24)
    pdf.set_text_color(22, 163, 74)
    pdf.cell(0, 12, f"{community_name} Energy Future", ln=True, align="C")
    pdf.set_font(pdf._font_family, "", 14)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 8, "Greensparc Anchor Customer Scenario Report", ln=True, align="C")
    pdf.ln(10)

    # Executive summary box
    pdf.set_fill_color(240, 253, 244)
    pdf.set_draw_color(22, 163, 74)
    pdf.rect(20, pdf.get_y(), 175, 50, style="DF")
    pdf.set_xy(25, pdf.get_y() + 5)
    pdf.set_font(pdf._font_family, "B", 11)
    pdf.set_text_color(22, 101, 52)
    pdf.cell(0, 6, "Executive Summary", ln=True)
    pdf.set_x(25)
    pdf.set_font(pdf._font_family, "", 10)
    pdf.set_text_color(55, 65, 81)

    cov = params.get("anchor_coverage", 0)
    rate_c_2030 = scenarios["C"].loc[2030, "rate_kwh"]
    rate_a_2030 = scenarios["A"].loc[2030, "rate_kwh"]
    base_rate = params["base_rate"]

    summary = (
        f"A {params['anchor_mw']:.1f} MW anchor at ${params['anchor_tariff_kwh']:.3f}/kWh "
        f"covers {min(cov, 1.0):.0%} of expansion debt. "
        f"By 2030, Scenario C rate: ${rate_c_2030:.4f}/kWh "
        f"({'below' if rate_c_2030 < base_rate else 'above'} today's ${base_rate:.4f}). "
        f"Status Quo would reach ${rate_a_2030:.4f}/kWh."
    )
    pdf.multi_cell(165, 5, summary)
    pdf.ln(15)

    # ── Scenario Parameters ───────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("Current Parameters")

    param_groups = [
        ("System", [
            ("Baseline load", f"{params['base_mwh']:,} MWh/yr"),
            ("SEAPA energy cap", f"{params['seapa_cap']:,} MWh/yr"),
            ("SEAPA wholesale rate", f"${params['seapa_rate']:.0f}/MWh"),
            ("Fixed costs", f"{fmt_dollar(params['fixed_cost'])}/yr"),
            ("Diesel base cost", f"${params['diesel_base_cost']:.0f}/MWh"),
            ("Diesel escalation", f"{params['diesel_escalation']*100:.1f}%/yr"),
        ]),
        ("Growth", [
            ("Phase 1 growth", f"{params['r1']*100:.1f}%/yr"),
            ("Phase 1 ends", str(params['phase1_end'])),
            ("Phase 2 growth", f"{params['r2']*100:.1f}%/yr"),
        ]),
        ("Expansion", [
            ("Online year", str(params['expansion_yr'])),
            ("New energy", f"{params['expansion_new_mwh']:,} MWh/yr"),
            ("Capex", fmt_dollar(params['capex'])),
            ("Debt share", f"{params['w_share']*100:.0f}%"),
            ("Debt service", f"{fmt_dollar(params['debt_service_yr'])}/yr"),
        ]),
        ("Anchor", [
            ("Nameplate", f"{params['anchor_mw']:.1f} MW"),
            ("Capacity factor", f"{params['anchor_cf']:.0%}"),
            ("Annual energy", f"{params['anchor_mwh_yr']:,.0f} MWh/yr"),
            ("Tariff", f"${params['anchor_tariff_kwh']:.3f}/kWh"),
            ("Coverage", f"{min(cov, 1.0):.0%}"),
        ]),
    ]

    for group_name, items in param_groups:
        pdf.set_font(pdf._font_family, "B", 11)
        pdf.set_text_color(22, 163, 74)
        pdf.cell(0, 7, group_name, ln=True)
        for key, val in items:
            pdf.key_value(f"  {key}", val)
        pdf.ln(3)

    # ── Rate Table ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("Rate Projections ($/kWh)")

    # Table header
    pdf.set_font(pdf._font_family, "B", 9)
    pdf.set_fill_color(243, 244, 246)
    col_widths = [25, 45, 45, 45]
    headers = ["Year", "Status Quo", "Expansion Only", "Exp + Anchor"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 7, h, border=1, fill=True, align="C")
    pdf.ln()

    # Table rows
    pdf.set_font(pdf._font_family, "", 9)
    display_years = [2023, 2025, 2027, 2028, 2029, 2030, 2031, 2033, 2035]
    for year in display_years:
        pdf.cell(col_widths[0], 6, str(year), border=1, align="C")
        for key in ["A", "B", "C"]:
            rate_val = scenarios[key].loc[year, "rate_kwh"]
            pdf.cell(col_widths[1 + ["A", "B", "C"].index(key)], 6,
                     f"${rate_val:.4f}", border=1, align="C")
        pdf.ln()

    pdf.ln(8)

    # ── Key Metrics ───────────────────────────────────────────────────────
    pdf.section_title("Key Outcomes")

    avoided_mwh = scenarios["A"]["diesel_mwh"].sum() - scenarios["C"]["diesel_mwh"].sum()
    cost_saved = scenarios["A"]["diesel_cost"].sum() - scenarios["C"]["diesel_cost"].sum()
    hh_kwh = params["hh_kwh"]
    cum_savings = sum(
        (scenarios["A"].loc[y, "rate_kwh"] - scenarios["C"].loc[y, "rate_kwh"]) * hh_kwh
        for y in range(2027, 2036)
    )

    metrics = [
        ("Diesel avoided (C vs A, 2023-2035)", f"{avoided_mwh:,.0f} MWh"),
        ("Diesel cost savings", fmt_dollar(cost_saved)),
        ("CO2 avoided", f"{avoided_mwh * 0.7:,.0f} tonnes"),
        ("Cumulative household savings (2027-2035)", f"{fmt_dollar(cum_savings)} per household"),
        ("Community-wide savings", fmt_dollar(cum_savings * params["n_hh"])),
    ]
    for key, val in metrics:
        pdf.key_value(key, val)

    pdf.ln(10)

    # ── Caveats ───────────────────────────────────────────────────────────
    pdf.section_title("Caveats")
    caveats = [
        "Illustrative projections - not a rate-case or regulatory filing.",
        f"SEAPA wholesale rate (${params['seapa_rate']:.0f}/MWh) is back-calculated, not published.",
        f"Debt share ({params['w_share']:.0%}) is proportional-load estimate.",
        "Diesel costs use fully-loaded estimates including remote fuel delivery.",
        "Two-phase load growth is assumption-based.",
        "Fixed costs are estimates pending audit confirmation.",
    ]
    for caveat in caveats:
        pdf.body_text(f"  - {caveat}")

    return bytes(pdf.output())
