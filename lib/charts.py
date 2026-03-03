# ─────────────────────────────────────────────────────────────────────────────
# Plotly chart builders
# ─────────────────────────────────────────────────────────────────────────────

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lib.config import (
    YEARS, SCENARIO_LABELS, SCENARIO_COLORS,
    C_A, C_B, C_C, C_HYDRO, C_DIESEL,
    C_HYDRO_FILL, C_DIESEL_FILL, C_REF,
)
from lib.financial import fmt_dollar


def _vline(fig, x, label, row=None, col=None):
    """Add a dashed vertical reference line at year x."""
    kwargs = dict(row=row, col=col) if row else {}
    fig.add_vline(
        x=x, line_dash="dot", line_color=C_REF, line_width=1.5,
        annotation_text=label, annotation_position="top right",
        annotation_font_size=11, annotation_font_color=C_REF,
        **kwargs,
    )


def chart_rate_trajectory(scenarios, base_rate, expansion_yr, pinned=None, pinned_label="Pinned"):
    """Three-line rate trajectory — the hero chart."""
    fig = go.Figure()

    # Baseline reference
    fig.add_hline(
        y=base_rate, line_dash="dot", line_color=C_REF, line_width=1.5,
        annotation_text=f"2023 rate: {base_rate*100:.1f}¢/kWh",
        annotation_position="bottom right",
        annotation_font_color=C_REF,
    )

    dashes = {"A": "dash", "B": "solid", "C": "solid"}
    widths = {"A": 2, "B": 2, "C": 3}

    # Draw C first, A last so Status Quo line stays visible until scenarios split
    for key in ["C", "B", "A"]:
        df  = scenarios[key]
        fig.add_trace(go.Scatter(
            x=YEARS,
            y=df["rate_kwh"].tolist(),
            mode="lines+markers",
            name=SCENARIO_LABELS[key],
            line=dict(color=SCENARIO_COLORS[key], dash=dashes[key], width=widths[key]),
            marker=dict(size=6 if key != "C" else 8),
            hovertemplate="%{x}: %{y:.4f} $/kWh<extra>" + SCENARIO_LABELS[key] + "</extra>",
        ))

    # Pinned overlay
    if pinned:
        for key in ["C", "B", "A"]:
            df = pinned[key]
            fig.add_trace(go.Scatter(
                x=YEARS,
                y=df["rate_kwh"].tolist(),
                mode="lines",
                name=f"{pinned_label} {SCENARIO_LABELS[key]}",
                line=dict(color=SCENARIO_COLORS[key], dash="dot", width=1),
                opacity=0.4,
                showlegend=(key == "C"),
                hovertemplate="%{x}: %{y:.4f} $/kWh<extra>" + pinned_label + " " + SCENARIO_LABELS[key] + "</extra>",
            ))

    # Scenario C "below today" annotation
    rate_c_2030 = scenarios["C"].loc[2030, "rate_kwh"]
    if rate_c_2030 < base_rate:
        fig.add_annotation(
            x=2030, y=rate_c_2030,
            text=f"↓ {abs(rate_c_2030 - base_rate)*100:.1f}¢ below today",
            showarrow=True, arrowhead=2, arrowcolor=C_C,
            font=dict(color=C_C, size=12, family="Arial"),
            ax=60, ay=-30,
        )

    _vline(fig, expansion_yr, "Expansion online")

    fig.update_layout(
        title="Retail Rate Trajectory — Three Scenarios ($/kWh)",
        xaxis=dict(title="Year", tickmode="linear", tick0=2023, dtick=1, tickangle=-45),
        yaxis=dict(title="Retail Rate ($/kWh)", tickformat="$.3f",
                   range=[0.09, 0.17]),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=480,
        margin=dict(t=80, b=60, l=80, r=40),
    )
    return fig


def chart_diesel_lines(scenarios, expansion_yr, pinned=None, pinned_label="Pinned"):
    """Three lines of diesel MWh/yr by year."""
    fig = go.Figure()
    dashes = {"A": "solid", "B": "dash", "C": "dot"}
    for key in ["A", "B", "C"]:
        df = scenarios[key]
        fig.add_trace(go.Scatter(
            x=YEARS,
            y=df["diesel_mwh"].tolist(),
            mode="lines+markers",
            name=SCENARIO_LABELS[key],
            line=dict(color=SCENARIO_COLORS[key], dash=dashes[key], width=2),
            marker=dict(size=6),
            hovertemplate="%{x}: %{y:,.0f} MWh<extra>" + SCENARIO_LABELS[key] + "</extra>",
        ))

    # Pinned overlay
    if pinned:
        for key in ["A", "B", "C"]:
            df = pinned[key]
            fig.add_trace(go.Scatter(
                x=YEARS,
                y=df["diesel_mwh"].tolist(),
                mode="lines",
                name=f"{pinned_label} {SCENARIO_LABELS[key]}",
                line=dict(color=SCENARIO_COLORS[key], dash="dot", width=1),
                opacity=0.4,
                showlegend=(key == "A"),
            ))

    _vline(fig, expansion_yr, "Expansion online")
    fig.update_layout(
        title="Annual Diesel Backup Usage (MWh/yr)",
        xaxis=dict(title="Year", tickmode="linear", tick0=2023, dtick=1, tickangle=-45),
        yaxis=dict(title="Diesel (MWh/yr)"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=340,
        margin=dict(t=70, b=60, l=80, r=40),
    )
    return fig


def chart_energy_stacks(scenarios, expansion_yr):
    """3-row stacked area chart: hydro + diesel by year, one row per scenario."""
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        subplot_titles=[SCENARIO_LABELS[k] for k in ["A", "B", "C"]],
        vertical_spacing=0.08,
    )
    for i, key in enumerate(["A", "B", "C"], start=1):
        df = scenarios[key]
        # Hydro area
        fig.add_trace(go.Scatter(
            x=YEARS, y=df["hydro_mwh"].tolist(),
            name="SEAPA Hydro" if i == 1 else None,
            showlegend=(i == 1),
            stackgroup="one",
            mode="none",
            fillcolor=C_HYDRO_FILL,
            hovertemplate="%{x}: %{y:,.0f} MWh hydro<extra></extra>",
        ), row=i, col=1)
        # Diesel area
        fig.add_trace(go.Scatter(
            x=YEARS, y=df["diesel_mwh"].tolist(),
            name="Diesel" if i == 1 else None,
            showlegend=(i == 1),
            stackgroup="one",
            mode="none",
            fillcolor=C_DIESEL_FILL,
            hovertemplate="%{x}: %{y:,.0f} MWh diesel<extra></extra>",
        ), row=i, col=1)

    # Expansion line on each subplot
    for i in range(1, 4):
        fig.add_vline(
            x=expansion_yr, line_dash="dot", line_color=C_REF,
            line_width=1, row=i, col=1,
        )

    fig.update_layout(
        title="Energy Mix — SEAPA Hydro vs Diesel (MWh/yr)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=620,
        margin=dict(t=100, b=60, l=80, r=40),
    )
    fig.update_yaxes(title_text="MWh/yr")
    fig.update_xaxes(title_text="Year", row=3, col=1,
                     tickmode="linear", tick0=2023, dtick=1, tickangle=-45)
    return fig


def chart_diesel_cost_bars(scenarios):
    """Grouped bar chart: diesel cost by year, three scenarios."""
    display_yrs = [2023, 2025, 2027, 2029, 2031, 2033, 2035]
    fig = go.Figure()
    for key in ["A", "B", "C"]:
        df = scenarios[key]
        vals = [df.loc[y, "diesel_cost"] for y in display_yrs]
        fig.add_trace(go.Bar(
            name=SCENARIO_LABELS[key],
            x=[str(y) for y in display_yrs],
            y=vals,
            marker_color=SCENARIO_COLORS[key],
            text=[f"${v/1e3:.0f}K" for v in vals],
            textposition="outside",
        ))
    fig.update_layout(
        barmode="group",
        title="Annual Diesel Cost ($/yr)",
        yaxis_title="$/year",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320,
        margin=dict(t=70, b=40, r=40),
    )
    return fig


def chart_expansion_waterfall(debt_svc, anchor_margin):
    """Waterfall: expansion debt → anchor offsets → residual on community."""
    residual = max(0.0, debt_svc - anchor_margin)
    over     = max(0.0, anchor_margin - debt_svc)
    measures = ["absolute", "relative", "total"] if over == 0 else ["absolute", "relative", "relative", "total"]
    xs       = ["Expansion\ndebt service", "Anchor\nmargin offset", "Residual\nfor ratepayers"] if over == 0 else \
               ["Expansion\ndebt service", "Anchor covers\nfull cost", "Rate reduction\nsurplus", "Net community\nimpact"]
    ys       = [-debt_svc, anchor_margin, 0] if over == 0 else [-debt_svc, debt_svc, over, 0]
    texts    = [fmt_dollar(debt_svc), fmt_dollar(anchor_margin),
                fmt_dollar(residual)] if over == 0 else \
               [fmt_dollar(debt_svc), fmt_dollar(debt_svc),
                fmt_dollar(over), fmt_dollar(over)]

    fig = go.Figure(go.Waterfall(
        measure=measures,
        x=xs,
        y=ys,
        text=texts,
        textposition="outside",
        connector={"line": {"color": "#9ca3af"}},
        increasing={"marker": {"color": C_C}},
        decreasing={"marker": {"color": C_A}},
        totals={"marker": {"color": C_B}},
    ))
    fig.update_layout(
        title="Annual Expansion Cost Allocation (representative year)",
        yaxis_title="$/year",
        yaxis_tickformat="$,.0f",
        height=360,
        margin=dict(t=70, b=40, r=40),
    )
    return fig


def chart_cumulative_coverage(debt_svc, anchor_margin, expansion_yr):
    """Cumulative debt vs anchor margin from expansion year → 2035."""
    post_yrs = [y for y in YEARS if y >= expansion_yr]
    cum_debt   = [debt_svc * (y - expansion_yr + 1) for y in post_yrs]
    cum_anchor = [anchor_margin * (y - expansion_yr + 1) for y in post_yrs]

    fig = go.Figure()
    # Shaded area between lines
    fig.add_trace(go.Scatter(
        x=post_yrs + post_yrs[::-1],
        y=cum_anchor + cum_debt[::-1],
        fill="toself",
        fillcolor="rgba(22,163,74,0.15)" if anchor_margin >= debt_svc else "rgba(220,38,38,0.10)",
        line=dict(width=0),
        showlegend=False, hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=post_yrs, y=cum_debt,
        name="Cumulative debt owed",
        line=dict(color=C_A, dash="dash", width=2),
        hovertemplate="%{x}: %{y:$,.0f}<extra>Debt owed</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=post_yrs, y=cum_anchor,
        name="Anchor margin contributed",
        line=dict(color=C_C, width=2.5),
        hovertemplate="%{x}: %{y:$,.0f}<extra>Anchor margin</extra>",
    ))
    fig.update_layout(
        title="Cumulative Expansion Cost vs Anchor Contribution (2027–2035)",
        xaxis=dict(title="Year", tickmode="linear", tick0=expansion_yr, dtick=1),
        yaxis=dict(title="Cumulative $", tickformat="$,.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=320,
        margin=dict(t=70, b=40, l=80, r=40),
    )
    return fig


def chart_household_bills(scenarios, base_rate, hh_kwh, pinned=None, pinned_label="Pinned"):
    """Grouped bar: annual household bill by year, three scenarios."""
    display_yrs = [2023, 2025, 2027, 2029, 2031, 2033, 2035]
    fig = go.Figure()
    for key in ["A", "B", "C"]:
        df = scenarios[key]
        bills = [df.loc[y, "rate_kwh"] * hh_kwh for y in display_yrs]
        fig.add_trace(go.Bar(
            name=SCENARIO_LABELS[key],
            x=[str(y) for y in display_yrs],
            y=bills,
            marker_color=SCENARIO_COLORS[key],
            text=[f"${b:,.0f}" for b in bills],
            textposition="outside",
        ))
    # Reference line: today's bill
    today_bill = base_rate * hh_kwh
    fig.add_hline(
        y=today_bill, line_dash="dot", line_color=C_REF,
        annotation_text=f"2023 bill: ${today_bill:,.0f}",
        annotation_position="top left",
        annotation_font_color=C_REF,
    )
    fig.update_layout(
        barmode="group",
        title=f"Annual Household Bill ({hh_kwh:,} kWh/yr)",
        yaxis_title="$/year",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(t=70, b=40, r=40),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Monthly dispatch chart
# ─────────────────────────────────────────────────────────────────────────────

def chart_monthly_dispatch(monthly_data: dict, scenario: str, expansion_yr: int):
    """Stacked area: hydro + diesel by month, showing seasonal pattern."""
    df = monthly_data[scenario].copy()

    # Create date labels for x-axis
    df["date_label"] = df.apply(lambda r: f"{r['year']}-{r['month']:02d}", axis=1)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date_label"],
        y=df["hydro_mwh"],
        name="SEAPA Hydro",
        stackgroup="one",
        mode="none",
        fillcolor=C_HYDRO_FILL,
        hovertemplate="%{x}: %{y:,.0f} MWh hydro<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["date_label"],
        y=df["diesel_mwh"],
        name="Diesel",
        stackgroup="one",
        mode="none",
        fillcolor=C_DIESEL_FILL,
        hovertemplate="%{x}: %{y:,.0f} MWh diesel<extra></extra>",
    ))

    # Hydro capacity line
    fig.add_trace(go.Scatter(
        x=df["date_label"],
        y=df["hydro_cap"],
        name="Hydro capacity",
        mode="lines",
        line=dict(color=C_REF, dash="dash", width=1.5),
        hovertemplate="%{x}: %{y:,.0f} MWh cap<extra></extra>",
    ))

    # Expansion year marker
    exp_label = f"{expansion_yr}-01"
    if exp_label in df["date_label"].values:
        fig.add_vline(
            x=exp_label, line_dash="dot", line_color=C_REF, line_width=1.5,
            annotation_text="Expansion online",
            annotation_position="top right",
            annotation_font_size=11, annotation_font_color=C_REF,
        )

    fig.update_layout(
        title=f"Monthly Energy Dispatch — {SCENARIO_LABELS[scenario]}",
        xaxis=dict(
            title="Month",
            tickmode="array",
            tickvals=[f"{y}-01" for y in range(2023, 2036)],
            ticktext=[str(y) for y in range(2023, 2036)],
            tickangle=-45,
        ),
        yaxis=dict(title="MWh/month"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        margin=dict(t=80, b=60, l=80, r=40),
    )
    return fig


def chart_monthly_diesel_heatmap(monthly_data: dict, scenario: str):
    """Heatmap: diesel MWh by month (y) and year (x). Reveals winter concentration."""
    df = monthly_data[scenario].copy()
    pivot = df.pivot_table(index="month", columns="year", values="diesel_mwh")

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = go.Figure(go.Heatmap(
        x=pivot.columns.tolist(),
        y=month_labels,
        z=pivot.values,
        colorscale=[[0, "#f0fdf4"], [0.3, "#fef9c3"], [0.6, "#fed7aa"], [1.0, C_A]],
        colorbar=dict(title="MWh"),
        hovertemplate="Year: %{x}<br>Month: %{y}<br>Diesel: %{z:,.0f} MWh<extra></extra>",
    ))

    fig.update_layout(
        title=f"Diesel Usage by Month — {SCENARIO_LABELS[scenario]}",
        xaxis_title="Year",
        yaxis=dict(autorange="reversed"),
        height=360,
        margin=dict(t=60, b=40, l=80, r=40),
    )
    return fig
