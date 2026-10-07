"""
app.py
-------
Data Breach Intelligence Dashboard
Analysis and Visualization of Publicly Reported Cybersecurity Breaches

MSc Artificial Intelligence & Cybersecurity — University Mini Project

Run with:
    streamlit run app.py
"""

import os
import sys

import pandas as pd
import streamlit as st

# Make sure src/ is importable regardless of working directory
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src import data_preprocessing as prep
from src import analysis as an
from src import visualizations as viz

# ------------------------------------------------------------------
# Page config + global style
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Data Breach Intelligence Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    /* ============================================================
       DESIGN SYSTEM — single source of truth for every color used
       in the app. All rules below reference these variables only.
       ============================================================ */
    :root {
        --bg-main: #fdf5e6;        /* main application background */
        --bg-card: #ffffff;        /* metric cards, dropdown menus, tables */
        --text-primary: #013220;   /* primary dark green — headings, key text */
        --text-secondary: #21421e; /* secondary dark green — body text, labels */
        --accent-soft: #8fbc8f;    /* soft green — borders, accents, hover tints */
        --accent-soft-tint: #eaf3ea; /* very light green tint for subtle fills */
        --line: #d8e6d8;           /* neutral green-compatible border/divider */
    }

    /* ---------- App background ---------- */
    .stApp { background-color: var(--bg-main); }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-card);
        border-right: 1px solid var(--line);
    }
    section[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small { color: var(--text-secondary) !important; }

    /* ---------- Typography ---------- */
    h1, h2 { color: var(--text-primary) !important; letter-spacing: -0.01em; }
    h3, h4, h5 { color: var(--text-secondary) !important; letter-spacing: -0.01em; }
    p, li, span, label, div { color: var(--text-primary); }
    .stMarkdown p { color: var(--text-secondary); }

    /* ---------- KPI metric cards ---------- */
    div[data-testid="stMetric"] {
        background-color: var(--bg-card);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(1, 50, 32, 0.06);
    }
    div[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
    div[data-testid="stMetricDelta"] { color: var(--accent-soft) !important; }
    div[data-testid="stMetricDelta"] svg { fill: var(--accent-soft) !important; }

    /* ---------- Insight callouts ---------- */
    .insight-box {
        background-color: var(--accent-soft-tint);
        border-left: 4px solid var(--accent-soft);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        color: var(--text-primary);
    }
    .insight-box b { color: var(--text-primary); }

    /* ---------- Hero badge (Executive Overview) ---------- */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 6px 14px;
        border-radius: 999px;
        background: var(--bg-card);
        border: 1px solid var(--line);
        font-size: 12.5px;
        color: var(--text-secondary);
        margin-bottom: 14px;
    }
    .hero-badge .dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--accent-soft); flex-shrink: 0;
    }

    /* ---------- Buttons ---------- */
    .stButton > button, .stDownloadButton > button {
        background-color: var(--text-secondary);
        color: #ffffff !important;
        border: 1px solid var(--text-secondary);
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: var(--text-primary);
        border-color: var(--text-primary);
        color: #ffffff !important;
    }
    .stButton > button p, .stDownloadButton > button p { color: #ffffff !important; }

    /* ---------- Text inputs ---------- */
    div[data-baseweb="input"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    div[data-baseweb="input"] input::placeholder { color: var(--text-secondary) !important; opacity: 0.6; }

    /* ---------- Selectbox / Multiselect (closed state, lives inside .stApp) ---------- */
    div[data-baseweb="select"] > div {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--line) !important;
        color: var(--text-primary) !important;
    }
    div[data-baseweb="select"] * { color: var(--text-primary) !important; fill: var(--text-primary) !important; }

    /* Multiselect selected-option tags (pills) */
    span[data-baseweb="tag"] {
        background-color: var(--text-secondary) !important;
        color: #ffffff !important;
    }
    span[data-baseweb="tag"] * { color: #ffffff !important; fill: #ffffff !important; }

    /* ---------- Popover menus / dropdown lists ----------
       These render in a portal appended to <body>, OUTSIDE .stApp, which
       is why sidebar- or app-scoped selectors never reach them and they
       fall back to a dark theme. Rules below are intentionally global
       (not nested under .stApp or the sidebar) so they always apply. */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--line) !important;
    }
    li[role="option"] {
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    li[role="option"]:hover,
    li[aria-selected="true"] {
        background-color: var(--accent-soft-tint) !important;
        color: var(--text-primary) !important;
    }

    /* ---------- Sliders ---------- */
    div[data-testid="stSlider"] { color: var(--text-primary) !important; }
    div[data-baseweb="slider"] div[data-testid="stTickBar"] { background: var(--line) !important; }
    div[data-baseweb="slider"] > div > div { background-color: var(--line) !important; } /* track */
    div[data-baseweb="slider"] > div > div > div { background-color: var(--accent-soft) !important; } /* filled range */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: var(--text-secondary) !important;
        border: 2px solid #ffffff !important;
    }
    div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] { color: var(--text-secondary) !important; }
    div[data-testid="stThumbValue"] { color: var(--text-primary) !important; background-color: var(--bg-card) !important; }

    /* ---------- Radio buttons (page navigation) ---------- */
    div[role="radiogroup"] label { color: var(--text-primary) !important; }
    div[role="radiogroup"] label div:first-child { border-color: var(--accent-soft) !important; }

    /* ---------- Dataframes / tables ---------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
        background-color: var(--bg-card);
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] { color: var(--text-secondary); }
    .stTabs [aria-selected="true"] { color: var(--text-primary) !important; }

    /* ---------- Alerts (info / warning boxes) ---------- */
    div[data-testid="stAlert"] {
        background-color: var(--accent-soft-tint);
        color: var(--text-primary);
        border: 1px solid var(--line);
    }
    div[data-testid="stAlert"] * { color: var(--text-primary) !important; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "original_dataset.csv")
CLEANED_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "cleaned_breaches.csv")


# ------------------------------------------------------------------
# Cached data loading pipeline
# ------------------------------------------------------------------
@st.cache_data(show_spinner="Loading and cleaning breach dataset...")
def get_data():
    df_raw, df_clean = prep.load_and_prepare(DATA_PATH)
    prep.save_cleaned_dataset(df_clean, CLEANED_OUTPUT_PATH)
    return df_raw, df_clean


try:
    df_raw, df_clean = get_data()
except (FileNotFoundError, ValueError) as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()


# ------------------------------------------------------------------
# Sidebar — Filters
# ------------------------------------------------------------------
st.sidebar.title("🛡️ Breach Intelligence")
st.sidebar.markdown("### Filters")

if st.sidebar.button("↺ Reset Filters"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

valid_years = df_clean["BreachYear"].dropna()
min_year = int(valid_years.min()) if not valid_years.empty else 2000
max_year = int(valid_years.max()) if not valid_years.empty else 2025

year_range = st.sidebar.slider(
    "Breach Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    key="year_range",
)

domain_options = sorted(df_clean["Domain"].dropna().unique().tolist())
selected_domains = st.sidebar.multiselect(
    "Organization / Domain",
    options=domain_options,
    default=[],
    help="Leave empty to include all domains.",
    key="domains",
)

verification_status = st.sidebar.selectbox(
    "Verification Status", ["All", "Verified only", "Unverified only"], key="verified"
)
sensitive_status = st.sidebar.selectbox(
    "Sensitive Status", ["All", "Sensitive only", "Non-sensitive only"], key="sensitive"
)
malware_status = st.sidebar.selectbox(
    "Malware Status", ["All", "Malware only", "Non-malware only"], key="malware"
)
spam_status = st.sidebar.selectbox(
    "Spam List Status", ["All", "Spam list only", "Non-spam only"], key="spam"
)


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    filtered = filtered[
        (filtered["BreachYear"].isna())
        | ((filtered["BreachYear"] >= year_range[0]) & (filtered["BreachYear"] <= year_range[1]))
    ]
    if selected_domains:
        filtered = filtered[filtered["Domain"].isin(selected_domains)]
    if verification_status == "Verified only":
        filtered = filtered[filtered["IsVerified"]]
    elif verification_status == "Unverified only":
        filtered = filtered[~filtered["IsVerified"]]
    if sensitive_status == "Sensitive only":
        filtered = filtered[filtered["IsSensitive"]]
    elif sensitive_status == "Non-sensitive only":
        filtered = filtered[~filtered["IsSensitive"]]
    if malware_status == "Malware only":
        filtered = filtered[filtered["IsMalware"]]
    elif malware_status == "Non-malware only":
        filtered = filtered[~filtered["IsMalware"]]
    if spam_status == "Spam list only":
        filtered = filtered[filtered["IsSpamList"]]
    elif spam_status == "Non-spam only":
        filtered = filtered[~filtered["IsSpamList"]]
    return filtered


df_filtered = apply_filters(df_clean)
exploded_filtered = prep.explode_data_classes(df_filtered)

st.sidebar.markdown("---")
st.sidebar.markdown("### Dataset Summary")
st.sidebar.metric("Filtered Records", f"{len(df_filtered):,}")
st.sidebar.metric("Total Records (unfiltered)", f"{len(df_clean):,}")
if df_clean["BreachDate"].notna().any():
    last_date = df_clean["BreachDate"].max()
    st.sidebar.markdown(f"**Last Available Breach Date:** {last_date.date()}")

st.sidebar.markdown("---")
st.sidebar.caption("MSc AI & Cybersecurity — Mini Project")

# ------------------------------------------------------------------
# Top-level navigation
# ------------------------------------------------------------------
PAGES = [
    "Executive Overview",
    "Breach Trend Analysis",
    "Data Exposure Analysis",
    "Cybersecurity Risk Analysis",
    "Breach Explorer",
    "Insights & Conclusion",
]
page = st.sidebar.radio("Navigate", PAGES, key="nav")


# ------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# ------------------------------------------------------------------
if page == "Executive Overview":
    st.markdown(
        "<span class='hero-badge'><span class='dot'></span>Live breach intelligence · "
        "updated dynamically from the dataset</span>",
        unsafe_allow_html=True,
    )
    st.title("Data Breach Intelligence Dashboard")
    st.markdown(
        "**Analysis and Visualization of Publicly Reported Cybersecurity Breaches**"
    )
    st.markdown(
        """
        Organizations and cybersecurity professionals need to understand patterns in
        publicly reported data breaches — which organizations were hit hardest, what data
        was exposed, and how breach activity has evolved over time. This dashboard
        transforms a raw breach intelligence dataset into actionable insight.
        """
    )

    if df_filtered.empty:
        st.warning("No breaches match the current filters. Adjust filters in the sidebar.")
    else:
        st.markdown("### Key Performance Indicators")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Breaches", f"{an.total_breaches(df_filtered):,}")
        c2.metric("Total Records Exposed", f"{an.total_records_exposed(df_filtered):,}")
        c3.metric("Avg Records / Breach", f"{an.average_records_per_breach(df_filtered):,.0f}")
        largest = an.largest_breach(df_filtered)
        c4.metric("Largest Breach", largest["Name"] if not largest.empty else "N/A",
                   f"{int(largest['PwnCount']):,} records" if not largest.empty else "")

        c5, c6, c7 = st.columns(3)
        flags = an.flag_counts(df_filtered)
        c5.metric("Verified Breaches", f"{flags['IsVerified']:,}")
        c6.metric("Sensitive Breaches", f"{flags['IsSensitive']:,}")
        c7.metric("Malware-Related Breaches", f"{flags['IsMalware']:,}")

        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(
                viz.breaches_by_year_chart(an.breaches_per_year(df_filtered)),
                use_container_width=True,
            )
        with col_b:
            st.plotly_chart(
                viz.top_breaches_bar_chart(an.top_n_breaches_by_pwncount(df_filtered, 10)),
                use_container_width=True,
            )

        st.plotly_chart(
            viz.common_data_classes_bar_chart(an.most_common_data_classes(exploded_filtered, 10)),
            use_container_width=True,
        )

        st.markdown("### Key Cybersecurity Insights")
        for insight in an.generate_dynamic_insights(df_filtered, exploded_filtered):
            st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# PAGE 2: BREACH TREND ANALYSIS
# ------------------------------------------------------------------
elif page == "Breach Trend Analysis":
    st.title("📈 Breach Trend Analysis")

    if df_filtered.empty:
        st.warning("No breaches match the current filters. Adjust filters in the sidebar.")
    else:
        year_counts = an.breaches_per_year(df_filtered)
        year_totals = an.records_exposed_per_year(df_filtered)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(viz.breaches_by_year_chart(year_counts), use_container_width=True)
        with col2:
            st.plotly_chart(viz.records_exposed_by_year_chart(year_totals), use_container_width=True)

        st.plotly_chart(viz.breach_trend_line_chart(year_counts), use_container_width=True)
        st.plotly_chart(viz.breaches_heatmap_year_month(df_filtered), use_container_width=True)

        st.markdown("### Observations")
        peak_year = an.year_with_most_breaches(df_filtered)
        peak_records_year = an.year_with_most_records_exposed(df_filtered)
        if peak_year:
            st.markdown(
                f"<div class='insight-box'>Breach reporting peaked in "
                f"<b>{peak_year[0]}</b> with <b>{peak_year[1]}</b> breaches.</div>",
                unsafe_allow_html=True,
            )
        if peak_records_year:
            st.markdown(
                f"<div class='insight-box'>The highest volume of exposed records in a "
                f"single year occurred in <b>{peak_records_year[0]}</b> "
                f"(<b>{peak_records_year[1]:,}</b> records).</div>",
                unsafe_allow_html=True,
            )


# ------------------------------------------------------------------
# PAGE 3: DATA EXPOSURE ANALYSIS
# ------------------------------------------------------------------
elif page == "Data Exposure Analysis":
    st.title("🗂️ Data Exposure Analysis")

    if df_filtered.empty:
        st.warning("No breaches match the current filters. Adjust filters in the sidebar.")
    else:
        top_n = st.slider("Number of top data categories to display", 5, 20, 15)
        st.plotly_chart(
            viz.common_data_classes_bar_chart(an.most_common_data_classes(exploded_filtered, top_n)),
            use_container_width=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(viz.data_classes_distribution_chart(df_filtered), use_container_width=True)
        with col2:
            st.plotly_chart(
                viz.top_data_class_count_bar_chart(an.top_breaches_by_data_class_count(df_filtered, 10)),
                use_container_width=True,
            )

        st.markdown("### Top Breaches Exposing Multiple Data Types")
        st.dataframe(
            an.top_breaches_by_data_class_count(df_filtered, 15),
            use_container_width=True,
            hide_index=True,
        )


# ------------------------------------------------------------------
# PAGE 4: CYBERSECURITY RISK ANALYSIS
# ------------------------------------------------------------------
elif page == "Cybersecurity Risk Analysis":
    st.title("🔐 Cybersecurity Risk Analysis")

    if df_filtered.empty:
        st.warning("No breaches match the current filters. Adjust filters in the sidebar.")
    else:
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.plotly_chart(viz.verified_donut_chart(df_filtered), use_container_width=True)
        with row1_col2:
            st.plotly_chart(viz.sensitive_donut_chart(df_filtered), use_container_width=True)

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.plotly_chart(viz.malware_donut_chart(df_filtered), use_container_width=True)
        with row2_col2:
            st.plotly_chart(viz.spam_donut_chart(df_filtered), use_container_width=True)

        st.markdown("### Distribution & Extremes")
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(viz.pwncount_log_histogram(df_filtered), use_container_width=True)
        with col_b:
            st.plotly_chart(viz.pwncount_boxplot(df_filtered), use_container_width=True)

        st.plotly_chart(viz.pwncount_vs_dataclasses_scatter(df_filtered), use_container_width=True)
        st.plotly_chart(viz.numeric_correlation_heatmap(df_filtered), use_container_width=True)

        flags = an.flag_counts(df_filtered)
        st.markdown("### Risk Flag Summary")
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Fabricated", f"{flags['IsFabricated']:,}")
        fc2.metric("Retired", f"{flags['IsRetired']:,}")
        fc3.metric("Spam List", f"{flags['IsSpamList']:,}")
        fc4.metric("Subscription-Free", f"{flags['IsSubscriptionFree']:,}")

        st.markdown("### Extreme Breaches (Outliers by Records Exposed)")
        extreme = an.identify_extreme_breaches(df_filtered)
        if extreme.empty:
            st.info("No statistically extreme outliers detected in the current filtered dataset.")
        else:
            st.dataframe(extreme, use_container_width=True, hide_index=True)


# ------------------------------------------------------------------
# PAGE 5: BREACH EXPLORER
# ------------------------------------------------------------------
elif page == "Breach Explorer":
    st.title("🔎 Breach Explorer")

    search_term = st.text_input("Search by Organization Name, Title, or Domain")

    explorer_df = df_filtered.copy()
    if search_term:
        term = search_term.lower()
        mask = (
            explorer_df["Name"].str.lower().str.contains(term, na=False)
            | explorer_df["Title"].str.lower().str.contains(term, na=False)
            | explorer_df["Domain"].str.lower().str.contains(term, na=False)
        )
        explorer_df = explorer_df[mask]

    st.markdown(f"**{len(explorer_df):,} breach(es) match the current search and filters.**")

    display_cols = [
        "Name", "Domain", "BreachDate", "PwnCount", "DataClasses",
        "IsVerified", "IsSensitive", "IsMalware",
    ]
    display_cols = [c for c in display_cols if c in explorer_df.columns]

    st.dataframe(
        explorer_df[display_cols].sort_values("PwnCount", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "PwnCount": st.column_config.NumberColumn("Records Exposed", format="%d"),
            "BreachDate": st.column_config.DateColumn("Breach Date"),
        },
    )

    csv_bytes = explorer_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered results as CSV",
        data=csv_bytes,
        file_name="filtered_breaches.csv",
        mime="text/csv",
    )


# ------------------------------------------------------------------
# PAGE 6: INSIGHTS AND CONCLUSION
# ------------------------------------------------------------------
elif page == "Insights & Conclusion":
    st.title("💡 Insights & Conclusion")

    if df_filtered.empty:
        st.warning("No breaches match the current filters. Adjust filters in the sidebar.")
    else:
        st.markdown("### Major Trends Discovered")
        for insight in an.generate_dynamic_insights(df_filtered, exploded_filtered):
            st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

        st.markdown("### Top 10 Largest Breaches (Reference)")
        st.dataframe(
            an.top_n_breaches_by_pwncount(df_filtered, 10),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Limitations of the Dataset")
        st.markdown(
            """
            <div class='insight-box'>
            This dataset reflects <b>publicly reported</b> breaches only and does not represent
            every breach that has occurred. Unverified breaches (see the Cybersecurity Risk
            Analysis page) carry additional uncertainty, and PwnCount figures are self-reported
            or third-party estimates rather than audited figures. BreachDate values are also
            sometimes approximate, particularly for older or unverified incidents.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Recommendations")
        st.markdown(
            """
            <div class='insight-box'>
            Organizations should prioritize monitoring for credential exposure given how
            frequently passwords and email addresses appear among compromised data
            categories, treat unverified breach reports as directional rather than
            conclusive, and pay particular attention to breaches flagged as sensitive or
            malware-related when prioritizing incident response and user notification.
            </div>
            """,
            unsafe_allow_html=True,
        )

st.sidebar.markdown("---")
