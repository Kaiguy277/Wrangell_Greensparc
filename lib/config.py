# ─────────────────────────────────────────────────────────────────────────────
# Shared constants: color palette, scenario labels, year range
# ─────────────────────────────────────────────────────────────────────────────

# Three-scenario palette — used consistently in every chart and callout
C_A      = "#dc2626"   # red    — Status Quo: diesel creep, rising rates
C_B      = "#d97706"   # amber  — Expansion Only: capital on ratepayers
C_C      = "#16a34a"   # green  — Expansion + Anchor: rates go down
C_HYDRO        = "#2563eb"              # blue   — SEAPA hydropower in stacked charts
C_DIESEL       = "#f97316"              # orange — diesel in stacked charts
C_HYDRO_FILL   = "rgba(37,99,235,0.75)"   # semi-transparent for stacked areas
C_DIESEL_FILL  = "rgba(249,115,22,0.75)"  # semi-transparent for stacked areas
C_REF    = "#6b7280"   # gray   — reference lines (today's rate, expansion date)

SCENARIO_LABELS = {
    "A": "🔴 Status Quo",
    "B": "🟡 Expansion Only",
    "C": "🟢 Expansion + Anchor",
}
SCENARIO_COLORS = {"A": C_A, "B": C_B, "C": C_C}

YEARS = list(range(2023, 2036))   # 2023 through 2035 inclusive
