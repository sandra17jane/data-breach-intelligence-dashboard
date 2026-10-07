"""
visualizations.py
-------------------
Plotly chart-building functions for the Data Breach Intelligence
Dashboard.

DESIGN SYSTEM
-------------
There is exactly ONE theme function in this file — apply_dashboard_theme().
Every chart-building function below calls it before returning its figure.
Do not add a second theme function; extend apply_dashboard_theme() instead
so every chart always stays visually consistent.

Palette (matches the Streamlit app's CSS in app.py):
    #fdf5e6  cream            — not used directly on charts; charts use
                                 white/near-white so data stays legible,
                                 per the "very light background" requirement
    #013220  primary dark green — chart titles, axis titles, primary data
    #21421e  secondary dark green — axis ticks, legend text, secondary data
    #8fbc8f  soft green        — accents, "negative/off" states, gridline tint
"""

import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------
# Shared theme constants — the single source of truth for color.
# Every function in this file pulls its colors from here only.
# ---------------------------------------------------------------
BG_COLOR = "#ffffff"          # plot background — very light, per spec
PAPER_COLOR = "#ffffff"       # paper (figure) background
GRID_COLOR = "#dcebdc"        # subtle green-tinted gridline, clearly visible
LINE_COLOR = "#c3ddc3"        # zero-lines / borders

TEXT_PRIMARY = "#013220"      # main font: chart titles, axis titles
TEXT_SECONDARY = "#21421e"    # secondary font: axis ticks, legend text

PRIMARY_GREEN = "#013220"     # primary dark green — main series color
SECONDARY_GREEN = "#21421e"   # secondary dark green — secondary series
SOFT_GREEN = "#8fbc8f"        # soft green — accents / tints / "off" states
SOFT_GREEN_LIGHT = "#d7e8d7"  # very light green tint (negative donut slices)
RISK_ACCENT = "#8b3a2e"       # muted rust — the ONLY non-green hue in the
                               # palette, used solely to flag risk/malware
                               # states where a second, contrasting color is
                               # needed for readability. Deliberately muted,
                               # not bright red, to stay within the brief.

# Ordered palette for multi-category charts — greens only, light to dark,
# with the muted rust reserved as the final "alert" entry if ever needed.
PALETTE = [
    PRIMARY_GREEN,
    SOFT_GREEN,
    SECONDARY_GREEN,
    "#4f7942",   # mid olive-green — supporting shade
    "#a9cba9",   # pale green — supporting shade
    "#0b3d2e",   # near-black green — supporting shade, still on-palette
]

HOVER_BG = "#ffffff"
HOVER_TEXT = "#013220"
HOVER_BORDER = "#8fbc8f"


def apply_dashboard_theme(fig: go.Figure, title: str = None) -> go.Figure:
    """The single centralized Plotly theme for the entire dashboard.

    Every chart-building function in this module must call this before
    returning its figure. Do not create a second/competing theme
    function — extend this one instead so all charts stay consistent.
    """
    fig.update_layout(
        paper_bgcolor=PAPER_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color=TEXT_PRIMARY, family="-apple-system, Segoe UI, sans-serif", size=13),
        title=dict(text=title, font=dict(size=17, color=TEXT_PRIMARY)) if title else None,
        margin=dict(l=40, r=30, t=60 if title else 20, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_PRIMARY, size=12),
        ),
        hoverlabel=dict(
            bgcolor=HOVER_BG,
            font_color=HOVER_TEXT,
            bordercolor=HOVER_BORDER,
        ),
    )
    fig.update_xaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=LINE_COLOR,
        color=TEXT_SECONDARY,
        title_font=dict(color=TEXT_PRIMARY),
        tickfont=dict(color=TEXT_SECONDARY),
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=LINE_COLOR,
        color=TEXT_SECONDARY,
        title_font=dict(color=TEXT_PRIMARY),
        tickfont=dict(color=TEXT_SECONDARY),
    )
    return fig


# ---------------------------------------------------------------
# Time-series charts
# ---------------------------------------------------------------
def breaches_by_year_chart(breach_year_counts) -> go.Figure:
    fig = px.bar(
        breach_year_counts,
        x="BreachYear",
        y="BreachCount",
        labels={"BreachYear": "Year", "BreachCount": "Number of Breaches"},
        color_discrete_sequence=[PRIMARY_GREEN],
    )
    return apply_dashboard_theme(fig, "Number of Breaches by Year")


def records_exposed_by_year_chart(records_year_totals) -> go.Figure:
    fig = px.area(
        records_year_totals,
        x="BreachYear",
        y="TotalRecordsExposed",
        labels={"BreachYear": "Year", "TotalRecordsExposed": "Total Records Exposed"},
        color_discrete_sequence=[SECONDARY_GREEN],
    )
    fig.update_traces(line=dict(width=2), fillcolor="rgba(143, 188, 143, 0.35)")
    return apply_dashboard_theme(fig, "Total Records Exposed by Year")


def breach_trend_line_chart(breach_year_counts) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=breach_year_counts["BreachYear"],
            y=breach_year_counts["BreachCount"],
            mode="lines+markers",
            line=dict(color=PRIMARY_GREEN, width=3),
            marker=dict(size=7, color=PRIMARY_GREEN, line=dict(color="#ffffff", width=1)),
            name="Breaches",
        )
    )
    return apply_dashboard_theme(fig, "Breach Frequency Trend Over Time")


# ---------------------------------------------------------------
# Bar charts
# ---------------------------------------------------------------
def top_breaches_bar_chart(top_breaches_df) -> go.Figure:
    fig = px.bar(
        top_breaches_df.sort_values("PwnCount"),
        x="PwnCount",
        y="Name",
        orientation="h",
        labels={"PwnCount": "Records Exposed", "Name": "Organization"},
        color="PwnCount",
        color_continuous_scale=[SOFT_GREEN_LIGHT, PRIMARY_GREEN],
        hover_data=["Domain", "BreachDate"],
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(textfont_color=TEXT_PRIMARY)
    return apply_dashboard_theme(fig, "Top 10 Largest Breaches by Records Exposed")


def common_data_classes_bar_chart(data_classes_df) -> go.Figure:
    fig = px.bar(
        data_classes_df.sort_values("Frequency"),
        x="Frequency",
        y="DataClass",
        orientation="h",
        labels={"Frequency": "Number of Breaches", "DataClass": "Data Category"},
        color_discrete_sequence=[SECONDARY_GREEN],
    )
    return apply_dashboard_theme(fig, "Most Commonly Exposed Data Categories")


def top_domains_bar_chart(top_domains_df) -> go.Figure:
    fig = px.bar(
        top_domains_df.sort_values("BreachCount"),
        x="BreachCount",
        y="Domain",
        orientation="h",
        labels={"BreachCount": "Number of Breaches", "Domain": "Domain"},
        color_discrete_sequence=[PRIMARY_GREEN],
    )
    return apply_dashboard_theme(fig, "Top Domains by Number of Breaches")


def top_data_class_count_bar_chart(top_by_class_count_df) -> go.Figure:
    fig = px.bar(
        top_by_class_count_df.sort_values("NumberOfDataClasses"),
        x="NumberOfDataClasses",
        y="Name",
        orientation="h",
        labels={"NumberOfDataClasses": "Number of Data Categories Exposed", "Name": "Organization"},
        color_discrete_sequence=[SECONDARY_GREEN],
        hover_data=["Domain", "PwnCount"],
    )
    return apply_dashboard_theme(fig, "Breaches Exposing the Most Data Categories")


# ---------------------------------------------------------------
# Pie / donut charts
# ---------------------------------------------------------------
def _donut(df, flag_col: str, title: str, positive_label: str, negative_label: str) -> go.Figure:
    counts = df[flag_col].value_counts()
    labels = [positive_label if v else negative_label for v in counts.index]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=counts.values,
                hole=0.55,
                marker=dict(colors=[PRIMARY_GREEN, SOFT_GREEN_LIGHT], line=dict(color="#ffffff", width=2)),
                textinfo="percent+label",
                textfont=dict(color=TEXT_PRIMARY, size=13),
                # Percent text sitting on the dark slice needs to flip to
                # white for contrast; Plotly picks this automatically when
                # insidetextfont differs from the base font color.
                insidetextfont=dict(color="#ffffff", size=13),
                outsidetextfont=dict(color=TEXT_PRIMARY, size=13),
            )
        ]
    )
    return apply_dashboard_theme(fig, title)


def verified_donut_chart(df) -> go.Figure:
    return _donut(df, "IsVerified", "Verified vs Unverified Breaches", "Verified", "Unverified")


def sensitive_donut_chart(df) -> go.Figure:
    return _donut(df, "IsSensitive", "Sensitive vs Non-Sensitive Breaches", "Sensitive", "Non-Sensitive")


def malware_donut_chart(df) -> go.Figure:
    return _donut(df, "IsMalware", "Malware vs Non-Malware Breaches", "Malware", "Non-Malware")


def spam_donut_chart(df) -> go.Figure:
    return _donut(df, "IsSpamList", "Spam List vs Non-Spam List Breaches", "Spam List", "Non-Spam List")


# ---------------------------------------------------------------
# Distribution charts
# ---------------------------------------------------------------
def pwncount_histogram(df) -> go.Figure:
    fig = px.histogram(
        df,
        x="PwnCount",
        nbins=40,
        color_discrete_sequence=[PRIMARY_GREEN],
        labels={"PwnCount": "Records Exposed"},
    )
    return apply_dashboard_theme(fig, "Distribution of Records Exposed (Raw)")


def pwncount_log_histogram(df) -> go.Figure:
    fig = px.histogram(
        df,
        x="LogPwnCount",
        nbins=40,
        color_discrete_sequence=[SECONDARY_GREEN],
        labels={"LogPwnCount": "Log10(Records Exposed)"},
    )
    return apply_dashboard_theme(fig, "Distribution of Records Exposed (Log-Scaled)")


def pwncount_boxplot(df) -> go.Figure:
    fig = px.box(
        df,
        y="PwnCount",
        points="outliers",
        color_discrete_sequence=[PRIMARY_GREEN],
        hover_data=["Name"] if "Name" in df.columns else None,
    )
    fig.update_traces(marker=dict(color=RISK_ACCENT, size=5), line=dict(color=PRIMARY_GREEN))
    return apply_dashboard_theme(fig, "Box Plot of Records Exposed")


def data_classes_distribution_chart(df) -> go.Figure:
    fig = px.histogram(
        df,
        x="NumberOfDataClasses",
        nbins=df["NumberOfDataClasses"].max() + 1 if len(df) else 1,
        color_discrete_sequence=[SOFT_GREEN],
        labels={"NumberOfDataClasses": "Number of Data Categories Exposed"},
    )
    fig.update_traces(marker_line_color=PRIMARY_GREEN, marker_line_width=1)
    return apply_dashboard_theme(fig, "Distribution of Number of Data Categories Exposed per Breach")


# ---------------------------------------------------------------
# Multivariate charts
# ---------------------------------------------------------------
def pwncount_vs_dataclasses_scatter(df) -> go.Figure:
    fig = px.scatter(
        df,
        x="NumberOfDataClasses",
        y="PwnCount",
        color="IsSensitive",
        size="PwnCount",
        size_max=40,
        hover_name="Name",
        hover_data={"Domain": True, "IsVerified": True, "IsMalware": True, "PwnCount": ":,", "NumberOfDataClasses": True},
        color_discrete_map={True: RISK_ACCENT, False: PRIMARY_GREEN},
        log_y=True,
        labels={
            "NumberOfDataClasses": "Number of Data Categories Exposed",
            "PwnCount": "Records Exposed (log scale)",
            "IsSensitive": "Sensitive",
        },
    )
    return apply_dashboard_theme(fig, "Records Exposed vs. Data Categories Compromised")


def breach_bubble_by_year(df) -> go.Figure:
    """Bubble chart: year vs pwncount, sized by number of data
    classes, colored by malware status.
    """
    plot_df = df.dropna(subset=["BreachYear"])
    fig = px.scatter(
        plot_df,
        x="BreachYear",
        y="PwnCount",
        size="NumberOfDataClasses",
        color="IsMalware",
        hover_name="Name",
        log_y=True,
        size_max=35,
        color_discrete_map={True: RISK_ACCENT, False: PRIMARY_GREEN},
        labels={"BreachYear": "Year", "PwnCount": "Records Exposed (log scale)", "IsMalware": "Malware-Related"},
    )
    return apply_dashboard_theme(fig, "Breach Landscape: Year vs Records Exposed vs Malware Status")


# ---------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------
def numeric_correlation_heatmap(df) -> go.Figure:
    """Correlation heatmap across meaningful numeric / derived
    fields only (not arbitrary booleans).
    """
    numeric_cols = ["PwnCount", "LogPwnCount", "NumberOfDataClasses", "BreachYear"]
    available = [c for c in numeric_cols if c in df.columns]
    corr = df[available].corr()

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale=[[0, SOFT_GREEN_LIGHT], [0.5, "#fdf5e6"], [1, PRIMARY_GREEN]],
            zmin=-1,
            zmax=1,
            text=corr.round(2).values,
            texttemplate="%{text}",
            textfont=dict(color=TEXT_PRIMARY),
            colorbar=dict(
                title=dict(text="Correlation", font=dict(color=TEXT_PRIMARY)),
                tickfont=dict(color=TEXT_SECONDARY),
            ),
        )
    )
    return apply_dashboard_theme(fig, "Correlation Heatmap: Breach Metrics")


def breaches_heatmap_year_month(df) -> go.Figure:
    """Heatmap of breach counts by year (rows) and month (columns) —
    useful for spotting seasonal reporting patterns.
    """
    plot_df = df.dropna(subset=["BreachYear", "BreachMonth"])
    pivot = (
        plot_df.groupby(["BreachYear", "BreachMonth"])
        .size()
        .reset_index(name="Count")
        .pivot(index="BreachYear", columns="BreachMonth", values="Count")
        .fillna(0)
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[str(int(m)) for m in pivot.columns],
            y=[str(int(y)) for y in pivot.index],
            colorscale=[[0, "#fdf5e6"], [1, PRIMARY_GREEN]],
            colorbar=dict(
                title=dict(text="Breaches", font=dict(color=TEXT_PRIMARY)),
                tickfont=dict(color=TEXT_SECONDARY),
            ),
        )
    )
    fig.update_xaxes(title="Month")
    fig.update_yaxes(title="Year")
    return apply_dashboard_theme(fig, "Breach Frequency Heatmap (Year x Month)")
